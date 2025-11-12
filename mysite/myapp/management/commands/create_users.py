from django.core.management.base import BaseCommand
from myapp.models import User,Group,Expense,Person
import random
from datetime import date,timedelta 
from myapp.utils import create_expense_shares

class Command(BaseCommand):
    help = 'Creates Testing Users'

    def add_arguments(self, parser):
        parser.add_argument('--with-sample-data',action='store_true',help='Also create sample groups and expenses')

    def get_random_date(self, start_date, end_date):
        """Generates a random date between two given dates (inclusive)."""
        delta = end_date - start_date
        total_days = delta.days
        random_days = random.randrange(total_days + 1)
        return start_date + timedelta(days=random_days)


    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating Users........'))

        sample_user = [
             {
                'username': 'alice_johnson',
                'email': 'alice.johnson@email.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'password': 'securepass123',
                'person_name': 'Alice Johnson'
            },
            {
                'username': 'bob_smith',
                'email': 'bob.smith@email.com',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'password': 'securepass123',
                'person_name': 'Bob Smith'
            },
            {
                'username': 'charlie_brown',
                'email': 'charlie.brown@email.com',
                'first_name': 'Charlie',
                'last_name': 'Brown',
                'password': 'securepass123',
                'person_name': 'Charlie Brown'
            },
            {
                'username': 'diana_prince',
                'email': 'diana.prince@email.com',
                'first_name': 'Diana',
                'last_name': 'Prince',
                'password': 'securepass123',
                'person_name': 'Diana Prince'
            },
            {
                'username': 'edward_norton',
                'email': 'edward.norton@email.com',
                'first_name': 'Edward',
                'last_name': 'Norton',
                'password': 'securepass123',
                'person_name': 'Edward Norton'
            },
            {
                'username': 'fiona_green',
                'email': 'fiona.green@email.com',
                'first_name': 'Fiona',
                'last_name': 'Green',
                'password': 'securepass123',
                'person_name': 'Fiona Green'
            },
            {
                'username': 'george_wilson',
                'email': 'george.wilson@email.com',
                'first_name': 'George',
                'last_name': 'Wilson',
                'password': 'securepass123',
                'person_name': 'George Wilson'
            }
        ]

        user_count = 0

        for user_data in sample_user:
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(self.style.WARNING(f'User exists..{user_data['username']}... Skipped'))
                continue
            try:
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                user_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ User created with username= {user_data['username']}"))
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error creating {user_data['username']}: {e}"))
                
        self.stdout.write(self.style.SUCCESS(f"Successfully Created {user_count} Users...."))
        self.stdout.write(self.style.SUCCESS('\n Database Statistics:'))
        self.stdout.write(f"Total Users: {User.objects.count()}")

        if options['with_sample_data']:
            self.create_sample_data()

    def create_sample_data(self):
        self.stdout.write(self.style.SUCCESS('\nCreating sample data...'))
        
        try:
            persons = list(Person.objects.all())
            if len(persons) < 3:
                self.stdout.write(
                    self.style.ERROR("Need at least 3 persons to create sample data")
                )
                return
            
            groups_data = [
                {
                    'name': 'Weekend Getaway',
                    'member_count': min(5, len(persons)),
                    'expenses': [
                        ('Hotel accommodation', 240.00),
                        ('Car rental', 180.00),
                        ('Restaurant dinner', 95.50),
                        ('Gas money', 60.00),
                        ('Grocery shopping', 75.25),
                        ('Activity tickets', 120.00)
                    ]
                },
                {
                    'name': 'Office Team Lunch',
                    'member_count': min(4, len(persons)),
                    'expenses': [
                        ('Pizza order', 85.00),
                        ('Coffee and drinks', 35.50),
                        ('Dessert platter', 28.75),
                        ('Tip for delivery', 12.00),
                        ('Paper plates and napkins', 8.50)
                    ]
                },
                {
                    'name': 'Apartment Roommates',
                    'member_count': min(3, len(persons)),
                    'expenses': [
                        ('Monthly electricity bill', 145.30),
                        ('Internet subscription', 89.99),
                        ('Cleaning supplies', 42.75),
                        ('Shared groceries', 156.80),
                        ('Netflix subscription', 15.99),
                        ('Water bill', 78.25)
                    ]
                },
                {
                    'name': 'College Study Group',
                    'member_count': min(4, len(persons)),
                    'expenses': [
                        ('Textbook purchase', 185.00),
                        ('Printing costs', 22.50),
                        ('Snacks for study session', 38.25),
                        ('Library late fees', 15.00),
                        ('Group project supplies', 67.80),
                        ('Cafe study session', 45.75)
                    ]
                }

            ]
 
            created_groups = []
            create_expense = []

            start_date = date(2023, 1, 1)
            end_date = date.today()

            for n,group in enumerate(groups_data,1):
                self.stdout.write(self.style.SUCCESS(f'Creating Group{n}-{group['name']}'))
                
                group_members = random.sample(persons, group['member_count'])
                group_creator = random.choice(group_members)
                g = ''
                try: 
                    g = Group.objects.get_or_create(
                        groupName = group['name'],
                        made_by=group_creator
                    )
                    g.members.add(*group_members)
                    created_groups.append(g)
                except:
                    g = Group.objects.get(groupName=group['name'])
                    g.members.add(*group_members)
                    created_groups.append(g)

                for expense_name,amt in group['expenses']:
                    payer = random.choice(group_members)
                    random_expense_date = self.get_random_date(start_date,end_date)
                    expense = Expense.objects.create(
                        expenseName = expense_name,
                        amount = amt,
                        payer=payer,
                        group=g,
                        description=f'{expense_name} paid by {payer.name}',
                        date=random_expense_date
                    )
                    print(random_expense_date)
                    create_expense_shares(expense,'equal',group_members,amt)
                    create_expense.append(expense_name)
                    self.stdout.write(self.style.SUCCESS(f'----Expense of {expense_name} in {group["name"]}'))
            
            
            self.stdout.write(self.style.SUCCESS(f"Create {len(created_groups)} of Groups and {len(create_expense)} of Expense......"))


        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creating sample data: {e}'))