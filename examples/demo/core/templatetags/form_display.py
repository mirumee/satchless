from django import template

register = template.Library()

@register.filter
def form_as_table(form, fieldnames=None):
    fieldnames = fieldnames.split(',') if fieldnames else form.fields.keys()

    fields = []
    for fieldname in fieldnames:
        fields.append(form[fieldname])
    return template.loader.render_to_string('core/form_as_table.html', {'fields': fields})

