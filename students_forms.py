"""
Django forms for student registration and authentication.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Student


class StudentRegistrationForm(UserCreationForm):
    """Custom registration form for students."""
    first_name = forms.CharField(max_length=100, required=True, label='First Name')
    last_name = forms.CharField(max_length=100, required=True, label='Last Name')
    email = forms.EmailField(required=True)
    roll_number = forms.CharField(max_length=20, required=True, label='Roll Number')
    phone = forms.CharField(max_length=15, required=False, label='Phone Number')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'roll_number', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Username for login (letters, digits, and @/./+/-/_ only)'
        self.fields['password1'].help_text = 'Password must contain letters, numbers, and special characters'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_roll_number(self):
        roll_number = self.cleaned_data.get('roll_number')
        if Student.objects.filter(roll_number=roll_number).exists():
            raise forms.ValidationError('This roll number is already registered.')
        return roll_number

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                roll_number=self.cleaned_data['roll_number'],
                phone=self.cleaned_data.get('phone', '')
            )
        return user


class StudentLoginForm(AuthenticationForm):
    """Custom login form for students."""
    username = forms.CharField(label='Username', max_length=254)
    password = forms.CharField(label='Password', strip=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'password')
