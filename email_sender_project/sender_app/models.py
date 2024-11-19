from django.db import models
from .fields import EncryptedEmailField
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
 
# from encrypted_model_fields.fields import EncryptedCharField

# class MyModel(models.Model):
#     secure_data = EncryptedCharField(max_length=100)

class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CompanyManager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    app_password = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='managers')
    login_count = models.IntegerField(default=0)
    send_mails = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.name} ({self.email})"

class EmailAccount(models.Model):
    email_account_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    smtp_server = models.CharField(max_length=255)
    smtp_port = models.IntegerField()
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='email_accounts')
    manager = models.ForeignKey(CompanyManager, on_delete=models.CASCADE, related_name='email_accounts')
    
    def __str__(self):
        return self.email

class EmailTemplate(models.Model):
    email_template_id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    manager = models.ForeignKey(CompanyManager, on_delete=models.CASCADE, related_name='email_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Template for {self.manager.name} - {self.subject}"



class Employee(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = EncryptedEmailField(max_length=254, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    manager = models.ForeignKey(CompanyManager, on_delete=models.CASCADE, related_name='employees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

           
class EmployeeResponse(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    response = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.response}"
    
    class Meta:
        unique_together = ('employee', 'date')

class WorkingDays(models.Model):
    MONTH_CHOICES = [
        (1, "January"), (2, "February"), (3, "March"),
        (4, "April"), (5, "May"), (6, "June"),
        (7, "July"), (8, "August"), (9, "September"),
        (10, "October"), (11, "November"), (12, "December")
    ]

    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    days = models.JSONField(default=list)
    manager = models.ForeignKey('CompanyManager', on_delete=models.CASCADE, related_name='working_days')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_month_display()} {self.year} - {self.manager.name}"

    class Meta:
        verbose_name_plural = "Working Days"
        unique_together = ('month', 'year', 'manager')

class OrganizationEvent(models.Model):
    event_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    date = models.DateField()
    manager = models.ForeignKey('CompanyManager', on_delete=models.CASCADE, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.date} (Managed by {self.manager.name})"

class EmployeeEventResponse(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    response = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    event = models.ForeignKey(OrganizationEvent, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.name} - {self.event.name} - {self.date} - {self.response}"
    
    class Meta:
        unique_together = ('employee', 'date', 'event')


