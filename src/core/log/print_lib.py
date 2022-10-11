import inspect
from datetime import datetime

from src.global_constants import DEBUG, LOG_SHOW_INSPECT


def clear_text(text: str) -> str:
    for color in ['\033[92m', '\033[0m', '\033[94m', '\033[91m', '\033[1m', '\033[93m']:
        text = text.replace(color, "")
    return text


class ConsoleColors:
    DEBUG = '\033[92m'
    SIMPLE = '\033[0m'
    INFO = '\033[94m'
    ERROR = '\033[91m'
    BOLD = '\033[1m'
    WARNING = '\033[93m'
    ERROR_HEADER = f'{BOLD}{ERROR}'
    ERROR_BODY = f'{SIMPLE}{ERROR}'


def print_base(mode: str, text: any, module: str, colors: list) -> None:
    """
    Custom print. Example: [$mode] $module: $text
    :param mode: DEBUG or ERROR
    :param text: Your print text
    :param module: module's name
    :return: None
    """
    print(f"{colors[0]}{datetime.now():%Y.%m.%d %H:%M:%S} [{mode}] {module}:{colors[1]}", *text)


def print_d(*text: any) -> None:
    """
    Debug print version
    :param text: Your print text
    :return: None
    """
    if DEBUG:
        if LOG_SHOW_INSPECT:
            current_frame = inspect.stack()[1]
            module = inspect.getmodule(current_frame[0])
            print_base("DEBUG", text, f"{module.__name__}|{current_frame.lineno} ",
                       [ConsoleColors.DEBUG, ConsoleColors.SIMPLE])
        else:
            print_base("DEBUG", text, "",
                       [ConsoleColors.DEBUG, ConsoleColors.SIMPLE])


def print_i(*text: any) -> None:
    """
    Info print version
    :param text: Your print text
    :return: None
    """
    if LOG_SHOW_INSPECT:
        current_frame = inspect.stack()[1]
        module = inspect.getmodule(current_frame[0])
        if module is not None:
            module_name = module.__name__
        else:
            module_name = "HZ "
        print_base("INFO", text, f"{module_name}|{current_frame.lineno} ",
                   [ConsoleColors.INFO, ConsoleColors.SIMPLE])
    else:
        print_base("INFO", text, "",
                   [ConsoleColors.INFO, ConsoleColors.SIMPLE])


def print_e(*text: any) -> None:
    """
    'Error' print version
    :param text: Your print text
    :return: None
    """
    if LOG_SHOW_INSPECT:
        current_frame = inspect.stack()[1]
        module = inspect.getmodule(current_frame[0])
        if module is not None:
            module_name = module.__name__
        else:
            module_name = "UNKNOWN"
        print_base("ERROR", text, f"{module_name}:{current_frame.lineno} ",
                   [ConsoleColors.ERROR_HEADER, ConsoleColors.ERROR_BODY])
    else:
        print_base("ERROR", text, "",
                   [ConsoleColors.ERROR_HEADER, ConsoleColors.ERROR_BODY])
