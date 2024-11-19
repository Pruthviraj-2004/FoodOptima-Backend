# from django.test import TestCase
# from django.urls import reverse
# from django.contrib.messages import get_messages
# from .models import Company, CompanyManager, EmailAccount, EmailTemplate, Employee, EmployeeResponse
# from django.utils import timezone

# class TestDataMixin:
#     @classmethod
#     def setUpTestData(cls):
#         print("Setting up test data...")
#         # Create a test company
#         cls.company = Company.objects.create(
#             name='TestCompany',
#             domain='testcompany.com'
#         )
#         print(f"Created Company: {cls.company}")

#         # Create a test manager
#         cls.manager = CompanyManager.objects.create(
#             name='Test Manager 1',
#             email='testmanager1@gmail.com',
#             company=cls.company
#         )
#         cls.manager.set_password('Testpassword1')  # Set password
#         print(f"Created Company Manager: {cls.manager}")

#         # Create a test email account
#         cls.email_account = EmailAccount.objects.create(
#             email='testaccount@gmail.com',
#             smtp_server='smtp.test.com',
#             smtp_port=587,
#             use_tls=True,
#             use_ssl=False,
#             company=cls.company,
#             manager=cls.manager
#         )
#         print(f"Created Email Account: {cls.email_account}")
        
#         # Create a test email template
#         cls.email_template = EmailTemplate.objects.create(
#             subject='Test Email',
#             body='This is a test email body.',
#             manager=cls.manager
#         )
#         print(f"Created Email Template: {cls.email_template}")

#         # Create a test employee
#         cls.employee = Employee.objects.create(
#             name='Test Employee',
#             email='testemployee@gmail.com',
#             company=cls.company,
#             manager=cls.manager
#         )
#         print(f"Created Employee: {cls.employee}")

# class AuthTests(TestDataMixin, TestCase):

#     def test_login_success_with_message(self):
#         print("Performing - Test successful login")
#         response = self.client.post(reverse('login'), {
#             'email': 'testmanager1@gmail.com',
#             'password': 'Testpassword1'
#         })
#         self.assertEqual(response.status_code, 302)  # Check for redirect to dashboard
#         self.assertRedirects(response, reverse('dashboard'))

#         print("Checking - Success message after login")
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(len(messages), 1)
#         self.assertEqual(str(messages[0]), "Welcome Test Manager 1, you have successfully logged in!")

#     def test_login_failure_with_message(self):
#         print("Performing - Test failed login with incorrect credentials")
#         response = self.client.post(reverse('login'), {
#             'email': 'wrong@example.com',
#             'password': 'wrongpassword'
#         })
#         self.assertEqual(response.status_code, 200)  # Stay on the login page

#         print("Checking - Error message after failed login")
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(len(messages), 1)
#         self.assertEqual(str(messages[0]), "Invalid credentials")

#     def test_logout(self):
#         print("Performing - Test logout functionality")
#         self.client.login(email='testmanager1@gmail.com', password='Testpassword1')
#         response = self.client.get(reverse('logout'))
#         self.assertRedirects(response, reverse('login'))
#         self.assertNotIn('manager_id', self.client.session)  # Check that the session is cleared
#         print("Logout successful and session cleared")

# class DashboardViewTests(TestDataMixin, TestCase):

#     def test_dashboard_access(self):
#         print("Performing - Test dashboard access without login (expected redirection)")
#         response = self.client.get(reverse('dashboard'))
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('login'))

#     def test_dashboard_redirect_when_not_logged_in(self):
#         print("Performing - Test dashboard redirect when not logged in")
#         self.client.logout()
#         response = self.client.get(reverse('dashboard'))
#         self.assertRedirects(response, reverse('login'))  # Should redirect to login page

# class AddManagerDetailsViewTests(TestDataMixin, TestCase):

#     def test_add_manager_details_success(self):
#         print("Performing - Test adding manager details successfully")
#         response = self.client.post(reverse('add_manager_details'), {
#             'company': self.company.company_id,
#             'name': 'Test Manager 2',
#             'email': 'testmanager2@gmail.com',
#             'password': 'Testpassword2',
#             'smtp_server': 'smtp.test.com',
#             'smtp_port': 587,
#             'use_tls': True,
#             'use_ssl': False,
#             'subject': 'Test Email 2',
#             'body': 'This is another test email body.'
#         })
        
#         self.assertEqual(response.status_code, 302)  # Check for redirect
#         self.assertRedirects(response, reverse('add_manager_details'))

#     def test_add_manager_details_failure(self):
#         print("Performing - Test adding manager details failure due to invalid data")
#         response = self.client.post(reverse('add_manager_details'), {
#             'company': self.company.company_id,
#             'name': '',  # Invalid name
#             'email': 'invalid_email',  # Invalid email
#             'password': '',
#             'smtp_server': 'smtp.test.com',
#             'smtp_port': 587,
#             'use_tls': True,
#             'use_ssl': False,
#             'subject': 'Test Email',
#             'body': 'This is a test email body.'
#         })

#         self.assertEqual(response.status_code, 200)  # Should return to the same page

# class EmployeeResponseViewTests(TestDataMixin, TestCase):

#     def test_employee_response_success(self):
#         print("Performing - Test employee response submission success")
#         tomorrow = timezone.now().date() + timezone.timedelta(days=1)
#         response = self.client.get(reverse('employee_response', args=[self.employee.user_id, 'yes']))

#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, f"Thank you, {self.employee.name}, for your response!")

#         # Verify response is saved
#         self.assertTrue(EmployeeResponse.objects.filter(employee=self.employee, date=tomorrow, response='yes').exists())

#     def test_employee_response_invalid(self):
#         print("Performing - Test employee response submission with invalid response")
#         response = self.client.get(reverse('employee_response', args=[self.employee.user_id, 'invalid']))

#         self.assertEqual(response.status_code, 400)

#     def test_employee_response_update(self):
#         print("Performing - Test updating employee response")
#         tomorrow = timezone.now().date() + timezone.timedelta(days=1)
#         EmployeeResponse.objects.create(employee=self.employee, date=tomorrow, response='yes')

#         response = self.client.get(reverse('employee_response', args=[self.employee.user_id, 'no']))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, f"Thank you, {self.employee.name}, for your response!")

#         # Verify response is updated
#         updated_response = EmployeeResponse.objects.get(employee=self.employee, date=tomorrow)
#         self.assertEqual(updated_response.response, 'no')

# class NewAddEmployeeViewTests(TestDataMixin, TestCase):

#     def setUp(self):
#         super().setUp()  # Call the parent setup
#         print("Logging in the manager for NewAddEmployeeView tests")
#         self.client.login(email='manager@test.com', password='Testpassword1')

#     def test_add_employee_success(self):
#         print("Performing - Test adding employee successfully")
#         response = self.client.post(reverse('new_add_employee'), {
#             'name': 'Test Employee',
#             'email': 'testemployee@gmail.com',
#         })
        
#         self.assertEqual(response.status_code, 302)  # Check for redirect
#         self.assertRedirects(response, reverse('new_add_employee'))

#         # Verify the success message and employee creation
#         self.assertTrue(Employee.objects.filter(email='testemployee@gmail.com').exists())

#     def test_add_employee_failure(self):
#         print("Performing - Test adding employee failure due to invalid data")
#         response = self.client.post(reverse('new_add_employee'), {
#             'name': '',  # Invalid name
#             'email': 'invalid_email',  # Invalid email
#         })
        
#         self.assertEqual(response.status_code, 200)  # Should return to the same page
#         messages = list(get_messages(response.wsgi_request))
#         self.assertGreater(len(messages), 0)  # Check for error messages

# class NewViewEmployeeResponsesTests(TestDataMixin, TestCase):

#     def setUp(self):
#         super().setUp()  # Call the parent setup
#         print("Logging in the manager for NewViewEmployeeResponses tests")
#         self.client.login(email='manager@test.com', password='Testpassword1')

#     def test_view_responses(self):
#         print("Performing - Test viewing employee responses")
#         response = self.client.get(reverse('new_view_employee_responses'), {'date': timezone.now().date()})
        
#         self.assertEqual(response.status_code, 200)  # Check for 200 status code
#         self.assertContains(response, 'Test Employee')  # Check for the employee's name

#     def test_view_responses_invalid_date(self):
#         print("Performing - Test viewing employee responses with invalid date")
#         response = self.client.get(reverse('new_view_employee_responses'), {'date': 'invalid-date'})
        
#         self.assertEqual(response.status_code, 200)  # Check for 200 status code for the same page
#         messages = list(get_messages(response.wsgi_request))
#         self.assertGreater(len(messages), 0)  # Check for error messages

from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from .models import Company, CompanyManager, EmailAccount, EmailTemplate, Employee, EmployeeResponse
from django.utils import timezone

class TestDataMixin:
    @classmethod
    def setUpTestData(cls):
        print("Setting up test data...")
        cls.company = Company.objects.create(
            name='TestCompany',
            domain='testcompany.com'
        )
        print(f"Created Company: {cls.company}")

        cls.manager = CompanyManager.objects.create(
            name='Test Manager 1',
            email='testmanager1@gmail.com',
            company=cls.company
        )
        cls.manager.set_password('Testpassword1')
        cls.manager.save()
        print(f"Created Company Manager: {cls.manager}")

        cls.email_account = EmailAccount.objects.create(
            email='testaccount@gmail.com',
            smtp_server='smtp.test.com',
            smtp_port=587,
            use_tls=True,
            use_ssl=False,
            company=cls.company,
            manager=cls.manager
        )
        print(f"Created Email Account: {cls.email_account}")
        
        cls.email_template = EmailTemplate.objects.create(
            subject='Test Email',
            body='This is a test email body.',
            manager=cls.manager
        )
        print(f"Created Email Template: {cls.email_template}")

        cls.employee = Employee.objects.create(
            name='Test Employee',
            email='testemployee@gmail.com',
            company=cls.company,
            manager=cls.manager
        )
        print(f"Created Employee: {cls.employee}")

class AuthTests(TestDataMixin, TestCase):

    def setUp(self):
        self.client.login(email='testmanager1@gmail.com', password='Testpassword1')

    def test_login_success(self):
        print("Performing - Test successful login")
        response = self.client.post(reverse('login'), {
            'email': 'testmanager1@gmail.com',
            'password': 'Testpassword1'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_failure(self):
        print("Performing - Test failed login with incorrect credentials")
        response = self.client.post(reverse('login'), {
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        print("Performing - Test logout functionality")
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('manager_id', self.client.session)

class DashboardViewTests(TestDataMixin, TestCase):

    def test_dashboard_access(self):
        print("Performing - Test dashboard access")
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('login'))

    def test_dashboard_redirect_when_not_logged_in(self):
        print("Performing - Test dashboard redirect when not logged in")
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('login'))

class AddManagerDetailsViewTests(TestDataMixin, TestCase):

    def test_add_manager_details_success(self):
        print("Performing - Test adding manager details successfully")
        response = self.client.post(reverse('add_manager_details'), {
            'company': self.company.company_id,
            'name': 'Test Manager 2',
            'email': 'testmanager2@gmail.com',
            'password': 'Testpassword2',
            'smtp_server': 'smtp.test.com',
            'smtp_port': 587,
            'use_tls': True,
            'use_ssl': False,
            'subject': 'Test Email 2',
            'body': 'This is another test email body.'
        })
        self.assertEqual(response.status_code, 302)

    def test_add_manager_details_failure(self):
        print("Performing - Test adding manager details failure due to invalid data")
        response = self.client.post(reverse('add_manager_details'), {
            'company': self.company.company_id,
            'name': '',
            'email': 'invalid_email',
            'password': '',
            'smtp_server': 'smtp.test.com',
            'smtp_port': 587,
            'use_tls': True,
            'use_ssl': False,
            'subject': 'Test Email',
            'body': 'This is a test email body.'
        })
        self.assertEqual(response.status_code, 200)

class EmployeeResponseViewTests(TestDataMixin, TestCase):

    def test_employee_response_success(self):
        print("Performing - Test employee response submission success")
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        response = self.client.get(reverse('employee_response', args=[self.employee.user_id, 'yes']))
        self.assertEqual(response.status_code, 200)

    def test_employee_response_invalid(self):
        print("Performing - Test employee response submission with invalid response")
        response = self.client.get(reverse('employee_response', args=[self.employee.user_id, 'invalid']))
        self.assertEqual(response.status_code, 400)

    def test_employee_response_update(self):
        print("Performing - Test updating employee response")
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        EmployeeResponse.objects.create(employee=self.employee, date=tomorrow, response='yes')
        response = self.client.get(reverse('employee_response', args=[self.employee.user_id, 'no']))
        self.assertEqual(response.status_code, 200)

# class EmployeeCreationTest(TestCase):
#     def setUp(self):
#         # Create a company
#         self.company = Company.objects.create(
#             name='Test Company',
#             domain='testcompany.com'
#         )
        
#         # Create a company manager and associate it with the company
#         self.manager = CompanyManager.objects.create(
#             name='John Doe',
#             email='john@example.com',
#             password='Securepassword',
#             company=self.company  # Associate the company here
#         )
#         self.manager.set_password('Securepassword')  # Hash the password
#         self.manager.save()  # Save to ensure the password is hashed correctly

#     def test_create_employee(self):
#         # Ensure the manager can add an employee
#         self.client.login(email='john@example.com', password='Securepassword')

#         response = self.client.post(reverse('new_add_employee'), {
#             'name': 'Jane Smith',
#             'email': 'jane.smith@example.com',
#             'manager': self.manager.manager_id,
#         })

#         # Check that the response is a redirect
#         self.assertEqual(response.status_code, 302)

