import src.rando as rando

def test_choice():
    """Test that all choices are approximately likely.

    There is no easy way to check this other than looking at the results.
    """
    random = rando.Rando(1234)
    items: list = [0,1,2,3,4,5,6,7,8,9]
    results = [0] * len(items)
    for _ in range(1000):
        result = random.choice(items)
        results[result] = results[result] + 1
    print(results)
    print('done')