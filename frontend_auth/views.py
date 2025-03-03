from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy


class FrontendLoginView(LoginView):
    template_name = 'frontend_auth/login.html'


class FrontendLogoutView(LogoutView):
    template_name = 'frontend_auth/logout.html'


class FrontendPasswordChangeView(PasswordChangeView):
    template_name = 'frontend_auth/password_change_form.html'
    success_url = reverse_lazy('frontend_auth:password_change_done')


class FrontendPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'frontend_auth/password_change_done.html'


class FrontendPasswordResetView(PasswordResetView):
    template_name = 'frontend_auth/password_reset_form.html'
    email_template_name = "frontend_auth/password_reset_email.html"
    success_url = reverse_lazy('frontend_auth:password_reset_done')


class FrontendPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'frontend_auth/password_reset_done.html'


class FrontendPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'frontend_auth/password_reset_form.html'
    success_url = reverse_lazy('frontend_auth:password_reset_complete')


class FrontendPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'frontend_auth/password_reset_complete.html'
