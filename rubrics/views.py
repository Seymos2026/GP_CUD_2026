from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
from .models import Rubric, Criterion


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_admin() or user.is_staff)


@login_required
@user_passes_test(is_admin)
def rubric_list(request):
    """List all rubrics"""
    rubrics = Rubric.objects.all()
    return render(request, 'rubrics/rubric_list.html', {'rubrics': rubrics})


@login_required
@user_passes_test(is_admin)
def rubric_detail(request, rubric_id):
    """View rubric details with sections grouped"""
    from decimal import Decimal
    
    rubric = get_object_or_404(Rubric, id=rubric_id)
    criteria = rubric.criteria.all().order_by('order')
    
    # Group criteria by section_title and calculate totals
    sections = {}
    for criterion in criteria:
        section_title = criterion.section_title or 'Other'
        if section_title not in sections:
            sections[section_title] = {
                'title': section_title,
                'criteria': [],
                'total': Decimal('0.00')
            }
        sections[section_title]['criteria'].append(criterion)
        sections[section_title]['total'] += criterion.max_score * criterion.weight
    
    # Convert to list for template
    section_list = [sections[key] for key in sorted(sections.keys())]
    
    return render(request, 'rubrics/rubric_detail.html', {
        'rubric': rubric,
        'criteria': criteria,
        'sections': section_list
    })


@login_required
@user_passes_test(is_admin)
def rubric_import(request):
    """Import rubric from Excel file"""
    if request.method == 'POST':
        if 'excel_file' not in request.FILES:
            messages.error(request, 'Please select an Excel file.')
            return render(request, 'rubrics/rubric_import.html')
        
        excel_file = request.FILES['excel_file']
        rubric_name = request.POST.get('rubric_name', '')
        
        if not rubric_name:
            messages.error(request, 'Please provide a rubric name.')
            return render(request, 'rubrics/rubric_import.html')
        
        try:
            # Read Excel file
            df = pd.read_excel(excel_file)
            
            # Expected columns: Criterion Name, Description (optional), Weight (optional), Max Score
            # Make column names case-insensitive
            df.columns = df.columns.str.strip().str.lower()
            
            # Validate required columns
            required_columns = ['criteria no', 'evaluation criteria', 'max score', 'section title']
            if not all(col in df.columns for col in required_columns):
                messages.error(
                    request, 
                    f'Excel file must contain columns: {", ".join(required_columns)}. '
                    f'Optional columns: Weight (defaults to 1.0). Found columns: {", ".join(df.columns)}'
                )
                return render(request, 'rubrics/rubric_import.html')
            
            # Validate section totals and overall total
            from decimal import Decimal
            import re
            
            # Group by section and calculate totals
            section_totals = {}
            overall_total = Decimal('0.00')
            
            for idx, row in df.iterrows():
                section_title = str(row['section title']).strip()
                max_score = Decimal(str(row['max score']))
                weight = Decimal(str(row.get('weight', 1.0))) if 'weight' in df.columns else Decimal('1.0')
                
                weighted_score = max_score * weight
                
                if section_title not in section_totals:
                    section_totals[section_title] = Decimal('0.00')
                
                section_totals[section_title] += weighted_score
                overall_total += weighted_score
            
            # Check section totals match expected values from section titles
            section_errors = []
            for section_title, calculated_total in section_totals.items():
                # Extract expected total from section title (e.g., "1. Midterm Presentation - 10.0 points")
                match = re.search(r'[-–]\s*(\d+\.?\d*)\s*points?', section_title, re.IGNORECASE)
                if match:
                    expected_total = Decimal(match.group(1))
                    # Allow small rounding differences (0.01)
                    if abs(calculated_total - expected_total) > Decimal('0.01'):
                        section_errors.append(
                            f"Section '{section_title}': Expected {expected_total} points, "
                            f"but calculated {calculated_total:.2f} points"
                        )
            
            if section_errors:
                messages.error(
                    request,
                    'Section total mismatch errors:\n' + '\n'.join(section_errors)
                )
                return render(request, 'rubrics/rubric_import.html')
            
            # Check overall total equals 100
            if abs(overall_total - Decimal('100.00')) > Decimal('0.01'):
                messages.error(
                    request,
                    f'Total score mismatch: All sections must total exactly 100.00 points. '
                    f'Calculated total: {overall_total:.2f} points'
                )
                return render(request, 'rubrics/rubric_import.html')
            
            # Create rubric
            rubric = Rubric.objects.create(
                name=rubric_name,
                description=request.POST.get('description', ''),
                created_by=request.user
            )
            
            # Calculate max total score
            max_total = 0
            
            # Create criteria
            for idx, row in df.iterrows():
                criteria_no = str(row['criteria no']).strip()
                evaluation_criteria = str(row['evaluation criteria']).strip()
                max_score = float(row['max score'])
                section_title = str(row['section title']).strip()
                weight = float(row.get('weight', 1.0)) if 'weight' in df.columns else 1.0
                
                Criterion.objects.create(
                    rubric=rubric,
                    name=criteria_no,  # Store criteria number as name
                    description=evaluation_criteria,  # Store evaluation criteria as description
                    weight=weight,
                    max_score=max_score,
                    section_title=section_title,
                    order=idx + 1
                )
                
                max_total += max_score * weight
            
            # Set max_total_score if not provided
            if not rubric.max_total_score:
                rubric.max_total_score = max_total
                rubric.save()
            
            messages.success(request, f'Rubric "{rubric_name}" imported successfully with {len(df)} criteria.')
            return redirect('rubrics:rubric_detail', rubric_id=rubric.id)
            
        except Exception as e:
            messages.error(request, f'Error importing rubric: {str(e)}')
            return render(request, 'rubrics/rubric_import.html')
    
    return render(request, 'rubrics/rubric_import.html')


@login_required
@user_passes_test(is_admin)
def download_rubric_template(request):
    """Download Excel template for rubric import"""
    # Create template DataFrame
    template_data = {
        'Criteria No': ['1.1', '1.2', '1.3', '2.1', '2.2', '2.3'],
        'Section Title': [
            '1. Midterm Presentation - 10.0 points',
            '1. Midterm Presentation - 10.0 points',
            '1. Midterm Presentation - 10.0 points',
            '2. Midterm Report - 20.0 points',
            '2. Midterm Report - 20.0 points',
            '2. Midterm Report - 20.0 points'
        ],
        'Evaluation Criteria': [
            'Participates in the establishment of goals and work plans of the team',
            'Applies software development lifecycles and methodologies',
            'The team demonstrates confidence in the subject matter',
            'Provides supporting details which enhance the quality of the report',
            'Evaluate alternative solutions',
            'A preliminary solution prototype is proposed'
        ],
        'Max Score': [3.33, 3.33, 3.34, 6.67, 6.67, 6.66],
        'Weight': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    }
    
    df = pd.DataFrame(template_data)
    
    # Create Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Rubric Template', index=False)
        
        # Get the workbook and worksheet to format
        workbook = writer.book
        worksheet = writer.sheets['Rubric Template']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    # Prepare response
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="rubric_template.xlsx"'
    
    return response


@login_required
@user_passes_test(is_admin)
def rubric_delete(request, rubric_id):
    """Delete a rubric"""
    rubric = get_object_or_404(Rubric, id=rubric_id)
    
    if request.method == 'POST':
        rubric_name = rubric.name
        rubric.delete()
        messages.success(request, f'Rubric "{rubric_name}" deleted successfully.')
        return redirect('rubrics:rubric_list')
    
    return render(request, 'rubrics/rubric_delete.html', {'rubric': rubric})
