from django import forms

from .models import Channel


class ChannelForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Channel name'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Channel description'}))

    class Meta:
        model = Channel
        fields = ('name', 'description',)
