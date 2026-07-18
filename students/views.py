"""
Views for student dashboard application.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Q
import json
import calendar

from .forms import StudentRegistrationForm, StudentLoginForm
from .models import Student, Performance, Attendance, RefreshToken
from .jwt_utils import JWTHandler


def _sample_performance_data():
    today = timezone.now().date()
    return [
        {'date_recorded': today - timedelta(days=28), 'score': 75},
        {'date_recorded': today - timedelta(days=21), 'score': 82},
        {'date_recorded': today - timedelta(days=14), 'score': 88},
        {'date_recorded': today - timedelta(days=7), 'score': 93},
        {'date_recorded': today, 'score': 90},
    ]


def _sample_attendance_rate():
    return 92.0


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
            return redirect('students:login')
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
        if request.user.is_staff:
            return redirect('students:manage_students')
        return redirect('students:dashboard')
    
    if request.method == 'POST':
        form = StudentLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if student access is enabled
                try:
                    student = user.student
                    if not student.is_active:
                        messages.error(request, 'Your account access has been disabled by the administrator.')
                        return render(request, 'login.html', {'form': form})
                except Student.DoesNotExist:
                    messages.error(request, 'Student profile not found.')
                    return render(request, 'login.html', {'form': form})
                
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
                return redirect('students:dashboard')
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
    return redirect('students:login')


@login_required(login_url='students:login')
def dashboard(request):
    """Display student dashboard with charts."""
    if request.user.is_staff:
        return redirect('students:manage_students')
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:login')
    
    today = timezone.now().date()
    current_year = today.year
    current_month = today.month
    
    performances = Performance.objects.filter(student=student).order_by('date_recorded')
    attendance_records = Attendance.objects.filter(student=student)
    attendance_count = attendance_records.count()
    present_count = attendance_records.filter(status='PRESENT').count()
    attendance_rate = round((present_count / attendance_count) * 100, 1) if attendance_count else _sample_attendance_rate()
    
    if performances.exists():
        performance_count = performances.count()
        average_score = performances.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    else:
        sample_data = _sample_performance_data()
        performance_count = len(sample_data)
        average_score = sum(item['score'] for item in sample_data) / performance_count

    context = {
        'student': student,
        'total_students': Student.objects.count(),
        'performance_count': performance_count,
        'avg_score': average_score,
        'attendance_rate': attendance_rate,
        'current_month': current_month,
        'current_year': current_year,
        'month_name': calendar.month_name[current_month],
    }
    
    return render(request, 'dashboard.html', context)


@login_required(login_url='students:login')
@require_http_methods(["GET"])
def chart_data_scores(request):
    """API endpoint for student scores chart data."""
    try:
        student = request.user.student
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    
    performances = Performance.objects.filter(student=student).order_by('date_recorded')
    if performances.exists():
        labels = [p.date_recorded.strftime('%b %d') for p in performances]
        scores = [p.score for p in performances]
    else:
        sample_data = _sample_performance_data()
        labels = [item['date_recorded'].strftime('%b %d') for item in sample_data]
        scores = [item['score'] for item in sample_data]
    
    data = {
        'labels': labels,
        'data': scores,
    }
    
    return JsonResponse(data)


@login_required(login_url='students:login')
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


@login_required(login_url='students:login')
def student_profile(request):
    """Display student profile."""
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:login')
    
    context = {
        'student': student,
    }
    
    return render(request, 'profile.html', context)


@login_required(login_url='students:login')
@require_http_methods(['GET'])
def api_student_count(request):
    """API endpoint to get total student count."""
    total_students = Student.objects.count()
    
    return JsonResponse({
        'count': total_students,
        'status': 'success'
    })


@login_required(login_url='students:login')
def calendar_view(request):
    """Display dedicated calendar page with registration data."""
    today = timezone.now()
    current_year = int(request.GET.get('year', today.year))
    current_month = int(request.GET.get('month', today.month))
    
    # Get the month name
    month_name = calendar.month_name[current_month]
    
    # Build calendar data
    cal = calendar.monthcalendar(current_year, current_month)
    
    # Get all registrations for the month
    registrations = Student.objects.filter(
        date_registered__year=current_year,
        date_registered__month=current_month
    ).values('date_registered__day').annotate(count=Count('id'))
    
    registrations_by_day = {str(reg['date_registered__day']): reg['count'] for reg in registrations}
    
    # Calculate statistics
    total_registrations = sum(registrations_by_day.values())
    peak_day = max(registrations_by_day.items(), key=lambda x: x[1]) if registrations_by_day else None
    active_days = len(registrations_by_day)
    
    context = {
        'current_year': current_year,
        'current_month': current_month,
        'month_name': month_name,
        'calendar_data': cal,
        'registrations_by_day': registrations_by_day,
        'total_registrations': total_registrations,
        'peak_day': peak_day,
        'active_days': active_days,
    }
    
    return render(request, 'calendar.html', context)


def admin_login(request):
    """Admin login page."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('students:manage_students')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome Admin {user.first_name}!')
            return redirect('students:manage_students')
        else:
            messages.error(request, 'Invalid credentials or not an admin.')
    
    return render(request, 'admin_login.html')


@login_required(login_url='students:admin_login')
def manage_students(request):
    """Manage student access with toggle buttons."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('students:login')
    
    students = Student.objects.all().select_related('user')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            models.Q(user__first_name__icontains=search_query) |
            models.Q(user__username__icontains=search_query) |
            models.Q(roll_number__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        students = students.filter(is_active=True)
    elif status_filter == 'inactive':
        students = students.filter(is_active=False)
    
    context = {
        'students': students,
        'total_students': Student.objects.count(),
        'active_students': Student.objects.filter(is_active=True).count(),
        'inactive_students': Student.objects.filter(is_active=False).count(),
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'manage_students.html', context)


@require_http_methods(["POST"])
def toggle_student_access(request, student_id):
    """Toggle student access status via AJAX."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        student = Student.objects.get(id=student_id)
        student.is_active = not student.is_active
        student.save()
        
        return JsonResponse({
            'success': True,
            'is_active': student.is_active,
            'message': f'Access {"enabled" if student.is_active else "disabled"} for {student.user.get_full_name()}'
        })
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
