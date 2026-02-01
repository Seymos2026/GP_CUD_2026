from django.shortcuts import render, redirect
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
    from projects.models import Project, Team
    from accounts.models import Student, Faculty
    from rubrics.models import Rubric
    from evaluations.models import Evaluation
    
    user = request.user
    context = {}
    
    if user.is_admin():
        context = {
            'total_projects': Project.objects.count(),
            'total_teams': Team.objects.count(),
            'total_students': Student.objects.count(),
            'total_judges': Faculty.objects.count(),  # Keep 'total_judges' for template compatibility
            'total_rubrics': Rubric.objects.count(),
            'total_evaluations': Evaluation.objects.count(),
            'submitted_evaluations': Evaluation.objects.filter(status=Evaluation.Status.SUBMITTED).count(),
            'recent_projects': Project.objects.all()[:5],
        }
        return render(request, 'accounts/dashboard.html', context)
    else:
        return redirect('projects:project_list')


@login_required
def profile(request):
    """User profile page"""
    return render(request, 'accounts/profile.html', {'user': request.user})


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
