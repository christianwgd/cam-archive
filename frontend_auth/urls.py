from django.urls import path

from frontend_auth import views

app_name = 'frontend_auth'

urlpatterns = [
    path('login/', views.FrontendLoginView.as_view(), name='login'),
    path('logout/', views.FrontendLogoutView.as_view(), name='logout'),
    path('password_change/', views.FrontendPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.FrontendPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', views.FrontendPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', views.FrontendPasswordResetDoneView.as_view(), name='password_reset_done'),
    path(
        'password_reset/<uidb64>/<token>/',
        views.FrontendPasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path('password_reset/done/', views.FrontendPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
