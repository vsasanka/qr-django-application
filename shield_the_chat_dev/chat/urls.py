from django.urls import path, include
from chat import views as chat_views
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.conf import settings
from . import views
from django.conf.urls.static import static
from authentication import views as sign_views

urlpatterns = [
	path("", views.chatPage, name="chat-page"),


	# login-section
	path("chat/", LoginView.as_view
		(template_name="chat/chatPage.html"), name="login-user"),
	path("", sign_views.home, name="logout-user"),
]



