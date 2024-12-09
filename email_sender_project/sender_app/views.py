import json
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives
from django.template import loader
from django.urls import reverse
from .models import CompanyManager, EmailAccount, EmailTemplate, Employee, EmployeeEventResponse, EmployeeResponse, OrganizationEvent, WorkingDays
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib import messages
from django.views.generic import View, TemplateView
from django.core.paginator import Paginator

from django.db.models import Count, Case, When, IntegerField
from django.db.models.functions import TruncDay
import csv

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime
from calendar import monthrange
from django.utils import timezone

from tablib import Dataset
from .resources import EmployeeResource, EmployeeResponseResource

import matplotlib
matplotlib.use('Agg') 

from io import BytesIO
import base64
import matplotlib.pyplot as plt

import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
import calendar

class SendConfirmationEmail(View):
    def get(self, request, employee_id):
        employee = get_object_or_404(Employee, pk=employee_id)
        html_message = loader.render_to_string(
            'email_sender_app/message.html',
            {
                'title': 'Office Attendance Confirmation',
                'body': f'Hello {employee.name}, this email is to verify whether you will attend the office tomorrow. Please confirm your attendance.',
                'sign': 'Your Manager',
                'employee_id': employee.user_id,
            })

        send_mail(
            'Will You Attend the Office Tomorrow?',
            'Please confirm your attendance for tomorrow.',
            'photo2pruthvi@gmail.com',  # Replace with your email address
            [employee.email],
            html_message=html_message,
            fail_silently=False,
        )

        return HttpResponse("Mail Sent!")

from .decorators import manager_login_required
from django.contrib.auth import logout

# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         try:
#             manager = CompanyManager.objects.get(email=email)

#             if manager.check_password(password):
#                 manager.login_count += 1
#                 manager.save()

#                 request.session['manager_id'] = manager.manager_id
#                 messages.success(request, f"Welcome {manager.name}, you have successfully logged in!")
                            
#                 return redirect('dashboard')
#             else:
#                 messages.error(request, 'Invalid credentials')
#                 return render(request, 'email_sender_app/login.html')
#         except CompanyManager.DoesNotExist:
#             messages.error(request, 'Invalid credentials')
#             return render(request, 'email_sender_app/login.html')
#     return render(request, 'email_sender_app/login.html')

# def logout_view(request):
#     logout(request)
#     messages.success(request, 'You have been successfully logged out.')
#     return redirect('login')

def login_view(request):
    # Redirect if already logged in
    if request.session.get('manager_id'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            manager = CompanyManager.objects.get(email=email)

            # Check password and log in if correct
            if manager.check_password(password):
                manager.login_count += 1
                manager.save()

                # Set manager ID in session to mark login
                request.session['manager_id'] = manager.manager_id
                messages.success(request, f"Welcome {manager.name}, you have successfully logged in!")
                
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid credentials')
                return render(request, 'email_sender_app/login.html')
        except CompanyManager.DoesNotExist:
            messages.error(request, 'Invalid credentials')
            return render(request, 'email_sender_app/login.html')
    return render(request, 'email_sender_app/login.html')

def logout_view(request):
    # Clear session data and log out manager
    if 'manager_id' in request.session:
        del request.session['manager_id']
    messages.success(request, "You have been logged out successfully.")
    return redirect(reverse('login'))

@method_decorator(manager_login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        manager_id = request.session.get('manager_id')
        manager = CompanyManager.objects.get(pk=manager_id)
        
        company = manager.company
        
        manager_employee_count = manager.employees.count()
        
        company_employee_count = Employee.objects.filter(company=company).count()
        today_date = timezone.now().strftime('%Y-%m-%d')
        
        context = {
            'manager': manager,
            'company': company,
            'manager_employee_count': manager_employee_count,
            'company_employee_count': company_employee_count,
            'today_date': today_date,
        }
        return render(request, 'email_sender_app/dashboard.html', context)

class EmployeeResponseView(View):
    def get(self, request, employee_id, response_value):
        employee = get_object_or_404(Employee, pk=employee_id)
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        
        if response_value in ['yes', 'no']:
            response, created = EmployeeResponse.objects.get_or_create(
                employee=employee,
                date=tomorrow,
                defaults={'response': response_value}
            )
            if not created:
                response.response = response_value
                response.save()

            return HttpResponse(f"Thank you, {employee.name}, for your response!")

        return HttpResponse("Invalid response.", status=400)

class AddCompanyView(View):
    def get(self, request):
        form = CompanyForm()
        return render(request, 'email_sender_app/add_company.html', {'form': form})

    def post(self, request):
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company added successfully!')
            return redirect('add_company')
        else:
            for field in form.errors:
                messages.error(request, f"{form.errors[field][0]}")

        return render(request, 'email_sender_app/add_company.html', {'form': form})

class AddCompanyManagerDetailsView(View):
    def get(self, request):
        company_form = CompanySelectionForm()
        manager_form = CompanyManagerForm()
        email_account_form = EmailAccountForm()
        email_template_form = EmailTemplateForm()
        return render(request, 'email_sender_app/add_manager_details.html', {
            'company_form': company_form,
            'manager_form': manager_form,
            'email_account_form': email_account_form,
            'email_template_form': email_template_form,
        })

    def post(self, request):
        company_form = CompanySelectionForm(request.POST)
        manager_form = CompanyManagerForm(request.POST)
        email_account_form = EmailAccountForm(request.POST)
        email_template_form = EmailTemplateForm(request.POST)
        
        if (company_form.is_valid() and manager_form.is_valid() and 
            email_account_form.is_valid() and email_template_form.is_valid()):
            
            company = company_form.cleaned_data['company']
            
            # Save the company manager
            manager = manager_form.save(commit=False)
            manager.company = company
            manager.set_password(manager_form.cleaned_data['password'])
            manager.save()
            
            # Save the email account
            email_account = email_account_form.save(commit=False)
            email_account.company = company
            email_account.manager = manager
            email_account.email = manager.email  # Set email account's email as manager's email
            email_account.save()
            
            # Save the email template
            email_template = email_template_form.save(commit=False)
            email_template.company = company
            email_template.manager = manager
            email_template.save()
            
            messages.success(request, 'Manager, Email Account, and Email Template added successfully!')
            return redirect('add_company_manager_details')
        
        return render(request, 'email_sender_app/add_manager_details.html', {
            'company_form': company_form,
            'manager_form': manager_form,
            'email_account_form': email_account_form,
            'email_template_form': email_template_form,
        })    

@method_decorator(manager_login_required, name='dispatch')
class EmployeeListView(View):
    def get(self, request):
        manager_id = request.session.get('manager_id')
        
        if manager_id:
            manager = get_object_or_404(CompanyManager, pk=manager_id)
            employees = Employee.objects.filter(manager=manager).order_by('name')
        else:
            employees = Employee.objects.none()

        paginator = Paginator(employees, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'email_sender_app/employees_list.html', {'page_obj': page_obj})

@method_decorator(manager_login_required, name='dispatch')
class EmployeeResponsesView(View):
    def get(self, request):
        manager_id = request.session.get('manager_id')
        
        if manager_id:
            try:
                manager = CompanyManager.objects.get(pk=manager_id)
                responses = EmployeeResponse.objects.filter(
                    # employee__company=manager.company
                    employee__manager=manager
                ).select_related('employee').order_by('-date')
            except CompanyManager.DoesNotExist:
                responses = EmployeeResponse.objects.none()
        else:
            responses = EmployeeResponse.objects.none()

        paginator = Paginator(responses, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'email_sender_app/employees_responses.html', {'page_obj': page_obj})
    
@method_decorator(manager_login_required, name='dispatch')
class AddEmployeeView(View):
    def get(self, request):
        form = EmployeeForm()
        return render(request, 'email_sender_app/add_employee.html', {'form': form})

    def post(self, request):
        form = EmployeeForm(request.POST)
        if form.is_valid():
            manager_id = request.session.get('manager_id')
            manager = CompanyManager.objects.get(pk=manager_id)
            
            employee = form.save(commit=False)
            employee.company = manager.company
            employee.manager = manager
            
            employee.save()

            messages.success(request, 'Employee added successfully!')
            return redirect('add_employee')
        else:
            for field in form.errors:
                messages.error(request, f"{form.errors[field][0]}")

        return render(request, 'email_sender_app/add_employee.html', {'form': form})


# @method_decorator(manager_login_required, name='dispatch')
# class ViewEmployeeResponses(View):
#     def get(self, request):
#         # selected_date = request.GET.get('date', timezone.now().date())
        
#         selected_date_str = request.GET.get('date', timezone.now().strftime('%Y-%m-%d'))
#         selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

#         form = DateForm(initial={'date': selected_date})
        
#         manager_id = request.session.get('manager_id')
#         manager = CompanyManager.objects.get(pk=manager_id)

#         responses = EmployeeResponse.objects.filter(date=selected_date, employee__manager=manager).order_by('employee__name')
        
#         paginator = Paginator(responses, 10)
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)

#         yes_count = responses.filter(response='yes').count()
#         no_count = responses.filter(response='no').count()

#         total_employees = Employee.objects.filter(manager=manager).count()
#         not_responded_count = total_employees - (yes_count + no_count)

#         labels = ['Yes', 'No', 'Not Responded']
#         sizes = [yes_count, no_count, not_responded_count]
#         colors = ['#28a745', '#dc3545', '#ffc107']
#         explode = (0.1, 0, 0)

#         valid_sizes = []
#         valid_labels = []
#         valid_colors = []
#         valid_explode = []

#         for size, label, color, explode_value in zip(sizes, labels, colors, explode):
#             if size > 0:
#                 valid_sizes.append(size)
#                 valid_labels.append(label)
#                 valid_colors.append(color)
#                 valid_explode.append(explode_value)

#         if valid_sizes:
#             plt.figure(figsize=(6, 4))
#             plt.pie(valid_sizes, explode=valid_explode, labels=valid_labels, colors=valid_colors,
#                     autopct=lambda p: '{:.0f}'.format(p * sum(valid_sizes) / 100), shadow=True, startangle=140)
#             plt.axis('equal')
#             buffer = BytesIO()
#             plt.savefig(buffer, format='png')
#             plt.close()
#             buffer.seek(0)

#             image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

#         else:
#             image_base64 = None

#         return render(request, 'email_sender_app/view_responses.html', {
#             'form': form,
#             'responses': page_obj,
#             'yes_count': yes_count,
#             'no_count': no_count,
#             'not_responded_count': not_responded_count,
#             # 'selected_date': selected_date,
#             'selected_date': selected_date_str,
#             'chart_image': image_base64,
#             'page_obj': page_obj
#         })

#     def post(self, request):
#         form = DateForm(request.POST)
#         if form.is_valid():
#             selected_date = form.cleaned_data['date']
#             return HttpResponseRedirect(f"?date={selected_date}")
#         else:
#             messages.error(request, 'Error in form submission.')
#             return render(request, 'email_sender_app/view_responses.html', {'form': form})

@method_decorator(manager_login_required, name='dispatch')
class ViewResponseByEmployee(View):
    def get(self, request):
        manager_id = request.session.get('manager_id')
        manager = CompanyManager.objects.get(pk=manager_id)

        form = EmployeeSelectForm(manager=manager)
        employee_id = request.GET.get('employee_id')

        if employee_id:
            employee = Employee.objects.get(pk=employee_id)
            responses = EmployeeResponse.objects.filter(employee=employee).order_by('-date')
            
            paginator = Paginator(responses, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            form.fields['employee'].initial = employee_id

            return render(request, 'email_sender_app/view_responses_employee.html', {
                'form': form,
                'page_obj': page_obj,
                'selected_user': employee
            })

        return render(request, 'email_sender_app/view_responses_employee.html', {'form': form})

    def post(self, request):
        manager_id = request.session.get('manager_id')
        manager = CompanyManager.objects.get(pk=manager_id)

        form = EmployeeSelectForm(request.POST, manager=manager)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            responses = EmployeeResponse.objects.filter(employee=employee).order_by('-date')
            
            paginator = Paginator(responses, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            form.fields['employee'].initial = employee.user_id
            
            if responses.exists():
                messages.success(request, f'Responses found for {employee.name}.')
            else:
                messages.warning(request, f'No responses found for {employee.name}.')
            
            return render(request, 'email_sender_app/view_responses_employee.html', {
                'form': form,
                'page_obj': page_obj,
                'selected_user': employee
            })
        else:
            messages.error(request, 'Error in form submission.')
            return render(request, 'email_sender_app/view_responses_employee.html', {'form': form})

@method_decorator(manager_login_required, name='dispatch')
class ViewResponsesByMonth(View):
    template_name = 'email_sender_app/view_responses_month.html'

    def get(self, request):
        current_month = timezone.now().month
        selected_month = request.GET.get('month', f"{current_month:02}")

        manager_id = request.session.get('manager_id')
        manager = CompanyManager.objects.get(pk=manager_id)

        responses_data = []
        month_name_dict = {
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
            7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        }

        months = [{'number': i, 'name': month_name_dict[i]} for i in range(1, 13)]
        month_name_str = month_name_dict.get(int(selected_month), "")

        image_base64 = None

        if selected_month:
            month_index = int(selected_month)
            month_name_str = month_name_dict[month_index]

            working_days = WorkingDays.objects.filter(manager=manager, month=month_index, year=timezone.now().year).first()

            if working_days:
                total_employees = Employee.objects.filter(manager=manager).count()

                responses_data = (EmployeeResponse.objects
                                  .filter(employee__manager=manager, date__month=month_index, date__year=timezone.now().year)
                                  .annotate(day=TruncDay('date'))
                                  .values('day')
                                  .annotate(
                                      total=Count('id'),
                                      yes_count=Count(Case(When(response='yes', then=1), output_field=IntegerField())),
                                      no_count=Count(Case(When(response='no', then=1), output_field=IntegerField()))
                                  )
                                  .order_by('day'))

                for data in responses_data:
                    data['not_responded_count'] = total_employees - (data['yes_count'] + data['no_count'])

                days = [data['day'].strftime('%Y-%m-%d') for data in responses_data]
                yes_counts = [data['yes_count'] for data in responses_data]
                no_counts = [data['no_count'] for data in responses_data]
                not_responded_counts = [data['not_responded_count'] for data in responses_data]

                plt.figure(figsize=(10, 6))
                bar_width = 0.5
                index = range(len(days))

                bars_yes = plt.bar(index, yes_counts, width=bar_width, color='#28a745', label='Yes')

                bars_no = plt.bar(index, no_counts, width=bar_width, bottom=yes_counts, color='#dc3545', label='No')

                bars_not_responded = plt.bar(index, not_responded_counts, width=bar_width,
                                             bottom=[yes + no for yes, no in zip(yes_counts, no_counts)],
                                             color='#ffc107', label='Not Responded')

                for bar, count in zip(bars_yes, yes_counts):
                    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, str(count), ha='center', va='center', color='white')

                for bar, yes, count in zip(bars_no, yes_counts, no_counts):
                    plt.text(bar.get_x() + bar.get_width() / 2, yes + bar.get_height() / 2, str(count), ha='center', va='center', color='white')

                for bar, yes, no, count in zip(bars_not_responded, yes_counts, no_counts, not_responded_counts):
                    plt.text(bar.get_x() + bar.get_width() / 2, yes + no + bar.get_height() / 2, str(count), ha='center', va='center', color='black')

                logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
                matplotlib.rcParams['font.family'] = 'DejaVu Sans'

                plt.xlabel('Day')
                plt.ylabel('Number of Responses')
                plt.title(f'Response Distribution for {month_name_str}')
                plt.xticks(index, days, rotation=45)
                plt.legend()
                plt.tight_layout()

                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                plt.close()
                buffer.seek(0)

                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

                messages.success(request, f"Displaying responses for {month_name_str} according to working days.")
            else:
                messages.warning(request, f"No working days found for {month_name_str}.")
        else:
            messages.warning(request, "Please select a valid month.")

        return render(request, self.template_name, {
            'months': months,
            'responses': responses_data,
            'month_name': month_name_str,
            'selected_month': selected_month,
            'chart_image': image_base64
        })

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(manager_login_required, name='dispatch')
class EmployeeDeleteView(View):
    def delete(self, request, user_id):
        try:
            manager_id = request.session.get('manager_id')
            manager = CompanyManager.objects.get(pk=manager_id)

            employee = get_object_or_404(Employee, user_id=user_id, manager=manager)
            
            employee.delete()
            messages.success(request, 'Employee deleted successfully.')
            return JsonResponse({'message': 'Employee deleted successfully.'}, status=204)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee not found or you do not have permission to delete this employee.'}, status=404)
        
@method_decorator(manager_login_required, name='dispatch')
class SelectMonthYearView(View):
    template_name = 'email_sender_app/month_year.html'

    def get(self, request):
        current_year = datetime.now().year
        current_month = datetime.now().month
        years = range(2024, 2031)

        month_name_dict = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }

        months = [{'number': i, 'name': month_name_dict[i]} for i in range(1, 13)]

        messages.info(request, 'Select a month and year to manage working days.')

        return render(request, self.template_name, {
            'years': years,
            'months': months,
            'current_year': current_year,
            'current_month': current_month
        })

@method_decorator(manager_login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ManageWorking(View):
    template_name = 'email_sender_app/manage_working.html'

    def get(self, request, year, month):
        manager_id = request.session.get('manager_id')
        try:
            working_days = WorkingDays.objects.get(month=month, year=year, manager_id=manager_id)
            days = working_days.days
        except WorkingDays.DoesNotExist:
            # days = []
            _, last_day_of_month = calendar.monthrange(year, month)
            days = [day for day in range(1, last_day_of_month + 1) if datetime(year, month, day).weekday() < 5]


        form = WorkingDaysForm(initial={'month': month, 'year': year})
        context = {
            'form': form,
            'days': json.dumps(days),
            'month': month,
            'year': year
        }
        return render(request, self.template_name, context)

    def post(self, request, year, month):
        manager_id = request.session.get('manager_id')
        try:
            data = json.loads(request.body)
            days = data.get('days')
            month = data.get('month')
            year = data.get('year')

            existing_record = WorkingDays.objects.filter(month=month, year=year, manager_id=manager_id).first()
            if existing_record:
                existing_record.days = days
                existing_record.save()
            else:
                WorkingDays.objects.create(
                    month=month,
                    year=year,
                    days=days,
                    manager_id=manager_id
                )
            return JsonResponse({'status': 'success'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

@method_decorator(manager_login_required, name='dispatch')
class SendEmailsToAllEmployees(View):
    def get(self, request):
        manager_id = request.session.get('manager_id')
        manager = CompanyManager.objects.get(pk=manager_id)

        # Check if send_mails is True
        if not manager.send_mails:
            messages.error(request, 'Email sending is disabled for your account. Please enable it to send emails.')
            return redirect('dashboard')

        today = timezone.now().date()
        current_month = today.month
        current_year = today.year

        current_month_working_days = WorkingDays.objects.filter(manager=manager, month=current_month, year=current_year).first()
        next_month_working_days = WorkingDays.objects.filter(manager=manager, month=current_month + 1, year=current_year).first()

        # Check if today is a working day
        if current_month_working_days and today.day in current_month_working_days.days:

            # Find the next working day
            next_working_day = self.get_next_working_day(today, current_month_working_days, next_month_working_days)

            if not next_working_day:
                messages.error(request, 'No upcoming working days found.')
                return redirect('dashboard')

            # Fetch the email account details
            email_account = EmailAccount.objects.get(manager=manager)

            # Fetch the email template
            email_template = EmailTemplate.objects.filter(manager=manager).first()
            if email_template:
                title = email_template.subject
                body = email_template.body
                signature = f'Sincerely, {manager.name}'
            else:
                title = 'Office Attendance Confirmation'
                body = 'Hello {employee.name}, this email is to verify whether you will attend the office on {date}. Please confirm your attendance.'
                signature = 'Your Manager'

            employees = Employee.objects.filter(manager=manager)

            email_backend = get_connection(
                host=email_account.smtp_server,
                port=email_account.smtp_port,
                username=email_account.email,
                password=email_account.manager.app_password,
                use_tls=email_account.use_tls,
                use_ssl=email_account.use_ssl,
            )

            for employee in employees:
                personalized_body = body.format(employee=employee, date=next_working_day)

                html_message = loader.render_to_string(
                    'email_sender_app/message.html',
                    {
                        'title': title,
                        'body': personalized_body,
                        'sign': signature,
                        'employee_id': employee.user_id,
                        'date': next_working_day,
                    })

                email = EmailMultiAlternatives(
                    title,
                    'Please confirm your attendance for the next working day.',
                    email_account.email,
                    [employee.email],
                    connection=email_backend
                )
                email.attach_alternative(html_message, "text/html")
                email.send(fail_silently=False)

            messages.success(request, f'Emails have been successfully sent to all your employees for {next_working_day}.')
        else:
            messages.error(request, 'Today is not a working day. Emails will not be sent.')

        return redirect('dashboard')

    def get_next_working_day(self, today, current_month_working_days, next_month_working_days):
        # Get the next working day in the current month
        upcoming_days = [day for day in current_month_working_days.days if day > today.day]
        if upcoming_days:
            next_day = min(upcoming_days)
            # Safeguard to ensure the next day exists in the current month
            last_day_of_month = monthrange(today.year, today.month)[1]
            if next_day <= last_day_of_month:
                return today.replace(day=next_day)

        # If no working days left in the current month, check the next month
        if next_month_working_days:
            next_day = min(next_month_working_days.days)
            next_month = today.month + 1
            next_year = today.year

            # Handle the year transition from December to January
            if next_month > 12:
                next_month = 1
                next_year += 1

            # Safeguard to ensure the next day exists in the next month
            last_day_of_next_month = monthrange(next_year, next_month)[1]
            if next_day <= last_day_of_next_month:
                return today.replace(year=next_year, month=next_month, day=next_day)

        return None

@method_decorator(manager_login_required, name='dispatch')
class SendSummaryEmail(View):
    def get(self, request):
        today = timezone.now().date()
        manager_id = request.session.get('manager_id')
        manager = CompanyManager.objects.get(pk=manager_id)

        # Check if send_mails is True
        if not manager.send_mails:
            messages.error(request, 'Email sending is disabled for your account. Please enable it to send emails.')
            return redirect('dashboard')

        email_account = EmailAccount.objects.get(manager=manager)

        responses = EmployeeResponse.objects.filter(employee__manager=manager, date=today)
        
        total_responses = responses.count()
        yes_count = responses.filter(response='yes').count()
        no_count = responses.filter(response='no').count()
        
        total_employees = Employee.objects.filter(manager=manager).count()
        not_responded_count = total_employees - total_responses

        html_message = loader.render_to_string(
            'email_sender_app/summary_message.html',
            {
                'title': 'Daily Attendance Summary',
                'body': f'Attendance summary for {today.strftime("%Y-%m-%d")}:',
                'total_responses': total_responses,
                'yes_count': yes_count,
                'no_count': no_count,
                'not_responded_count': not_responded_count,
                'sign': 'Your Manager',
            }
        )

        email_backend = get_connection(
            host=email_account.smtp_server,
            port=email_account.smtp_port,
            username=email_account.email,
            password=email_account.manager.app_password,
            use_tls=email_account.use_tls,
            use_ssl=email_account.use_ssl,
        )

        email = EmailMultiAlternatives(
            'Daily Attendance Summary',
            'Here is the summary of today\'s attendance responses.',
            email_account.email,
            [manager.email],
            connection=email_backend
        )
        email.attach_alternative(html_message, "text/html")
        
        email.send(fail_silently=False)

        messages.success(request, 'Summary email has been successfully sent to you.')
        return redirect('dashboard')

class AddCompanyOrManagerView(View):
    def get(self, request):
        return render(request, 'email_sender_app/add_details_company.html')

class MainPageView(View):
    def get(self, request):
        return render(request, 'email_sender_app/main_page.html')

@method_decorator(manager_login_required, name='dispatch')
class EmployeeExportView(View):
    def get(self, request):
        manager_id = request.session.get('manager_id')
        manager = CompanyManager.objects.get(pk=manager_id)
        
        current_date = timezone.now().strftime('%Y-%m-%d')
        
        employee_resource = EmployeeResource()
        queryset = Employee.objects.filter(manager_id=manager_id)
        
        dataset = employee_resource.export(queryset)
        export_format = request.GET.get('format', 'csv')
        
        file_name = f"Employees_{manager.name}_{current_date}".replace(' ', '_')
        
        if export_format == 'csv':
            content_type = 'text/csv'
            response = HttpResponse(dataset.csv, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{file_name}.csv"'
        elif export_format == 'xls':
            content_type = 'application/vnd.ms-excel'
            response = HttpResponse(dataset.xls, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{file_name}.xls"'
        else:
            return HttpResponse("Unsupported format", status=400)
        
        return response

@method_decorator(manager_login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class UploadFileView(View):
    def get(self, request):
        return render(request, 'email_sender_app/upload.html')

    def post(self, request):
        if 'file' in request.FILES:
            new_employees = request.FILES['file']
            file_extension = new_employees.name.split('.')[-1].lower()

            if file_extension not in ['csv', 'xls', 'xlsx']:
                messages.error(request, 'Invalid file format. Please upload a .csv or .xls/.xlsx file.')
                return redirect('upload_file')

            try:
                dataset = Dataset()

                if file_extension == 'csv':
                    imported_data = dataset.load(new_employees.read().decode('utf-8'), format='csv')
                elif file_extension in ['xls', 'xlsx']:
                    imported_data = dataset.load(new_employees.read(), format=file_extension)

                manager_id = request.session.get('manager_id')
                manager = CompanyManager.objects.get(pk=manager_id)

                # Set of existing employees in the database (for the current manager)
                existing_employee_set = set(Employee.objects.filter(manager=manager)
                                            .values_list('name', 'email'))

                # Set to track CSV employees
                csv_employee_set = set()

                created_count = 0
                skipped_count = 0

                # Iterate over CSV data and populate the CSV employee set
                for row in imported_data:
                    name = row[0].strip()
                    email = row[1].strip()

                    # Add employee from CSV to the set
                    csv_employee_set.add((name, email))

                    # Check if employee exists in the database
                    if (name, email) not in existing_employee_set:
                        # Create a new employee if not already in the database
                        Employee.objects.create(
                            name=name,
                            email=email,
                            company=manager.company,
                            manager=manager
                        )
                        created_count += 1
                    else:
                        skipped_count += 1

                # Identify employees to delete (existing in DB but absent in the CSV)
                employees_to_delete = existing_employee_set - csv_employee_set
                delete_count = 0

                # Delete employees who are present in the DB but absent in the CSV
                for name, email in employees_to_delete:
                    try:
                        # Retrieve the employee object based on name and email for the current manager
                        employee_to_delete = Employee.objects.get(
                            name=name, 
                            manager=manager
                        )                    
                        # Use the user_id for deletion
                        employee_to_delete_id = employee_to_delete.user_id
                        Employee.objects.filter(user_id=employee_to_delete_id).delete()
                        delete_count += 1

                    except Employee.DoesNotExist:
                        print(f"Employee not found for deletion: {name} ({email})")


                messages.success(request, f'{created_count} employees were successfully created. '
                                          f'{skipped_count} records were skipped. '
                                          f'{delete_count} employees were deleted.')

            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')

            return redirect('upload_file')

        messages.error(request, 'No file was provided.')
        return redirect('upload_file')

@method_decorator(manager_login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class SendCustomEmailsToAllEmployees(View):
    def get(self, request):
        form = EmailForm()
        return render(request, 'email_sender_app/email_form.html', {'form': form})

    def post(self, request):
        form = EmailForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            sign = form.cleaned_data['sign']
            
            manager = CompanyManager.objects.get(pk=request.session.get('manager_id'))
            email_account = EmailAccount.objects.get(manager=manager)

            # Check if send_mails is True
            if not manager.send_mails:
                messages.error(request, 'Email sending is disabled for your account. Please enable it to send emails.')
                return redirect('dashboard')

            employees = Employee.objects.filter(manager=manager)

            email_backend = get_connection(
                host=email_account.smtp_server,
                port=email_account.smtp_port,
                username=email_account.email,
                password=email_account.manager.app_password,
                use_tls=email_account.use_tls,
                use_ssl=email_account.use_ssl,
            )

            for employee in employees:
                formatted_body = body.replace('\n', '<br>').replace(' ', '&nbsp;')
                html_message = loader.render_to_string(
                    'email_sender_app/custom_message.html',
                    {
                        'title': title,
                        'body': f'Hello {employee.name},<br>{formatted_body}',  # Preserving new lines and spaces
                        'sign': sign,
                        'employee_id': employee.user_id,
                    }
                )

                email = EmailMultiAlternatives(
                    title,
                    body,
                    email_account.email,
                    [employee.email],
                    connection=email_backend
                )
                email.attach_alternative(html_message, "text/html")
                email.send(fail_silently=False)

            messages.success(request, 'Custom emails have been successfully sent to all your employees.')
            return redirect('dashboard')
        else:
            return render(request, 'email_sender_app/email_form.html', {'form': form})     

@method_decorator(manager_login_required, name='dispatch')
class ExportResponsesByDateView(View):
    def get(self, request):
        selected_date = request.GET.get('date')
        
        if not selected_date:
            messages.error(request, 'Date is required for exporting responses.')
            return redirect('view_responses_by_date')
        
        try:
            formatted_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

            manager_id = request.session.get('manager_id')
            manager = CompanyManager.objects.get(pk=manager_id)

            responses = EmployeeResponse.objects.filter(date=formatted_date, employee__manager=manager)

            if not responses.exists():
                messages.error(request, f'No responses found for the selected date: {formatted_date}.')
                return redirect('view_responses_by_date')

            employee_response_resource = EmployeeResponseResource()
            dataset = employee_response_resource.export(responses)

            filename = f'Employee_Responses_{manager.name}_{formatted_date.strftime("%Y-%m-%d")}.csv'
            
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except ValueError:
            messages.error(request, 'Invalid date format. Please use "DD-MM-YYYY".')
            return redirect('view_responses_by_date')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('view_responses_by_date')

@method_decorator(manager_login_required, name='dispatch')
class ExportResponsesByEmployeeView(View):
    def get(self, request, employee_id):
        try:
            employee = get_object_or_404(Employee, pk=employee_id)

            responses = EmployeeResponse.objects.filter(employee=employee).order_by('date')

            if not responses.exists():
                messages.error(request, 'No responses found for the selected employee.')
                return redirect('view_responses_by_employee')

            employee_response_resource = EmployeeResponseResource()
            dataset = employee_response_resource.export(responses)

            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="Responses_{employee.name}_{datetime.now().strftime("%Y-%m-%d")}.csv"'
            return response

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('view_responses_by_employee') 

@method_decorator(manager_login_required, name='dispatch')
class ExportMonthlySummaryView(View):
    def get(self, request):
        selected_month = request.GET.get('month')

        manager_id = request.session.get('manager_id')
        manager = CompanyManager.objects.get(pk=manager_id)

        month_name_dict = {
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
            7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        }

        try:
            month_index = int(selected_month)
            month_name_str = month_name_dict[month_index]

            responses_data = (EmployeeResponse.objects
                              .filter(employee__manager=manager, date__month=month_index, date__year=timezone.now().year)
                              .annotate(day=TruncDay('date'))
                              .values('day')
                              .annotate(
                                  total=Count('id'),
                                  yes_count=Count(Case(When(response='yes', then=1), output_field=IntegerField())),
                                  no_count=Count(Case(When(response='no', then=1), output_field=IntegerField()))
                              )
                              .order_by('day'))

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="Monthly_Summary_{month_name_str}_{datetime.now().strftime("%Y-%m-%d")}.csv"'

            writer = csv.writer(response)
            writer.writerow(['Date', 'Total Responses', 'Yes Count', 'No Count', 'Not Responded'])

            total_employees = Employee.objects.filter(manager=manager).count()

            for data in responses_data:
                not_responded_count = total_employees - (data['yes_count'] + data['no_count'])
                writer.writerow([data['day'].strftime('%Y-%m-%d'), data['total'], data['yes_count'], data['no_count'], not_responded_count])

            return response

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('view_responses_by_month')

@method_decorator(manager_login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class EmployeeUpdateView(View):
    template_name = 'email_sender_app/update_employee.html'
    
    def get(self, request, user_id):
        employee = get_object_or_404(Employee, user_id=user_id)
        form = EmployeeNameUpdateForm(instance=employee)
        return render(request, self.template_name, {'form': form, 'employee': employee})

    def post(self, request, user_id):
        employee = get_object_or_404(Employee, user_id=user_id)
        form = EmployeeNameUpdateForm(request.POST, instance=employee)
        
        if form.is_valid():
            form.save()
            return redirect('employee_list')
        return render(request, self.template_name, {'form': form, 'employee': employee})

def send_outlook_email(request):
    subject = 'Test Email from Django'
    message = 'This is a test email sent using Outlook SMTP.'
    recipient_list = ['rajsavanur2003@gmail.com']  # Add your recipient email here
    try:
        send_mail(
            subject,
            message,
            'rajsavanur2003@outlook.com',
            recipient_list,
            fail_silently=False,
        )
        return HttpResponse("Email sent successfully!")
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        return HttpResponse(f"Failed to send email: {str(e)}")
    

@method_decorator(manager_login_required, name='dispatch')
class ViewResponsesByDate(View):
    def get(self, request, date):
        selected_date_str = request.GET.get('date', date)
        
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.now().date()

        manager_id = request.session.get('manager_id')
        manager = get_object_or_404(CompanyManager, pk=manager_id)

        all_employees = Employee.objects.filter(manager=manager)
        responses = EmployeeResponse.objects.filter(date=selected_date, employee__manager=manager).order_by('employee__name')

        responded_employees = responses.values_list('employee__user_id', flat=True)
        not_responded_employees = all_employees.exclude(user_id__in=responded_employees)

        all_responses = list(not_responded_employees) + list(responses)

        paginator = Paginator(all_responses, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        yes_count = responses.filter(response='yes').count()
        no_count = responses.filter(response='no').count()

        total_employees = all_employees.count()
        not_responded_count = not_responded_employees.count()

        labels = ['Yes', 'No', 'Not Responded']
        sizes = [yes_count, no_count, not_responded_count]
        colors = ['#28a745', '#dc3545', '#ffc107']
        explode = (0.1, 0, 0)

        valid_sizes = []
        valid_labels = []
        valid_colors = []
        valid_explode = []

        for size, label, color, explode_value in zip(sizes, labels, colors, explode):
            if size > 0:
                valid_sizes.append(size)
                valid_labels.append(label)
                valid_colors.append(color)
                valid_explode.append(explode_value)

        if valid_sizes:
            # logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
            matplotlib.rcParams['font.family'] = 'DejaVu Sans'
            plt.figure(figsize=(6, 4))
            plt.pie(valid_sizes, explode=valid_explode, labels=valid_labels, colors=valid_colors,
                    autopct=lambda p: '{:.0f}'.format(p * sum(valid_sizes) / 100), shadow=True, startangle=140)
            plt.axis('equal')
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)

            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        else:
            image_base64 = None

        return render(request, 'email_sender_app/view_responses_by_date.html', {
            'page_obj': page_obj,
            'yes_count': yes_count,
            'no_count': no_count,
            'not_responded_count': not_responded_count,
            'selected_date': selected_date.strftime('%Y-%m-%d'),
            'chart_image': image_base64,
            'page_obj': page_obj
        })

@method_decorator(manager_login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class UpdateManagerNameView(View):
    def get(self, request):
        manager = CompanyManager.objects.get(pk=request.session['manager_id'])
        form = UpdateManagerNameForm(instance=manager)
        return render(request, 'email_sender_app/update_manager_details.html', {'form': form})

    def post(self, request):
        manager = CompanyManager.objects.get(pk=request.session['manager_id'])
        form = UpdateManagerNameForm(request.POST, instance=manager)
        if form.is_valid():
            form.save()
            messages.success(request, 'Manager details updated successfully.')
            return redirect('dashboard')
        return render(request, 'email_sender_app/update_manager_details.html', {'form': form})    

@method_decorator(manager_login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class UpdateManagerEmailTemplateView(View):
    def get(self, request):
        manager = request.session.get('manager_id')
        if not manager:
            return HttpResponseBadRequest('Manager not logged in')

        template = get_object_or_404(EmailTemplate, manager__manager_id=manager)
        return render(request, 'email_sender_app/update_email_template.html', {'template': template})

    def post(self, request):
        # Check if it's a PUT request simulated via POST
        method = request.POST.get('_method', '').upper()
        if method != 'PUT':
            return HttpResponseBadRequest('Invalid method')

        manager = request.session.get('manager_id')
        if not manager:
            return HttpResponseBadRequest('Manager not logged in')

        template = get_object_or_404(EmailTemplate, manager__manager_id=manager)
        form = EmailTemplateForm(request.POST, instance=template)

        if form.is_valid():
            form.save()
            messages.success(request, 'Email template updated successfully.')
            return redirect('dashboard')  # Redirect to the dashboard with a success message
        else:
            return HttpResponseBadRequest('Form validation failed')

@method_decorator(manager_login_required, name='dispatch')
class ManagerSettingsView(TemplateView):
    template_name = 'email_sender_app/manager_details_dashboard.html'        

class UpdateManagerEmailAccountView(View):
    def get(self, request):
        manager_id = request.session.get('manager_id')
        if not manager_id:
            return redirect('login')  # Redirect to login if manager is not logged in

        email_account = get_object_or_404(EmailAccount, manager__manager_id=manager_id)
        return render(request, 'email_sender_app/update_email_account.html', {'email_account': email_account})

    def post(self, request):
        manager_id = request.session.get('manager_id')
        if not manager_id:
            return redirect('login')

        email_account = get_object_or_404(EmailAccount, manager__manager_id=manager_id)
        form = UpdateEmailAccountForm(request.POST, instance=email_account)

        if form.is_valid():
            form.save()
            messages.success(request, 'Email account details updated successfully.')
            return redirect('dashboard')
        else:
            return render(request, 'email_sender_app/update_email_account.html', {'email_account': email_account, 'form': form})

class AboutUsView(TemplateView):
    template_name = 'email_sender_app/about_us.html'
      
class GetEmployeeUserIDView(View):
    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')
        if not email:
            return JsonResponse({"error": "Email parameter is required."}, status=400)

        all_emails = [emp.email for emp in Employee.objects.all()]

        try:
            employee = None
            for emp in Employee.objects.all():
                if emp.email == email:
                    employee = emp
                    break

            if not employee:
                return JsonResponse({"error": "Employee not found."}, status=404)

            return JsonResponse({"user_id": employee.user_id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
               
class GetEmployeeUserIDByEmail(View):
    def get(self, request, email, *args, **kwargs):
        if not email:
            return JsonResponse({"error": "Email parameter is required."}, status=400)

        all_emails = [emp.email for emp in Employee.objects.all()]
        print("Decrypted emails in database:", all_emails)

        try:
            employee = None
            for emp in Employee.objects.all():
                if emp.email == email:
                    employee = emp
                    break

            if not employee:
                return JsonResponse({"error": "Employee not found."}, status=404)

            return JsonResponse({"user_id": employee.user_id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class GetWorkingDaysForCurrentMonth(View):
    def get(self, request, employee_id, *args, **kwargs):
        try:
            employee = Employee.objects.get(user_id=employee_id)
            
            manager = employee.manager
            
            today = timezone.now()
            current_month = today.month
            current_year = today.year
            
            working_days = WorkingDays.objects.filter(manager=manager, month=current_month, year=current_year).first()
            
            if not working_days:
                return JsonResponse({"error": "Working days not found for the current month."}, status=404)

            return JsonResponse({
                "working_days": working_days.days
            })
        
        except Employee.DoesNotExist:
            return JsonResponse({"error": "Employee not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

