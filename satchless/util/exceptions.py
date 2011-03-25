class FinalValue(Exception):
    "Force a value and break the handler chain"
    def __init__(self, value):
        self.value = value
