from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='Название группы',
            description='Описание группы',
            slug='group_slug',
        )

        cls.count_posts = 9
        cls.count_pages = (cls.count_posts // settings.POST_QUANTITY) + 1
        if cls.count_posts > 10:
            cls.count_pages = (cls.count_posts // settings.POST_QUANTITY) + 1
            cls.rez = cls.count_posts % settings.POST_QUANTITY
        else:
            cls.count_pages = cls.count_posts / settings.POST_QUANTITY
            settings.POST_QUANTITY = cls.count_posts
            cls.rez = settings.POST_QUANTITY

        for cls.post in range(cls.count_posts):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Текст поста',
                group=cls.group,
            )

    def test_paginator_on_pages(self):
        """ Проверка пагинации на страницах"""
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ),
            reverse('posts:profile',
                    kwargs={'username': self.user}
                    ),
        ]
        for reverse_ in urls:
            with self.subTest(reverse_=reverse):
                self.assertEqual(
                    len(self.client.get(reverse_).context.get('page_obj')),
                    settings.POST_QUANTITY)
                self.assertEqual(len(self.client.get(
                    reverse_ + f'?page={self.count_pages}').context.get(
                    'page_obj')),
                    self.rez)
