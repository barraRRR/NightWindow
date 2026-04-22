import sys
import os
import itertools
import threading
import functools
from datetime import datetime
from readchar import readkey
from time import sleep
from typing import Optional
from config import TEXTS, LOGO


class Spinner:
    """
    A threaded spinner animation for displaying loading status in the terminal.
    Runs a Braille animation on a background thread while the main thread processes data.
    """
    def __init__(self, msg: str = 'Loading...'):
        """
        Initialize a Spinner instance.
        
        Args:
            msg (str): The message to display alongside the spinner (default: 'Loading...')
        """
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.delay: float = 0.1
        self.msg: str = msg
        self.running: bool = False
        self.thread: Optional[threading.Thread] = None

    def _spin(self) -> None:
        """
        Internal method that runs the spinning animation on a separate thread.
        Continuously cycles through spinner characters and updates the terminal.
        """
        while self.running:
            sys.stdout.write(f'\r{next(self.spinner)} {self.msg}')
            sys.stdout.flush()
            sleep(self.delay)
    
    def __enter__(self) -> None:
        """
        Context manager entry point. Starts the spinner animation on a background thread.
        
        Returns:
            None: Returns self for context manager protocol.
        """
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context manager exit point. Stops the spinner animation and clears the terminal line.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_value: Exception value if an exception occurred
            traceback: Exception traceback if an exception occurred
        """
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * (len(self.msg) + 2) + '\r')
        sys.stdout.flush()


def with_spinner(msg_key: str, success_key: str = None, delay: float = 0.5):
    """
    Decorator that wraps a function with a loading spinner and optional success message.
    Displays a spinner while the function executes, then shows a success message.
    
    Args:
        msg_key (str): Key to retrieve loading message from TEXTS['status']
        success_key (str): Key to retrieve success message from TEXTS['status'] (optional)
        delay (float): Delay in seconds before showing success message (default: 0.5)
        
    Returns:
        function: Decorated function that runs with spinner feedback.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            load_msg = TEXTS['status'].get(msg_key, 'Loading...')
            
            with Spinner(load_msg):
                result = func(*args, **kwargs)

                if delay > 0:
                    sleep(delay)
                
                if success_key:
                    success_msg = TEXTS['status'].get(success_key, success_key)
                    sys.stdout.write('\r' + ' ' * (len(load_msg) + 2) + '\r')
                    print(f'{success_msg}')
            return result
        return wrapper
    return decorator


def get_option(msg: str, options: list[str]) -> str:
    """
    Display a menu with options and wait for single-key user input.
    Allows instant keypresses without requiring Enter key.
    
    Args:
        msg (str): The prompt message to display
        options (list[str]): List of option strings to display
        
    Returns:
        str: The selected option number as a string (1-indexed).
    """
    print(msg)
    for i, option in enumerate(options, start=1):
        print(f'   [{i}] - {option}') 
    print('   [q] - Quit')

    while True:
        try:
            key = readkey().lower()
            if key == 'q':
                app_exit()            
            selection = int(key)
            if 1 <= selection <= len(options):
                return key
            raise ValueError(
                TEXTS['errors']['invalid_option']
                )
        except ValueError as e:
            print('\n', e)


def end() -> None:
    """
    Display an end-of-program prompt and wait for user confirmation or exit.
    Allows user to press Enter to return to menu or 'q' to quit.
    """
    print(TEXTS['ui']['end_prompt'])

    while True:
        key = readkey().lower()
        if key == '\n':
            break
        elif key == 'q':
            app_exit()


def clear() -> None:
    """
    Clear the terminal screen and display the application logo.
    Uses platform-specific commands (cls for Windows, clear for Unix-like systems).
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(LOGO)


def app_exit() -> None:
    """
    Clean exit function. Clears the terminal and displays a farewell message before exiting.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    sys.exit(TEXTS['ui']['exit'])

