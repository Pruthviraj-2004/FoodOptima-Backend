from django import forms
from django.utils import timezone
from .models import Company, CompanyManager, EmailAccount, EmailTemplate, EmployeeEventResponse, EmployeeResponse, Employee, OrganizationEvent, WorkingDays

class EmployeeResponseForm(forms.ModelForm):
    class Meta:
        model = EmployeeResponse
        fields = ['employee', 'date', 'response']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'value': timezone.localdate()
                }
            ),
            'response': forms.Select(attrs={'class': 'form-control'}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'email'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class DateForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'value': timezone.localdate(),
                'class': 'form-control'
            }
        )
    )

class EmployeeSelectForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all().order_by('name'),
        label="Select Employee",
        empty_label="Choose...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        manager = kwargs.pop('manager', None)
        super(EmployeeSelectForm, self).__init__(*args, **kwargs)
        if manager:
            self.fields['employee'].queryset = Employee.objects.filter(manager=manager)

class FilterResponseForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all().order_by('name'),
        required=False,
        label="Select Employee",
        empty_label="All Employees",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        required=False,
        label="Select Date"
    )

class WorkingDaysForm(forms.ModelForm):
    class Meta:
        model = WorkingDays
        fields = ['month', 'year', 'days', 'manager']
        widgets = {
            'month': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'days': forms.TextInput(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(WorkingDaysForm, self).__init__(*args, **kwargs)
        # Optionally filter the queryset for the 'manager' field if necessary
        self.fields['manager'].queryset = CompanyManager.objects.all()

class EmailForm(forms.Form):
    title = forms.CharField(
        max_length=128,
        label='Email Title',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the email title'})
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter the body of the email', 'rows': 5})
    )
    sign = forms.CharField(
        max_length=64,
        label='Signature',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your signature'})
    )

class OrganizationEventForm(forms.ModelForm):
    class Meta:
        model = OrganizationEvent
        fields = ['name', 'date', 'manager']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'value': timezone.localdate()
                }
            ),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(OrganizationEventForm, self).__init__(*args, **kwargs)
        # Optionally filter the queryset for the 'manager' field if necessary
        self.fields['manager'].queryset = CompanyManager.objects.all()

class EmployeeEventResponseForm(forms.ModelForm):
    class Meta:
        model = EmployeeEventResponse
        fields = ['employee', 'event', 'date', 'response']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'event': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'value': timezone.localdate()
                }
            ),
            'response': forms.Select(attrs={'class': 'form-control'}),
        }

class EventSelectForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=OrganizationEvent.objects.all(),
        empty_label="Select an event",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class EventEmailForm(forms.Form):
    title = forms.CharField(
        max_length=128,
        label='Email Title',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the email title'})
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter the body of the email', 'rows': 5})
    )
    sign = forms.CharField(
        max_length=64,
        label='Signature',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your signature'})
    )
    event = forms.ModelChoiceField(
        queryset=OrganizationEvent.objects.all(),
        label='Select Event',
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select an event"
    )

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'domain']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'domain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Domain'}),
        }

class CompanySelectionForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        label='Select Company',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class CompanyManagerForm(forms.ModelForm):
    class Meta:
        model = CompanyManager
        fields = ['name', 'email', 'password', 'app_password']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Manager Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Manager Email'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password for Login'}),
            'app_password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'App Password with spaces (Example for gmail:aaaa aaaa aaaa aaaa) (Example for outlook: aaaaaaaaaaaa)'}),
        }

class EmailAccountForm(forms.ModelForm):
    class Meta:
        model = EmailAccount
        fields = ['smtp_server', 'smtp_port', 'use_tls', 'use_ssl']
        widgets = {
            'smtp_server': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SMTP Server'}),
            'smtp_port': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'SMTP Port(587)'}),
            'use_tls': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'use_ssl': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Subject'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Email Body', 'rows': 5}),
        }

class EmployeeNameUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter new name',
                'style': 'width: 100%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px;'
            }),
        }

class UpdateManagerNameForm(forms.ModelForm):
    class Meta:
        model = CompanyManager
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter new name',
                'style': 'width: 100%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px;'
            }),
        }

class UpdateEmailAccountForm(forms.ModelForm):
    class Meta:
        model = EmailAccount
        fields = ['email', 'smtp_server', 'smtp_port', 'use_tls', 'use_ssl']
        
            