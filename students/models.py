from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    roll_number = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    date_registered = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Check to allow student access")

    class Meta:
        ordering = ['-date_registered']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.roll_number})"


class Performance(models.Model):
    """Student performance records (scores and attendance)."""
    SUBJECT_CHOICES = [
        ('MATH', 'Mathematics'),
        ('ENG', 'English'),
        ('SCI', 'Science'),
        ('HIST', 'History'),
        ('GEO', 'Geography'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='performances')
    subject = models.CharField(max_length=10, choices=SUBJECT_CHOICES)
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    date_recorded = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_recorded']
        unique_together = ('student', 'subject', 'date_recorded')

    def __str__(self):
        return f"{self.student.user.username} - {self.subject}: {self.score}"


class Attendance(models.Model):
    """Student attendance records."""
    ATTENDANCE_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES, default='PRESENT')

    class Meta:
        ordering = ['-date']
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.user.username} - {self.date}: {self.status}"


class RefreshToken(models.Model):
    """Stores issued refresh tokens for validation and revocation."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.TextField(unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_revoked = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_revoked']),
            models.Index(fields=['token']),
        ]
    
    def __str__(self):
        return f"RefreshToken for {self.user.username} - Revoked: {self.is_revoked}"
    
    def is_expired(self):
        """Check if refresh token has expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if refresh token is valid (not revoked and not expired)."""
        return not self.is_revoked and not self.is_expired()

