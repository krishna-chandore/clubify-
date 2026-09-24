from django.contrib import admin
from django.urls import path
from clubapp import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('' ,views.user_login, name= 'login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup_view, name='signup'),

    path('home/', views.index, name='home'),
    path('create-event/', views.create_event, name='create_event'),
    path('contact/', views.contact, name='contact'),
    path('join_clubs/', views.join_clubs, name='join_clubs'),

    # Club detail by slug
    path('club/<slug:slug>/', views.club_detail, name='club_detail'),

    # Club admin login page
    path('club-admin-login/', views.club_admin_login, name='club_admin_login'),

    # Optional: club dashboard for club admins
    path('dashboard/', views.club_dashboard, name='club_dashboard'),

    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
]
