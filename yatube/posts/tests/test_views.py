from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='Первая группа ',
            description='О первой группе',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Первый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_all_posts_pages_uses_correct_template(self):
        """ Проверяем корректности url адресов
        для всех шаблоново из posts и about """
        templates_pages_names = {
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}),
            'posts/post_create.html': reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.user}),
            'about/tech.html': reverse('about:tech'),
            'about/author.html': reverse('about:author'),
            'posts/index.html': reverse('posts:index'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def context_info(self, context):
        """ Функция проверки контекста для index, group_list, profile,
        post_detail """
        with self.subTest(context=context):
            self.assertEqual(context.author, self.post.author)
            self.assertEqual(context.text, self.post.text)
            self.assertEqual(context.group, self.post.group)
            self.assertEqual(context.id, self.post.id)

    def test_index_first_page_context(self):
        """ Шаблон index сформирован с правильным контекстом """
        response = self.authorized_client.get(reverse('posts:index'))
        self.context_info(response.context['page_obj'][0])

    def test_groups_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом """
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.context_info(response.context['page_obj'][0])

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом """
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.context_info(response.context['page_obj'][0])

    def test_post_detail_show_correct_context(self):
        """ Шаблон post_detail сформирован с правильным контекстом """
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    )
        )
        self.context_info(response.context['post'])

    def test_create_page_shows_correct_context(self):
        """ Шаблон post_create сформирован с правильным контекстом """
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """ Шаблон post_edit сформирован с правильным контекстом """
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_appears_on_the_home_page(self):
        """ Проверка отображения поста на первой странице """
        response = self.authorized_client.get(reverse('posts:index'))
        self.context_info(response.context['page_obj'][0])

    def test_post_appears_on_the_profile_page(self):
        """ Проверка отображения поста в profile пользователя"""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user})
        )
        self.context_info(response.context['page_obj'][0])

    def test_post_appears_on_the_group_list_page(self):
        """ Проверка отображения поста в группе """
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.context_info(response.context['page_obj'][0])

    def test_cache_index_page(self):
        """Тестирование использование кеширования"""
        cache.clear()
        post = Post.objects.get(pk=self.post.id)
        content_on_page = self.client.get(
            reverse('posts:index')).content
        post.delete()
        content_on_page_delete = self.client.get(
            reverse('posts:index')).content
        self.assertEqual(content_on_page, content_on_page_delete)
        cache.clear()
        cache_clear = self.client.get(
            reverse('posts:index')).content
        self.assertNotEqual(content_on_page, cache_clear)
