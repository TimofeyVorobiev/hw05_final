from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='Группа',
            description='О группе',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls(self):
        templates_url_names = {
            'users/signup.html': '/auth/signup/',
            'users/login.html': '/auth/login/',
            'users/password_change_form.html': '/auth/password_change/',
            'users/password_change_done.html': '/auth/password_change/done/',
            'users/password_reset_form.html': '/auth/password_reset/',
            'users/password_reset_done.html': '/auth/password_reset/done/',
            'users/password_reset_complete.html': '/auth/reset/done/',
            'users/logged_out.html': '/auth/logout/',
        }

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_guest_correct_template_and_location_post(self):
        """ Проверяем доступность всех шаблонов и адресов из
        приложения posts и about всем пользователям """
        templates_url_names_guest = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_url_names_guest.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_correct_location(self):
        """Проверяем доступность к несуществующей странице """
        response_auth = self.authorized_client.get('/unexisting_page/')
        response_guest = self.client.get('/unexisting_page/')
        self.assertEqual(response_auth.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response_guest.status_code, HTTPStatus.NOT_FOUND)

    def test_auth_user_post_create_teamplate(self):
        """Проверка шаблона создания поста для авторизованного пользователя """
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_auth_user_post_create_response(self):
        """Проверка доступа к страницы создания поста
        для авторизованного пользователя """
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_user_post_create_redirect(self):
        """Проверка редиректа с страницы создания поста
        для неавторизованного пользователя """
        response = self.client.get(reverse('posts:post_create'))
    #    self.assertRedirects(response, '/auth/login/?next=/create/')
        p1 = reverse('posts:post_create')
        p2 = reverse('users:login')
        self.assertRedirects(response, f'{p2}?next={p1}')
        self.assertEqual(response.status_code, 302)

    def test_guest_user_post_edit(self):
        """Проверка доступа к странице редактирования поста
        для неавторизованного пользователя """
        response = self.client.get(f'posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_user_post_edit(self):
        """Проверка доступа к странице редактирования поста
        для автора поста """
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_comment_create(self):
        """Проверка редиректа со страницы создания комментария неавторизованным
        пользователем"""
        response = self.client.get(f'/posts/{self.post.id}/comment/')
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )

    def test_comment_field_exists_at_desired_location_anonymous(self):
        """Проверка доступности страницы создания комментария"""
        response = self.client.get(f'/posts/{self.post.id}/comment/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_404(self):
        """Проверка доступа к странице "ошибка 404" любым пользователем """
        response = self.client.get('/page_not_found/')
        self.assertTemplateUsed(response, 'core/404.html')
