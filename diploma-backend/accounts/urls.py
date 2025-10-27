from django.urls import path
from .views import SignInView, SignUpView, SignOutView, ProfileUserView, AvatarUploadView, ChangeUserPasswordView

app_name = 'accounts'

urlpatterns = [
    path('sign-in', SignInView.as_view(), name='sign-in'),
    path('sign-up', SignUpView.as_view(), name='sign-up'),
    path('sign-out', SignOutView.as_view(), name='sign-out'),
    path('profile', ProfileUserView.as_view(), name='profile'),
    path('profile/avatar', AvatarUploadView.as_view(), name='avatar-upload'),
    path('profile/password', ChangeUserPasswordView.as_view(), name='change-password')
]
