"""
    Project 4: Work Log with Database
    Team Treehouse Python Techdegree

    Author: Kevin Valverde
    Created: 11/16/2016
    Last Updated: 11/16/2016

    Note: Building off of prior work log from Project 3. Added the database model and reworked all the options.

    Features - Minimum Requirements
    1. Add a new entry or lookup existing
    2. date, employee name, task name, time spent, optional notes
    3. lookup by employee, date, search term
    4. give list of dates and allow one to be selected
    5. exact string search should look through name or notes and return corresponding entries

    Features - Exceeds Expectations
    7. User can quit at any time by typing quit
    8. User can search by date range
    9. Multiple employees with same name are all found and possible matches given
    10. User can page through records (Previous, Next)

    Test Coverage
    I'm learning about unit tests and using coverage.py but I couldn't figure out how to implement tests when the script
    is asking for user input and my methods don't have return values.
    So, test coverage is 0%

"""

from datetime import datetime, timedelta
from peewee import *
import re
import sys

db = SqliteDatabase('work_log.db')


class Entry(Model):
    """database model for work log entries"""

    date = DateTimeField(default=datetime.now)
    employee = CharField(max_length=255, unique=True)
    task_title = CharField(max_length=255)
    task_notes = TextField()
    minutes = IntegerField(default=0)

    class Meta:
        database = db


class WorkLog:
    """Work log program"""

    def __init__(self):
        print('----------------------------------------\n'
              '--------- Welcome to Work Log! ---------\n\n'
              'Instructions are wrapped in parentheses.\n'
              'Example: (C)reate means you type the letter C to run the Create command\n\n'
              'Type (M)enu at any time to return to the main menu.\n'
              'Type (Q)uit at any time to quit and exit Work Log.\n')

        # initialize the database and table if they don't exist
        db.connect()
        db.create_tables([Entry], safe=True)

    def main(self):
        """Generates the main menu"""

        while True:
            print('Main Menu:')
            user_input = input('What would you like to do? (C)reate new record or (L)ookup existing? ').lower().strip()
            self.check_input(user_input)

            if user_input == 'c':
                print('Great! Let\'s create a new log entry!\n')
                self.create_entry()
            elif user_input == 'l':
                print('Awesome! Let\'s look up some entries!\n')
                self.lookup_entry()

    def create_entry(self):
        emp_name_input = input('What is your name? ')
        self.check_input(emp_name_input)
        title_input = input('First give the entry a title: ')
        self.check_input(title_input)
        notes_input = input('Now, write in some notes for the entry: ')
        self.check_input(notes_input)
        min_input = input('How many minutes? (example: 30.5) ')
        self.check_input(min_input)

        while True:
            try:
                float(min_input)
                break
            except ValueError:
                min_input = input(
                    'Whoops, something is wrong with your input. How many minutes was that? (example 1.75) ')
        while True:
            proceed = input('\nDoes this look right?\n\nEmployee: {}, Task Title: {}, Task Notes: {},  Time Spent: {} minutes\n\n'
                            '(Y/N): '.format(emp_name_input, title_input, notes_input, min_input)).lower().strip()
            self.check_input(proceed)

            if proceed == 'y':
                # update CSV with entry
                entry = {'Employee': emp_name_input, 'Task Title': title_input, 'Task Notes': notes_input,
                         'Time Spent': min_input}
                self.add_entry(entry)
                print('Entry successfully created!\n')
                break
            elif proceed == 'n':
                temp_input = input('Shoot!, would you like to try that again? (Y/N) ').lower().strip()
                self.check_input(temp_input)

                if temp_input == 'y':
                    self.create_entry()
                elif temp_input == 'n':
                    self.main()
            else:
                print('Sorry, didn\'t catch that. Type Y for "Yes, that looks good" or N for "No, that is wrong."')

    def lookup_entry(self):
        search_action = None
        print('How would you like to search?\n'
              '1. Find by (E)mployee name\n'
              '2. Find by (D)ate\n'
              '3. Find by (S)earch term\n')

        search_action = input("Enter E, D, or S: ").lower().strip()
        self.check_input(search_action)

        while search_action not in ['e', 'd', 's']:
            search_action = input("Sorry, please choose E, D, or S.")
            self.check_input(search_action)

        self.search_entries(search_action)

    def check_input(self, input):
        if input.lower() == 'q':
            self.quit()
        elif input.lower() == 'm':
            print('')
            self.main()

    def quit(self):
        print('\nGoodbye!')
        sys.exit()

    def add_entry(self, entry):
        """Add an entry"""
        Entry.create(employee=entry['Employee'], task_title=entry['Task Title'], task_notes=entry['Task Notes'],
                     minutes=entry['Time Spent'])

    def search_entries(self, search_action):
        """Search an entry by employee name, date, or text"""
        if search_action == 'e':
            search_query = input('Enter the employee name you want to search for: ')
        elif search_action == 'd':
            print('Enter the date range you want to search for (format MM/DD/YYYY).')
            beg_date = input('Beginning date (i.e. MM/DD/YYYY): ')
            while True:
                try:
                    beg_date = datetime.strptime(beg_date, '%m/%d/%Y')
                    break
                except ValueError:
                    beg_date = input('Whoops, make sure it is the correct format (i.e. MM/DD/YYYY): ')
            end_date = input('Beginning date (i.e. MM/DD/YYYY): ')
            while True:
                try:
                    end_date = datetime.strptime(end_date, '%m/%d/%Y')
                    break
                except ValueError:
                    end_date = input('Whoops, make sure it is the correct format (i.e. MM/DD/YYYY): ')

            if beg_date <= end_date:
                search_query = [beg_date, end_date]
            else:
                search_query = [end_date, beg_date]

            search_query[1] = search_query[1] + timedelta(hours=23, minutes=59, seconds=59)
        elif search_action == 's':
            search_query = input('Enter the text you want to search for: ')
        else:
            search_query = None

        self.view_entries(search_query, search_action)

    def view_entries(self, search_query=None, search_action=None):
        """View previous entries"""
        entries = Entry.select().order_by(Entry.date.desc())

        if search_query:
            if search_action == 'e':
                # check possible matches
                possible_entries = entries.where([Entry.employee.contains(search_query)])
                employee_names = []
                for entry in possible_entries:
                    if entry.employee not in employee_names:
                        employee_names.append(entry.employee)

                if len(employee_names) > 1:
                    print('Several possible matches. Please choose one.')
                    j = 1
                    for name in employee_names:
                        print('{}) {}'.format(j, name))
                        j += 1
                    action = input('Select the number corresponding to the employee name: ')
                    while True:
                        try:
                            action = int(action) - 1
                            break
                        except ValueError:
                            action = input('Whoops, didn\'t catch that. Select the number of the employee name: ')

                    search_query = employee_names[action]

                    entries = entries.where([Entry.employee == search_query])
                else:
                    entries = possible_entries

            elif search_action == 'd':
                entries = entries.where([Entry.date.between(search_query[0], search_query[1])])
            elif search_action == 's':
                entries = entries.where((Entry.task_title.contains(search_query)) | (Entry.task_notes.contains(search_query)))
            else:
                search_query = None

        if len(entries) > 0:

            if len(entries) == 1:
                print('\nFound 1 entry.\n')
            else:
                print('\nFound {} entries.\n'.format(len(entries)))

            entry_list = []
            for entry in entries:
                entry_list.append(entry)

            i = 0
            while True:
                timestamp = entry_list[i].date.strftime('%A %B %d, %Y %I:%M%p')
                print('{}) {}'.format(i + 1, timestamp))
                print('='*len(timestamp))
                print('Employee: {} | Task: {} | Time spent: {} minutes'.format(entry_list[i].employee, entry_list[i].task_title, entry_list[i].minutes))
                print('Notes: {}\n'.format(entry_list[i].task_notes))

                action = input('What now? (P)revious, (N)ext, (D)elete, or (M)enu? ').lower().strip()
                self.check_input(action)
                if action == 'n':
                    if i == len(entry_list) - 1:
                        i = 0
                    else:
                        i += 1
                    continue
                elif action == 'p':
                    i -= 1
                    if i < 0:
                        i = len(entry_list) - 1
                    continue
                elif action == 'd':
                    self.delete_entry(entry_list[i])
                    del entry_list[i]
                    if len(entry_list) > 0:
                        i = 0

            print('No more entries.\n')
        else:
            print('\nThere are no entries.\n')

    def delete_entry(self, entry):
        """Delete an entry"""
        if input('Are you sure? (Y/N) ').lower().strip() == 'y':
            entry.delete_instance()
            print("Entry deleted!\n")


if __name__ == '__main__':
    work_log = WorkLog()
    work_log.main()
