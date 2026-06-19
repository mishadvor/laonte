from .models import SiteSettings


def site_settings(request):
    """
    Контекстный процессор для передачи настроек сайта в шаблоны
    """
    try:
        settings = SiteSettings.objects.get()
    except SiteSettings.DoesNotExist:
        settings = None
    return {"site_settings": settings}
