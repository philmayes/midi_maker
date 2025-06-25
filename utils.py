import logging
import re

re_float = re.compile(r'\d*\.?\d+$')

def get_float(text: str, min_val: float=0.0, max_val: float=1.0) -> float | None:
    """Returns string as float in range or None."""
    assert text != '', f'Float number is missing'
    if re_float.match(text):
        result = float(text)
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
