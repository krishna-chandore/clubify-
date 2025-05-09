# club/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('leader/dashboard/', views.leader_dashboard, name='leader_dashboard'),
    path('leader/edit-club/', views.edit_club, name='edit_club'),
    path('leader/upload-media/', views.upload_media, name='upload_media'),
    path('leader/create-event/', views.create_event, name='create_event'),
    path('leader/edit-event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('leader/delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('leader/create-post/', views.create_post, name='create_post'),

]

