from django import forms
from .models import Album, Photo


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description', 'visibility', 'cover_image', 'collaborators']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Album title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'collaborators': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description', 'image', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Photo title (optional)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'title', 'description']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title (optional)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description (optional)'}),
        }
