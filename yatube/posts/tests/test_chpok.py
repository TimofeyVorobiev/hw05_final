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

def test_create_post(self):
    """Валидная форма создает запись в БД."""
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
    posts_count = Post.objects.count()
    form_data = {
        'group': self.group.id,
        'text': self.post.text,
        # создние поста с картинокй в БД
        'image': uploaded,
    }
    response = self.authorized_client.post(
        reverse('posts:post_create'),
        data=form_data,
        follow=True
    )
    self.assertRedirects(
        response, reverse(
            'posts:profile',
            kwargs={'username': self.author.username})
    )
    self.assertEqual(Post.objects.count(), posts_count + 1)
    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertTrue(
        Post.objects.filter(
            group=form_data['group'],
            text=form_data['text'],
            image='posts/small.gif',
        ).exists()
    )