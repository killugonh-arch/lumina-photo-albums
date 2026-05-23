from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden
from django.db.models import Q
import cloudinary.uploader

from .models import Album, Photo
from .forms import AlbumForm, PhotoForm, PhotoUploadForm


class AlbumListView(ListView):
    model = Album
    template_name = 'albums/album_list.html'
    context_object_name = 'albums'
    paginate_by = 12

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Album.objects.filter(
                Q(visibility='public') |
                Q(owner=user) |
                Q(collaborators=user)
            ).distinct()
        return Album.objects.filter(visibility='public')


class AlbumDetailView(DetailView):
    model = Album
    template_name = 'albums/album_detail.html'

    def get_object(self):
        album = get_object_or_404(Album, pk=self.kwargs['pk'])
        if not album.user_can_view(self.request.user):
            return None
        return album

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden("You don't have permission to view this album.")
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.object.user_can_edit(self.request.user)
        context['can_add_photos'] = self.object.user_can_add_photos(self.request.user)
        context['photos'] = self.object.photos.all()
        context['photo_form'] = PhotoUploadForm()
        return context


class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    form_class = AlbumForm
    template_name = 'albums/album_form.html'

    def form_valid(self, form):
        album = form.save(commit=False)
        album.owner = self.request.user

        # Upload cover image directly to Cloudinary
        cover_file = self.request.FILES.get('cover_image')
        if cover_file:
            result = cloudinary.uploader.upload(
                cover_file,
                folder='album_covers',
                resource_type='image',
            )
            album.cover_image = result['secure_url']

        album.save()
        form.save_m2m()
        messages.success(self.request, 'Album created successfully!')
        return redirect(album.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Album'
        context['action'] = 'Create'
        return context


class AlbumUpdateView(LoginRequiredMixin, UpdateView):
    model = Album
    form_class = AlbumForm
    template_name = 'albums/album_form.html'

    def get_object(self):
        album = get_object_or_404(Album, pk=self.kwargs['pk'])
        if not album.user_can_edit(self.request.user):
            return None
        return album

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        album = form.save(commit=False)

        # Upload new cover image directly to Cloudinary if provided
        cover_file = self.request.FILES.get('cover_image')
        if cover_file:
            result = cloudinary.uploader.upload(
                cover_file,
                folder='album_covers',
                resource_type='image',
            )
            album.cover_image = result['secure_url']

        album.save()
        form.save_m2m()
        messages.success(self.request, 'Album updated successfully!')
        return redirect(album.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Album'
        context['action'] = 'Update'
        return context


class AlbumDeleteView(LoginRequiredMixin, DeleteView):
    model = Album
    template_name = 'albums/album_confirm_delete.html'
    success_url = reverse_lazy('albums:album_list')

    def get_object(self):
        album = get_object_or_404(Album, pk=self.kwargs['pk'])
        if not album.user_can_edit(self.request.user):
            return None
        return album

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden()
        messages.success(request, 'Album deleted successfully.')
        return self.delete(request, *args, **kwargs)


class PhotoUploadView(LoginRequiredMixin, View):
    def post(self, request, album_pk):
        album = get_object_or_404(Album, pk=album_pk)
        if not album.user_can_add_photos(request.user):
            return HttpResponseForbidden()

        image_file = request.FILES.get('image')
        if not image_file:
            messages.error(request, 'Please select an image file.')
            return redirect('albums:album_detail', pk=album_pk)

        try:
            # Upload directly to Cloudinary
            result = cloudinary.uploader.upload(
                image_file,
                folder='photos',
                resource_type='image',
            )
            cloudinary_url = result['secure_url']

            photo = Photo(
                album=album,
                uploaded_by=request.user,
                title=request.POST.get('title', ''),
                description=request.POST.get('description', ''),
            )
            # Save the Cloudinary URL directly into the image field
            photo.image = cloudinary_url
            photo.save()
            messages.success(request, 'Photo uploaded successfully!')
        except Exception as e:
            messages.error(request, f'Upload failed: {str(e)}')

        return redirect('albums:album_detail', pk=album_pk)


class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'albums/photo_detail.html'

    def get_object(self):
        photo = get_object_or_404(Photo, pk=self.kwargs['pk'])
        if not photo.album.user_can_view(self.request.user):
            return None
        return photo

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden()
        return self.render_to_response(self.get_context_data(object=self.object))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.object.album.user_can_edit(self.request.user)
        return context


class PhotoUpdateView(LoginRequiredMixin, UpdateView):
    model = Photo
    form_class = PhotoForm
    template_name = 'albums/photo_form.html'

    def get_object(self):
        photo = get_object_or_404(Photo, pk=self.kwargs['pk'])
        if not photo.album.user_can_edit(self.request.user):
            return None
        return photo

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        photo = form.save(commit=False)

        # If a new image file was provided, upload it to Cloudinary
        image_file = self.request.FILES.get('image')
        if image_file:
            result = cloudinary.uploader.upload(
                image_file,
                folder='photos',
                resource_type='image',
            )
            photo.image = result['secure_url']

        photo.save()
        messages.success(self.request, 'Photo updated successfully!')
        return redirect(reverse('albums:album_detail', kwargs={'pk': photo.album.pk}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PhotoDeleteView(LoginRequiredMixin, DeleteView):
    model = Photo
    template_name = 'albums/photo_confirm_delete.html'

    def get_object(self):
        photo = get_object_or_404(Photo, pk=self.kwargs['pk'])
        if not photo.album.user_can_edit(self.request.user):
            return None
        return photo

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden()
        messages.success(request, 'Photo deleted.')
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('albums:album_detail', kwargs={'pk': self.object.album.pk})


class MyAlbumsView(LoginRequiredMixin, ListView):
    model = Album
    template_name = 'albums/my_albums.html'
    context_object_name = 'albums'

    def get_queryset(self):
        return Album.objects.filter(owner=self.request.user)
