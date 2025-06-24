import utils

def test_signed_number():
    assert utils.get_signed_int('11') == 11
    assert utils.get_signed_int('-22') == -22
    assert utils.get_signed_int('+33') == 33
    assert utils.get_signed_int('bad') == None
    assert utils.get_signed_int('+bad') == None
    assert utils.get_signed_int('-bad') == None
