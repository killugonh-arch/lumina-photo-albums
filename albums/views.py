from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden
from django.db.models import Q
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
        form.instance.owner = self.request.user
        messages.success(self.request, 'Album created successfully!')
        return super().form_valid(form)

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
            return HttpResponseForbidden("You don't have permission to edit this album.")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden("You don't have permission to edit this album.")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Album updated successfully!')
        return super().form_valid(form)

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
            return HttpResponseForbidden("You don't have permission to delete this album.")
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden()
        messages.success(request, 'Album deleted successfully.')
        self.object.delete()
        return redirect(self.success_url)


class PhotoUploadView(LoginRequiredMixin, View):
    def post(self, request, album_pk):
        album = get_object_or_404(Album, pk=album_pk)
        if not album.user_can_add_photos(request.user):
            return HttpResponseForbidden()
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.album = album
            photo.uploaded_by = request.user
            photo.save()
            messages.success(request, 'Photo uploaded successfully!')
        else:
            messages.error(request, 'Error uploading photo. Please try again.')
        return redirect('albums:album_detail', pk=album_pk)


class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'albums/photo_detail.html'
    context_object_name = 'photo'

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
        messages.success(self.request, 'Photo updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('albums:album_detail', kwargs={'pk': self.object.album.pk})


class PhotoDeleteView(LoginRequiredMixin, DeleteView):
    model = Photo
    template_name = 'albums/photo_confirm_delete.html'
    context_object_name = 'photo'

    def get_object(self):
        photo = get_object_or_404(Photo, pk=self.kwargs['pk'])
        if not photo.album.user_can_edit(self.request.user):
            return None
        return photo

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return HttpResponseForbidden()
        # Store album pk BEFORE deletion so get_success_url works
        album_pk = self.object.album.pk
        messages.success(request, 'Photo deleted.')
        self.object.delete()
        return redirect('albums:album_detail', pk=album_pk)

    def get_success_url(self):
        # Fallback — not called when post() redirects directly, but kept for safety
        return reverse('albums:album_list')


class MyAlbumsView(LoginRequiredMixin, ListView):
    model = Album
    template_name = 'albums/my_albums.html'
    context_object_name = 'albums'

    def get_queryset(self):
        return Album.objects.filter(owner=self.request.user)
