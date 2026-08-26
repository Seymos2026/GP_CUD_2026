from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import User
from .forms import EmailAuthenticationForm


def home(request):
    """Home page - redirect based on user role"""
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect('projects:project_list')  # Show projects list instead of admin panel
        elif request.user.is_faculty():
            return redirect('projects:project_list')
        elif request.user.is_student_user():
            return redirect('projects:project_list')
    return render(request, 'accounts/home.html')


@login_required
def dashboard(request):
    """Admin dashboard with statistics"""
    from projects.models import Project, Team, FacultyProjectAssignment
    from accounts.models import Student, Faculty
    from rubrics.models import Rubric
    from evaluations.models import Evaluation
    
    user = request.user
    context = {}
    
    if user.is_admin():
        # Get status filter from query params
        status_filter = request.GET.get('status', None)
        
        # Get all projects with judge status information
        projects_data = []
        all_projects = Project.objects.all().order_by('-created_at')
        
        # Apply status filter if provided
        if status_filter:
            all_projects = all_projects.filter(status=status_filter)
        
        for project in all_projects:
            # Get all judges assigned to this project
            judge_assignments = FacultyProjectAssignment.objects.filter(
                project=project,
                role=FacultyProjectAssignment.Role.JUDGE
            )
            
            judges_status = []
            for assignment in judge_assignments:
                # Check if evaluation exists and its status
                evaluation = Evaluation.objects.filter(
                    project=project,
                    faculty=assignment.faculty
                ).first()
                
                if evaluation:
                    status = evaluation.status
                    submitted_at = evaluation.submitted_at
                else:
                    status = 'PENDING'
                    submitted_at = None
                
                # Check if reminder was sent (from session)
                reminder_key = f'reminder_sent_{project.id}_{assignment.faculty.id}'
                reminder_sent_str = request.session.get('reminder_sent', {}).get(reminder_key)
                reminder_sent = None
                if reminder_sent_str:
                    try:
                        from django.utils.dateparse import parse_datetime
                        reminder_sent = parse_datetime(reminder_sent_str)
                    except:
                        reminder_sent = None
                
                judges_status.append({
                    'faculty': assignment.faculty,
                    'assignment': assignment,
                    'status': status,
                    'submitted_at': submitted_at,
                    'evaluation': evaluation,
                    'reminder_sent': reminder_sent,
                })
            
            submitted_count = sum(1 for j in judges_status if j['status'] == 'SUBMITTED')
            total_judges = len(judges_status)
            
            # Auto-update project status: if all judges submitted, mark as Completed
            if total_judges > 0 and submitted_count == total_judges:
                if project.status != Project.Status.COMPLETED:
                    project.status = Project.Status.COMPLETED
                    project.save(update_fields=['status'])
            elif project.status == Project.Status.COMPLETED and submitted_count < total_judges:
                # If status was Completed but now has pending judges, change back to Evaluating
                project.status = Project.Status.EVALUATING
                project.save(update_fields=['status'])
            
            projects_data.append({
                'project': project,
                'judges': judges_status,
                'total_judges': total_judges,
                'submitted_count': submitted_count,
                'pending_count': sum(1 for j in judges_status if j['status'] == 'PENDING' or j['status'] == 'DRAFT'),
            })
        
        context = {
            'total_projects': Project.objects.count(),
            'total_teams': Team.objects.count(),
            'total_students': Student.objects.count(),
            'total_judges': Faculty.objects.count(),
            'total_rubrics': Rubric.objects.count(),
            'total_evaluations': Evaluation.objects.count(),
            'submitted_evaluations': Evaluation.objects.filter(status=Evaluation.Status.SUBMITTED).count(),
            'recent_projects': Project.objects.all()[:5],
            'projects_data': projects_data,
            'status_filter': status_filter,
            'status_choices': Project.Status.choices,
        }
        return render(request, 'accounts/dashboard.html', context)
    else:
        return redirect('projects:project_list')


@login_required
def profile(request):
    """User profile page"""
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def send_reminder(request, project_id, faculty_id):
    """Open email client with pre-filled reminder email"""
    from projects.models import Project, FacultyProjectAssignment
    from accounts.models import Faculty
    from urllib.parse import quote
    from django.utils import timezone
    
    if not request.user.is_admin():
        messages.error(request, 'Only admins can send reminders.')
        return redirect('accounts:dashboard')
    
    project = get_object_or_404(Project, id=project_id)
    faculty = get_object_or_404(Faculty, id=faculty_id)
    
    # Verify the faculty is assigned as judge for this project
    assignment = FacultyProjectAssignment.objects.filter(
        project=project,
        faculty=faculty,
        role=FacultyProjectAssignment.Role.JUDGE
    ).first()
    
    if not assignment:
        messages.error(request, 'This faculty member is not assigned as a judge for this project.')
        return redirect('accounts:dashboard')
    
    recipient_email = faculty.user.email
    
    if not recipient_email:
        messages.error(request, 'The judge does not have an email address.')
        return redirect('accounts:dashboard')
    
    # Track reminder sent in session
    reminder_key = f'reminder_sent_{project_id}_{faculty_id}'
    if 'reminder_sent' not in request.session:
        request.session['reminder_sent'] = {}
    
    # Mark as sent when link is clicked
    if request.GET.get('sent') == '1':
        request.session['reminder_sent'][reminder_key] = timezone.now().isoformat()
        request.session.modified = True
        messages.success(request, f'Reminder email opened for {faculty.user.get_full_name() or faculty.user.username}.')
        return redirect('accounts:dashboard')
    
    # Get faculty name with "Dr." prefix
    faculty_name = faculty.user.get_full_name() or faculty.user.username
    if not faculty_name.startswith('Dr.') and not faculty_name.startswith('Dr '):
        faculty_name = f'Dr. {faculty_name}'
    
    # Create email template
    default_subject = f'Reminder: Evaluation Pending for {project.title}'
    default_message = f"""Dear {faculty_name},

This is a reminder that you have a pending evaluation for the project:

Project: {project.title}
Status: Pending

Please complete your evaluation at your earliest convenience.

Thank you,
GP Coordinator"""
    
    # Create mailto link with tracking parameter
    mailto_subject = quote(default_subject)
    mailto_body = quote(default_message)
    # Add tracking to know when email was opened
    tracking_url = request.build_absolute_uri(f'{request.path}?sent=1')
    mailto_link = f"mailto:{recipient_email}?subject={mailto_subject}&body={mailto_body}"
    
    # Check if reminder was already sent
    reminder_sent_str = request.session.get('reminder_sent', {}).get(reminder_key)
    reminder_sent = None
    if reminder_sent_str:
        try:
            from django.utils.dateparse import parse_datetime
            reminder_sent = parse_datetime(reminder_sent_str)
        except:
            reminder_sent = None
    
    context = {
        'project': project,
        'faculty': faculty,
        'assignment': assignment,
        'recipient_email': recipient_email,
        'mailto_link': mailto_link,
        'tracking_url': tracking_url,
        'default_subject': default_subject,
        'default_message': default_message,
        'reminder_sent': reminder_sent,
    }
    
    return render(request, 'accounts/send_reminder.html', context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Custom login view that accepts email"""
    if request.user.is_authenticated:
        return redirect('accounts:home')
    
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # 'username' field contains email
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                # Redirect based on user role
                if user.is_admin():
                    return redirect('projects:project_list')
                elif user.is_faculty():
                    return redirect('projects:project_list')
                elif user.is_student_user():
                    return redirect('projects:project_list')
                return redirect('accounts:home')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmailAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})
