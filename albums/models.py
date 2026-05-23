from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Album(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('shared', 'Shared'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    collaborators = models.ManyToManyField(User, blank=True, related_name='shared_albums')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    cover_image = models.ImageField(upload_to='album_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('albums:album_detail', kwargs={'pk': self.pk})

    @property
    def photo_count(self):
        return self.photos.count()

    @property
    def cover_image_url(self):
        """Returns Cloudinary URL or None — never a broken local path."""
        val = str(self.cover_image) if self.cover_image else ''
        if not val:
            return None
        if val.startswith(('http://', 'https://')):
            return val
        return None  # local path = broken, treat as no image

    def user_can_view(self, user):
        if self.visibility == 'public':
            return True
        if not user.is_authenticated:
            return False
        return (self.owner == user or
                user in self.collaborators.all() or
                user.is_staff)

    def user_can_edit(self, user):
        if not user.is_authenticated:
            return False
        return self.owner == user or user.is_staff

    def user_can_add_photos(self, user):
        if not user.is_authenticated:
            return False
        return (self.owner == user or
                user in self.collaborators.all() or
                user.is_staff)


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_photos')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return self.title or f"Photo in {self.album.title}"

    def get_absolute_url(self):
        return reverse('albums:photo_detail', kwargs={'pk': self.pk})

    @property
    def image_url(self):
        """Returns Cloudinary URL or None — never a broken local path."""
        val = str(self.image) if self.image else ''
        if not val:
            return None
        if val.startswith(('http://', 'https://')):
            return val
        return None  # local path = broken, treat as no image
