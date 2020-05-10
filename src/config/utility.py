import logging
logger = logging.getLogger("app")

def convert_none(s):
    if s is None:
        return None
    if s == 'None':
        return None
    if s == '':
        return None
    return s

def str_to_integer(s):
    try:
        s = convert_none(s)
        if s is None:
            return None
        return int(s)

    except Exception:
        logger.error(f"wired string:{s}")
        s = None

    return s

def str_to_int(s):
    s = str_to_integer(s)

    if s is None:
        return 0

    return s

def convert_to_bool(s):
    s = convert_none(s)
    if s is None:
        return False
    if type(s) is bool:
        return s
    if type(s) is str:
        return s in {'1', 'True', 'true'}
    if type(s) is int:
        return s == 1
    return False
