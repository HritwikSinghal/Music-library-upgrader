import os

from Base import main


def start(test=0):
    if test:
        main.start(1)
    else:
        print("""
            This program will Download songs songs in your library with upgraded quality.
            For more info, visit https://github.com/HritwikSinghal/Music-library-upgrader
        """)

        print('''
            Warning: This program is in early stages so it may download wrong song sometimes.
                        It will store downloaded songs of each dir in folder named 'Downloaded_songs'
                        which will be located in the dir itself.
                        Enter 1 TO RUN OR 0 TO EXIT
        ''')

        x = input()

        if x == 1:
            print("Starting Program....")
            main.start(test)

            print("""
                    If there were errors during running this program, please upload log file
                    named 'Music-library-repairer_LOGS.txt' in each dir and open an issue on github
                    you can find those log files by using default search in folders or by manually
                    finding each.
                """)
            print('''
                    Thank you for Using this program....
                    By Hritwik
                    https://github.com/HritwikSinghal
                ''')
        else:
            print("Exiting....")
            exit(0)


if os.path.isfile('Base/test_bit.py'):
    test = 1
else:
    test = 0

start(test=test)

# todo: add logs
