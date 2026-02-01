# Graduation Project Evaluation System - System Design

## 1. Overview

A web-based system for evaluating graduation projects using rubrics, supporting multiple judges, teams, and comprehensive reporting.

## 2. Database Schema

### 2.1 Core Entities

#### User (extends Django's AbstractUser)
- `id`: Primary key
- `username`: Unique username
- `email`: Email address
- `first_name`, `last_name`: Name fields
- `role`: Choice field (ADMIN, JUDGE, STUDENT)
- `is_active`, `is_staff`: Django default fields

#### Project
- `id`: Primary key
- `title`: Project title
- `description`: Project description
- `rubric`: Foreign key to Rubric
- `created_at`: Timestamp
- `updated_at`: Timestamp
- `status`: Choice field (DRAFT, EVALUATING, COMPLETED)

#### Team
- `id`: Primary key
- `project`: Foreign key to Project (one project has one team)
- `team_name`: Optional team name
- `created_at`: Timestamp

#### Student
- `id`: Primary key
- `user`: OneToOne relationship with User
- `student_id`: Unique student identifier
- `team`: Foreign key to Team (many students per team)
- `created_at`: Timestamp

#### Judge
- `id`: Primary key
- `user`: OneToOne relationship with User
- `judge_id`: Unique judge identifier
- `specialization`: Optional field
- `assigned_projects`: ManyToMany with Project (for future assignment tracking)

#### Rubric
- `id`: Primary key
- `name`: Rubric name/title
- `description`: Rubric description
- `max_total_score`: Maximum possible total score
- `created_at`: Timestamp
- `created_by`: Foreign key to User (Admin)
- `file_path`: Optional path to original Excel file

#### Criterion
- `id`: Primary key
- `rubric`: Foreign key to Rubric
- `name`: Criterion name
- `description`: Criterion description
- `weight`: Decimal field (default 1.0, used for weighted average)
- `max_score`: Maximum score for this criterion
- `order`: Integer for ordering criteria
- `created_at`: Timestamp

#### Evaluation
- `id`: Primary key
- `project`: Foreign key to Project
- `judge`: Foreign key to Judge
- `status`: Choice field (DRAFT, SUBMITTED)
- `total_score`: Calculated total score
- `comments`: General comments from judge
- `created_at`: Timestamp
- `submitted_at`: Timestamp (when submitted)
- `updated_at`: Timestamp
- Unique constraint: (project, judge) - one evaluation per judge per project

#### Score
- `id`: Primary key
- `evaluation`: Foreign key to Evaluation
- `criterion`: Foreign key to Criterion
- `score`: Decimal field (actual score given)
- `comments`: Text field (criterion-specific feedback)
- `created_at`: Timestamp
- `updated_at`: Timestamp
- Unique constraint: (evaluation, criterion) - one score per criterion per evaluation

## 3. Data Flow

### 3.1 Rubric Import Workflow

1. **Admin uploads Excel file**
   - Excel format: Columns = Criterion Name, Description, Weight, Max Score
   - System parses Excel using pandas/openpyxl
   - Validates data (weights, max scores)
   - Creates Rubric and Criterion records

2. **Rubric Assignment**
   - Admin creates Project
   - Admin assigns Rubric to Project
   - System validates rubric compatibility

### 3.2 Project & Team Setup

1. **Create Project**
   - Admin creates Project with title, description
   - Admin assigns Rubric

2. **Create Team**
   - Admin creates Team for Project
   - Admin adds Students to Team
   - Each Student has User account (or can be created)

3. **Assign Judges**
   - Admin assigns Judges to Projects (optional assignment system)

### 3.3 Judge Evaluation Workflow

1. **Judge Login**
   - Judge logs in with credentials
   - Views assigned projects or all projects (based on permissions)

2. **Start Evaluation**
   - Judge selects Project
   - System shows Rubric with all Criteria
   - If evaluation exists (DRAFT), loads previous scores/comments

3. **Enter Scores**
   - Judge enters score per criterion (validated against max_score)
   - Judge adds comments per criterion (optional)
   - Judge can add general comments

4. **Save/Submit**
   - Save as DRAFT: Allows editing later
   - Submit: Marks evaluation as SUBMITTED (may lock editing)

### 3.4 Score Calculation Workflow

1. **Per Criterion Average**
   - For each criterion: Calculate average of all submitted judge scores
   - Formula: `avg_score[criterion] = sum(scores) / count(judges)`

2. **Weighted Score Calculation**
   - If weights exist: `weighted_score[criterion] = avg_score[criterion] * weight[criterion]`
   - Else: `weighted_score[criterion] = avg_score[criterion]`

3. **Total Project Score**
   - `total_score = sum(weighted_scores for all criteria)`
   - If max_total_score exists in rubric: `percentage = (total_score / max_total_score) * 100`

4. **Per Student Score**
   - Currently: All team members get the same project score
   - Future: Could support individual student adjustments

### 3.5 Reporting Workflow

1. **Generate Report**
   - Admin or Judge selects Project
   - System aggregates:
     - All evaluations (judge scores per criterion)
     - Average scores per criterion
     - Total project score
     - All comments

2. **Export Options**
   - **Excel Export**: Spreadsheet with sheets for:
     - Summary (totals, averages)
     - Judge evaluations (detailed scores)
     - Comments section
   - **PDF Export**: Formatted report with tables and charts

3. **Student View** (if enabled)
   - Student logs in
   - Views assigned projects
   - Sees final scores, averages, comments

## 4. Calculation Logic

### 4.1 Per Criterion Average
```
For criterion C in rubric R:
  scores = [Score.score for Score in all submitted evaluations for projects using R where Score.criterion = C]
  avg_score[C] = sum(scores) / len(scores)
```

### 4.2 Weighted Score
```
If criterion C has weight W:
  weighted_score[C] = avg_score[C] * W
Else:
  weighted_score[C] = avg_score[C]
```

### 4.3 Total Project Score
```
total_score = sum(weighted_score[C] for all C in rubric)
```

### 4.4 Normalization (if max_total_score exists)
```
percentage = (total_score / rubric.max_total_score) * 100
```

## 5. User Roles & Permissions

### 5.1 Admin
- Create/Edit/Delete Projects, Teams, Students
- Upload and manage Rubrics
- Assign Judges to Projects
- View all evaluations and reports
- Export reports
- Manage users

### 5.2 Judge
- View assigned/all projects (based on settings)
- Create/Edit evaluations (DRAFT state)
- Submit evaluations
- View own evaluations
- View project reports (read-only)

### 5.3 Student
- View own team's projects
- View final scores and comments
- View project reports (read-only)

## 6. Technical Architecture

### 6.1 Backend
- **Framework**: Django 4.x (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Excel Processing**: pandas, openpyxl
- **PDF Generation**: reportlab or weasyprint
- **Excel Export**: openpyxl or xlsxwriter

### 6.2 Frontend
- Django Templates with Bootstrap 5
- Simple, responsive UI
- AJAX for dynamic score calculations

### 6.3 API (Optional)
- Django REST Framework for future API access
- JSON endpoints for scores, evaluations

## 7. Security Considerations

1. **Authentication**: Django's built-in authentication
2. **Authorization**: Role-based permissions using decorators
3. **Data Validation**: Server-side validation for all inputs
4. **File Upload**: Validate Excel file format and size
5. **SQL Injection**: Django ORM protects against SQL injection
6. **XSS**: Django templates auto-escape by default

## 8. File Structure

```
project_evaluation/
├── manage.py
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py (User, Judge, Student)
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── projects/
│   ├── models.py (Project, Team)
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── rubrics/
│   ├── models.py (Rubric, Criterion)
│   ├── views.py (import functionality)
│   ├── urls.py
│   └── admin.py
├── evaluations/
│   ├── models.py (Evaluation, Score)
│   ├── views.py (scoring, calculation, reporting)
│   ├── urls.py
│   ├── utils.py (calculation logic)
│   └── admin.py
├── reports/
│   ├── views.py (export functionality)
│   ├── urls.py
│   └── exporters.py (Excel, PDF export)
└── templates/
    └── (HTML templates)
```

## 9. Future Enhancements

1. Judge assignment system (assign specific judges to projects)
2. Individual student scoring (allow judges to score team members separately)
3. Evaluation deadlines and reminders
4. Dashboard with statistics and charts
5. Email notifications
6. Multi-language support
7. Advanced analytics and comparisons
8. Mobile-responsive design improvements