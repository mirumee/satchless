from categories.app import product_app

def root_categories(request):
    return {'root_categories': product_app.Category.objects.filter(parent__isnull=True)}
