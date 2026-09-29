from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from .models import (
    FacultyProjectAssignment, Project, Team, WeeklyAttendance, WeeklyProgress,
)
from .forms import WeeklyProgressForm
from accounts.models import Student
from evaluations.models import Evaluation, Score
from rubrics.models import Criterion
import pandas as pd
from io import BytesIO


@login_required
def project_list(request):
    """List all projects"""
    user = request.user
    
    if user.is_admin():
        projects = Project.objects.all()
    elif user.is_faculty():
        # Faculty see projects they are assigned to (as Judge or Supervisor)
        from projects.models import FacultyProjectAssignment
        try:
            faculty = user.faculty_profile
            assignments = FacultyProjectAssignment.objects.filter(faculty=faculty)
            projects = Project.objects.filter(faculty_assignments__in=assignments).distinct()
        except:
            projects = Project.objects.none()
    elif user.is_student_user():
        # Students see projects for their team
        try:
            student = user.student_profile
            team = student.team
            if team:
                projects = Project.objects.filter(team=team)
            else:
                projects = Project.objects.none()
        except:
            projects = Project.objects.none()
    else:
        projects = Project.objects.none()
    
    # For faculty users, check their role (Judge or Supervisor) for each project
    project_assignments = {}
    if user.is_faculty():
        from projects.models import FacultyProjectAssignment
        try:
            faculty = user.faculty_profile
            assignments = FacultyProjectAssignment.objects.filter(faculty=faculty)
            for assignment in assignments:
                project_assignments[assignment.project_id] = assignment.role
        except:
            pass
    
    return render(request, 'projects/project_list.html', {
        'projects': projects,
        'user_role': user.role,
        'project_assignments': project_assignments
    })


@login_required
def project_detail(request, project_id):
    """View project details"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check permissions
    user = request.user
    if not user.is_admin():
        if user.is_student_user():
            try:
                student = user.student_profile
                if not student.team or student.team.project != project:
                    messages.error(request, 'You do not have permission to view this project.')
                    return redirect('projects:project_list')
            except:
                messages.error(request, 'You do not have permission to view this project.')
                return redirect('projects:project_list')
    
    # Get evaluation summary
    from evaluations.utils import get_project_evaluation_summary
    evaluation_summary = get_project_evaluation_summary(project)
    
    # Check if current faculty (assigned as judge) has an evaluation
    judge_evaluation = None
    is_judge = False
    is_supervisor = False
    if user.is_faculty():
        try:
            faculty = user.faculty_profile
            judge_evaluation = Evaluation.objects.filter(project=project, faculty=faculty).first()
            
            # Check if faculty is assigned as Judge or Supervisor for this project
            from projects.models import FacultyProjectAssignment
            assignment = FacultyProjectAssignment.objects.filter(
                project=project,
                faculty=faculty
            ).first()
            
            if assignment:
                if assignment.role == FacultyProjectAssignment.Role.JUDGE:
                    is_judge = True
                elif assignment.role == FacultyProjectAssignment.Role.SUPERVISOR:
                    is_supervisor = True
        except:
            pass
    
    # Safely get team to avoid RelatedObjectDoesNotExist
    team = None
    try:
        team = project.team
    except Team.DoesNotExist:
        team = None
    except AttributeError:
        team = None
    
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'evaluation_summary': evaluation_summary,
        'judge_evaluation': judge_evaluation,
        'team': team,
        'is_judge': is_judge,
        'is_supervisor': is_supervisor
    })


@login_required
def export_all_students_grades(request):
    """Export all students with their grades across all projects"""
    user = request.user
    
    # Check permissions - only admin can export all students
    if not user.is_admin():
        messages.error(request, 'You do not have permission to export student grades.')
        return redirect('projects:project_list')
    
    # Get all projects with teams and students
    projects = Project.objects.filter(team__isnull=False).distinct()
    
    # Collect all unique criteria across all projects, grouped by rubric
    all_criteria = Criterion.objects.filter(
        rubric__projects__in=projects
    ).order_by('rubric__id', 'order').distinct()
    
    # Create a mapping of criterion to display name (e.g., "1.1", "1.2")
    criterion_names = {}
    import re
    from collections import defaultdict
    
    # Group criteria by rubric and section
    rubric_sections = defaultdict(lambda: defaultdict(list))
    for criterion in all_criteria:
        section_title = criterion.section_title or 'Other'
        rubric_sections[criterion.rubric_id][section_title].append(criterion)
    
    # Number criteria within each section for each rubric
    for rubric_id, sections in rubric_sections.items():
        # Sort sections by first criterion order to maintain section order
        sorted_sections = sorted(sections.items(), key=lambda x: min(c.order for c in x[1]))
        
        section_num = 1
        for section_title, criteria_list in sorted_sections:
            # Try to extract section number from section_title if it starts with a number
            match = re.search(r'^(\d+)\.', section_title)
            if match:
                section_num = int(match.group(1))
            
            # Sort criteria by order within section
            criteria_list.sort(key=lambda c: c.order)
            
            # Number criteria within section (1.1, 1.2, etc.)
            criterion_index = 1
            for criterion in criteria_list:
                criterion_id = f"{section_num}.{criterion_index}"
                criterion_names[criterion.id] = criterion_id
                criterion_index += 1
            
            section_num += 1
    
    # Build data rows
    rows = []
    for project in projects:
        team = getattr(project, 'team', None)
        if not team:
            continue
        
        rubric = project.rubric
        if not rubric:
            continue
        
        # Get all submitted evaluations for this project
        evaluations = Evaluation.objects.filter(
            project=project,
            status=Evaluation.Status.SUBMITTED
        )
        
        for student in team.students.all():
            student_name = student.user.get_full_name() or student.user.username
            student_id = student.student_id or 'N/A'
            student_major = student.major or 'N/A'
            
            # Build row data
            row_data = {
                'Student Name': student_name,
                'Student ID': student_id,
                'Project': project.title,
                'Major': student_major
            }
            
            # Add scores for each criterion (only for criteria in this project's rubric)
            project_criteria = rubric.criteria.all().order_by('order')
            for criterion in project_criteria:
                criterion_key = criterion_names.get(criterion.id, f"Criterion_{criterion.id}")
                
                # Get average score for this student-criterion combination
                scores = Score.objects.filter(
                    evaluation__in=evaluations,
                    criterion=criterion,
                    student=student
                ).values_list('score', flat=True)
                
                if scores:
                    avg_score = sum(scores) / len(scores)
                    row_data[criterion_key] = f"{float(avg_score):.2f}"
                else:
                    row_data[criterion_key] = "N/A"
            
            rows.append(row_data)
    
    # Create DataFrame
    if not rows:
        messages.warning(request, 'No student data found to export.')
        return redirect('projects:project_list')
    
    # Get all unique criterion keys from all rows to ensure consistent columns
    all_criterion_keys = set()
    for row in rows:
        all_criterion_keys.update([k for k in row.keys() if k not in ['Student Name', 'Student ID', 'Project', 'Major']])
    
    # Sort criterion keys (e.g., "1.1", "1.2", "2.1", etc.)
    def sort_criterion_key(key):
        # Try to extract numbers for sorting
        match = re.match(r'^(\d+)\.(\d+)$', key)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        return (999, 999)  # Put non-matching keys at the end
    
    sorted_criterion_keys = sorted(all_criterion_keys, key=sort_criterion_key)
    
    # Ensure all rows have all columns
    base_columns = ['Student Name', 'Student ID', 'Project', 'Major'] + sorted_criterion_keys
    for row in rows:
        for key in sorted_criterion_keys:
            if key not in row:
                row[key] = "N/A"
    
    df = pd.DataFrame(rows, columns=base_columns)
    
    # Create Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='All Students Grades', index=False)
    
    # Prepare response
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="all_students_grades.xlsx"'
    
    return response


# ---------------------------------------------------------------------------
# Weekly progress sheets
# ---------------------------------------------------------------------------

def _can_manage_weekly(user, project):
    """Admins, and the faculty member assigned as this project's supervisor."""
    if not user.is_authenticated:
        return False
    if user.is_admin():
        return True
    if not user.is_faculty():
        return False
    try:
        faculty = user.faculty_profile
    except Exception:
        return False
    return FacultyProjectAssignment.objects.filter(
        project=project,
        faculty=faculty,
        role=FacultyProjectAssignment.Role.SUPERVISOR,
    ).exists()


@login_required
def weekly_progress_list(request, project_id):
    """Every weekly sheet recorded for one project."""
    project = get_object_or_404(Project, id=project_id)

    if not _can_manage_weekly(request.user, project):
        messages.error(request, 'You do not have permission to view progress sheets for this project.')
        return redirect('projects:project_detail', project_id=project.id)

    reports = (
        WeeklyProgress.objects
        .filter(project=project)
        .prefetch_related('attendance__student__user')
        .order_by('-week_number')
    )

    return render(request, 'projects/weekly_progress_list.html', {
        'project': project,
        'reports': reports,
        'team': project.get_team(),
    })


@login_required
def weekly_progress_form(request, project_id, report_id=None):
    """Create or edit one weekly sheet, with an attendance row per team member."""
    project = get_object_or_404(Project, id=project_id)

    if not _can_manage_weekly(request.user, project):
        messages.error(request, 'You do not have permission to record progress for this project.')
        return redirect('projects:project_detail', project_id=project.id)

    report = None
    if report_id is not None:
        report = get_object_or_404(WeeklyProgress, id=report_id, project=project)

    team = project.get_team()
    students = list(team.members) if team else []

    if not students:
        messages.warning(request, 'This project has no team members yet, so there is nobody to mark attendance for.')

    if request.method == 'POST':
        form = WeeklyProgressForm(request.POST, instance=report, project=project)
        if form.is_valid():
            report = form.save(commit=False)
            report.project = project
            if report.supervisor is None and request.user.is_faculty():
                try:
                    report.supervisor = request.user.faculty_profile
                except Exception:
                    pass
            report.save()

            valid_statuses = {choice[0] for choice in WeeklyAttendance.Status.choices}
            for student in students:
                status = request.POST.get(f'attendance_{student.id}', WeeklyAttendance.Status.PRESENT)
                if status not in valid_statuses:
                    status = WeeklyAttendance.Status.PRESENT
                WeeklyAttendance.objects.update_or_create(
                    report=report, student=student, defaults={'status': status},
                )

            messages.success(request, f'Week {report.week_number} progress sheet saved.')
            return redirect('projects:weekly_progress_list', project_id=project.id)
    else:
        initial = {}
        if report is None:
            last = WeeklyProgress.objects.filter(project=project).order_by('-week_number').first()
            initial['week_number'] = (last.week_number + 1) if last else 1
            initial['meeting_date'] = timezone.localdate()
        form = WeeklyProgressForm(instance=report, initial=initial, project=project)

    # Existing marks, so editing a sheet shows what was recorded before.
    existing = {}
    if report is not None:
        existing = {a.student_id: a.status for a in report.attendance.all()}

    rows = [
        {'student': s, 'status': existing.get(s.id, WeeklyAttendance.Status.PRESENT)}
        for s in students
    ]

    return render(request, 'projects/weekly_progress_form.html', {
        'project': project,
        'form': form,
        'report': report,
        'rows': rows,
        'status_choices': WeeklyAttendance.Status.choices,
    })
