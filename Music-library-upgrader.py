import os

from src import main


def start(test=0):
    if test:
        main.start(1)
    else:

        print("""
            ___  ___          _        _     _ _                            _   _                           _           
            |  \/  |         (_)      | |   (_) |                          | | | |                         | |          
            | .  . |_   _ ___ _  ___  | |    _| |__  _ __ __ _ _ __ _   _  | | | |_ __   __ _ _ __ __ _  __| | ___ _ __ 
            | |\/| | | | / __| |/ __| | |   | | '_ \| '__/ _` | '__| | | | | | | | '_ \ / _` | '__/ _` |/ _` |/ _ \ '__|
            | |  | | |_| \__ \ | (__  | |___| | |_) | | | (_| | |  | |_| | | |_| | |_) | (_| | | | (_| | (_| |  __/ |   
            \_|  |_/\__,_|___/_|\___| \_____/_|_.__/|_|  \__,_|_|   \__, |  \___/| .__/ \__, |_|  \__,_|\__,_|\___|_|   
                                                                     __/ |       | |     __/ |                          
                                                                    |___/        |_|    |___/                           
                """)

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

        if x == '1':
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


if os.path.isfile('src/test_bit.py'):
    test = 1
else:
    test = 0

start(test=test)

# todo : add automatic support where it will download all songs that are auto-matched and leaves others
# todo: app support for extra terms to be added to end of search url to enhance results

# todo : add m4a support
# todo: add mode for old songs which checks year < 2000 and other fixes
# todo: add logs
# todo: add support to download songs from txt file with song names

"""
Rd burman
op nayyer
Laxmikant pyarelal
Mohd rafi
soundtrack


Revival
instrumental

"""