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
    def __init__(self, msg: str = 'Loading...'):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.delay: float = 0.1
        self.msg: str = msg
        self.running: bool = False
        self.thread: Optional[threading.Thread] = None

    def _spin(self) -> None:
        while self.running:
            sys.stdout.write(f'\r{next(self.spinner)} {self.msg}')
            sys.stdout.flush()
            sleep(self.delay)
    
    def __enter__(self) -> None:
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * (len(self.msg) + 2) + '\r')
        sys.stdout.flush()


def with_spinner(msg_key: str, success_key: str = None, delay: float = 0.5):
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


def get_filename(date: datetime, city: str) -> str:
    safe_date = date.strftime('%Y%m%d')
    safe_city = city.strip().lower().replace(' ', '_')

    return f'nightwindow_{safe_date}_{safe_city}.gif'


def end() -> None:
    print(TEXTS['ui']['end_prompt'])

    while True:
        key = readkey().lower()
        if key == '\n':
            break
        elif key == 'q':
            app_exit()


def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')
    print(LOGO)


def app_exit() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')
    sys.exit(TEXTS['ui']['exit'])

