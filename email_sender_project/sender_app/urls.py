from django.urls import path
from sender_app import views

from .views import *

urlpatterns = [
    path('', MainPageView.as_view(), name='main_page'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path('send-emails-to-all/', SendEmailsToAllEmployees.as_view(), name='send_emails_to_all'),
    path('send-summary-email/', SendSummaryEmail.as_view(), name='send_summary_email'),
    path('send-custom-emails/', SendCustomEmailsToAllEmployees.as_view(), name='send_custom_emails'),

    path('add-company-or-manager/', AddCompanyOrManagerView.as_view(), name='add_company_or_manager'),
    path('add-company/', AddCompanyView.as_view(), name='add_company'),
    path('add-company-manager-details/', AddCompanyManagerDetailsView.as_view(), name='add_company_manager_details'),

    path('manager-settings/', ManagerSettingsView.as_view(), name='manager_settings'),
    path('update-manager-name/', UpdateManagerNameView.as_view(), name='update_manager_name'),
    path('update-email-template/', UpdateManagerEmailTemplateView.as_view(), name='update_manager_email_template'),
    path('update-email-account/', UpdateManagerEmailAccountView.as_view(), name='update_manager_email_account'),

    path('employees-list/', EmployeeListView.as_view(), name='employee_list'),
    path('add-employee/', AddEmployeeView.as_view(), name='add_employee'),
    path('employee/update/<int:user_id>/', EmployeeUpdateView.as_view(), name='update_employee'),
    path('delete-employee/<int:user_id>/', EmployeeDeleteView.as_view(), name='delete_employee'),

    path('upload-file/', UploadFileView.as_view(), name='upload_file'),
    path('export-employees/', EmployeeExportView.as_view(), name='employee_export'),

    path('employee-responses/', EmployeeResponsesView.as_view(), name='employee_responses'),
    path('response/<int:employee_id>/<str:response_value>/', EmployeeResponseView.as_view(), name='employee_response'),

    path('view-responses-date/<str:date>/', ViewResponsesByDate.as_view(), name='view_responses_by_date'),
    path('view-responses-employee/', ViewResponseByEmployee.as_view(), name='view_responses_by_employee'),
    path('view-responses-month/', ViewResponsesByMonth.as_view(), name='view_responses_by_month'),

    path('select-month-year/', SelectMonthYearView.as_view(), name='select_month_year'),
    path('manage-working/<int:year>/<int:month>/', ManageWorking.as_view(), name='manage_working'),

    path('export-responses-date/', ExportResponsesByDateView.as_view(), name='export_employee_responses'),
    path('export-responses-employee/<int:employee_id>/', ExportResponsesByEmployeeView.as_view(), name='export_employee_responses'),
    path('export-month-summary/', ExportMonthlySummaryView.as_view(), name='export_month_summary'),



    path('sssend-email/', send_outlook_email, name='send_email'),



    path('about-us/', AboutUsView.as_view(), name='about_us'),

    # path('send-email/<int:employee_id>/', SendConfirmationEmail.as_view(), name='send_email'),

]