import random

MAX_RANDOM = 10000
table = [0.0] * MAX_RANDOM

random.seed(1)
# Fill table with random numbers in range [0.0, 1.0)
for n in range(MAX_RANDOM):
    table[n] = random.random()

class Rando:
    """A pseudo-random number generator.
    It provides numbers in the range [0.0, 1.0) by indexing into a table
    of predetermined random numbers.
    It is used to ensure that a series of random number requests are
    repeatable for a given seed. Results using the python random module
    would vary depending on how much it had been called elsewhere.
    """
    def __init__(self, seed: int):
        assert 0 <= seed < MAX_RANDOM
        self.index = seed

    @property
    def number(self) -> float:
        """Returns the next pseudo-random number."""
        index = self.index
        self.index = (index + 1) % len(table)
        return table[index]

    def test(self, value: float) -> bool:
        """Returns True when <value> is greater than a random number."""
        assert value < 1.0
        return value > self.number
