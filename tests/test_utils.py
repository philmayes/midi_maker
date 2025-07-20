import src.utils as utils

def test_get_float():
    assert utils.get_float('11') == None
    assert utils.get_float('1') == None
    assert utils.get_float('0.11') == 0.11
    assert utils.get_float('0.11', 0.0, 1.0) == 0.11
    assert utils.get_float('0.11', 0.2, 1.0) == None
    assert utils.get_float('bad') == None
    assert utils.get_float('-5.4') == None
    assert utils.get_float('1.0', inc=True) == 1.0

def test_get_int():
    assert utils.get_int('11') == 11
    assert utils.get_int('1') == 1
    assert utils.get_int('0.11') == None
    assert utils.get_int('bad') == None
    assert utils.get_int('-5') == None

def test_signed_number():
    assert utils.get_signed_int('11') == 11
    assert utils.get_signed_int('-22') == -22
    assert utils.get_signed_int('+33') == 33
    assert utils.get_signed_int('bad') == None
    assert utils.get_signed_int('+bad') == None
    assert utils.get_signed_int('-bad') == None

def test_is_name():
    assert utils.is_name('fred')
    assert utils.is_name('_')
    assert utils.is_name('_fred1')
    assert utils.is_name('f1red')
    assert not utils.is_name('1fred')
    assert not utils.is_name('1Fred')
    assert not utils.is_name('1fred!')

def test_get_error():
    for i in range(20):
        print(f'{i}= ', end='')
        for j in range(20):
            # Print results to assess the distribution by eye.
            # Use pytest -rP ..\tests\test_utils.py
            v2: int = utils.add_error(100, i)
            print(f' {v2}', end='')
            # Check that negative results are not returned.
            v2: int = utils.add_error(0, i)
            assert v2 >= 0
        print()
