from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Company, CompanyManager, EmailAccount, EmailTemplate, OrganizationEvent, Employee, EmployeeEventResponse, EmployeeResponse, WorkingDays
from .resources import CompanyManagerResource, CompanyResource, EmailAccountResource, EmailTemplateResource, EmployeeEventResponseResource, EmployeeResource, EmployeeResponseResource, OrganizationEventResource, WorkingDaysResource

@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResource
    list_display = ('user_id', 'name', 'email', 'company', 'manager', 'created_at', 'updated_at')
    list_filter = ('company', 'manager')
    search_fields = ('name', 'email', 'company__name', 'manager__name')


@admin.register(EmployeeResponse)
class EmployeeResponseAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResponseResource
    list_display = ('employee', 'date', 'response', 'created_at', 'updated_at')
    list_filter = ('employee', 'date', 'response')
    search_fields = ('employee__name', 'employee__email')

@admin.register(WorkingDays)
class WorkingDaysAdmin(ImportExportModelAdmin):
    resource_class = WorkingDaysResource
    list_display = ['month', 'year', 'manager', 'get_days', 'created_at', 'updated_at']
    list_filter = ['month', 'year', 'manager']
    search_fields = ['manager__name', 'year', 'month']
    
    def get_days(self, obj):
        return f"{len(obj.days)} days: {obj.days[:10]}..." if len(obj.days) > 10 else obj.days
    get_days.short_description = "Working Days"

@admin.register(OrganizationEvent)
class OrganizationEventAdmin(ImportExportModelAdmin):
    resource_class = OrganizationEventResource
    list_display = ('event_id', 'name', 'date', 'manager', 'created_at', 'updated_at')
    search_fields = ('event_id', 'name', 'manager__name')
    list_filter = ('date', 'manager')

@admin.register(EmployeeEventResponse)
class EmployeeEventResponseAdmin(ImportExportModelAdmin):
    resource_class = EmployeeEventResponseResource
    list_display = ('employee', 'event', 'date', 'response', 'created_at', 'updated_at')
    search_fields = ('employee__name', 'event__name', 'response')
    list_filter = ('date', 'response')

@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
    resource_class = CompanyResource
    list_display = ('company_id', 'name', 'domain', 'created_at', 'updated_at')
    search_fields = ('name', 'domain')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)

class EmailAccountAdmin(ImportExportModelAdmin):
    resource_class = EmailAccountResource
    list_display = ('email', 'smtp_server', 'manager', 'use_tls', 'use_ssl')
    search_fields = ('email', 'smtp_server', 'manager__name')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Modify the form to set the default email field value if creating new
        if not obj:
            # Set the email field with the manager's email
            manager_id = request.GET.get('manager_id')
            if manager_id:
                manager = CompanyManager.objects.get(pk=manager_id)
                form.base_fields['email'].initial = manager.email
        return form

admin.site.register(EmailAccount, EmailAccountAdmin)

@admin.register(EmailTemplate)
class EmailTemplateAdmin(ImportExportModelAdmin):
    resource_class = EmailTemplateResource
    list_display = ('email_template_id', 'subject', 'manager', 'created_at', 'updated_at')
    search_fields = ('subject', 'manager__name')
    list_filter = ('manager',)
    ordering = ('subject',)
    fields = ('subject', 'body', 'manager')

class CompanyManagerAdmin(ImportExportModelAdmin):
    resource_class = CompanyManagerResource
    list_display = ('manager_id', 'name', 'email', 'company', 'login_count', 'send_mails', 'created_at', 'updated_at')
    search_fields = ('name', 'email')
    readonly_fields = ('created_at', 'updated_at', 'login_count', 'manager_id')
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'password', 'app_password', 'company')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('login_count', 'send_mails','created_at', 'updated_at'),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Hash the password if it's being set for the first time or updated
        if change and 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        elif not change:
            # For new objects, ensure password is hashed
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

admin.site.register(CompanyManager, CompanyManagerAdmin)
