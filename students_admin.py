"""
Admin configuration for students app.
"""
from django.contrib import admin
from .models import Student, Performance, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'roll_number', 'phone', 'date_registered', 'is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'roll_number']
    list_filter = ['date_registered', 'is_active']
    readonly_fields = ['date_registered', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Student Details', {
            'fields': ('roll_number', 'phone', 'date_of_birth')
        }),
        ('Access Control', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('date_registered', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        """Bulk action to activate students."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} student(s) activated.')
    make_active.short_description = "Mark selected students as Active"
    
    def make_inactive(self, request, queryset):
        """Bulk action to deactivate students."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} student(s) deactivated.')
    make_inactive.short_description = "Mark selected students as Inactive"


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'score', 'date_recorded']
    search_fields = ['student__user__username', 'student__roll_number']
    list_filter = ['subject', 'date_recorded']
    date_hierarchy = 'date_recorded'
    readonly_fields = ['date_recorded']
    
    fieldsets = (
        ('Student & Subject', {
            'fields': ('student', 'subject')
        }),
        ('Performance', {
            'fields': ('score', 'remarks')
        }),
        ('Date', {
            'fields': ('date_recorded',)
        }),
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status']
    search_fields = ['student__user__username', 'student__roll_number']
    list_filter = ['status', 'date']
    date_hierarchy = 'date'
    readonly_fields = ['date']
    
    fieldsets = (
        ('Student', {
            'fields': ('student',)
        }),
        ('Attendance', {
            'fields': ('date', 'status')
        }),
    )
