from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('signin', views.signin, name='signin'),
    path('', include('chat.urls')),
    path('signout', views.signout, name='signout'),
    path('request', views.request1, name='request'),
    path('verify-otp', views.otp_authentication, name='otp_authentication'),

    
]
