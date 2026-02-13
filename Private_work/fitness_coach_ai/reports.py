"""
PDF report generation
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from pathlib import Path
from typing import List

from models import Client, AnalysisResult, Prediction, Recommendation
from visualizations import generate_all_charts


class PDFReportGenerator:
    """Generate PDF reports for clients"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        ))

        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d')
        ))

    def generate_client_report(self, client: Client, analysis: AnalysisResult,
                              prediction: Prediction, recommendations: List[Recommendation],
                              output_path: str = None) -> str:
        """Generate comprehensive PDF report for a client"""
        if output_path is None:
            output_dir = Path("exports/reports")
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"{client.client_id}_report_{timestamp}.pdf"

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        story = []

        # Title
        title = Paragraph(
            f"FITNESS PROGRESS REPORT<br/>{client.name}",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Client Info
        info_data = [
            ["Client ID:", client.client_id],
            ["Report Date:", datetime.now().strftime("%B %d, %Y")],
            ["Start Date:", datetime.fromisoformat(client.start_date).strftime("%B %d, %Y")],
            ["Weeks Active:", str((datetime.now() - client.start_date_obj).days // 7)]
        ]

        info_table = Table(info_data, colWidths=[2 * inch, 3 * inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3 * inch))

        # Performance Metrics Section
        story.append(Paragraph("PERFORMANCE METRICS", self.styles['SectionHeader']))

        metrics_data = [
            ["Metric", "Value", "Status"],
            ["Workout Consistency", f"{analysis.consistency_score:.1f}%",
             self._get_status(analysis.consistency_score, 80, 60)],
            ["Missed Workouts", f"{analysis.missed_workouts_pct:.1f}%",
             self._get_status(100 - analysis.missed_workouts_pct, 70, 50)],
            ["Strength Progression", f"{analysis.progression_rate:+.1f}%",
             self._get_status(analysis.progression_rate, 5, 0)],
            ["Nutrition Compliance", f"{analysis.nutrition_compliance:.1f}%",
             self._get_status(analysis.nutrition_compliance, 80, 60)],
            ["Strength Trend", analysis.strength_trend.upper(), ""],
        ]

        metrics_table = Table(metrics_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.3 * inch))

        # Risk Assessment Section
        story.append(Paragraph("RISK ASSESSMENT", self.styles['SectionHeader']))

        risk_color = self._get_risk_color(prediction.dropout_risk)
        risk_data = [
            ["Dropout Risk Level:", prediction.dropout_risk.upper()],
            ["Risk Score:", f"{prediction.dropout_risk_score:.0f}%"],
            ["Plateau Detected:", "YES" if prediction.plateau_detected else "NO"],
        ]

        if prediction.plateau_detected:
            risk_data.append(["Weeks at Plateau:", str(prediction.weeks_at_plateau)])

        risk_data.append([
            "Intervention Needed:",
            "YES - URGENT" if prediction.intervention_needed else "NO"
        ])

        risk_table = Table(risk_data, colWidths=[2.5 * inch, 3 * inch])
        risk_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (1, 0), (1, 0), risk_color),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 0.3 * inch))

        # Recommendations Section
        story.append(Paragraph("AI RECOMMENDATIONS", self.styles['SectionHeader']))

        for i, rec in enumerate(recommendations, 1):
            priority_color = self._get_priority_color(rec.priority)

            rec_title = Paragraph(
                f"<b>#{i}: {rec.suggestion}</b>",
                self.styles['Normal']
            )
            story.append(rec_title)

            rec_details = [
                ["Priority:", rec.priority.upper()],
                ["Category:", rec.category.upper()],
                ["Status:", rec.status.upper()],
            ]

            rec_table = Table(rec_details, colWidths=[1 * inch, 4 * inch])
            rec_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
                ('BACKGROUND', (1, 0), (1, 0), priority_color),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(rec_table)

            reasoning = Paragraph(
                f"<i>Reasoning:</i> {rec.reasoning}",
                self.styles['Normal']
            )
            story.append(reasoning)
            story.append(Spacer(1, 0.15 * inch))

        # Page break before charts
        story.append(PageBreak())

        # Charts Section
        story.append(Paragraph("PERFORMANCE CHARTS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2 * inch))

        # Generate and include charts
        chart_paths = generate_all_charts(client)

        for chart_path in chart_paths[:4]:  # Include up to 4 charts
            try:
                img = Image(chart_path, width=6 * inch, height=3 * inch)
                story.append(img)
                story.append(Spacer(1, 0.2 * inch))
            except Exception as e:
                print(f"Warning: Could not include chart {chart_path}: {e}")

        # Footer
        story.append(Spacer(1, 0.3 * inch))
        footer = Paragraph(
            "<i>Generated by Fitness Coach AI Assistant</i>",
            self.styles['Normal']
        )
        story.append(footer)

        # Build PDF
        doc.build(story)
        return str(output_path)

    def _get_status(self, value: float, good_threshold: float, ok_threshold: float) -> str:
        """Get status indicator based on value"""
        if value >= good_threshold:
            return "✓ Good"
        elif value >= ok_threshold:
            return "⚠ Needs Improvement"
        else:
            return "✗ Poor"

    def _get_risk_color(self, risk_level: str) -> colors.Color:
        """Get color for risk level"""
        if risk_level == "high":
            return colors.HexColor('#e74c3c')
        elif risk_level == "medium":
            return colors.HexColor('#f39c12')
        else:
            return colors.HexColor('#27ae60')

    def _get_priority_color(self, priority: str) -> colors.Color:
        """Get color for priority level"""
        if priority == "high":
            return colors.HexColor('#e74c3c')
        elif priority == "medium":
            return colors.HexColor('#f39c12')
        else:
            return colors.HexColor('#3498db')
