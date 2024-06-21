from django import forms

from .models import Comment, Review


class ReviewForm(forms.ModelForm):
    """
    Форма для создания и редактирования отзыва.

    Поля формы включают текст и оценку.
    """

    class Meta:
        model = Review
        fields = ('text', 'score')


class CommentForm(forms.ModelForm):
    """
    Форма для создания комментария к отзыву.

    Поля формы включают текст.
    """

    class Meta:
        model = Comment
        fields = ('text',)
