# coding: utf-8

from django.conf import settings
from django.shortcuts import get_object_or_404

from news.models import News
from lib.decorators import render_to
from lib.helpers import get_flatpage_or_none


@render_to('mainpage.html')
def mainpage(request):
    """
    Site main page
    
    Shows content from flatpage and latest news list
    """
    
    flatpage = get_flatpage_or_none(request)
    news_list = News.objects.all()[:settings.LATEST_NEWS_COUNT]
    
    return {
        'flatpage': flatpage,
        'news_list': news_list,
    }


@render_to('news/single.html')
def single(request, news_id):
    """
    Single news page
    """
    
    news = get_object_or_404(News, id=news_id)
    
    return {
        'news': news,
    }


@render_to('news/archive.html')
def archive(request):
    """
    News archive
    """
    
    news_list = News.objects.all()
    
    return {
        'news_list': news_list,
    }
