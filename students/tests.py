from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Student


class AdminStudentAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin'
        )
        
        # Create a non-admin student user
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='studentpassword',
            first_name='John',
            last_name='Doe'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            roll_number='ROLL001',
            phone='1234567890',
            is_active=True
        )

        # Create another student to verify search filters
        self.student_user_2 = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='studentpassword',
            first_name='Jane',
            last_name='Smith'
        )
        self.student_2 = Student.objects.create(
            user=self.student_user_2,
            roll_number='ROLL002',
            phone='0987654321',
            is_active=False
        )

    def test_manage_students_requires_admin(self):
        """Verify that non-admin users cannot access the student management view."""
        # Not logged in
        response = self.client.get(reverse('students:manage_students'))
        self.assertRedirects(response, f"{reverse('students:admin_login')}?next={reverse('students:manage_students')}", fetch_redirect_response=False)
        
        # Logged in as student
        self.client.login(username='student1', password='studentpassword')
        response = self.client.get(reverse('students:manage_students'))
        self.assertRedirects(response, reverse('students:login'), fetch_redirect_response=False)
        
        # Logged in as admin
        self.client.logout()
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('students:manage_students'))
        self.assertEqual(response.status_code, 200)

    def test_manage_students_search_and_filters(self):
        """Verify that the search functionality and active status filters work properly without crashing."""
        self.client.login(username='adminuser', password='adminpassword')
        
        # Search by username
        response = self.client.get(reverse('students:manage_students'), {'search': 'student1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'student1')
        self.assertNotContains(response, 'student2')
        
        # Search by roll number
        response = self.client.get(reverse('students:manage_students'), {'search': 'ROLL002'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'student2')
        self.assertNotContains(response, 'student1')

        # Filter by status: active
        response = self.client.get(reverse('students:manage_students'), {'status': 'active'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'student1')
        self.assertNotContains(response, 'student2')

        # Filter by status: inactive
        response = self.client.get(reverse('students:manage_students'), {'status': 'inactive'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'student2')
        self.assertNotContains(response, 'student1')

    def test_toggle_student_access_authorized(self):
        """Verify that toggle_student_access flips the active status for authorized admins."""
        self.client.login(username='adminuser', password='adminpassword')
        
        # Verify student 1 is active initially
        self.assertTrue(self.student.is_active)
        
        # Toggle status
        url = reverse('students:toggle_student', args=[self.student.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify status flipped to False
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_active)
        
        # Toggle status back
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_active)

    def test_toggle_student_access_unauthorized(self):
        """Verify that non-admin users cannot toggle student status."""
        # Logged in as normal student
        self.client.login(username='student1', password='studentpassword')
        url = reverse('students:toggle_student', args=[self.student.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        
        # Verify status did not change
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_active)
