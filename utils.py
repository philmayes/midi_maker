import logging

default_volume = 100

def get_signed_number(text: str) -> int | None:
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
