from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import viewsets, filters
from admin_api.models import News, Category, Tag
from .serializers import NewsUserSerializer
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.http import JsonResponse
from admin_api.models import News


from django.core.cache import cache
from django.http import JsonResponse
from django.db.models import Q
from admin_api.models import News

def news_list(request):
    search_query = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()
    tag_id = request.GET.get('tag', '').strip()

    cache_key = f"news_list:search={search_query}:category={category_id}:tag={tag_id}"

    news = cache.get(cache_key)
    if news is None:
        news_qs = News.objects.filter(is_published=True)

        if search_query:
            news_qs = news_qs.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        if category_id.isdigit():
            news_qs = news_qs.filter(category_id=int(category_id))
        if tag_id.isdigit():
            news_qs = news_qs.filter(tags__id=int(tag_id))

        news = list(news_qs.values(
            'title', 'content', 'slug', 'author__username', 'published_at'
        ))

        cache.set(cache_key, news, timeout=300)
  
    return JsonResponse(news, safe=False)




class NewsUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.filter(is_published=True).order_by('-created_at')
    serializer_class = NewsUserSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title','content','tags_name','category_name']
    lookup_field = "slug"

def news_list_view(request):
    search_query = request.GET.get('search')
    category_id = request.GET.get('category')
    tag_id = request.GET.get('tag')

    news_list = News.objects.filter(is_published=True).order_by('-created_at')

    if search_query:
        news_list = news_list.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    if category_id:
        news_list = news_list.filter(category_id=category_id)
    if tag_id:
        news_list = news_list.filter(tags__id=tag_id)

    categories = Category.objects.all()
    tags = Tag.objects.all()

    return render(request, 'user_api/news_list.html', {
        'news_list': news_list,
        'categories': categories,
        'tags': tags,
        'active_category_id': int(category_id) if category_id else None,
        'active_tag_id': int(tag_id) if tag_id else None,
        'search_query': search_query or ''
    })
def news_detail_view(request, slug):
    news = get_object_or_404(News, slug=slug, is_published=True)
    return render(request, 'user_api/news_detail.html', {'news': news})
