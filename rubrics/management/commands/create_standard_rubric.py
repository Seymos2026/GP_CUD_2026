"""
Management command to create the standard BCS-410 graduation project evaluation rubric
"""
from django.core.management.base import BaseCommand
from rubrics.models import Rubric, Criterion
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates the standard BCS-410 graduation project evaluation rubric'

    def handle(self, *args, **options):
        # Get or create rubric
        rubric_name = "BCS-410 Graduation Project Evaluation Rubric"
        rubric, created = Rubric.objects.get_or_create(
            name=rubric_name,
            defaults={
                'description': 'Standard rubric for evaluating Computer Science graduation projects (BCS-410). Includes group-based and individual evaluations. Total: 100 points.',
                'max_total_score': 100.00  # 10 + 20 + 5 + 15 + 30 + 20 = 100
            }
        )
        
        # Update max_total_score if rubric exists
        if not created:
            rubric.max_total_score = 100.00
            rubric.description = 'Standard rubric for evaluating Computer Science graduation projects (BCS-410). Includes group-based and individual evaluations. Total: 100 points.'
            rubric.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created rubric: {rubric_name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Rubric already exists: {rubric_name}'))
            # Clear existing criteria to recreate
            rubric.criteria.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing criteria'))

        # Define rubric structure with correct weights
        # Format: (order, name, description, max_score, weight, section_name, section_order, section_total)
        criteria_data = [
            # Section 1: Midterm Presentation (Group) - Total: 10 points [2.5, 2.5, 5]
            (1, '1.1', 'Participates in the establishment of goals and work plans of the team (The presentation includes a specific and clear problem statement, with a well-defined action plan, work distribution, and timeline).', 2.5, 1.0, 'Midterm Presentation', 1, 10),
            (2, '1.2', 'Applies software development lifecycles and methodologies (The presentation shows how the project applies software development lifecycles, methodologies, or cyber security best practices effectively).', 2.5, 1.0, 'Midterm Presentation', 1, 10),
            (3, '1.3', 'The team demonstrates confidence in the subject matter, effectively answers all questions, and all members actively participate in the presentation.', 5.0, 1.0, 'Midterm Presentation', 1, 10),
            
            # Section 2: Midterm Report (Group) - Total: 20 points [5, 5, 10]
            (4, '2.1', 'Provides supporting details which enhance the quality of the report (Includes a complete literature review, comparison with other work, conclusions, and references from various resources).', 5.0, 1.0, 'Midterm Report', 2, 20),
            (5, '2.2', 'Evaluate alternative solutions (Proposes at least three solutions for the problem, with a rationale for selecting the best solution).', 5.0, 1.0, 'Midterm Report', 2, 20),
            (6, '2.3', 'A preliminary solution prototype (visual, physical, technical sketch, etc.) is proposed.', 10.0, 1.0, 'Midterm Report', 2, 20),
            
            # Section 3: Poster Design (Group) - Total: 5 points
            (7, '3.1', 'The poster is informative and well-organized, presenting information in a logical sequence and thoroughly covers all key aspects of the project.', 5.0, 1.0, 'Poster Design', 3, 5),
            
            # Section 4: Final Presentations (Individual) - Total: 15 points [2.5, 2.5, 5, 5]
            # Note: This section is scored individually for each student
            (8, '4.1', 'Uses language appropriate to audience analysis (Demonstrates technical terms and engineering knowledge in presenting the problem and proposing solutions).', 2.5, 1.0, 'Final Presentation', 4, 15),
            (9, '4.2', 'Includes a strong introduction, clear transitions, organized ideas, and a solid conclusion.', 2.5, 1.0, 'Final Presentation', 4, 15),
            (10, '4.3', 'Contributes to the development of a collaborative team environment (All team members actively participate in various aspects of the presentation and show confidence in their understanding of the subject matter).', 5.0, 1.0, 'Final Presentation', 4, 15),
            (11, '4.4', 'Uses visuals which enhance audience understanding (The presentation includes visuals and text to clearly communicate the project\'s objectives and results).', 5.0, 1.0, 'Final Presentation', 4, 15),
            
            # Section 5: Final Report (Group) - Total: 30 points [10, 10, 5, 5]
            (12, '5.1', 'Includes a complete literature review, comparison with other work, and comprehensive references from various sources.', 10.0, 1.0, 'Final Report', 5, 30),
            (13, '5.2', 'Quality of technical documentation, including architecture diagrams, API documentation, and user manuals.', 10.0, 1.0, 'Final Report', 5, 30),
            (14, '5.3', 'Includes well-organized contents, tables, figures, and properly categorized citations.', 5.0, 1.0, 'Final Report', 5, 30),
            (15, '5.4', 'Exhibits dependability in the achievement of the team\'s goals (All team members contribute equally to report writing, and future improvements for the solution are recommended).', 5.0, 1.0, 'Final Report', 5, 30),
            
            # Section 6: Final Implementation and Demonstration (Group) - Total: 20 points [5, 5, 5, 5]
            (16, '6.1', 'Design and Architecture (Quality of the system design and architecture.)', 5.0, 1.0, 'Final Implementation and Demonstration', 6, 20),
            (17, '6.2', 'Implement a computer-based solution for the problem to meet desired goals within realistic constraints/Produce a computer-based solution for a real-world problem (The final prototype is error-free, providing a secure/ computer-based solution for a real-world problem).', 5.0, 1.0, 'Final Implementation and Demonstration', 6, 20),
            (18, '6.3', 'Applies new knowledge and skills in real-world projects (Comprehensive test results have been made with limitations and strengths).', 5.0, 1.0, 'Final Implementation and Demonstration', 6, 20),
            (19, '6.4', 'Analyze the performance of computing-based solutions using computer science theory and algorithms/Analyze security measures against threats to maintain the system operation.', 5.0, 1.0, 'Final Implementation and Demonstration', 6, 20),
        ]

        # Create criteria
        created_count = 0
        for order, name, description, max_score, weight, section_name, section_order, section_total in criteria_data:
            full_description = description
            criterion, created = Criterion.objects.get_or_create(
                rubric=rubric,
                order=order,
                defaults={
                    'name': name,
                    'description': full_description,
                    'max_score': max_score,
                    'weight': weight,
                    'section_title': section_name,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created criterion {order}: {name} ({section_name}) - {max_score} pts'))
            else:
                criterion.name = name
                criterion.description = full_description
                criterion.max_score = max_score
                criterion.weight = weight
                criterion.section_title = section_name
                criterion.save()
                self.stdout.write(self.style.WARNING(f'  Updated criterion {order}: {name} ({section_name}) - {max_score} pts'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created/updated {created_count} criteria for rubric: {rubric_name}'))
        
        # Display summary
        self.stdout.write(self.style.SUCCESS('\n=== Rubric Summary ==='))
        self.stdout.write(f'Rubric: {rubric.name}')
        self.stdout.write(f'Max Total Score: {rubric.max_total_score}')
        self.stdout.write(f'Total Criteria: {rubric.criteria.count()}')
        
        # Group criteria by section_title
        sections = {}
        for criterion in rubric.criteria.all():
            section_name = criterion.section_title or 'Other'
            if section_name not in sections:
                sections[section_name] = []
            sections[section_name].append(criterion)
        
        self.stdout.write('\n=== Rubric Sections ===')
        # Display sections in order
        section_order_map = {
            'Midterm Presentation': 1,
            'Midterm Report': 2,
            'Poster Design': 3,
            'Final Presentation': 4,
            'Final Report': 5,
            'Final Implementation and Demonstration': 6,
        }
        sorted_sections = sorted(sections.items(), key=lambda x: section_order_map.get(x[0].split('(')[0].strip(), 999))
        
        for section_name, criteria_list in sorted_sections:
            section_total = sum(c.max_score * c.weight for c in criteria_list)
            self.stdout.write(f'\n{section_name} ({section_total} points):')
            for criterion in sorted(criteria_list, key=lambda x: x.order):
                self.stdout.write(f'  - {criterion.name}: {criterion.max_score} pts (Weight: {criterion.weight})')
        
        self.stdout.write(self.style.SUCCESS('\nRubric is ready to use!'))
