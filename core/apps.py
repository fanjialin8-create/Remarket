from django.apps import AppConfig


def ensure_categories(app_config, **kwargs):
    """Ensure initial categories exist (created on first run)"""
    try:
        from .models import Category
        if not Category.objects.exists():
            for name, slug in [('Electronics', 'electronics'), ('Books', 'books'), ('Clothing', 'clothing'), ('Daily', 'daily'), ('Other', 'other')]:
                Category.objects.get_or_create(slug=slug, defaults={'name': name})
    except Exception:
        pass  # Table may not exist yet


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(ensure_categories, sender=self)
