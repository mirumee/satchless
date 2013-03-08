class InvalidData(Exception):

    pass


class Step(object):

    def validate(self):
        raise NotImplementedError()  # pragma: no cover


class ProcessManager(object):

    def validate_step(self, step):
        try:
            step.validate()
            return True
        except InvalidData:
            return False

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
        return not self.get_next_step()

    def __getitem__(self, step_id):
        for step in self:
            if str(step) == step_id:
                return step
        raise KeyError('%r is not a valid step' % (step_id,))
