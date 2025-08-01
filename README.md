# Splitewise Using ![Django](/mysite/static/images/Extra/djagno.png)

This document outlined a comprehensive plan for developing a web application that closely mirrored the functionality of Splitwise, a popular expense-sharing platform. The application was built using Python with the Django framework for the backend, Tailwind CSS and JavaScript for the frontend.

# Installation
To install the project, follow these steps:

1. Clone the repository using git clone https://github.com/ayushpatelse/Splitewise-using-django.git
2. Install the required dependencies using pip install -r requirements.txt.
3. Set up the database by running python manage.py makemigrations and python manage.py migrate.
4. Create a superuser account using python manage.py createsuperuser.
5. Start the development server using python manage.py runserver.


# Stack
- **Backend:** Python 3, Django 4 , Sqlite
- **Frontend:** Tailwind, Javascript
- **Version Control:** Git

# Core Features
- **Smarter Bill Splitting:**
    - **Custom Splits**: Easily handle complex bills where some people pay fixed amounts and others split the rest evenly.
    - **Exclude People**: Create an expense for a group but leave out the people who weren't involved.
- **Automatic Expense Division**
- **Balance Simplification:** An algorithm that calculates the simplest way for a group to settle up, so    people don't have to make a dozen small payments to each other
- **Group Exit Validation:** Implement a backend validation check to prevent a user from leaving a group if their net balance is non-zero.

# Creator
- **Created By:** [Ayush Patel](https://github.com/ayushpatelse) 
- **Explore Repositories** [Click here](https://github.com/ayushpatelse?tab=repositories)