from django.urls import path
from user_profile import views

app_name="profile"


urlpatterns = [	
    path('register/', views.CustomRegistrationView.as_view(), name="register"),
    path('login/', views.CustomAuthenticationView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name="password_change"),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name="password_reset_request"),
    path('password_reset_confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('recover_username/', views.RecoverUsernameView.as_view(), name="recover_username"),
    path('password_validation/', views.PasswordValidationView.as_view(), name='password_validation'),
    path('ajax_password_validation', views.ajax_password_validation_view, name='ajax_password_validation'),

    path('', views.HomeView.as_view(), name="home"),   
    path('add_phone/', views.AddPhoneView.as_view(), name="add_phone"),
    path('verify_phone/', views.PhoneVerificationView.as_view(), name='phone_verification'),
	path('profile/', views.ProfileView.as_view(), name="profile"),
    path('update_profile/', views.UpdateProfileView.as_view(), name="update_profile"),
]
