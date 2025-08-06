"""General utility functions."""

import logging
import math
import re

import rando

re_float = re.compile(r'\d*\.?\d+$')
re_text = re.compile('[a-z_][a-z0-9_]*$')

error_tables = {}
random = rando.Rando(1)

def add_error(value: int, max_error: int, floor: int=0, ceil: int=99999999) -> int:
    """Returns a random number in the range -max_error...max_error.
    
    <floor> is the lowest number that will be returned.
    """
    if max_error not in error_tables:
        error_tables[max_error] = make_error_table(max_error)
    errs = error_tables[max_error]

    err = random.choice(errs)
    value += err
    return min(max(value, floor), ceil)

def get_float(text: str,
              min_val: float=0.0,
              max_val: float=1.0,
              inc: bool=False) -> float | None:
    """Returns string as float in range or None."""
    assert text != '', f'Float number is missing'
    if re_float.match(text):
        result = float(text)
        if inc:
            if min_val <= result <= max_val:
                return result
        else:
            if min_val <= result < max_val:
                return result

def get_int(text: str, min_val: int=0, max_val: int=128) -> int | None:
    """Returns string as int in range or None."""
    assert text != '', f'Int number is missing'
    if text.isdigit():
        result = int(text)
        if min_val <= result < max_val:
            return result 

def get_signed_int(text: str) -> int | None:
    """Returns possibly signed number as int or None."""
    assert text != '', f'Number is missing'
    neg = False
    if not text.isdigit():
        neg = text.startswith('-')
        text = text[1:]
    if text.isdigit():
        number = int(text)
        if neg:
            number = -number
        return number

def is_name(text: str) -> bool:
    return re_text.match(text) is not None

def make_error_table(amount: int) -> list[int]:
    """Makes an error table
    Maximum error == ±<amount>.
    Smaller errors are more probable.
    """
    table = []
    for err in range(amount + 1):
        for no in range(-err, err + 1):
            table.append(no)
    amount //= 2
    if amount > 0:
        table.extend(make_error_table(amount))
    return table

def make_in_range(value: int, max_value: int, desc: str) -> int:
    """Coerces a value into range.
    
    Valid range is 0 <= value < max_value.
    """
    if value >= max_value:
        logging.warning(f'{desc} value {value} too high')
        value = max_value - 1
    elif value < 0:
        logging.warning(f'{desc} value {value} too low')
        value = 0
    return value

def pct_to_range(pct: int, min_val: int=0, max_val: int=127, desc: str='') -> int:
    """Converts a percentage into a value within range.
    
    Valid range is 0 <= value < max_value.
    """
    if pct > 100:
        logging.warning(f'{desc} value {pct}% too high')
        pct = 100
    elif pct < 0:
        logging.warning(f'{desc} value {pct}% too low')
        pct = 0
    value = math.ceil((max_val - min_val) * pct / 100)
    return value

def truth(text: str) -> bool | None:
    lower = text.lower()
    if lower in ['t', 'true', 'y', 'yes', '1']:
        return True
    if lower in ['f', 'false', 'n', 'no', '0']:
        return False
    logging.warning(f'Unknown truth value "{text}"')
    return None
