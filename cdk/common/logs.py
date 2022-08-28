import logging
import sys


def setlog():
    app_log = logging.getLogger('cdk')
    app_log.setLevel(logging.INFO)

    if app_log.hasHandlers():
        app_log.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    fmt = '[time=%(asctime)s] [%(filename)s:%(lineno)s - %(funcName)10s() ] [%(levelname)-7s] %(message)s'
    console_handler.setFormatter(logging.Formatter(
        fmt=fmt, datefmt='%m/%d/%Y %I:%M:%S %p'))
    app_log.addHandler(console_handler)

    return app_log
