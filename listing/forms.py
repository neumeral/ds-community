from django import forms
from listing.models import Post, Category


class CreatePostForm(forms.ModelForm):
    type = [('Video','video'),
            ('Book','Book'),
            ('Tutorial','Tutorial'),
            ]
    post_type = forms.ChoiceField(choices=type)
    
    class Meta:
        model = Post
        exclude = ['submitted_user', 'approved']