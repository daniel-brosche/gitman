"""Common exceptions, classes, and functions."""

import os
import sys
import argparse
import logging

from . import settings


class WideHelpFormatter(argparse.HelpFormatter):
    """Command-line help text formatter with wider help text."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, max_help_position=40, **kwargs)


class WarningFormatter(logging.Formatter):
    """Logging formatter that displays verbose formatting for WARNING+."""

    def __init__(self, default_format, verbose_format, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_format = default_format
        self.verbose_format = verbose_format

    def format(self, record):
        """A hack to change the formatting style dynamically."""
        # pylint: disable=protected-access
        if record.levelno > logging.INFO:
            self._style._fmt = self.verbose_format
        else:
            self._style._fmt = self.default_format
        return super().format(record)


def positive_int(value):
    """Custom `int` that must be positive."""
    value = int(value)
    if value < 1:
        raise TypeError
    return value


class _Config:
    """Share configuration options."""

    MAX_VERBOSITY = 4

    verbosity = 0
    indent_level = 0


def configure_logging(count=0):
    """Configure logging using the provided verbosity count."""
    if count == -1:
        level = settings.QUIET_LOGGING_LEVEL
        default_format = settings.DEFAULT_LOGGING_FORMAT
        verbose_format = settings.LEVELED_LOGGING_FORMAT
    elif count == 0:
        level = settings.DEFAULT_LOGGING_LEVEL
        default_format = settings.DEFAULT_LOGGING_FORMAT
        verbose_format = settings.LEVELED_LOGGING_FORMAT
    elif count == 1:
        level = settings.VERBOSE_LOGGING_LEVEL
        default_format = settings.VERBOSE_LOGGING_FORMAT
        verbose_format = settings.VERBOSE_LOGGING_FORMAT
    elif count == 2:
        level = settings.VERBOSE2_LOGGING_LEVEL
        default_format = settings.VERBOSE_LOGGING_FORMAT
        verbose_format = settings.VERBOSE_LOGGING_FORMAT
    elif count == 3:
        level = settings.VERBOSE2_LOGGING_LEVEL
        default_format = settings.VERBOSE2_LOGGING_FORMAT
        verbose_format = settings.VERBOSE2_LOGGING_FORMAT
    else:
        level = settings.VERBOSE2_LOGGING_LEVEL - 1
        default_format = settings.VERBOSE2_LOGGING_FORMAT
        verbose_format = settings.VERBOSE2_LOGGING_FORMAT

    # Set a custom formatter
    logging.basicConfig(level=level)
    logging.captureWarnings(True)
    formatter = WarningFormatter(default_format, verbose_format,
                                 datefmt=settings.LOGGING_DATEFMT)
    logging.root.handlers[0].setFormatter(formatter)
    logging.getLogger('yorm').setLevel(max(level, settings.YORM_LOGGING_LEVEL))

    # Warn about excessive verbosity
    if count > _Config.MAX_VERBOSITY:
        msg = "Maximum verbosity level is {}".format(_Config.MAX_VERBOSITY)
        logging.warning(msg)
        _Config.verbosity = _Config.MAX_VERBOSITY
    else:
        _Config.verbosity = count


def indent():
    """Increase the indent of future output lines."""
    _Config.indent_level += 1


def dedent(level=None):
    """Decrease (or reset) the indent of future output lines."""
    if level is None:
        _Config.indent_level = max(0, _Config.indent_level - 1)
    else:
        _Config.indent_level = level


def newline():
    """Write a new line to standard output."""
    show("")


def show(*messages, color=None,
         file=sys.stdout, log=logging.getLogger(__name__)):
    """Write to standard output or error if enabled."""
    for message in messages:
        if _Config.verbosity == 0:
            text = ' ' * 2 * _Config.indent_level + style(message, color)
            print(text, file=file)
        elif _Config.verbosity >= 1:
            message = message.strip()
            if message and log:
                if color == 'error':
                    log.error(message)
                else:
                    log.info(message)


BOLD = '\033[1m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
RESET = '\033[0m'

COLORS = dict(
    path='',
    git_rev=BOLD + BLUE,
    git_dirty=BOLD + MAGENTA,
    git_changes=YELLOW,
    shell_output=CYAN,
    shell_error=YELLOW,
    message=BOLD + WHITE,
    success=BOLD + GREEN,
    error=BOLD + RED,
)


def style(msg, name):
    is_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    supports_ansi = sys.platform != 'win32' or 'ANSICON' in os.environ
    if not (is_tty and supports_ansi):
        return msg

    if name == 'shell':
        return msg.replace("$ ", BOLD + GREEN + "$ " + RESET)

    color = COLORS.get(name)
    if color:
        return color + msg + RESET

    if msg:
        assert color is not None, \
            "Unknown style name requested: {!r}".format(name)

    return msg
