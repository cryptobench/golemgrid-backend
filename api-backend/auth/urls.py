from django.urls import path
from . import views
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView


app_name = 'auth'

urlpatterns = [
    path('register', views.RegisterView.as_view()),
    path('reset-password',
         PasswordResetView.as_view(),
         name='rest_password_reset'
         ),

    path('reset-password/confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),



]
