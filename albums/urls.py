from django.urls import path
from . import views

app_name = 'albums'

urlpatterns = [
    path('', views.AlbumListView.as_view(), name='album_list'),
    path('my-albums/', views.MyAlbumsView.as_view(), name='my_albums'),
    path('album/create/', views.AlbumCreateView.as_view(), name='album_create'),
    path('album/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detail'),
    path('album/<int:pk>/edit/', views.AlbumUpdateView.as_view(), name='album_edit'),
    path('album/<int:pk>/delete/', views.AlbumDeleteView.as_view(), name='album_delete'),
    path('album/<int:album_pk>/upload/', views.PhotoUploadView.as_view(), name='photo_upload'),
    path('photo/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('photo/<int:pk>/edit/', views.PhotoUpdateView.as_view(), name='photo_edit'),
    path('photo/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo_delete'),
]
