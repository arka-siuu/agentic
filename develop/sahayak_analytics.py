#!/usr/bin/env python3
"""SAHAYAK Analytics Engine - Refactored for Web Deployment"""

import os
import json
import datetime
import tempfile
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np
import warnings
from google.api_core.retry import Retry

warnings.filterwarnings('ignore')

# PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

class SahayakAnalytics:
    def __init__(self, custom_data_path=None):
        """Initialize SAHAYAK Analytics with optional custom data"""
        
        # Initialize AI client
        # GOOGLE_API_KEY is no longer required when using Application Default Credentials
        genai.configure()
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Load student data
        if custom_data_path and os.path.exists(custom_data_path):
            with open(custom_data_path, 'r') as f:
                self.student_data = json.load(f)
        else:
            # Default demo data
            self.student_data = [
                {"name": "Arjun", "grade": "Class 4", "subject": "Mathematics", "remark": "Arjun excels in basic arithmetic but struggles with word problems. Shows excellent focus during individual work but gets distracted in group settings. Needs support in reading comprehension for math problems.", "exam_date": "2024-12-15"},
                {"name": "Priya", "grade": "Class 5", "subject": "English", "remark": "Priya has strong vocabulary but struggles with sentence construction. She helps younger students during reading time, showing leadership qualities. Needs structured grammar practice and confidence building for writing.", "exam_date": "2024-12-14"},
                {"name": "Rohan", "grade": "Class 3", "subject": "Science", "remark": "Rohan asks insightful questions about nature and experiments but has difficulty following multi-step instructions. Very curious but needs help organizing his thoughts and answers. Great potential for hands-on learning.", "exam_date": "2024-12-13"},
                {"name": "Kavya", "grade": "Class 5", "subject": "Mathematics", "remark": "Kavya is advanced in calculations and often helps classmates. However, she rushes through problems and makes careless errors. Shows impatience when others are slower to understand concepts.", "exam_date": "2024-12-12"},
                {"name": "Aman", "grade": "Class 4", "subject": "Hindi", "remark": "Aman has difficulty with reading fluency but loves storytelling in his local dialect. Struggles with formal Hindi writing but shows creativity in oral expression. Needs bridge between his native language and formal Hindi.", "exam_date": "2024-12-11"},
            ]
        
        # Create temp directory for generated files
        self.temp_dir = tempfile.mkdtemp()
    
    def analyze_student_with_ai(self, student_data):
        """Enhanced AI analysis with retry and improved error handling"""
        prompt = self._build_prompt(student_data)

        try:
            # Configure a retry mechanism for transient API errors
            retry = Retry(
                initial=1.0,
                maximum=60.0,
                multiplier=2.0,
                deadline=120.0,
                predicate=Retry.if_transient_error
            )

            # Generate content with retry
            response = self.model.generate_content(prompt, request_options={'retry': retry})

            if response and hasattr(response, 'text'):
                response_text = response.text
                # Clean up response if it's formatted as a JSON code block
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()

                return json.loads(response_text)
            else:
                print(f"Error analyzing {student_data.get('name', 'student')}: No response or missing 'text' attribute")
                print("Raw response:", response)
                return self.create_enhanced_fallback_analysis(student_data)

        except json.JSONDecodeError:
            print(f"JSON parsing issue for {student_data['name']}, using fallback")
            return self.create_enhanced_fallback_analysis(student_data)
        except Exception as e:
            print(f"Error analyzing {student_data['name']}: {e}")
            return self.create_enhanced_fallback_analysis(student_data)

    def _build_prompt(self, student_data):
        """Build the AI prompt for student analysis"""
        # This function now only builds the prompt, no API call
        return f"""
        You are SAHAYAK, an AI teaching assistant for teachers in multi-grade, under-resourced Indian classrooms. 
        Analyze this student and provide EXTREMELY SPECIFIC, ACTIONABLE insights that a teacher can implement TODAY.

        Student: {student_data['name']} (Grade: {student_data['grade']})
        Subject: {student_data['subject']}
        Teacher Observation: "{student_data['remark']}"
        
        CRITICAL: Every recommendation must include EXACTLY what to do, WHEN to do it, HOW LONG it takes, and WHAT materials are needed.
        Be specific about classroom positioning, peer interactions, daily schedules, and concrete activities.
        
        Provide detailed analysis in JSON format with HYPER-SPECIFIC teaching strategies:

        {{
            "student_profile": {{
                "current_grade_level": "{student_data['grade']}",
                "functional_level": "Grade X equivalent",
                "learning_pace": "Fast/Average/Slow",
                "attention_span": "Short/Medium/Long",
                "peer_interaction": "Helpful/Neutral/Needs_Support",
                "independence_level": "High/Medium/Low"
            }},
            "academic_performance": {{
                "subject_mastery": 7,
                "comprehension_level": 6,
                "application_skills": 5,
                "problem_solving": 6,
                "retention_rate": 7
            }},
            "multi_grade_considerations": {{
                "can_help_younger_students": true,
                "needs_advanced_challenges": false,
                "requires_individualized_attention": true,
                "works_well_in_mixed_groups": false
            }},
            "detailed_strengths": [
                {{
                    "strength": "Strong arithmetic foundation",
                    "evidence": "excels in basic arithmetic",
                    "classroom_application": "Can be peer tutor for younger students",
                    "teaching_strategy": "Use as math helper during multi-grade activities"
                }}
            ],
            "detailed_challenges": [
                {{
                    "challenge": "Word problem comprehension",
                    "root_cause": "Reading comprehension difficulties affecting math",
                    "severity": "Medium",
                    "impact_on_multi_grade": "May struggle when class does combined reading-math activities",
                    "immediate_intervention": "Provide visual word problem templates"
                }}
            ],
            "sahayak_interventions": [
                {{
                    "intervention": "Create visual math problem templates using classroom objects",
                    "specific_implementation": "EXACTLY: Use 5 stones, 3 sticks, and 2 books to create word problems. Say 'Student has 5 stones, gives away 2 to friend. How many stones left?' while physically moving objects",
                    "daily_schedule": "WHEN: Every day at 10:15 AM, right after morning prayers, for exactly 8 minutes",
                    "classroom_positioning": "WHERE: Seat in front row, second seat from left, facing the demonstration table",
                    "materials_needed": "5 small stones, 3 wooden sticks, 2 old textbooks, 1 small cloth to place objects",
                    "step_by_step_process": [
                        "Step 1: Place objects on cloth (30 seconds)",
                        "Step 2: Read problem aloud while pointing to objects (1 minute)",
                        "Step 3: Have student physically move objects to solve (2 minutes)",
                        "Step 4: Ask them to explain what they did (1 minute)",
                        "Step 5: Write the number sentence on blackboard together (30 seconds)"
                    ],
                    "zero_cost_adaptation": "Use broken chalk pieces, torn paper strips, and small stones from playground",
                    "expected_outcome": "After 2 weeks: Can solve 3 object-based word problems independently. After 4 weeks: Can draw pictures to solve word problems without objects",
                    "how_to_measure_success": "Count how many word problems they attempt vs avoid. Success = attempts 80% of word problems given"
                }}
            ],
            "personalized_summary": {{
                "immediate_actions_for_tomorrow": [
                    "TOMORROW 10:15 AM: Introduce object-based word problems using specific materials",
                    "TOMORROW: Move student's seat to optimal position for learning",
                    "TOMORROW: Collect necessary materials and place on student's desk corner"
                ],
                "this_week_implementation": [
                    "MONDAY: Start daily sessions",
                    "TUESDAY: Begin buddy system if applicable", 
                    "WEDNESDAY: Send parent communication note home",
                    "THURSDAY: Implement progress tracking",
                    "FRIDAY: Assess week 1 progress"
                ],
                "success_timeline_with_numbers": "Week 2: 50% improvement. Week 4: 70% improvement. Week 6: 80% improvement + can explain to peer. Week 8: Independent with visual supports"
            }}
        }}
        
        Focus on practical, low-resource solutions suitable for teachers managing multiple grades with limited materials.
        """

    def create_enhanced_fallback_analysis(self, student_data):
        """Enhanced fallback with multi-grade considerations"""
        return {
            "student_profile": {
                "current_grade_level": student_data['grade'],
                "functional_level": "Grade level assessment needed",
                "learning_pace": "Average",
                "attention_span": "Medium",
                "peer_interaction": "Neutral",
                "independence_level": "Medium"
            },
            "academic_performance": {
                "subject_mastery": 6,
                "comprehension_level": 6,
                "application_skills": 5,
                "problem_solving": 6,
                "retention_rate": 6
            },
            "multi_grade_considerations": {
                "can_help_younger_students": False,
                "needs_advanced_challenges": False,
                "requires_individualized_attention": True,
                "works_well_in_mixed_groups": True
            },
            "detailed_strengths": [{"strength": "Shows potential", "evidence": "Teacher observation", "classroom_application": "Can participate in group activities", "teaching_strategy": "Provide encouragement and support"}],
            "detailed_challenges": [{"challenge": "Needs assessment", "root_cause": "Requires detailed evaluation", "severity": "Medium", "impact_on_multi_grade": "May need individualized attention", "immediate_intervention": "Closer observation needed"}],
            "sahayak_interventions": [{"intervention": "Individual assessment", "specific_implementation": "One-on-one evaluation with specific activities", "daily_schedule": "During individual work time", "materials_needed": "Basic classroom materials", "zero_cost_adaptation": "Use existing materials", "expected_outcome": "Better understanding of needs"}],
            "personalized_summary": {
                "immediate_actions_for_tomorrow": [f"Observe {student_data['name']} more closely during lessons", "Note specific areas of strength and challenge", "Plan targeted interventions based on observations"],
                "this_week_implementation": ["Monday: Detailed observation", "Tuesday: Try different teaching approaches", "Wednesday: Note what works best", "Thursday: Implement successful strategies", "Friday: Assess progress"],
                "success_timeline_with_numbers": "Week 2: Better understanding of student needs. Week 4: Targeted interventions showing results. Week 6: Consistent improvement visible"
            }
        }

    def create_student_visualization(self, student_data, student_id):
        """Create comprehensive student visualization for PDF"""
        analysis = student_data['analysis']
        name = student_data['student_name']
        grade = student_data.get('grade', 'Unknown')
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'SAHAYAK Student Report: {name} ({grade})', fontsize=20, fontweight='bold', y=0.95)
        
        # Academic Performance Radar Chart
        if 'academic_performance' in analysis:
            perf_data = analysis['academic_performance']
            categories = list(perf_data.keys())
            values = list(perf_data.values())
            
            # Close the radar chart
            values += values[:1]
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]
            
            axes[0, 0].plot(angles, values, 'o-', linewidth=2, color='blue')
            axes[0, 0].fill(angles, values, alpha=0.25, color='blue')
            axes[0, 0].set_xticks(angles[:-1])
            axes[0, 0].set_xticklabels([cat.replace('_', ' ').title() for cat in categories], fontsize=9)
            axes[0, 0].set_ylim(0, 10)
            axes[0, 0].set_title('Academic Performance Profile', fontweight='bold', fontsize=12)
            axes[0, 0].grid(True)
        
        # Student Profile Information
        if 'student_profile' in analysis:
            profile = analysis['student_profile']
            profile_text = []
            for key, value in profile.items():
                profile_text.append(f"{key.replace('_', ' ').title()}: {value}")
            
            axes[0, 1].text(0.1, 0.9, '\n'.join(profile_text), fontsize=10, 
                           transform=axes[0, 1].transAxes, verticalalignment='top',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
            axes[0, 1].set_title('Student Profile', fontweight='bold', fontsize=12)
            axes[0, 1].axis('off')
        
        # Multi-Grade Considerations
        if 'multi_grade_considerations' in analysis:
            mg_data = analysis['multi_grade_considerations']
            labels = []
            values = []
            colors_list = []
            
            for key, value in mg_data.items():
                labels.append(key.replace('_', ' ').title())
                if isinstance(value, bool):
                    values.append(1 if value else 0)
                    colors_list.append('green' if value else 'red')
                else:
                    values.append(0.5)
                    colors_list.append('orange')
            
            axes[0, 2].barh(labels, values, color=colors_list, alpha=0.7)
            axes[0, 2].set_xlim(0, 1)
            axes[0, 2].set_title('Multi-Grade Classroom Fit', fontweight='bold', fontsize=12)
            axes[0, 2].set_xlabel('Suitability')
        
        # Strengths vs Challenges
        strengths_count = len(analysis.get('detailed_strengths', []))
        challenges_count = len(analysis.get('detailed_challenges', []))
        interventions_count = len(analysis.get('sahayak_interventions', []))
        
        categories = ['Strengths', 'Challenges', 'Interventions']
        counts = [strengths_count, challenges_count, interventions_count]
        colors_bar = ['green', 'orange', 'blue']
        
        axes[1, 0].bar(categories, counts, color=colors_bar, alpha=0.7)
        axes[1, 0].set_title('Learning Profile Overview', fontweight='bold', fontsize=12)
        axes[1, 0].set_ylabel('Count')
        
        # Progress Implementation
        if 'personalized_summary' in analysis and 'this_week_implementation' in analysis['personalized_summary']:
            impl_text = '\n'.join([f"• {item}" for item in analysis['personalized_summary']['this_week_implementation'][:4]])
            
            axes[1, 1].text(0.05, 0.95, 'This Week Implementation:', fontweight='bold', fontsize=11,
                           transform=axes[1, 1].transAxes, verticalalignment='top')
            axes[1, 1].text(0.05, 0.80, impl_text, fontsize=9,
                           transform=axes[1, 1].transAxes, verticalalignment='top',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
            axes[1, 1].set_title('Implementation Plan', fontweight='bold', fontsize=12)
            axes[1, 1].axis('off')
        
        # Timeline
        if 'personalized_summary' in analysis:
            timeline_text = analysis['personalized_summary'].get('success_timeline_with_numbers', 'Timeline to be determined')
            axes[1, 2].text(0.05, 0.5, timeline_text, fontsize=10,
                           transform=axes[1, 2].transAxes, verticalalignment='center',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"),
                           wrap=True)
            axes[1, 2].set_title('Success Timeline', fontweight='bold', fontsize=12)
            axes[1, 2].axis('off')
        
        plt.tight_layout()
        filename = os.path.join(self.temp_dir, f'sahayak_student_{student_id}_{name.replace(" ", "_")}.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return filename

    def create_class_analytics_dashboard(self, reports):
        """Create comprehensive class analytics for multi-grade classroom"""
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('SAHAYAK Class Analytics Dashboard - Multi-Grade Classroom Insights', 
                     fontsize=18, fontweight='bold', y=0.95)
        
        # Grade Distribution
        grade_counts = {}
        for report in reports:
            grade = report.get('grade', 'Unknown')
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        if grade_counts:
            grades = list(grade_counts.keys())
            counts = list(grade_counts.values())
            axes[0, 0].pie(counts, labels=grades, autopct='%1.1f%%', startangle=90)
            axes[0, 0].set_title('Grade Distribution', fontweight='bold')
        
        # Academic Performance by Grade
        grade_performance = {}
        for report in reports:
            grade = report.get('grade', 'Unknown')
            if 'analysis' in report and 'academic_performance' in report['analysis']:
                perf = report['analysis']['academic_performance']
                avg_score = np.mean(list(perf.values()))
                if grade not in grade_performance:
                    grade_performance[grade] = []
                grade_performance[grade].append(avg_score)
        
        if grade_performance:
            grades = list(grade_performance.keys())
            avg_scores = [np.mean(scores) for scores in grade_performance.values()]
            
            bars = axes[0, 1].bar(grades, avg_scores, color='skyblue', alpha=0.8)
            axes[0, 1].set_title('Academic Performance by Grade', fontweight='bold')
            axes[0, 1].set_ylabel('Average Score (1-10)')
            axes[0, 1].set_ylim(0, 10)
            
            # Add value labels on bars
            for bar, score in zip(bars, avg_scores):
                height = bar.get_height()
                axes[0, 1].text(bar.get_x() + bar.get_width()/2., height + 0.1,
                               f'{score:.1f}', ha='center', va='bottom')
        
        # Multi-Grade Classroom Dynamics
        peer_helpers = 0
        needs_individual_attention = 0
        works_in_groups = 0
        
        for report in reports:
            if 'analysis' in report and 'multi_grade_considerations' in report['analysis']:
                mg = report['analysis']['multi_grade_considerations']
                if mg.get('can_help_younger_students', False):
                    peer_helpers += 1
                if mg.get('requires_individualized_attention', False):
                    needs_individual_attention += 1
                if mg.get('works_well_in_mixed_groups', False):
                    works_in_groups += 1
        
        categories = ['Peer Helpers', 'Need Individual\nAttention', 'Good in\nMixed Groups']
        values = [peer_helpers, needs_individual_attention, works_in_groups]
        colors_mg = ['green', 'orange', 'blue']
        
        axes[0, 2].bar(categories, values, color=colors_mg, alpha=0.7)
        axes[0, 2].set_title('Multi-Grade Classroom Dynamics', fontweight='bold')
        axes[0, 2].set_ylabel('Number of Students')
        
        # Subject-wise Performance Distribution
        subject_performance = {}
        for report in reports:
            subject = report.get('subject', 'Unknown')
            if 'analysis' in report and 'academic_performance' in report['analysis']:
                perf = report['analysis']['academic_performance']
                avg_score = np.mean(list(perf.values()))
                if subject not in subject_performance:
                    subject_performance[subject] = []
                subject_performance[subject].append(avg_score)
        
        if subject_performance:
            subjects = list(subject_performance.keys())
            box_data = [subject_performance[subject] for subject in subjects]
            
            bp = axes[1, 0].boxplot(box_data, labels=subjects, patch_artist=True)
            for patch in bp['boxes']:
                patch.set_facecolor('lightcoral')
            axes[1, 0].set_title('Subject Performance Distribution', fontweight='bold')
            axes[1, 0].set_ylabel('Performance Score')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Learning Pace Distribution
        pace_distribution = {'Fast': 0, 'Average': 0, 'Slow': 0}
        for report in reports:
            if 'analysis' in report and 'student_profile' in report['analysis']:
                pace = report['analysis']['student_profile'].get('learning_pace', 'Average')
                if pace in pace_distribution:
                    pace_distribution[pace] += 1
        
        paces = list(pace_distribution.keys())
        pace_counts = list(pace_distribution.values())
        colors_pace = ['red', 'yellow', 'green']
        
        axes[1, 1].pie(pace_counts, labels=paces, autopct='%1.1f%%', colors=colors_pace, startangle=90)
        axes[1, 1].set_title('Learning Pace Distribution', fontweight='bold')
        
        # Attention Span Analysis
        attention_data = {'Short': 0, 'Medium': 0, 'Long': 0}
        for report in reports:
            if 'analysis' in report and 'student_profile' in report['analysis']:
                attention = report['analysis']['student_profile'].get('attention_span', 'Medium')
                if attention in attention_data:
                    attention_data[attention] += 1
        
        attention_spans = list(attention_data.keys())
        attention_counts = list(attention_data.values())
        
        axes[1, 2].bar(attention_spans, attention_counts, color='purple', alpha=0.6)
        axes[1, 2].set_title('Attention Span Distribution', fontweight='bold')
        axes[1, 2].set_ylabel('Number of Students')
        
        plt.tight_layout()
        filename = os.path.join(self.temp_dir, 'sahayak_class_analytics.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return filename

    def generate_complete_report(self):
        """Generate complete SAHAYAK report and return list of generated files"""
        try:
            print("🎓 Starting SAHAYAK Analysis...")
            
            # Step 1: AI Analysis
            reports = []
            for i, student_data in enumerate(self.student_data, 1):
                print(f"   🔍 Analyzing {student_data['name']} ({student_data['grade']})...")
                
                analysis = self.analyze_student_with_ai(student_data)
                if analysis:
                    report = {
                        'student_id': i,
                        'student_name': student_data['name'],
                        'grade': student_data['grade'],
                        'subject': student_data['subject'],
                        'exam_date': student_data['exam_date'],
                        'original_remark': student_data['remark'],
                        'analysis_date': datetime.datetime.now().isoformat(),
                        'analysis': analysis
                    }
                    reports.append(report)
                    print(f"   ✅ {student_data['name']} analysis complete")
            
            if not reports:
                print("❌ No successful analyses.")
                return []
            
            print(f"✅ Analysis Complete: {len(reports)} students processed")
            
            # Step 2: Create Visualizations
            print("📊 Creating Visualizations...")
            individual_charts = []
            
            for report in reports:
                chart_file = self.create_student_visualization(report, report['student_id'])
                individual_charts.append(chart_file)
                print(f"   📈 Chart created for {report['student_name']}")
            
            # Step 3: Class Analytics
            print("🎓 Creating Class Analytics...")
            class_chart = self.create_class_analytics_dashboard(reports)
            print(f"   📊 Class dashboard created")
            
            # Step 4: Generate PDF Report
            print("📄 Generating PDF Report...")
            pdf_filename = self.generate_comprehensive_pdf_report(reports, individual_charts, class_chart)
            print(f"   📋 PDF Report generated")
            
            # Step 5: Save Raw Data
            print("💾 Saving Analysis Data...")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = os.path.join(self.temp_dir, f"sahayak_analysis_data_{timestamp}.json")
            
            with open(json_filename, 'w') as f:
                json.dump({
                    "metadata": {
                        "system": "SAHAYAK - AI Teaching Assistant",
                        "version": "1.0 - Multi-Grade Classroom Analytics",
                        "total_students": len(reports),
                        "analysis_date": datetime.datetime.now().isoformat(),
                        "designed_for": "Under-resourced multi-grade classrooms in India"
                    },
                    "students": reports
                }, f, indent=2)
            
            print("🎉 SAHAYAK Analysis Complete!")
            
            # Return all generated files
            generated_files = [pdf_filename, class_chart, json_filename] + individual_charts
            return [f for f in generated_files if os.path.exists(f)]
            
        except Exception as e:
            print(f"Error in generate_complete_report: {e}")
            return []

    def generate_comprehensive_pdf_report(self, reports, individual_charts, class_chart):
        """Generate comprehensive PDF report with visualizations and insights"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.temp_dir, f'SAHAYAK_Complete_Report_{timestamp}.pdf')
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkgreen
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkred
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        # Title Page
        story.append(Paragraph("SAHAYAK", title_style))
        story.append(Paragraph("AI Teaching Assistant - Complete Student Analytics Report", heading_style))
        story.append(Spacer(1, 20))
        
        # Context and objective
        context_text = """
        <b>The Challenge:</b> In countless under-resourced schools across India, a single teacher often manages 
        multiple grades in one classroom. These educators are stretched thin, lacking the time and tools to create 
        localized teaching aids, address diverse learning levels, and personalize education for every child.
        <br/><br/>
        <b>SAHAYAK's Objective:</b> This AI-powered teaching assistant empowers teachers in multi-grade, 
        low-resource environments with comprehensive student analytics, actionable insights, and practical 
        intervention strategies.
        """
        story.append(Paragraph(context_text, body_style))
        story.append(Spacer(1, 30))
        
        # Report summary
        total_students = len(reports)
        grades_represented = len(set(report.get('grade', 'Unknown') for report in reports))
        
        summary_data = [
            ['Report Generated:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M")],
            ['Total Students Analyzed:', str(total_students)],
            ['Grades Represented:', str(grades_represented)],
            ['Analysis Type:', 'Comprehensive AI-Powered Assessment'],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(PageBreak())
        
        # Class Overview Dashboard
        story.append(Paragraph("Class Overview Dashboard", heading_style))
        story.append(Spacer(1, 12))
        
        if class_chart and os.path.exists(class_chart):
            story.append(Image(class_chart, width=7*inch, height=4.2*inch))
            story.append(Spacer(1, 20))
        
        # Class-wide insights
        story.append(Paragraph("Class-Wide Strategic Insights", subheading_style))
        
        # Generate class insights
        class_insights = self.generate_class_strategic_insights(reports)
        for insight in class_insights:
            story.append(Paragraph(f"• {insight}", body_style))
        
        story.append(PageBreak())
        
        # Individual Student Reports
        story.append(Paragraph("Individual Student Reports", heading_style))
        story.append(Spacer(1, 12))
        
        for i, report in enumerate(reports):
            if i > 0:
                story.append(PageBreak())
            
            name = report['student_name']
            grade = report.get('grade', 'Unknown')
            subject = report['subject']
            
            # Student header
            story.append(Paragraph(f"Student Report: {name} ({grade})", subheading_style))
            story.append(Paragraph(f"Subject Focus: {subject}", body_style))
            story.append(Spacer(1, 12))
            
            # Student visualization
            if i < len(individual_charts) and os.path.exists(individual_charts[i]):
                story.append(Image(individual_charts[i], width=7*inch, height=4.2*inch))
                story.append(Spacer(1, 15))
            
            # Detailed analysis
            analysis = report.get('analysis', {})
            
            # Teacher's original observation
            story.append(Paragraph("Teacher's Observation:", ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')))
            story.append(Paragraph(f'"{report.get("original_remark", "No observation recorded")}"', body_style))
            story.append(Spacer(1, 10))
            
            # SAHAYAK Analysis Summary
            if 'personalized_summary' in analysis and 'immediate_actions_for_tomorrow' in analysis['personalized_summary']:
                summary = analysis['personalized_summary']
                story.append(Paragraph("SAHAYAK AI Analysis - Immediate Actions:", ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')))
                for action in summary['immediate_actions_for_tomorrow']:
                    story.append(Paragraph(f"• {action}", body_style))
                story.append(Spacer(1, 10))
            
            # Strengths
            if 'detailed_strengths' in analysis:
                story.append(Paragraph("Key Strengths:", ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')))
                for strength in analysis['detailed_strengths']:
                    story.append(Paragraph(f"• {strength.get('strength', 'N/A')}: {strength.get('teaching_strategy', 'Strategy to be developed')}", body_style))
                story.append(Spacer(1, 8))
            
            # Immediate Interventions
            if 'sahayak_interventions' in analysis:
                story.append(Paragraph("Immediate Action Items:", ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')))
                for intervention in analysis['sahayak_interventions'][:3]:  # Top 3
                    story.append(Paragraph(f"• {intervention.get('intervention', 'N/A')} - {intervention.get('daily_schedule', 'Schedule TBD')}", body_style))
                story.append(Spacer(1, 8))
            
            # Implementation timeline
            if 'personalized_summary' in analysis and 'this_week_implementation' in analysis['personalized_summary']:
                story.append(Paragraph("This Week Implementation:", ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')))
                for item in analysis['personalized_summary']['this_week_implementation']:
                    story.append(Paragraph(f"• {item}", body_style))
                story.append(Spacer(1, 10))
        
        # Final page: Multi-Grade Teaching Recommendations
        story.append(PageBreak())
        story.append(Paragraph("Multi-Grade Teaching Recommendations", heading_style))
        story.append(Spacer(1, 12))
        
        recommendations = self.generate_multi_grade_recommendations(reports)
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", body_style))
            story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        return filename

    def generate_class_strategic_insights(self, reports):
        """Generate HYPER-SPECIFIC strategic insights for multi-grade classroom management"""
        insights = []
        
        total_students = len(reports)
        student_names = [report['student_name'] for report in reports]
        
        # Calculate detailed metrics
        high_performers = []
        need_urgent_support = []
        peer_helpers = []
        individual_attention_students = []
        
        grade_distribution = {}
        subject_specific_issues = {}
        attention_span_data = {}
        
        for report in reports:
            name = report['student_name']
            grade = report.get('grade', 'Unknown')
            subject = report.get('subject', 'Unknown')
            
            # Grade distribution
            if grade not in grade_distribution:
                grade_distribution[grade] = []
            grade_distribution[grade].append(name)
            
            if 'analysis' in report:
                analysis = report['analysis']
                
                # Performance categorization with names
                if 'academic_performance' in analysis:
                    avg_score = np.mean(list(analysis['academic_performance'].values()))
                    if avg_score >= 7.5:
                        high_performers.append(name)
                    elif avg_score < 5.5:
                        need_urgent_support.append(name)
                
                # Multi-grade helpers identification
                if 'multi_grade_considerations' in analysis:
                    mg = analysis['multi_grade_considerations']
                    if mg.get('can_help_younger_students', False):
                        peer_helpers.append(name)
                    if mg.get('requires_individualized_attention', False):
                        individual_attention_students.append(name)
                
                # Attention span tracking
                if 'student_profile' in analysis:
                    attention = analysis['student_profile'].get('attention_span', 'Medium')
                    if attention not in attention_span_data:
                        attention_span_data[attention] = []
                    attention_span_data[attention].append(name)
                
                # Subject-specific detailed issues
                if 'detailed_challenges' in analysis:
                    for challenge in analysis['detailed_challenges']:
                        issue = challenge.get('challenge', 'Unknown issue')
                        severity = challenge.get('severity', 'Medium')
                        if subject not in subject_specific_issues:
                            subject_specific_issues[subject] = []
                        subject_specific_issues[subject].append({
                            'student': name,
                            'issue': issue,
                            'severity': severity
                        })
        
        # Generate EXTREMELY SPECIFIC insights
        insights.append(f"<b>IMMEDIATE CLASSROOM SETUP (Implement Tomorrow):</b>")
        insights.append(f"   • TOTAL CLASS SIZE: {total_students} students requiring {len(individual_attention_students)} individual support stations")
        
        # Specific grade arrangement
        for grade, students in grade_distribution.items():
            insights.append(f"   • {grade}: {len(students)} students ({', '.join(students)}) - Seat together in rows 2-3")
        
        # Detailed peer tutoring system
        if peer_helpers and need_urgent_support:
            insights.append(f"<b>PEER TUTORING SYSTEM (Start This Week):</b>")
            insights.append(f"   • TUTORS AVAILABLE: {', '.join(peer_helpers)} can help struggling classmates")
            insights.append(f"   • STUDENTS NEEDING HELP: {', '.join(need_urgent_support)} require daily support")
            
            # Specific pairing recommendations
            for i, helper in enumerate(peer_helpers):
                if i < len(need_urgent_support):
                    struggling_student = need_urgent_support[i]
                    insights.append(f"   • PAIR: {helper} (tutor) + {struggling_student} (learner) - Meet Tuesdays & Thursdays 11:30-11:50 AM, back-left corner desk")
        
        # Time management with specific schedule
        insights.append(f"<b>DAILY SCHEDULE OPTIMIZATION (Exact Times):</b>")
        
        if individual_attention_students:
            insights.append(f"   • 10:15-10:30 AM: Individual support time for {', '.join(individual_attention_students[:3])} while others do independent work")
            if len(individual_attention_students) > 3:
                insights.append(f"   • 2:45-3:00 PM: Individual support time for {', '.join(individual_attention_students[3:])} while others clean classroom")
        
        # Subject-specific interventions
        for subject, issues_list in subject_specific_issues.items():
            high_severity_count = sum(1 for issue in issues_list if issue['severity'] == 'High')
            if high_severity_count > 0:
                insights.append(f"<b>URGENT {subject.upper()} INTERVENTIONS:</b>")
                high_severity_students = [issue['student'] for issue in issues_list if issue['severity'] == 'High']
                insights.append(f"   • STUDENTS NEEDING IMMEDIATE HELP: {', '.join(high_severity_students)}")
                insights.append(f"   • ACTION: Dedicate first 15 minutes of {subject} class to small group instruction with these students")
                insights.append(f"   • LOCATION: Front corner of classroom, use visual aids and manipulatives")
        
        # Attention span management
        if attention_span_data:
            if 'Short' in attention_span_data:
                short_attention_students = attention_span_data['Short']
                insights.append(f"<b>ATTENTION SPAN MANAGEMENT:</b>")
                insights.append(f"   • SHORT ATTENTION ({', '.join(short_attention_students)}): Change activities every 8-10 minutes, use movement breaks")
                insights.append(f"   • STRATEGY: Ring bell every 8 minutes, have these students stand and stretch for 30 seconds")
        
        # Physical classroom arrangement
        insights.append(f"<b>CLASSROOM LAYOUT (Rearrange This Week):</b>")
        insights.append(f"   • FRONT ROW: Individual attention students ({', '.join(individual_attention_students[:4])})")
        insights.append(f"   • MIDDLE ROWS: Grade-level groups - Class 3 left side, Class 4 center, Class 5 right side") 
        insights.append(f"   • BACK LEFT CORNER: Peer tutoring station with small desk and manipulation materials")
        insights.append(f"   • BACK RIGHT CORNER: Independent work station for advanced students")
        
        # Weekly assessment strategy
        insights.append(f"<b>PROGRESS TRACKING SYSTEM (Start Monday):</b>")
        insights.append(f"   • MONDAY: Quick assessment - check weekend practice with {', '.join(need_urgent_support) if need_urgent_support else 'all students'}")
        insights.append(f"   • WEDNESDAY: Peer tutor feedback - ask {', '.join(peer_helpers) if peer_helpers else 'advanced students'} 'How is your buddy doing?'")
        insights.append(f"   • FRIDAY: Weekly goals check - use simple ✓/X marking for each student's target skills")
        
        # Resource requirements
        insights.append(f"<b>MATERIALS NEEDED (Zero Cost):</b>")
        insights.append(f"   • 20 small stones for counting (collect from playground)")
        insights.append(f"   • 3 cloth pieces for manipulation activities (use old saris/clothes)")
        insights.append(f"   • 2 small containers for storing materials (use empty containers)")
        insights.append(f"   • 1 progress tracking sheet per student (draw grid on paper)")
        
        return insights

    def generate_multi_grade_recommendations(self, reports):
        """Generate EXTREMELY SPECIFIC recommendations for multi-grade classroom management"""
        
        # Analyze the specific students in this class
        student_names = [report['student_name'] for report in reports]
        grade_groups = {}
        for report in reports:
            grade = report.get('grade', 'Unknown')
            if grade not in grade_groups:
                grade_groups[grade] = []
            grade_groups[grade].append(report['student_name'])
        
        recommendations = [
            f"<b>ZONE-BASED CLASSROOM SETUP (Implement This Week):</b> Divide classroom into 4 zones: (1) Front-left: Teacher instruction area with all grades, (2) Front-right: Individual help station for struggling students, (3) Back-left: Peer tutoring corner with {', '.join(student_names[:2])}, (4) Back-right: Independent work zone for advanced students. Each zone needs clear visual boundaries using chalk lines on floor.",
            
            f"<b>BUDDY SYSTEM IMPLEMENTATION (Start Tuesday):</b> Create specific pairs: Pair each struggling student with a peer helper. Meet every Tuesday 11:30-11:50 AM and Thursday 2:30-2:50 PM. Buddies sit together during these times only, return to grade groups for regular lessons. Teacher checks each pair for 2 minutes during buddy time.",
            
            f"<b>MULTI-LEVEL MATERIALS CREATION (Make This Weekend):</b> Create ONE set of counting materials that serves all grades: Use 30 bottle caps numbered 1-30. Class 3 uses caps 1-10 for basic counting, Class 4 uses caps 1-20 for addition/subtraction, Class 5 uses all 30 for multiplication tables. Store in 3 labeled cloth bags: 'छोटे नंबर' (1-10), 'मध्यम नंबर' (11-20), 'बड़े नंबर' (21-30).",
            
            f"<b>ROTATION SCHEDULE (Daily Implementation):</b> 9:00-9:20 AM: All grades together for morning song/prayer. 9:20-9:40 AM: Grade-specific instruction (teacher moves between {len(grade_groups)} groups every 7 minutes). 9:40-10:00 AM: Mixed-grade collaborative project. 10:00-10:15 AM: Individual work time. 10:15-10:30 AM: Cleanup and reflection with buddy pairs.",
            
            f"<b>WEEKLY GOAL CONTRACTS (Start Monday):</b> Give each student a simple card with 3 specific goals: For example, {student_names[0] if student_names else 'Sample student'}: (1) Solve 2 word problems using objects, (2) Help one classmate with addition, (3) Read math problems aloud before solving. Students check off goals daily, teacher reviews every Friday afternoon for 5 minutes per student.",
            
            f"<b>PARENT HOME ACTIVITIES (Send Note Wednesday):</b> Create specific activity sheets for each grade level that parents can do with ZERO additional cost: Class 3: Count household items while doing chores, Class 4: Use cooking ingredients for addition/subtraction practice, Class 5: Calculate change while shopping. Include exact phrases for parents to use: 'आज हमारे पास कितने रोटी हैं? अगर 2 खा लें तो कितने बचेंगे?'",
            
            f"<b>OBSERVATION-BASED ASSESSMENT (Daily 5-Minute Protocol):</b> Use simple tally system on one sheet of paper: Each student gets ✓ (doing well), → (needs practice), or X (struggling) for that day's focus skill. Check 3 students per day in detail, rotate so each student gets detailed observation twice per week. Friday: Quick review of week's tallies to plan next week.",
            
            f"<b>CROSS-GRADE LEARNING MATERIALS (Create Using Old Books):</b> Make story cards from old textbook pictures: One picture can be used for Class 3 vocabulary practice, Class 4 sentence writing, and Class 5 paragraph creation. Example: Picture of market scene → Class 3 names items, Class 4 writes simple sentences, Class 5 creates story problems. Need 10 different picture cards total.",
            
            f"<b>STUDENT LEADERSHIP SYSTEM (Assign Monday):</b> Rotate weekly responsibilities: {student_names[0] if student_names else 'Advanced student'} = Material Manager (distributes/collects supplies), {student_names[1] if len(student_names) > 1 else 'Second student'} = Time Keeper (uses hand clap to signal transitions), {student_names[2] if len(student_names) > 2 else 'Third student'} = Help Coordinator (identifies who needs assistance). Change roles weekly so everyone gets leadership practice.",
            
            f"<b>FOCUSED PROGRESS TRACKING (Target 2 Skills Per Student):</b> Instead of tracking everything, focus on just 2 critical skills per student for 2 weeks: For example, if {student_names[0] if student_names else 'sample student'} struggles with reading comprehension and math word problems, track only these two. Use simple notebook page: Student name, Skill 1 daily rating (1-5), Skill 2 daily rating (1-5), weekly summary. This makes progress visible and manageable for teacher and student."
        ]
        
        return recommendations