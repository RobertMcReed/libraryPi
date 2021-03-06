import termios, fcntl, sys, os
from asciimatics.effects import Cycle, Stars, Julia
from asciimatics.renderers import FigletText
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import StopApplication
from asciimatics.event import KeyboardEvent
from title import title
from getpass import getpass
import bcrypt


def stop_on_keypress(event):
    if isinstance(event, KeyboardEvent):
        raise StopApplication("User terminated app")


def julia(screen):
    effects = [Julia(screen)]
    screen.play([Scene(effects)], unhandled_input=stop_on_keypress)


def concur_labs(screen):
    effects = [
        Cycle(
            screen,
            FigletText("LibraryPi", font='big'),
            int(screen.height / 2 - 8)),
        Cycle(
            screen,
            FigletText("ConcurLabs", font='small'),
            int(screen.height / 2 + 3)),
        Stars(screen, 100)
    ]
    screen.play([Scene(effects)], unhandled_input=stop_on_keypress)


def start_labs():
    Screen.wrapper(concur_labs)


def start_julia():
    Screen.wrapper(julia)


def wait_for_keys(message, keys=True):
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    print(message)

    try:
        while 1:
            try:
                c = sys.stdin.read(1)
                if keys is True:
                    if c:
                        return
                elif c in keys:
                    return c
            except IOError:
                pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        os.system('clear')


def login_or_signup():
    title("LibraryPi", "", "Concur Labs")

    message = """
Welcome to the Concur Labs Library!

You can check out and return books at your leisure.




Please CREATE an account or LOGIN.


[1] LOGIN to an Existing Account
    
[2] CREATE an Account

[3] Instructions

[J] Julia Set Visualizer

[Q] Quit

"""
    wait_keys = ['1', '2', '3', 'j', 'J', 'q', 'Q']

    return wait_for_keys(message, wait_keys)



def signup(add_user_to_db):
    email = ''
    password = ''

    while len(email) == 0:
        title("Create an Account")
        email = input('Email: ')

    email = email.lower()

    while len(password) == 0:
        title("Create an Account")
        print("Email: {}".format(email))
        password = getpass('Password: ')

    hash = bcrypt.hashpw(password, bcrypt.gensalt(6))
    user = {'email': email, 'hash': hash}
    user = add_user_to_db(user)

    return user


def login(check_credentials_in_db):
    email = ''
    password = ''

    while len(email) == 0:
        title("Login")
        email = input('Email: ')

    email = email.lower()

    while len(password) == 0:
        title("Login")
        print("Email: {}".format(email))
        password = getpass('Password: ')

    user = {'email': email, 'password': password}
    user = check_credentials_in_db(user)

    return user


def handle_auth(add_user_to_db, check_credentials_in_db):
    while True:
        intent = login_or_signup()

        if intent == '1':
            user, error = login(check_credentials_in_db)
            if error == 'not found':
                error = 'That email address is not in our system. If this is your first time using our library, please create an account.'
            elif error == 'unauthorized':
                error = 'Your password is incorrect.'
        elif intent == '2':
            user, error = signup(add_user_to_db)
            if error == 'duplicate':
                error = 'There is already an account associated with that email address.'
        elif intent == '3':
            display_instructions()
            continue
        elif intent.lower() == 'j':
            start_julia()
            continue
        else:
            start_labs()
            continue

        if error:
            title("Authentication Error")

            message = """Uh oh. {}

Press any key to return to the main menu.\n\n""".format(error)
            wait_for_keys(message)
            continue

        new_user = intent == '2'

        return user, new_user


def greet(user, get_display_name):
    title("Welcome, {}!".format(user[0]))

    isbns = user[2:4]
    books = [isbn for isbn in isbns if isbn != 'None']
    num_books = len(books)

    message = "You currently have {} {} checked out.".format(num_books, 'book' if num_books == 1 else 'books')

    if num_books == 2:
        message += '\n\n\nYou must return a book before checking out any more.\n'

    if num_books > 0:
        message += """
    
        
[1] {}        
""".format(get_display_name(books[0]))

    if num_books > 1:
        message += """
        
[2] {}        
""".format(get_display_name(books[1]))

    message += "\n\n\nPress any key to to start the video feed.\n\n"
    wait_for_keys(message)


def display_instructions(new_user=False):
    title("Using the Library")
    message = """1) Wait for the video stream to initialize.

2) Hold the barcode of a book up to the camera. 

   If the camera can read it, its information will be displayed.

3) Once the book has been identified, press "Y" to check it out, or "R" to return it. 

   You may have at most two books checked out at the same time.
   
   Make sure the video window is focused before typing.
   
4) To quit and logout, press "Q".



Press any key to {}.\n\n""".format('begin' if new_user else 'return')
    wait_for_keys(message)
