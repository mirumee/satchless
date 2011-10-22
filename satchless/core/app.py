class SatchlessApp(object):
    app_name = None
    name = None

    def __init__(self, name=None):
        self.name = name

    def get_context_data(self, request, **kwargs):
        return kwargs

    def get_urls(self, prefix=None):
        raise NotImplementedError()

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name