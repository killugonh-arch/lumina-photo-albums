from django.contrib import admin
from .models import Album, Photo


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0
    fields = ['image', 'title', 'uploaded_by', 'order']
    readonly_fields = ['uploaded_by']


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'visibility', 'photo_count', 'created_at']
    list_filter = ['visibility', 'created_at']
    search_fields = ['title', 'owner__username']
    inlines = [PhotoInline]
    filter_horizontal = ['collaborators']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'album', 'uploaded_by', 'uploaded_at']
    list_filter = ['album', 'uploaded_at']
    search_fields = ['title', 'album__title']
