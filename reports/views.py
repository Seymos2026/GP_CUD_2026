from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from projects.models import Project
from evaluations.utils import get_project_evaluation_summary


@login_required
def project_report(request, project_id):
    """Generate project evaluation report"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check permissions
    user = request.user
    if not user.is_admin():
        if user.is_student_user():
            try:
                student = user.student_profile
                if not student.team or student.team.project != project:
                    return HttpResponse("Unauthorized", status=403)
            except:
                return HttpResponse("Unauthorized", status=403)
    
    evaluation_summary = get_project_evaluation_summary(project)
    
    # Add weighted scores to judge evaluations for template
    for je in evaluation_summary['judge_evaluations']:
        for score in je['scores']:
            score.weighted_score = float(score.score) * float(score.criterion.weight)
    
    return render(request, 'reports/project_report.html', {
        'project': project,
        'evaluation_summary': evaluation_summary
    })


@login_required
def export_excel(request, project_id):
    """Export project evaluation report to Excel with detailed per-student marks"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check permissions
    user = request.user
    if not user.is_admin():
        return HttpResponse("Unauthorized", status=403)
    
    evaluation_summary = get_project_evaluation_summary(project)
    
    # Create Excel writer
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = {
            'Metric': ['Total Score', 'Max Total Score', 'Percentage', 'Number of Evaluations', 'Draft Evaluations'],
            'Value': [
                float(evaluation_summary['total_score']),
                float(evaluation_summary['max_total_score']),
                f"{float(evaluation_summary['percentage']):.2f}%",
                evaluation_summary['evaluation_count'],
                evaluation_summary['draft_count']
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Student Evaluation Results (Average Scores Across All Judges) - Detailed per student
        if evaluation_summary.get('student_averages'):
            for student_data in evaluation_summary['student_averages']:
                student_name = student_data['student'].user.get_full_name() or student_data['student'].user.username
                student_id = student_data['student'].student_id
                sheet_name = f"Student_{student_id}"[:31]  # Excel sheet name limit
                
                # Student summary row
                student_summary = [{
                    'Field': 'Student Name',
                    'Value': student_name
                }, {
                    'Field': 'Student ID',
                    'Value': student_id
                }, {
                    'Field': 'Total Average Score',
                    'Value': f"{float(student_data['total_average']):.2f} / {float(evaluation_summary['max_total_score']):.2f}"
                }]
                df_student_summary = pd.DataFrame(student_summary)
                df_student_summary.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)
                
                # Student criterion scores
                if student_data['criterion_scores']:
                    criterion_data = []
                    for cs in student_data['criterion_scores']:
                        criterion_data.append({
                            'Criterion': cs['criterion'].name,
                            'Average Score': float(cs['average']),
                            'Max Score': float(cs['max_score']),
                            'Weight': float(cs['weight']),
                            'Weighted Average': float(cs['weighted_average']),
                            'Judges Count': cs['judge_count']
                        })
                    df_student_criteria = pd.DataFrame(criterion_data)
                    df_student_criteria.to_excel(writer, sheet_name=sheet_name, index=False, startrow=4)
        
        # Individual Judge Evaluations - Per Student Detailed Scores
        if evaluation_summary.get('student_averages') and evaluation_summary['judge_evaluations']:
            from evaluations.models import Score
            for student_data in evaluation_summary['student_averages']:
                student_name = student_data['student'].user.get_full_name() or student_data['student'].user.username
                student_id = student_data['student'].student_id
                
                # Get detailed scores from each judge for this student
                detailed_scores = []
                for je in evaluation_summary['judge_evaluations']:
                    # Use 'faculty' key if available, otherwise 'judge' for backward compatibility
                    faculty_obj = je.get('faculty') or je.get('judge')
                    if not faculty_obj:
                        continue
                    judge_name = faculty_obj.user.get_full_name() or faculty_obj.user.username
                    evaluation = je['evaluation']
                    # Get scores for this specific student from this evaluation
                    student_scores = Score.objects.filter(
                        evaluation=evaluation,
                        student=student_data['student']
                    )
                    for score in student_scores:
                        detailed_scores.append({
                            'Judge': judge_name,
                            'Faculty ID': faculty_obj.faculty_id or 'N/A',
                            'Criterion': score.criterion.name,
                            'Score': float(score.score) if score.score else 0.0,
                            'Max Score': float(score.criterion.max_score),
                            'Weight': float(score.criterion.weight),
                            'Weighted Score': float(score.score * score.criterion.weight) if score.score else 0.0,
                            'Comments': score.comments or ''
                        })
                
                if detailed_scores:
                    sheet_name = f"JudgeScores_{student_id}"[:31]
                    df_detailed = pd.DataFrame(detailed_scores)
                    df_detailed.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Judge Evaluations Summary
        judge_data = []
        for je in evaluation_summary['judge_evaluations']:
            # Use 'faculty' key if available, otherwise 'judge' for backward compatibility
            faculty_obj = je.get('faculty') or je.get('judge')
            if faculty_obj:
                judge_data.append({
                    'Judge': faculty_obj.user.get_full_name() or faculty_obj.user.username,
                    'Faculty ID': faculty_obj.faculty_id or 'N/A',
                    'Total Score': float(je['total_score']),
                    'Status': je['evaluation'].get_status_display(),
                    'Submitted At': je['evaluation'].submitted_at.strftime('%Y-%m-%d %H:%M') if je['evaluation'].submitted_at else 'N/A',
                    'General Comments': je['comments'] or ''
                })
        if judge_data:
            df_judges = pd.DataFrame(judge_data)
            df_judges.to_excel(writer, sheet_name='Judge Evaluations', index=False)
    
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="project_{project_id}_evaluation.xlsx"'
    return response


@login_required
def export_pdf(request, project_id):
    """Export project evaluation report to PDF - Summary only with student final scores and judge signatures"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check permissions
    user = request.user
    if not user.is_admin():
        return HttpResponse("Unauthorized", status=403)
    
    evaluation_summary = get_project_evaluation_summary(project)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"<b>Project Evaluation Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Paragraph(f"<b>Project:</b> {project.title}", styles['Heading2']))
    if project.supervisor:
        elements.append(Paragraph(f"<b>Supervisor:</b> {project.supervisor.get_full_name() or project.supervisor.username}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Summary Section
    elements.append(Paragraph("<b>Summary</b>", styles['Heading2']))
    summary_data = [
        ['Total Score', f"{evaluation_summary['total_score']:.2f} / {evaluation_summary['max_total_score']:.2f}"],
        ['Percentage', f"{evaluation_summary['percentage']:.2f}%"],
        ['Number of Evaluations', str(evaluation_summary['evaluation_count'])],
        ['Draft Evaluations', str(evaluation_summary['draft_count'])]
    ]
    summary_table = Table(summary_data, colWidths=[200, 200])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Students Table with Final Scores
    if evaluation_summary.get('student_averages'):
        elements.append(Paragraph("<b>Student Final Scores</b>", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Create students table
        students_data = [['Student Name', 'Student ID', 'Final Score', 'Percentage']]
        for student_data in evaluation_summary['student_averages']:
            student_name = student_data['student'].user.get_full_name() or student_data['student'].user.username
            student_id = student_data['student'].student_id
            final_score = float(student_data['total_average'])
            max_score = float(evaluation_summary['max_total_score'])
            percentage = (final_score / max_score * 100) if max_score > 0 else 0.0
            
            students_data.append([
                student_name,
                student_id,
                f"{final_score:.2f} / {max_score:.2f}",
                f"{percentage:.2f}%"
            ])
        
        students_table = Table(students_data, colWidths=[150, 120, 120, 100])
        students_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (3, -1), 'CENTER'),  # Center align scores and percentages
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        elements.append(students_table)
        elements.append(Spacer(1, 20))
    
    # Judge Signatures Section
    if evaluation_summary['judge_evaluations']:
        elements.append(Paragraph("<b>Judge Signatures</b>", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Create signature boxes in two columns
        signature_data = []
        for idx, je in enumerate(evaluation_summary['judge_evaluations'], 1):
            # Use 'faculty' key if available, otherwise 'judge' for backward compatibility
            faculty_obj = je.get('faculty') or je.get('judge')
            if not faculty_obj:
                continue
            judge_name = faculty_obj.user.get_full_name() or faculty_obj.user.username
            judge_id = faculty_obj.faculty_id or 'N/A'
            
            # Create signature box with border
            signature_info = f"<b>Judge {idx}:</b> {judge_name}"
            if judge_id != 'N/A':
                signature_info += f"<br/><b>Faculty ID:</b> {judge_id}"
            signature_info += "<br/><br/><i>Signature Line (Please sign manually)</i>"
            
            signature_cell = [Paragraph(signature_info, styles['Normal'])]
            signature_data.append(signature_cell)
        
        if signature_data:
            # Arrange in two columns
            rows = []
            for i in range(0, len(signature_data), 2):
                row = []
                row.append(signature_data[i][0] if i < len(signature_data) else "")
                row.append(signature_data[i+1][0] if i+1 < len(signature_data) else "")
                rows.append(row)
            
            signature_table = Table(rows, colWidths=[250, 250])
            signature_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 50),
                ('LINEBELOW', (0, 0), (-1, -1), 2, colors.black),
                ('LINEABOVE', (0, 0), (-1, -1), 1, colors.grey),
                ('LINEAFTER', (0, 0), (0, -1), 1, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(signature_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="project_{project_id}_evaluation.pdf"'
    return response
