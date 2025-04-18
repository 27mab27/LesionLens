from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from base.forms import StyledPasswordResetForm

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('add-user/', views.add_user, name='add_user'),
    path('add-patient/', views.add_patient, name='add_patient'),
    path('profile/', views.profile_tab, name='profile_tab'),
    path('diagnosis-history/', views.diagnosis_history, name='diagnosis_history'),
    path('ajax/get-patient-name/', views.get_patient_name, name='get_patient_name'),
    path('ajax/diagnose-now/', views.ajax_diagnose_now, name='ajax_diagnose_now'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('logout/', views.logout_view, name='logout'),
    path('edit-patient/<int:patient_id>/', views.edit_patient, name='edit_patient'),

path('retrieve-password/', auth_views.PasswordResetView.as_view(
    template_name='retrieve_password.html',
    email_template_name='reset_password_email.html',
    subject_template_name='reset_password_subject.txt',
    success_url='/retrieve-password/done/'
), name='password_reset'),

    path('retrieve-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='retrieve_password_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='reset_password_form.html',
        success_url='/reset-password/done/'
    ), name='password_reset_confirm'),

    path('reset-password/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='reset_password_done.html'
    ), name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
