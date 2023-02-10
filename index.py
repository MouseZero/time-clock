import sqlite3
from datetime import datetime, timedelta
import sys
import os
import pandas as pd

# create the database if it does not exist
database = 'time_entries.db'
if not os.path.exists(database):
    open(database, 'a').close()

# connect to the database
conn = sqlite3.connect(database)
c = conn.cursor()

def setupDB():
    # if statement to check if the 'time_entry' table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='time_entry'")
    result = c.fetchone()
    if result is None:
        # create the table if it does not exist
        c.execute('''CREATE TABLE time_entry (
            id INTEGER PRIMARY KEY,
            date DATE,
            start_time TIME,
            end_time TIME,
            duration REAL,
            catagory TEXT,
        )''')

def get_date_from_input():
    date_str = input("Enter a date in the format (YYYY-MM-DD): ")
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date
    except ValueError:
        print("Incorrect date format, should be YYYY-MM-DD")
        return None

# function name end_time_entry that gets the last time_netry record and update the end_time (with the current time), duration fields
def close_last_time_entry():
    # get the last time entry
    c.execute("SELECT * FROM time_entry ORDER BY id DESC LIMIT 1")
    result = c.fetchone()
    if result is None:
        return
    # get the start time from the last time entry
    start_time = result[2]
    # get the current time
    end_time = datetime.now().strftime('%H:%M:%S')
    # get the duration in seconds
    duration = datetime.strptime(end_time, '%H:%M:%S') - datetime.strptime(start_time, '%H:%M:%S')
    # update the time entry
    c.execute("UPDATE time_entry SET end_time=?, duration=? WHERE id=?", (end_time, duration.total_seconds(), result[0]))
    conn.commit()

# function name delete_time_entry that deletes a time entry by id
def delete_time_entry():
    view_time_entries()
    # get the id of the time entry to delete
    id = input('Enter the id of the time entry to delete: ')
    # delete the time entry by id
    c.execute("DELETE FROM time_entry WHERE id=?", (id,))
    conn.commit()
    print('Time entry deleted')
    return menu()

# function to create a new time entry
def create_time_entry():
    close_last_time_entry()
    # current date as 'date' variable
    date = datetime.now().strftime('%Y-%m-%d')
    start_time = datetime.now().strftime('%H:%M:%S')
    catagory = get_user_selection_of_catagory()
    c.execute("INSERT INTO time_entry (date, start_time, catagory) VALUES (?, ?, ?)", (date, start_time, catagory))
    conn.commit()

def view_time_entries():
    # get all time_entries today print id, catagory, start_time, duration
    c.execute("SELECT id, catagory, start_time, duration FROM time_entry WHERE date=?", (datetime.now().strftime('%Y-%m-%d'),))
    result = c.fetchall()
    if result is None:
        return
    # Print data as a table with lables id, catagory, start_time, duration using pandas
    df = pd.DataFrame(result, columns=['id', 'catagory', 'start_time', 'duration'])
    df['duration'] = df['duration'].apply(convert_seconds_to_hours_and_minutes)
    print(df)

def convert_seconds_to_hours_and_minutes(minutes):
    hours = minutes // 3600
    minutes = (minutes % 3600) // 60
    return str(int(hours)) + 'h ' + str(int(minutes)) + 'm'

def get_unique_catorgories_from_last_10_days_in_time_entries():
    c.execute("SELECT DISTINCT catagory FROM time_entry WHERE date BETWEEN date('now', '-10 day') AND date('now')")
    result = c.fetchall()
    if result is None:
        return
    return result

def get_user_selection_of_catagory():
    catagories = get_unique_catorgories_from_last_10_days_in_time_entries()
    catagories.append(('Other ...',))
    # User selects a catogory and return the selection
    print('Select a catagory')
    for i in range(len(catagories)):
        print(str(i) + '. ' + catagories[i][0])
    try:
        option = int(input('Enter an option: '))
    except ValueError:
        print('An error occured, please enter a number 1-' + str(len(catagories)))
        return get_user_selection_of_catagory()
    if option >= 0 and option < len(catagories) - 1:
        return catagories[option][0]
    elif option == len(catagories) - 1:
        newOption = input('Enter a new catagory: ');
        return newOption
    else:
        print('An error occured, please enter a number 1-' + str(len(catagories)))
        return get_user_selection_of_catagory()

def view_catagories():
    print('Catagory Sums from ' + datetime.now().strftime('%Y/%m/%d'))
    # get all catagories print catagory, duration sum (in hours and minutes)) from todays time entries
    c.execute("SELECT catagory, SUM(duration) FROM time_entry WHERE date=? GROUP BY catagory", (datetime.now().strftime('%Y-%m-%d'),))
    result = c.fetchall()
    if result is None:
        return
    # Print data as a table with lables id, catagory, start_time, duration using pandas
    df = pd.DataFrame(result, columns=['catagory', 'duration'])
    df['duration'] = df['duration'].apply(convert_seconds_to_hours_and_minutes)
    print(df)

def view_sprint_report(start_date):
    formatedStartDate = start_date.strftime('%Y/%m/%d')
    date2WeeksLater = start_date + timedelta(days=14)
    formatedDate2WeeksLater = date2WeeksLater.strftime('%Y/%m/%d')
    print('Catagory Summory from ' + formatedStartDate + ' - ' + formatedDate2WeeksLater)
    # get all catagories print catagory, duration sum (in hours and minutes)) from todays time entries
    c.execute("SELECT catagory, SUM(duration) FROM time_entry WHERE date BETWEEN ? AND date(?, '+14 day') GROUP BY catagory", (start_date, start_date))
    result = c.fetchall()
    if result is None:
        return
    # Print data as a table with lables id, catagory, start_time, duration using pandas
    df = pd.DataFrame(result, columns=['catagory', 'duration'])
    df['duration'] = df['duration'].apply(convert_seconds_to_hours_and_minutes)
    print(df)

def menu():
    print('1. New time entry')
    print('2. Clock out')
    print('3. Print entries')
    print('4. Print Catagories')
    print('5. Delete a time entry')
    print('6. Print sprint report')
    print('7. Exit')
    try:
        option = int(input('Enter an option: '))
    except ValueError:
        print('An error occured, please enter a number 1-7')
        return menu()
    if option == 1:
        create_time_entry()
    elif option == 2:
        close_last_time_entry()
    elif option == 3:
        view_time_entries()
    elif option == 4:
        view_catagories()
    elif option == 5:
        delete_time_entry()
    elif option == 6:
        start_date = get_date_from_input()
        view_sprint_report(start_date)
    elif option == 7:
        sys.exit()
    else:
        print('An error occured, please enter a number 1-7')
        return menu()

setupDB()
while(True):
    menu()
conn.close()
