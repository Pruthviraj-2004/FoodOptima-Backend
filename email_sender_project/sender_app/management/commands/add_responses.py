from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from sender_app.models import Employee, EmployeeResponse, WorkingDays

class Command(BaseCommand):
    help = 'Add responses for an employee for specified months'

    def handle(self, *args, **kwargs):
        self.add_responses_for_employee(8)  # Replace '1' with the desired employee ID

    def add_responses_for_employee(self, employee_id):
        employee = Employee.objects.get(user_id=employee_id)
        print(f"Processing responses for {employee.name}")

        months_workdays = {
            7: [0, 3],  # July: Tuesday (1) and Thursday (3)
            8: [1, 2],  # August: Tuesday (1) and Thursday (3)
            9: [0, 3, 4],  # September: Tuesday (1) and Wednesday (2)
        }

        start_date = datetime(2024, 7, 1)
        end_date = datetime(2024, 9, 30)

        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() in [5, 6]:
                print(f"Skipping weekend: {current_date}")
                current_date += timedelta(days=1)
                continue

            try:
                working_days = WorkingDays.objects.get(month=current_date.month, year=current_date.year)
                if current_date.day not in working_days.days:
                    print(f"Skipping non-working day: {current_date}")
                    current_date += timedelta(days=1)
                    continue
            except WorkingDays.DoesNotExist:
                print(f"No working days defined for {current_date.month}/{current_date.year}")
                current_date += timedelta(days=1)
                continue

            if current_date.month in months_workdays and current_date.weekday() in months_workdays[current_date.month]:
                response_value = 'yes'
            else:
                response_value = 'no'

            response, created = EmployeeResponse.objects.get_or_create(
                employee=employee,
                date=current_date,
                defaults={'response': response_value}
            )
            
            if created:
                print(f"Added response '{response_value}' for {employee.name} on {current_date}")
            else:
                print(f"Response for {employee.name} on {current_date} already exists")

            current_date += timedelta(days=1)
