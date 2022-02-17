from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import Textarea
from django.core.exceptions import ValidationError

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        labels = {
            'text': _('Текст поста'),
            'group': _('Группа'),
        }

        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        widgets = {
            "text": Textarea(attrs={
                'class': 'form-control', 'placeholder': "Текст нового поста"
            })
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

        def clean_text(self):
            data = self.cleaned_data['text']
            if data == '':
                raise ValidationError
            return data

        labels = {
            'text': _('Текст комментария'),
        }

        help_texts = {
            'text': 'Текст нового комментария',
        }
        widgets = {
            "text": Textarea(attrs={
                'class': 'form-control', 'placeholder': "Текст нового комментария"
            })
        }
