from django.urls import path

from apps.accounts.views import AuthLandingView, ProfileView, SignupView, UserLoginView, UserLogoutView


app_name = "accounts"

urlpatterns = [
    path("", AuthLandingView.as_view(), name="landing"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
