class FinalValue(Exception):
    "Break hanlders chain with given value."
    def __init__(self, value):
        self.value = value
