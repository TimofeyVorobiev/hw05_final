from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='Группа',
            slug='test_slug',
            description='О группе',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Поста',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_models_post_have_correct_object_names(self):
        """Модель POST.Проверка длинны поста до 15 символов и __str__"""
        self.assertEqual(self.post.text[:15], str(self.post))

    def test_models_group_have_correct_object_names(self):
        """Модель Group.Проверка __str__"""
        self.assertEqual(self.group.title, str(self.group))
