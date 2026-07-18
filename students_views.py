from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg
import json
import calendar

from .forms import StudentRegistrationForm, StudentLoginForm
from .students_models import Student, Performance, Attendance, RefreshToken
from .jwt_utils import JWTHandler


def register(request):
    """Handle student registration."""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Generate JWT tokens for API access
            from django.conf import settings
            jwt_handler = JWTHandler(settings.SECRET_KEY)
            access_token = jwt_handler.generate_access_token(user.id, user.username)
            refresh_token_str = jwt_handler.generate_refresh_token()
            
            # Store refresh token
            expires_at = timezone.now() + timedelta(days=7)
            RefreshToken.objects.create(
                user=user,
                token=refresh_token_str,
                expires_at=expires_at
            )
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """Handle student login and issue JWT tokens."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = StudentLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Generate JWT tokens for API access
                from django.conf import settings
                jwt_handler = JWTHandler(settings.SECRET_KEY)
                access_token = jwt_handler.generate_access_token(user.id, user.username)
                refresh_token_str = jwt_handler.generate_refresh_token()
                
                # Store refresh token
                expires_at = timezone.now() + timedelta(days=7)
                RefreshToken.objects.create(
                    user=user,
                    token=refresh_token_str,
                    expires_at=expires_at
                )
                
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = StudentLoginForm()
    
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Handle logout and revoke refresh tokens."""
    # Revoke all refresh tokens for this user
    if request.user.is_authenticated:
        RefreshToken.objects.filter(user=request.user, is_revoked=False).update(is_revoked=True)
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    """Display student dashboard with charts."""
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('login')
    
    today = timezone.now().date()
    current_year = today.year
    current_month = today.month
    
    context = {
        'student': student,
        'total_students': Student.objects.count(),
        'current_month': current_month,
        'current_year': current_year,
        'month_name': calendar.month_name[current_month],
    }
    
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def chart_data_scores(request):
    """API endpoint for student scores chart data."""
    try:
        student = request.user.student
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    
    performances = Performance.objects.filter(student=student).order_by('date_recorded')
    
    data = {
        'labels': [str(p.date_recorded) for p in performances],
        'datasets': [
            {
                'label': f'{p.get_subject_display()}',
                'data': [p.score for p in performances if p.subject == p.subject],
                'borderColor': 'rgba(75, 192, 192, 1)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'tension': 0.1
            }
        ]
    }
    
    return JsonResponse(data)


@login_required(login_url='login')
@require_http_methods(["GET"])
def chart_data_attendance(request):
    """API endpoint for attendance chart data."""
    try:
        student = request.user.student
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    
    last_30_days = timezone.now().date() - timedelta(days=30)
    attendance_records = Attendance.objects.filter(
        student=student,
        date__gte=last_30_days
    ).values('status').annotate(count=Count('status'))
    
    labels = [record['status'] for record in attendance_records]
    data = [record['count'] for record in attendance_records]
    
    chart_data = {
        'labels': labels,
        'datasets': [
            {
                'label': 'Attendance Count (Last 30 Days)',
                'data': data,
                'backgroundColor': [
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(255, 193, 7, 0.6)',
                ],
                'borderColor': [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 193, 7, 1)',
                ],
                'borderWidth': 2
            }
        ]
    }
    
    return JsonResponse(chart_data)


@login_required(login_url='login')
@require_http_methods(["GET"])
def chart_data_total_students(request):
    """API endpoint for total registered students (pie chart)."""
    # Group students by registration month
    students = Student.objects.values('date_registered__month').annotate(count=Count('id'))
    
    labels = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    month_data = {}
    
    for record in students:
        month = record['date_registered__month']
        month_data[month] = record['count']
    
    data = [month_data.get(i+1, 0) for i in range(12)]
    
    chart_data = {
        'labels': labels,
        'datasets': [
            {
                'label': 'Total Students Registered',
                'data': data,
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(199, 199, 199, 0.7)',
                    'rgba(83, 102, 255, 0.7)',
                    'rgba(255, 99, 255, 0.7)',
                    'rgba(99, 255, 132, 0.7)',
                    'rgba(255, 193, 7, 0.7)',
                    'rgba(63, 81, 181, 0.7)',
                ],
                'borderWidth': 2
            }
        ]
    }
    
    return JsonResponse(chart_data)


@require_http_methods(["GET"])
def calendar_data(request):
    """API endpoint for calendar registration data by date."""
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month
    
    # Get number of days in the month
    _, num_days = calendar.monthrange(year, month)
    
    # Get registrations for each day of the month
    registrations_by_day = {}
    students = Student.objects.filter(
        date_registered__year=year,
        date_registered__month=month
    ).values('date_registered__day').annotate(count=Count('id'))
    
    for record in students:
        day = record['date_registered__day']
        registrations_by_day[day] = record['count']
    
    # Build calendar data
    calendar_data = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'days': [],
        'total_registrations': sum(registrations_by_day.values()),
        'registrations_by_day': registrations_by_day
    }
    
    # Get the calendar matrix
    cal_matrix = calendar.monthcalendar(year, month)
    for week in cal_matrix:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': 0, 'count': 0})
            else:
                count = registrations_by_day.get(day, 0)
                week_data.append({'day': day, 'count': count})
        calendar_data['days'].append(week_data)
    
    return JsonResponse(calendar_data)


@login_required(login_url='login')
def student_profile(request):
    """Display student profile."""
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('login')
    
    context = {
        'student': student,
    }
    
    return render(request, 'profile.html', context)
