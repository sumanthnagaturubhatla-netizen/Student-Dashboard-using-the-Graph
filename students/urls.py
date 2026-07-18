from django.urls import path
from . import views
from . import api

app_name = 'students'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.student_profile, name='profile'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/chart-scores/', views.chart_data_scores, name='chart_scores'),
    path('api/chart-attendance/', views.chart_data_attendance, name='chart_attendance'),
    path('api/chart-students/', views.chart_data_total_students, name='chart_students'),
    path('api/calendar-data/', views.calendar_data, name='calendar_data'),
    path('api/student-count/', views.api_student_count, name='api_student_count'),
    
    # Admin access management
    path('admin-login/', views.admin_login, name='admin_login'),
    path('manage-students/', views.manage_students, name='manage_students'),
    path('api/toggle-student/<int:student_id>/', views.toggle_student_access, name='toggle_student'),
    
    # JWT API endpoints
    path('api/login/', api.api_login, name='api_login'),
    path('api/refresh/', api.api_refresh, name='api_refresh'),
    path('api/logout/', api.api_logout, name='api_logout'),
    path('api/verify/', api.api_verify_token, name='api_verify_token'),
    path('api/verify-get/', api.api_verify_token_get, name='api_verify_token_get'),
]
