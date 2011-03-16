from django.conf import settings

def google_analytics(ctx):
    return {'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', '')}
