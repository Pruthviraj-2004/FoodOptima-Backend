from django.core.management.base import BaseCommand
from sender_app.models import Employee, Company, CompanyManager
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create random employees for testing purposes'

    def handle(self, *args, **kwargs):
        num_employees = 20
        employees_data = []

        for i in range(num_employees):
            name = f"4Test Employee1 {i + 1}"
            email = f"tes4t{i + 11}@gmail.com"
            company_id = 1
            manager_id = 4
            
            try:
                company = Company.objects.get(pk=company_id)
                manager = CompanyManager.objects.get(pk=manager_id)
                employee = Employee(
                    name=name,
                    email=email,
                    company=company,
                    manager=manager,
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                )
                employees_data.append(employee)
            except Company.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Company with ID {company_id} does not exist."))
            except CompanyManager.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Manager with ID {manager_id} does not exist."))

        Employee.objects.bulk_create(employees_data)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_employees} random employees.'))
