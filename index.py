import sqlite3
from datetime import datetime
import sys
import os

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
    # Print data as a table with lables id, catagory, start_time, duration
    print('id\tcatagory\tstart_time\tduration')
    for row in result:
        print(str(row[0]) + '\t' + row[1] + '\t' + row[2] + '\t' + convert_minutes_to_hours_and_minutes(row[3]))

def convert_minutes_to_hours_and_minutes(minutes):
    hours = int(minutes / 60)
    minutes = int(minutes % 60)
    return str(hours) + ' hours ' + str(minutes) + ' minutes'

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

# input menu for user to select an option 1-4 create a new time entry, close time entry, view time entries, delete time entry
def menu():
    print('1. New time entry')
    print('2. Clock out')
    print('3. View time entries')
    print('4. Delete a time entry')
    print('5. Exit')
    try:
        option = int(input('Enter an option: '))
    except ValueError:
        print('An error occured, please enter a number 1-5')
        return menu()
    if option == 1:
        create_time_entry()
    elif option == 2:
        close_last_time_entry()
    elif option == 3:
        view_time_entries()
    elif option == 4:
        delete_time_entry()
    elif option == 5:
        sys.exit()
    else:
        print('An error occured, please enter a number 1-5')
        return menu()

setupDB()
menu()
conn.close()
