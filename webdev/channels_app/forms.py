from django import forms

from .models import Channel


class ChannelForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Channel name'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Channel description'}))
    tags = forms.SelectMultiple()

    class Meta:
        model = Channel
        fields = ('name', 'description', 'tags',)


class SearchForm(forms.Form):
    query = forms.CharField(
            widget=forms.TextInput(attrs={'placeholder': 'Enter the name, tags, author'}),
            required=False
    )
