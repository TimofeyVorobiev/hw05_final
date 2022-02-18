from django.conf import settings
from django.core.paginator import Paginator, Page
from django.db.models import QuerySet


def posts_on_page(page_number: int,
                  post_list: QuerySet,
                  on_screen_posts: int = settings.POST_QUANTITY) -> Page:
    paginator = Paginator(post_list, on_screen_posts)
    page_posts = paginator.get_page(page_number)
    return page_posts
