from django.core.management.base import BaseCommand
from django.template import loader
from django.utils import timezone
from calendar import monthrange
from django.core.mail import get_connection, EmailMultiAlternatives
from django.utils import timezone
from sender_app.models import CompanyManager, Employee, EmailAccount, EmployeeResponse, WorkingDays, EmailTemplate



class Command(BaseCommand):
    help = 'Send daily emails to all users'

    def handle(self, *args, **kwargs):
        self.send_daily_summary_email()
        self.send_emails_to_all_users()

    def send_emails_to_all_users(self):
        today = timezone.now().date()
        current_month = today.month
        current_year = today.year

        # Retrieve all managers dynamically
        managers = CompanyManager.objects.all()

        for manager in managers:
            # Check if send_mails is True
            if not manager.send_mails:
                print(f"Email sending is disabled for Manager {manager.name}. Skipping.")
                continue

            # Get the working days for the current and next month for each manager
            current_month_working_days = WorkingDays.objects.filter(manager=manager, month=current_month, year=current_year).first()
            next_month_working_days = WorkingDays.objects.filter(manager=manager, month=current_month + 1, year=current_year).first()

            # Check if today is a working day for this manager
            if current_month_working_days and today.day in current_month_working_days.days:
                # Get the next working day for the current manager
                next_working_day = self.get_next_working_day(today, current_month_working_days, next_month_working_days)

                if not next_working_day:
                    print(f"No upcoming working days found for manager {manager.name} after {today}. Emails will not be sent.")
                    continue

                # Fetch the email account details for the current manager
                email_account = EmailAccount.objects.filter(manager=manager).first()
                if not email_account:
                    print(f"No email account found for Manager {manager.name}. Skipping this manager.")
                    continue

                # Establish the email backend connection for each manager
                email_backend = get_connection(
                    host=email_account.smtp_server,
                    port=email_account.smtp_port,
                    username=email_account.email,
                    password=email_account.manager.app_password,
                    use_tls=email_account.use_tls,
                    use_ssl=email_account.use_ssl,
                )

                # Fetch the email template or use the default template
                email_template = EmailTemplate.objects.filter(manager=manager).first()
                if email_template:
                    title = email_template.subject
                    body = email_template.body
                    signature = f'Sincerely, {manager.name}'
                else:
                    title = 'Office Attendance Confirmation'
                    body = 'Hello {employee.name}, this email is to verify whether you will attend the office on {date}. Please confirm your attendance.'
                    signature = 'Your Manager'

                # Send emails to the manager's employees for the next working day
                employees = Employee.objects.filter(manager=manager)
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
                        }
                    )

                    email = EmailMultiAlternatives(
                        title,
                        'Please confirm your attendance for the next working day.',
                        email_account.email,
                        [employee.email],
                        connection=email_backend
                    )
                    email.attach_alternative(html_message, "text/html")
                    email.send(fail_silently=False)

                print(f"Emails sent to employees of Manager {manager.name} for the next working day: {next_working_day}.")

            else:
                print(f"Today ({today}) is not a working day for Manager {manager.name}. No emails sent.")

    # Helper function to get the next working day
    def get_next_working_day(self, today, current_month_working_days, next_month_working_days):
        # Get the next working day in the current month
        upcoming_days = [day for day in current_month_working_days.days if day > today.day]
        if upcoming_days:
            next_day = min(upcoming_days)
            last_day_of_month = monthrange(today.year, today.month)[1]
            if next_day <= last_day_of_month:
                return today.replace(day=next_day)

        # If no working days left in the current month, check the next month
        if next_month_working_days:
            next_day = min(next_month_working_days.days)
            next_month = today.month + 1
            next_year = today.year
            if next_month > 12:
                next_month = 1
                next_year += 1

            last_day_of_next_month = monthrange(next_year, next_month)[1]
            if next_day <= last_day_of_next_month:
                return today.replace(year=next_year, month=next_month, day=next_day)

        return None

    def send_daily_summary_email(self):
        today = timezone.now().date()  # Get today's date
        month = today.month
        year = today.year

        # Retrieve all managers
        managers = CompanyManager.objects.all()

        for manager in managers:
            # Check if send_mails is True
            if not manager.send_mails:
                print(f"Email sending is disabled for Manager {manager.name}. Skipping.")
                continue
            try:
                # Check if today is a working day for the current manager
                working_days = WorkingDays.objects.filter(manager=manager, month=month, year=year).first()

                if working_days and today.day in working_days.days:  # Check if today is a working day for this manager
                    # Get responses from the employees of this manager
                    responses = EmployeeResponse.objects.filter(employee__manager=manager, date=today)

                    total_responses = responses.count()
                    yes_count = responses.filter(response='yes').count()
                    no_count = responses.filter(response='no').count()

                    # Fetch the email account details for the manager
                    email_account = EmailAccount.objects.filter(manager=manager).first()
                    if not email_account:
                        print(f"No email account found for Manager {manager.name}. Skipping this manager.")
                        continue

                    # Establish email backend connection for each manager
                    email_backend = get_connection(
                        host=email_account.smtp_server,
                        port=email_account.smtp_port,
                        username=email_account.email,
                        password=email_account.manager.app_password,
                        use_tls=email_account.use_tls,
                        use_ssl=email_account.use_ssl,
                    )

                    # Render the email message for this manager
                    html_message = loader.render_to_string(
                        'email_sender_app/summary_message.html',
                        {
                            'title': f'Daily Attendance Summary for {manager.name}',
                            'body': f'Attendance summary for {today.strftime("%Y-%m-%d")}:',
                            'total_responses': total_responses,
                            'yes_count': yes_count,
                            'no_count': no_count,
                            'sign': f'Sincerely, {manager.name}',
                        }
                    )

                    # Send the email summary to the manager
                    email = EmailMultiAlternatives(
                        f'Daily Attendance Summary for {today.strftime("%Y-%m-%d")}',
                        'Here is the summary of today\'s attendance responses.',
                        email_account.email,
                        [manager.email],  # Send the summary to the current manager's email
                        connection=email_backend
                    )
                    email.attach_alternative(html_message, "text/html")
                    email.send(fail_silently=False)

                    print(f"Summary email sent to Manager {manager.name} for {today}.")

                else:
                    print(f"Today ({today}) is not a working day for Manager {manager.name}. No summary email sent.")

            except WorkingDays.DoesNotExist:
                print(f"No working days configuration found for Manager {manager.name} for {month}/{year}.")

