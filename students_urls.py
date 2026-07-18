"""
URL routing for students app.
"""
from django.urls import path
from . import views
from . import students_api

app_name = 'students'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.student_profile, name='profile'),
    path('api/chart-scores/', views.chart_data_scores, name='chart_scores'),
    path('api/chart-attendance/', views.chart_data_attendance, name='chart_attendance'),
    path('api/chart-students/', views.chart_data_total_students, name='chart_students'),
    path('api/calendar-data/', views.calendar_data, name='calendar_data'),
    
    # JWT API endpoints
    path('api/login/', students_api.api_login, name='api_login'),
    path('api/refresh/', students_api.api_refresh, name='api_refresh'),
    path('api/logout/', students_api.api_logout, name='api_logout'),
    path('api/verify/', students_api.api_verify_token, name='api_verify_token'),
    path('api/verify-get/', students_api.api_verify_token_get, name='api_verify_token_get'),
]
