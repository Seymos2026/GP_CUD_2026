from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from .models import Evaluation, Score
from .utils import calculate_project_total_score, get_project_evaluation_summary
from projects.models import Project


@login_required
def evaluation_list(request):
    """List all evaluations for the current user"""
    user = request.user
    
    if user.is_admin():
        # Admins see all evaluations
        evaluations = Evaluation.objects.all()
    elif user.is_faculty():
        # Faculty see their own evaluations
        try:
            faculty = user.faculty_profile
            evaluations = Evaluation.objects.filter(faculty=faculty)
        except:
            evaluations = Evaluation.objects.none()
    else:
        # Students don't have evaluations
        evaluations = Evaluation.objects.none()
    
    return render(request, 'evaluations/evaluation_list.html', {
        'evaluations': evaluations,
        'user_role': user.role
    })


@login_required
def evaluation_create(request, project_id):
    """Create or edit an evaluation for a project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user is faculty
    if not request.user.is_faculty():
        messages.error(request, 'Only faculty members can create evaluations.')
        return redirect('projects:project_list')
    
    try:
        faculty = request.user.faculty_profile
    except:
        messages.error(request, 'You need a faculty profile to create evaluations.')
        return redirect('projects:project_list')
    
    # Check if faculty is assigned as Judge for this project
    from projects.models import FacultyProjectAssignment
    assignment = FacultyProjectAssignment.objects.filter(
        project=project,
        faculty=faculty
    ).first()
    
    if not assignment:
        messages.error(request, 'You are not assigned to this project.')
        return redirect('projects:project_detail', project_id=project.id)
    
    if assignment.role != FacultyProjectAssignment.Role.JUDGE:
        messages.error(request, f'You are assigned as {assignment.get_role_display()} for this project. Only faculty assigned as Judge can create evaluations.')
        return redirect('projects:project_detail', project_id=project.id)
    
    rubric = project.rubric
    
    if not rubric:
        messages.error(request, 'This project does not have a rubric assigned.')
        return redirect('projects:project_list')
    
    # Get or create evaluation
    evaluation, created = Evaluation.objects.get_or_create(
        project=project,
        faculty=faculty,
        defaults={'status': Evaluation.Status.DRAFT}
    )
    
    # Get team members
    team = getattr(project, 'team', None)
    students = []
    if team:
        students = team.students.all()
    
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        
        # Get all scores from form (per student per criterion)
        with transaction.atomic():
            for criterion in rubric.criteria.all():
                for student in students:
                    score_key = f'score_{criterion.id}_{student.id}'
                    comments_key = f'comments_{criterion.id}_{student.id}'
                    
                    score_value = request.POST.get(score_key)
                    comments_value = request.POST.get(comments_key, '')
                    
                    if score_value:
                        try:
                            score_float = float(score_value)
                            if score_float < 0:
                                messages.error(request, f'Score for {criterion.name} - {student.user.get_full_name() or student.user.username} cannot be negative.')
                                return redirect('evaluations:evaluation_create', project_id=project_id)
                            if score_float > criterion.max_score:
                                messages.error(request, f'Score for {criterion.name} - {student.user.get_full_name() or student.user.username} cannot exceed {criterion.max_score}.')
                                return redirect('evaluations:evaluation_create', project_id=project_id)
                            
                            # Get or create score for this student
                            score_obj, created = Score.objects.get_or_create(
                                evaluation=evaluation,
                                criterion=criterion,
                                student=student,
                                defaults={'score': score_float, 'comments': comments_value}
                            )
                            if not created:
                                # Update existing score
                                score_obj.score = score_float
                                score_obj.comments = comments_value
                            score_obj.save()
                        except ValueError:
                            messages.error(request, f'Invalid score format for {criterion.name} - {student.user.get_full_name() or student.user.username}.')
                            return redirect('evaluations:evaluation_create', project_id=project_id)
            
            # Update general comments and signature
            evaluation.comments = request.POST.get('general_comments', '')
            evaluation.judge_signature = request.POST.get('judge_signature', '') or evaluation.faculty.user.get_full_name() or evaluation.faculty.user.username
            
            # Update status
            if action == 'submit':
                evaluation.status = Evaluation.Status.SUBMITTED
                from django.utils import timezone
                evaluation.submitted_at = timezone.now()
                messages.success(request, 'Evaluation submitted successfully.')
            else:
                messages.success(request, 'Evaluation saved as draft.')
            
            # Ensure total_score is None or properly rounded to 2 decimal places
            # Since we're not calculating it per-student, set it to None
            evaluation.total_score = None
            
            evaluation.save()
            # Don't calculate team-level total_score - it's misleading when scoring per student
            # evaluation.calculate_total_score()  # This averages across students, which is wrong for per-student scoring
            
            return redirect('evaluations:evaluation_detail', evaluation_id=evaluation.id)
    
    # Get existing scores organized by student and criterion
    criteria_with_scores = evaluation.get_all_criteria_scores()
    
    # Organize scores by student for template
    student_scores_list = []
    for student in students:
        student_data = {
            'student': student,
            'scores': {}
        }
        for criterion in rubric.criteria.all():
            score = Score.objects.filter(evaluation=evaluation, criterion=criterion, student=student).first()
            student_data['scores'][criterion.id] = score
        student_scores_list.append(student_data)
    
    # Group criteria by section_title for better organization
    from collections import defaultdict
    from decimal import Decimal
    
    criteria_by_section = defaultdict(list)
    for criterion in rubric.criteria.all():
        section = criterion.section_title or "Other"
        criteria_by_section[section].append(criterion)
    
    # Calculate section totals (max possible scores per section)
    sections_data = []
    for section_title, section_criteria in criteria_by_section.items():
        # Calculate max total for this section (sum of max_score * weight for all criteria)
        section_max_total = Decimal('0.00')
        for c in section_criteria:
            section_max_total += Decimal(str(c.max_score)) * Decimal(str(c.weight))
        
        # Get the minimum order from criteria in this section for sorting
        min_order = min(c.order for c in section_criteria) if section_criteria else 0
        
        sections_data.append({
            'title': section_title,
            'criteria': section_criteria,
            'max_total': section_max_total,
            'order': min_order
        })
    
    # Sort sections by order
    sections_data.sort(key=lambda x: x['order'])
    
    return render(request, 'evaluations/evaluation_form.html', {
        'project': project,
        'evaluation': evaluation,
        'rubric': rubric,
        'criteria_with_scores': criteria_with_scores,
        'students': students,
        'student_scores_list': student_scores_list,
        'sections_data': sections_data
    })


@login_required
def evaluation_detail(request, evaluation_id):
    """View evaluation details"""
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    
    # Check permissions
    user = request.user
    if not user.is_admin():
        if user.is_faculty():
            try:
                faculty = user.faculty_profile
                if evaluation.faculty != faculty:
                    messages.error(request, 'You do not have permission to view this evaluation.')
                    return redirect('evaluations:evaluation_list')
            except:
                messages.error(request, 'You do not have permission to view this evaluation.')
                return redirect('evaluations:evaluation_list')
        else:
            messages.error(request, 'You do not have permission to view this evaluation.')
            return redirect('evaluations:evaluation_list')
    
    # Get team and students
    team = getattr(evaluation.project, 'team', None)
    students = team.students.all() if team else []
    
    # Organize scores by student
    student_scores_data = []
    rubric = evaluation.project.rubric
    if rubric:
        for student in students:
            student_data = {
                'student': student,
                'scores': [],
                'total_score': 0
            }
            for criterion in rubric.criteria.all():
                score = Score.objects.filter(
                    evaluation=evaluation,
                    criterion=criterion,
                    student=student
                ).first()
                if score:
                    weighted = float(score.score) * float(criterion.weight)
                    student_data['total_score'] += weighted
                    student_data['scores'].append({
                        'criterion': criterion,
                        'score': score,
                        'weighted_score': weighted
                    })
                else:
                    student_data['scores'].append({
                        'criterion': criterion,
                        'score': None,
                        'weighted_score': 0
                    })
            student_scores_data.append(student_data)
    
    return render(request, 'evaluations/evaluation_detail.html', {
        'evaluation': evaluation,
        'students': students,
        'student_scores_data': student_scores_data,
        'rubric': rubric
    })
