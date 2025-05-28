from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import News, Category, Tag


@receiver([post_save, post_delete], sender=News)
@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Tag)
def clear_news_cache(sender, **kwargs):
    try:
        client = cache.client.get_client()
        keys = client.keys("news_list:*")
        if keys:
            client.delete(*keys)
    except Exception:
        cache.delete_pattern("news_list*") 

