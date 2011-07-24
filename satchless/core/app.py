from django.template.response import TemplateResponse

class SatchlessApp(object):
    app_name = None
    name = None

    def __init__(self, name=None):
        self.name = name

    def get_context_data(self, request, **kwargs):
        return kwargs

    def respond(self, request, context, **kwargs):
        return TemplateResponse(request, self.get_template_names(**kwargs),
                                context)

    def get_urls(self, prefix=None):
        raise NotImplementedError()

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name
