from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
import random
from sender_app.models import Employee, EmployeeResponse, WorkingDays

class Command(BaseCommand):
    help = 'Create random employee responses for working days in September 2024'

    def handle(self, *args, **kwargs):
        year = 2024
        month = 12

        # Filter employees based on revised IDs
        # employee_ids = list(range(150, 157)) + [161]  # Includes 68-87, 148, 162
        # employee_ids.remove(76)  # Remove the deleted employee ID
        # employees = Employee.objects.filter(user_id__in=employee_ids)

        employees = Employee.objects.filter(user_id__range=(68, 147))

        for employee in employees:
            # Get the working days for the employee's manager
            working_days = WorkingDays.objects.filter(manager=employee.manager, month=month, year=year).first()

            if working_days and working_days.days:
                # print(f"Working days for {employee.manager.name}: {working_days.days}")  # Debug print
                for day in working_days.days:
                    try:
                        response_date = date(year, month, day)  # Create a date object for each working day

                        # Check if the response already exists
                        if not EmployeeResponse.objects.filter(employee=employee, date=response_date).exists():
                            response_value = random.choice(['yes', 'no'])  # Randomly choose between 'yes' and 'no'
                            response = EmployeeResponse(
                                employee=employee,
                                date=response_date,
                                response=response_value,
                                created_at=timezone.now(),
                                updated_at=timezone.now()
                            )
                            response.save()
                    except ValueError as e:
                        print(f"Error creating date for day {day}: {e}")  # Handle invalid day values

        self.stdout.write(self.style.SUCCESS(f'Successfully added random responses for {len(employees)} employees for working days in 2024.'))
