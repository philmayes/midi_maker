import utils

def test_get_float():
    assert utils.get_float('11') == None
    assert utils.get_float('1') == None
    assert utils.get_float('0.11') == 0.11
    assert utils.get_float('bad') == None
    assert utils.get_float('-5.4') == None

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
