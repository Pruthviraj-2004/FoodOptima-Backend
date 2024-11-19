# from import_export import resources, fields
# from import_export.widgets import ForeignKeyWidget
# from .models import OrganizationEvent, Employee, EmployeeEventResponse, EmployeeResponse

# class EmployeeResource(resources.ModelResource):
#     name_email = fields.Field(
#         attribute='name_email',
#         column_name='Name and Email',
#         readonly=True
#     )

#     class Meta:
#         model = Employee
#         fields = ('user_id', 'name', 'email', 'name_email')
#         export_order = ('user_id', 'name', 'email', 'name_email')
#         import_id_fields = ['user_id']
#         skip_unchanged = True
#         report_skipped = False
#         use_natural_foreign_keys = True

#     def dehydrate_name_email(self, employee):
#         """
#         Custom method to create a combined representation of the name and email for export.
#         """
#         return f"{employee.name} <{employee.email}>"

#     def before_import_row(self, row, **kwargs):
#         """
#         Optional method to handle data before importing, such as data cleanup or validation.
#         """
#         if 'id' in row:
#             row['user_id'] = row.pop('id')

# class EmployeeResponseResource(resources.ModelResource):
#     employee = fields.Field(
#         column_name='Employee Name',
#         attribute='employee',
#         widget=ForeignKeyWidget(Employee, 'name')
#     )

#     class Meta:
#         model = EmployeeResponse
#         fields = ('employee', 'date', 'response')
#         export_order = ('employee', 'date', 'response')
#         import_id_fields = ['employee', 'date']
#         skip_unchanged = True
#         report_skipped = False
#         use_natural_foreign_keys = False 

# class OrganizationEventResource(resources.ModelResource):
#     class Meta:
#         model = OrganizationEvent
#         fields = ('event_id', 'name', 'date')
#         export_order = ('event_id', 'name', 'date')
#         import_id_fields = ['event_id']
#         skip_unchanged = True
#         report_skipped = False

# class EmployeeEventResponseResource(resources.ModelResource):
#     event = fields.Field(
#         column_name='Event Name',
#         attribute='event',
#         widget=ForeignKeyWidget(OrganizationEvent, 'name')
#     )
#     employee = fields.Field(
#         column_name='Employee Name',
#         attribute='employee',
#         widget=ForeignKeyWidget(Employee, 'name')
#     )

#     class Meta:
#         model = EmployeeEventResponse
#         fields = ('employee', 'event', 'date', 'response')
#         export_order = ('employee', 'event', 'date', 'response')
#         import_id_fields = ['employee', 'event', 'date']
#         skip_unchanged = True
#         report_skipped = False
#         use_natural_foreign_keys = True

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import EmailAccount, EmailTemplate, Employee, Company, CompanyManager, EmployeeEventResponse, EmployeeResponse, OrganizationEvent, WorkingDays

# class EmployeeResource(resources.ModelResource):
#     name_email = fields.Field(
#         attribute='name_email',
#         column_name='Name and Email',
#         readonly=True
#     )
#     company = fields.Field(
#         column_name='Company',
#         attribute='company',
#         widget=ForeignKeyWidget(Company, 'name')
#     )
#     manager = fields.Field(
#         column_name='Manager',
#         attribute='manager',
#         widget=ForeignKeyWidget(CompanyManager, 'name')
#     )

#     class Meta:
#         model = Employee
#         fields = ('user_id', 'name', 'email', 'company', 'manager', 'name_email')
#         export_order = ('user_id', 'name', 'email', 'company', 'manager', 'name_email')
#         import_id_fields = ['user_id']
#         skip_unchanged = True
#         report_skipped = False
#         use_natural_foreign_keys = True

#     def dehydrate_name_email(self, employee):
#         """
#         Custom method to create a combined representation of the name and email for export.
#         """
#         return f"{employee.name} <{employee.email}>"

#     def before_import_row(self, row, **kwargs):
#         """
#         Optional method to handle data before importing, such as data cleanup or validation.
#         """
#         if 'id' in row:
#             row['user_id'] = row.pop('id')

from import_export.results import RowResult

class EmployeeResource(resources.ModelResource):
    company = fields.Field(
        column_name='Company',
        attribute='company',
        widget=ForeignKeyWidget(Company, 'name')
    )
    manager = fields.Field(
        column_name='Manager',
        attribute='manager',
        widget=ForeignKeyWidget(CompanyManager, 'name')
    )

    class Meta:
        model = Employee
        fields = ('user_id', 'name', 'email', 'company', 'manager')
        export_order = ('user_id', 'name', 'email', 'company', 'manager')
        import_id_fields = ['user_id']
        skip_unchanged = True
        report_skipped = False
        use_natural_foreign_keys = True

    def before_import_row(self, row, **kwargs):
        """
        Check if an employee with the same name and email already exists.
        If it does, skip the row.
        """
        name = row.get('name')
        email = row.get('email')

        # Check if an employee with the same name and email already exists
        if Employee.objects.filter(name=name, email=email).exists():
            # Skip this row by marking it as skipped
            return RowResult.SKIP

class EmployeeImportResource(resources.ModelResource):
    class Meta:
        model = Employee
        fields = ('name', 'email')  # Specify the fields to import

    def before_import_row(self, row, **kwargs):
        # Clean up the row data if needed
        row['email'] = row['email'].strip() 

    def save_instance(self, instance, using_transactions=True, **kwargs):
        # Get the current logged-in manager from the context
        manager_id = kwargs.get('manager_id')
        manager = CompanyManager.objects.get(pk=manager_id)

        # Set the manager for the employee instance
        instance.manager = manager
        super().save_instance(instance, using_transactions, **kwargs)
        

class EmployeeResponseResource(resources.ModelResource):
    employee = fields.Field(
        column_name='Employee Name',
        attribute='employee',
        widget=ForeignKeyWidget(Employee, 'name')
    )

    class Meta:
        model = EmployeeResponse
        fields = ('employee', 'date', 'response')
        export_order = ('employee', 'date', 'response')
        import_id_fields = ['employee', 'date']
        skip_unchanged = True
        report_skipped = False
        use_natural_foreign_keys = False

class OrganizationEventResource(resources.ModelResource):
    manager = fields.Field(
        column_name='Manager',
        attribute='manager',
        widget=ForeignKeyWidget(CompanyManager, 'name')
    )

    class Meta:
        model = OrganizationEvent
        fields = ('event_id', 'name', 'date', 'manager')
        export_order = ('event_id', 'name', 'date', 'manager')
        import_id_fields = ['event_id']
        skip_unchanged = True
        report_skipped = False

class EmployeeEventResponseResource(resources.ModelResource):
    event = fields.Field(
        column_name='Event Name',
        attribute='event',
        widget=ForeignKeyWidget(OrganizationEvent, 'name')
    )
    employee = fields.Field(
        column_name='Employee Name',
        attribute='employee',
        widget=ForeignKeyWidget(Employee, 'name')
    )

    class Meta:
        model = EmployeeEventResponse
        fields = ('employee', 'event', 'date', 'response')
        export_order = ('employee', 'event', 'date', 'response')
        import_id_fields = ['employee', 'event', 'date']
        skip_unchanged = True
        report_skipped = False
        use_natural_foreign_keys = True

class EmailAccountResource(resources.ModelResource):
    company = fields.Field(
        column_name='Company',
        attribute='company',
        widget=ForeignKeyWidget(Company, 'name')
    )
    manager = fields.Field(
        column_name='Manager',
        attribute='manager',
        widget=ForeignKeyWidget(CompanyManager, 'name')
    )

    class Meta:
        model = EmailAccount
        fields = ('email_account_id', 'email', 'smtp_server', 'smtp_port', 'use_tls', 'use_ssl', 'company', 'manager')
        export_order = ('email_account_id', 'email', 'smtp_server', 'smtp_port', 'use_tls', 'use_ssl', 'company', 'manager')
        import_id_fields = ['email_account_id']
        skip_unchanged = True
        report_skipped = False

class EmailTemplateResource(resources.ModelResource):
    manager = fields.Field(
        column_name='Manager',
        attribute='manager',
        widget=ForeignKeyWidget(CompanyManager, 'name')
    )

    class Meta:
        model = EmailTemplate
        fields = ('email_template_id', 'subject', 'body', 'manager')
        export_order = ('email_template_id', 'subject', 'body', 'manager')
        import_id_fields = ['email_template_id']
        skip_unchanged = True
        report_skipped = False

class WorkingDaysResource(resources.ModelResource):
    manager = fields.Field(
        column_name='Manager',
        attribute='manager',
        widget=ForeignKeyWidget(CompanyManager, 'name')
    )

    class Meta:
        model = WorkingDays
        fields = ('month', 'year', 'days', 'manager')
        export_order = ('month', 'year', 'days', 'manager')
        import_id_fields = ['month', 'year', 'manager']
        skip_unchanged = True
        report_skipped = False

class CompanyResource(resources.ModelResource):
    class Meta:
        model = Company
        fields = ('company_id', 'name', 'domain', 'created_at', 'updated_at')
        export_order = ('company_id', 'name', 'domain', 'created_at', 'updated_at')
        import_id_fields = ['company_id']
        skip_unchanged = True
        report_skipped = False

class CompanyManagerResource(resources.ModelResource):
    company = fields.Field(
        column_name='Company Name',
        attribute='company',
        widget=ForeignKeyWidget(Company, 'name')
    )

    class Meta:
        model = CompanyManager
        fields = ('manager_id', 'name', 'email', 'company', 'login_count', 'created_at', 'updated_at')
        export_order = ('manager_id', 'name', 'email', 'company', 'login_count', 'created_at', 'updated_at')
        import_id_fields = ['manager_id']
        skip_unchanged = True
        report_skipped = False
        use_natural_foreign_keys = True
