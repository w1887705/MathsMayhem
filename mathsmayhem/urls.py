from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/",  auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    # Logout via POST (Django 5+) — we handle it with a form in the base template
    path("logout/", auth_views.LogoutView.as_view(next_page="/login/"), name="logout"),
    path("", include("core.urls")),
]
