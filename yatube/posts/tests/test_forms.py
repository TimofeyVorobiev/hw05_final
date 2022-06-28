import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, Comment, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='Группа',
            slug='group_slug',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Текст комментария',
            post=cls.post
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower = User.objects.create_user(username='follower')

    def test_create_post(self):
        """ Проверка создания нового поста """
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
            'author': self.post.author,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, form_data['author'])
        self.assertEqual(post.image, f'posts/{uploaded.name}')

    def test_existing_post_editing(self):
        tostform_data = {
            'text': 'Отредактированный текст',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=tostform_data,
            follow=True
        )
        self.assertEqual(Post.objects.get(id=self.post.id).text, 'Отредактированный текст')


    def test_edit_postrrr(self):
        """ Проверка редактирования поста """
        edit_form_data = {
            'text': self.post.text,
            'group': self.group.id,
            'author': self.post.author,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=edit_form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        post = Post.objects.latest('id')
        self.assertEqual(post.text, edit_form_data['text'])
        self.assertEqual(post.group.id, edit_form_data['group'])
        self.assertEqual(post.author, edit_form_data['author'])

    def test_comment(self):
        """ Проверка создания нового коммента """
        comments_count = Comment.objects.count()
        form_data = {
            'text': self.comment.text,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(Comment.objects.last().text, self.comment.text)
        self.assertEqual(Comment.objects.last().post, self.comment.post)

    def test_authorized_client_can_comment_post(self):
        comment_count = Comment.objects.count()
        form_data ={
            'text': 'text comment'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        last_comment = Comment.objects.latest('created')
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            text='text comment'
        ).exists()
        )
        self.assertEqual(last_comment.text, form_data['text'])
        self.assertEqual(last_comment.author, self.user)

    def test_follow(self):
        """ Проверка создания подписки """
        follow_count = Follow.objects.count()
        self.authorized_client.post(reverse(
            'posts:profile_follow', kwargs={'username': self.follower}
        ))
        self.assertIs(
            Follow.objects.filter(
                user=self.user, author=self.follower
            ).exists(),
            True
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_unfollow(self):
        """ Проверка отмены подписки """
        Follow.objects.create(user=self.user, author=self.follower)
        self.authorized_client.post(reverse(
            'posts:profile_unfollow', kwargs={'username': self.follower}
        ))
        self.assertIs(
            Follow.objects.filter(
                user=self.user, author=self.follower
            ).exists(),
            False
        )

    def test_new_post_in_favourites(self):
        """ Проверка поста избранного автора """
        Follow.objects.get_or_create(user=self.user, author=self.follower)
        follow_post = Post.objects.create(author=self.follower)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(follow_post, response.context['page_obj'])
        self.authorized_client.logout()
        User.objects.create_user(username='NewUser', password='New12345')
        self.client.login(username='NewUser', password='New12345')
        response = self.client.get(reverse('posts:follow_index'))
        self.assertNotIn(follow_post, response.context['page_obj'])


class SignUpPageTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.signup_data = {
            'username': 'username',
            'password1': '1234_Abc',
            'password2': '1234_Abc',
        }

    def test_signup_url_exists_at_desired_location(self):
        """ Проверка доступности страницы регистрации нового пользователя """
        response = self.client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_created(self):
        """Проверка создания нового пользователя."""
        users_count = User.objects.count()
        response = self.client.post(
            reverse('users:signup'),
            data=self.signup_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertRedirects(response, reverse('users:login'))
