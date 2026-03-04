from django.urls import path
from . import views
from .views import logout_view,get_current_user,api_signup, api_login,get_all_users,get_logged_in_user
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Basic pages
    path('', views.index, name='talentShield'),
    path('resumebuilder.html', views.resume, name='resumepage'),
    path('upload.html', views.upload, name='uploadpage'),
    path('option.html', views.option, name='optionpage'),
    path('signup.html', views.signup, name='signuppage'),
    path('login.html', views.login_view, name='loginpage'),  # Fixed: Should use login_view, not signup
    path('results.html', views.results, name='resultpage'),
    path('profile.html', views.profile, name='profilepage'),
    path('candidate.html', views.candidate, name='candidatepage'),
    path('hrmanager.html', views.hrmanager, name='hrmanagerpage'),
    
    # Resume functionality
    path('resume/', views.resume, name='resume'),
    path("generate-pdf/", views.generate_pdf, name="generate_pdf"),
    
    # Upload and dashboard
    path('upload/', views.upload_resume, name='upload_resume'),
    path('hr-dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('view-resume/<int:resume_id>/', views.view_resume, name='view_resume'),
    path('update-status/<int:resume_id>/', views.update_status, name='update_status'),
    
    # Profile management
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('candidate-dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('logout/', views.login_view, name='logout'),
    
    # API endpoints
    path("api/login/", api_login, name="api_login"),
    path("api/signup/", api_signup, name="api_signup"),
    
    ###
    path('api/users/', get_all_users, name="users_api"),
    #############
    
    path('api/my-profile/', get_logged_in_user, name="logged_in_user_api"),
    
    ##
    
    path('api/current-user/', get_current_user, name="current_user"),
    ##
    path('api/logout/', logout_view, name="logout"),

    ########33

   

    path('hr-login/', views.hr_login, name='hr_login'),

]
# Static and media files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)