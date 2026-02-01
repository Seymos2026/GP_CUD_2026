"""
Utility functions for score calculations and evaluation processing
"""
from decimal import Decimal
from django.db.models import Avg, Sum
from .models import Evaluation, Score


def calculate_criterion_average(project, criterion):
    """
    Calculate average score for a criterion across all submitted evaluations for a project.
    
    Args:
        project: Project instance
        criterion: Criterion instance
    
    Returns:
        dict with 'average', 'count', 'scores', 'judge_count' keys
    """
    evaluations = project.evaluations.filter(status=Evaluation.Status.SUBMITTED)
    scores = Score.objects.filter(
        evaluation__in=evaluations,
        criterion=criterion
    ).values_list('score', flat=True)
    
    # Count unique judges (evaluations) that have scores for this criterion
    judge_count = Score.objects.filter(
        evaluation__in=evaluations,
        criterion=criterion
    ).values('evaluation').distinct().count()
    
    if not scores:
        return {
            'average': Decimal('0.00'),
            'count': 0,
            'scores': [],
            'judge_count': judge_count
        }
    
    scores_list = list(scores)
    average = sum(scores_list) / len(scores_list)
    
    return {
        'average': Decimal(str(average)),
        'count': len(scores_list),
        'scores': scores_list,
        'judge_count': judge_count
    }


def calculate_weighted_score(avg_score, weight):
    """
    Calculate weighted score from average and weight.
    
    Args:
        avg_score: Decimal average score
        weight: Decimal weight value
    
    Returns:
        Decimal weighted score
    """
    return avg_score * weight


def calculate_project_total_score(project):
    """
    Calculate total weighted score for a project across all criteria.
    
    Args:
        project: Project instance
    
    Returns:
        dict with 'total_score', 'max_total_score', 'percentage', 'criterion_scores'
    """
    rubric = project.rubric
    if not rubric:
        return {
            'total_score': Decimal('0.00'),
            'max_total_score': Decimal('0.00'),
            'percentage': Decimal('0.00'),
            'criterion_scores': []
        }
    
    criterion_scores = []
    total_score = Decimal('0.00')
    max_total_score = Decimal('0.00')
    
    for criterion in rubric.criteria.all():
        criterion_avg = calculate_criterion_average(project, criterion)
        weighted_score = calculate_weighted_score(criterion_avg['average'], criterion.weight)
        
        criterion_max_weighted = criterion.max_score * criterion.weight
        
        criterion_scores.append({
            'criterion': criterion,
            'average': criterion_avg['average'],
            'weight': criterion.weight,
            'weighted_score': weighted_score,
            'max_score': criterion.max_score,
            'max_weighted': criterion_max_weighted,
            'judge_count': criterion_avg.get('judge_count', criterion_avg.get('count', 0))
        })
        
        total_score += weighted_score
        max_total_score += criterion_max_weighted
    
    # Use rubric max_total_score if set, otherwise calculate from criteria
    rubric_max = rubric.max_total_score if rubric.max_total_score else max_total_score
    percentage = (total_score / rubric_max * 100) if rubric_max > 0 else Decimal('0.00')
    
    return {
        'total_score': total_score,
        'max_total_score': rubric_max,
        'percentage': percentage,
        'criterion_scores': criterion_scores
    }


def get_project_evaluation_summary(project):
    """
    Get comprehensive evaluation summary for a project with per-student averages.
    
    Args:
        project: Project instance
    
    Returns:
        dict with evaluation statistics and details including per-student averages
    """
    from accounts.models import Student
    
    evaluations = project.evaluations.filter(status=Evaluation.Status.SUBMITTED)
    project_scores = calculate_project_total_score(project)
    
    # Get individual faculty (judge) scores
    judge_evaluations = []
    for evaluation in evaluations:
        if evaluation.faculty:  # Only include evaluations with faculty assigned
            # Calculate total score for this evaluation if not set
            # Since we're scoring per-student, calculate average across all students
            total_score = evaluation.total_score
            if total_score is None:
                # Calculate total from all scores for this evaluation
                total_score = Decimal('0.00')
                for score in evaluation.scores.all():
                    weighted = Decimal(str(score.score)) * Decimal(str(score.criterion.weight))
                    total_score += weighted
                # Average across students if multiple students
                student_ids = evaluation.scores.values('student').distinct().count()
                if student_ids > 0:
                    # Get unique students and calculate per-student totals, then average
                    from collections import defaultdict
                    student_totals = defaultdict(Decimal)
                    for score in evaluation.scores.all():
                        if score.student:
                            weighted = Decimal(str(score.score)) * Decimal(str(score.criterion.weight))
                            student_totals[score.student.id] += weighted
                    if student_totals:
                        total_score = sum(student_totals.values()) / len(student_totals)
                        # Round to 2 decimal places
                        from decimal import ROUND_HALF_UP
                        total_score = total_score.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            judge_evaluations.append({
                'judge': evaluation.faculty,  # Keep 'judge' key for template compatibility
                'faculty': evaluation.faculty,  # Add 'faculty' key
                'evaluation': evaluation,
                'total_score': total_score,
                'scores': evaluation.scores.all(),
                'comments': evaluation.comments,
                'signature': evaluation.judge_signature or evaluation.faculty.user.get_full_name() or evaluation.faculty.user.username
            })
    
    # Calculate per-student averages across all judges
    # Use getattr to safely access team property
    team = getattr(project, 'team', None)
    student_averages = []
    if team:
        rubric = project.rubric
        if rubric:
            for student in team.students.all():
                student_data = {
                    'student': student,
                    'criterion_scores': [],
                    'total_average': Decimal('0.00'),
                    'judge_scores': {}  # Individual scores from each judge
                }
                
                # Get scores from each faculty (judge) for this student
                for evaluation in evaluations:
                    if not evaluation.faculty:  # Skip if no faculty assigned
                        continue
                    judge_scores = []
                    for criterion in rubric.criteria.all():
                        score = Score.objects.filter(
                            evaluation=evaluation,
                            criterion=criterion,
                            student=student
                        ).first()
                        if score:
                            judge_scores.append({
                                'criterion': criterion,
                                'score': score.score,
                                'weighted': float(score.score) * float(criterion.weight),
                                'comments': score.comments
                            })
                    student_data['judge_scores'][evaluation.faculty.id] = {
                        'judge': evaluation.faculty,  # Keep 'judge' key for template compatibility
                        'faculty': evaluation.faculty,  # Add 'faculty' key
                        'scores': judge_scores,
                        'total': sum(s['weighted'] for s in judge_scores)
                    }
                
                # Calculate averages per criterion
                for criterion in rubric.criteria.all():
                    scores = Score.objects.filter(
                        evaluation__in=evaluations,
                        criterion=criterion,
                        student=student
                    ).values_list('score', flat=True)
                    
                    if scores:
                        avg_score = sum(scores) / len(scores)
                        weighted_avg = avg_score * criterion.weight
                        student_data['criterion_scores'].append({
                            'criterion': criterion,
                            'average': Decimal(str(avg_score)),
                            'weighted_average': Decimal(str(weighted_avg)),
                            'max_score': criterion.max_score,
                            'weight': criterion.weight,
                            'judge_count': len(scores)
                        })
                        student_data['total_average'] += Decimal(str(weighted_avg))
                
                student_averages.append(student_data)
    
    return {
        'project': project,
        'total_score': project_scores['total_score'],
        'max_total_score': project_scores['max_total_score'],
        'percentage': project_scores['percentage'],
        'criterion_scores': project_scores['criterion_scores'],
        'judge_evaluations': judge_evaluations,
        'student_averages': student_averages,
        'evaluation_count': evaluations.count(),
        'draft_count': project.evaluations.filter(status=Evaluation.Status.DRAFT).count()
    }
