# Graduation Project Evaluation System

A comprehensive web-based system for evaluating graduation projects using rubrics, supporting multiple judges, teams, and comprehensive reporting.

## Features

1. **Rubric Management**
   - Import rubrics from Excel files
   - Each rubric can have multiple criteria with weights
   - Support for maximum scores per criterion

2. **Project & Team Management**
   - Projects can have multiple team members (3 or more)
   - Track grades per student based on team evaluation

3. **Judge Evaluation System**
   - Multiple judges can log in and evaluate projects
   - Judges enter scores and comments per criterion
   - Text feedback for each criterion

4. **Automatic Score Calculation**
   - Calculate average scores per criterion across judges
   - Aggregate scores with weights
   - Calculate total marks per student and per project

5. **Reporting & Export**
   - Generate reports per student and per project
   - Export to Excel or PDF formats
   - Show judges' scores, comments, averages, and final grades

6. **User Accounts & Roles**
   - **Admin**: Upload rubrics, add projects/judges, manage users
   - **Judge**: Evaluate projects, view evaluations
   - **Student**: View grades (if allowed)

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

**Note for Mac M1 (Apple Silicon):**
- Use `python3` explicitly (not `python`)
- Ensure you have Python installed via Homebrew or official installer
- Some packages may need to be installed with `arch -arm64` prefix if compatibility issues occur

### Setup Steps

1. **Clone or navigate to the project directory**

```bash
cd "eb-based graduation project evaluation system"
```

2. **Create and activate virtual environment**

**On Mac (including M1):**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

**Mac M1 Note:** If you encounter architecture-related errors, try:
```bash
arch -arm64 pip install -r requirements.txt
```

4. **Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create a superuser (admin account)**

```bash
python manage.py createsuperuser
```

6. **Run the development server**

Choose one of the following options:

**Option A: Run on localhost (127.0.0.1)**
```bash
python manage.py runserver
# or explicitly:
python manage.py runserver 127.0.0.1:8000
```

**Mac M1 Note:** Use `python3` if `python` doesn't work:
```bash
python3 manage.py runserver
```
- Access at: http://127.0.0.1:8000/ or http://localhost:8000/
- Only accessible from the same machine

**Option B: Run on a specific IP address**
```bash
python manage.py runserver 10.100.81.190:8000
```
- Access at: http://10.100.81.190:8000/
- Accessible from other devices on the same network
- Make sure the IP is in `ALLOWED_HOSTS` in `settings.py`

**Option C: Run on all network interfaces (0.0.0.0)**
```bash
python manage.py runserver 0.0.0.0:8000
```
- Accessible from any device on the network using your machine's IP
- Access at: http://YOUR_IP_ADDRESS:8000/
- Make sure your IP is in `ALLOWED_HOSTS` in `settings.py`

7. **Access the application**

- Web Interface: http://127.0.0.1:8000/ (localhost) or http://YOUR_IP:8000/ (network)
- Admin Panel: http://127.0.0.1:8000/admin/ or http://YOUR_IP:8000/admin/

## Usage Guide

### For Administrators

1. **Create User Accounts**
   - Go to Admin Panel → Users → Add User
   - Set the role (Admin, Judge, or Student)
   - Create associated Judge or Student profiles if needed

2. **Import Rubrics**
   - Go to Rubrics → Import Rubric
   - Upload an Excel file with columns:
     - **Criterion Name** (required)
     - **Max Score** (required)
     - **Description** (optional)
     - **Weight** (optional, default: 1.0)

3. **Create Projects**
   - Go to Admin Panel → Projects → Add Project
   - Assign a rubric to the project
   - Create a team and add students to the team

### For Judges

1. **Login** with your judge credentials
2. **View Projects** from the Projects page
3. **Click "Evaluate"** on a project
4. **Enter scores** for each criterion
5. **Add comments** (optional) for each criterion or general comments
6. **Save as Draft** or **Submit** the evaluation

### For Students

1. **Login** with your student credentials
2. **View your team's projects** from the Projects page
3. **View project details** including final scores and comments

## Excel Rubric Format

Create an Excel file with the following columns:

| Criterion Name | Description | Weight | Max Score |
|----------------|-------------|--------|-----------|
| Technical Quality | Evaluation of technical implementation | 1.5 | 30 |
| Documentation | Quality of documentation | 1.0 | 20 |
| Presentation | Oral presentation quality | 1.0 | 25 |
| Innovation | Level of innovation | 0.5 | 15 |

**Notes:**
- Column names are case-insensitive
- Criterion Name and Max Score are required
- Description and Weight are optional (Weight defaults to 1.0)

## Project Structure

```
project_evaluation/
├── manage.py
├── requirements.txt
├── config/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/            # User management
│   ├── models.py        # User, Judge, Student models
│   ├── views.py
│   └── admin.py
├── projects/            # Project and team management
│   ├── models.py        # Project, Team models
│   ├── views.py
│   └── admin.py
├── rubrics/             # Rubric management
│   ├── models.py        # Rubric, Criterion models
│   ├── views.py         # Import functionality
│   └── admin.py
├── evaluations/         # Evaluation and scoring
│   ├── models.py        # Evaluation, Score models
│   ├── views.py         # Evaluation forms
│   ├── utils.py         # Calculation logic
│   └── admin.py
├── reports/             # Reporting and export
│   ├── views.py         # Export to Excel/PDF
│   └── urls.py
└── templates/           # HTML templates
    ├── base.html
    └── ...
```

## Database Schema

- **User**: Custom user model with roles (Admin, Judge, Student)
- **Project**: Project entity with title, description, rubric, status
- **Team**: Team entity linked to project (one team per project)
- **Student**: Student profile linked to user and team
- **Judge**: Judge profile linked to user
- **Rubric**: Rubric with name, description, max_total_score
- **Criterion**: Individual criterion within rubric (weight, max_score)
- **Evaluation**: Judge's evaluation for a project (status, total_score, comments)
- **Score**: Individual score for a criterion (score, comments)

## Score Calculation Logic

1. **Per Criterion Average**: Average of all submitted judge scores for each criterion
2. **Weighted Score**: `average_score * weight` for each criterion
3. **Total Project Score**: Sum of all weighted scores
4. **Percentage**: `(total_score / max_total_score) * 100`

## API Endpoints

- `/` - Home page
- `/admin/` - Django admin interface
- `/rubrics/` - Rubric management
- `/projects/` - Project listing and details
- `/evaluations/` - Evaluation forms and listing
- `/reports/project/<id>/` - Project evaluation report
- `/reports/project/<id>/excel/` - Export to Excel
- `/reports/project/<id>/pdf/` - Export to PDF

## Security

- Django's built-in authentication system
- Role-based permissions
- Server-side validation for all inputs
- SQL injection protection via Django ORM
- XSS protection via template auto-escaping

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

After modifying models:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Troubleshooting

1. **ImportError: No module named 'django'**
   - Make sure the virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **Database errors**
   - Run `python manage.py migrate` to apply migrations

3. **Permission errors**
   - Make sure users have the correct role set
   - Check that Judge/Student profiles are created for users

## License

This project is open-source and free to use.

## Support

For issues or questions, please check the design document (`DESIGN.md`) for detailed system architecture information.
