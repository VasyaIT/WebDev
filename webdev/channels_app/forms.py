from django import forms

from .models import Channel


class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ('name', 'description', 'tags')
        widgets = {'name': forms.TextInput(attrs={'placeholder': 'Channel name'}),
                   'description': forms.Textarea(attrs={'placeholder': 'Channel description'})}


class SearchForm(forms.Form):
    query = forms.CharField(
            widget=forms.TextInput(attrs={'placeholder': 'Enter the name, tags, author'}),
            required=False
    )
