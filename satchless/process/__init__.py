__all__ = ['InvalidData', 'Step', 'ProcessManager']


class InvalidData(Exception):
    """
    Raised for by step validation process
    """
    pass


class Step(object):
    """
    A single step in a multistep process
    """
    def __str__(self):
        raise NotImplementedError()  # pragma: no cover

    def validate(self):
        raise NotImplementedError()  # pragma: no cover


class ProcessManager(object):
    """
    A multistep process handler
    """
    def __iter__(self):
        raise NotImplementedError()  # pragma: no cover

    def __getitem__(self, step_id):
        for step in self:
            if str(step) == step_id:
                return step
        raise KeyError('%r is not a valid step' % (step_id,))

    def validate_step(self, step):
        try:
            step.validate()
        except InvalidData:
            return False
        return True

    def get_next_step(self):
        for step in self:
            if not self.validate_step(step):
                return step

    def get_errors(self):
        errors = {}
        for step in self:
            try:
                step.validate()
            except InvalidData as error:
                errors[str(step)] = error
        return errors

    def is_complete(self):
        return self.get_next_step() is None
