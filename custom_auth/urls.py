"""Urls list for 'custom_auth' app."""
from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy

from async_views.auth.views import (
    AsyncLogoutView,
    AsyncPasswordChangeView,
    AsyncPasswordResetCompleteView,
    AsyncPasswordResetConfirmView,
    AsyncPasswordResetDoneView,
    AsyncPasswordResetView,
)

from .views import (
    CustomAsyncLoginView,
    CustomLoginView,
    ModPasswordChangeView,
    ModPasswordResetCompleteView,
    ModPasswordResetConfirmView,
    ModPasswordResetDoneView,
    ModPasswordResetView,
    RegisterUserView,
)

app_name = "custom_auth"

urlpatterns = []
# urlpatterns = [
#     path("signup/", RegisterUserView.as_view(), name="signup"),
#     path("signin/", CustomLoginView.as_view(), name="signin"),
#     path("logout/", LogoutView.as_view(next_page="main_page:main_page"), name="logout"),
#     path("password-change/", ModPasswordChangeView.as_view(), name="password_change"),
#     path("password-reset/", ModPasswordResetView.as_view(), name="password_reset"),
#     path(
#         "password-reset/done/",
#         ModPasswordResetDoneView.as_view(),
#         name="password_reset_done",
#     ),
#     path(
#         "reset/<uidb64>/<token>/",
#         ModPasswordResetConfirmView.as_view(),
#         name="password_reset_confirm",
#     ),
#     path(
#         "reset/done",
#         ModPasswordResetCompleteView.as_view(),
#         name="password_reset_complete",
#     ),
#     path("a_signin/", CustomAsyncLoginView.as_view(), name="async_signin"),
#     path(
#         "a_logout/",
#         AsyncLogoutView.as_view(next_page="main_page:main_page"),
#         name="async_logout",
#     ),
#     path(
#         "a_password-change",
#         AsyncPasswordChangeView.as_view(
#             template_name="custom_auth/password_change_form.html",
#             login_url="/auth/a_signin/",
#             success_url=reverse_lazy("main_page:main_page"),
#         ),
#         name="async_change_view",
#     ),
#     path(
#         "a_password-reset",
#         AsyncPasswordResetView.as_view(
#             template_name="custom_auth/password_reset_form.html",
#             email_template_name="custom_auth/password_reset_email.html",
#             success_url=reverse_lazy("custom_auth:password_reset_done"),
#             extra_context={"title": "Password reset"},
#         ),
#         name="async_password_reset",
#     ),
#     path(
#         "a_password-reset/done/",
#         AsyncPasswordResetDoneView.as_view(
#             template_name="custom_auth/password_reset_done.html",
#             extra_context={"title": "Password reset"},
#         ),
#         name="async_password_reset_done",
#     ),
#     path(
#         "async_reset/<uidb64>/<token>/",
#         AsyncPasswordResetConfirmView.as_view(
#             template_name="custom_auth/password_reset_confirm.html",
#             success_url=reverse_lazy("custom_auth:password_reset_complete"),
#             extra_context={"title": "Password reset confirm"},
#         ),
#         name="async_password_reset_confirm",
#     ),
#     path(
#         "reset/done",
#         AsyncPasswordResetCompleteView.as_view(
#             template_name="custom_auth/password_reset_complete.html",
#             extra_context={"title": "Password reset done"},
#         ),
#         name="async_password_reset_complete",
#     ),
# ]
