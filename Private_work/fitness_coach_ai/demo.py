"""
Demo script showing the Fitness Coach AI in action
Run this to see a complete analysis of all demo clients
"""

from rich.console import Console
from rich.table import Table
from rich import box

from data_manager import DataManager
from analysis import analyze_client, validate_client_data
from predictions import predict_dropout_risk, DropoutPredictor, detect_anomalies
from recommendations import generate_recommendations, prioritize_recommendations
from reports import PDFReportGenerator
from visualizations import generate_all_charts

console = Console()
data_manager = DataManager()
predictor = DropoutPredictor()
pdf_generator = PDFReportGenerator()


def demo_dashboard():
    """Show the multi-client dashboard"""
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]       FITNESS COACH AI ASSISTANT - DEMO       [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]\n")

    clients = data_manager.get_all_clients()

    console.print(f"[bold]Total Clients: {len(clients)}[/bold]\n")

    # Dashboard table
    table = Table(title="📊 CLIENT DASHBOARD", box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Name", style="bold", width=18)
    table.add_column("Consistency", justify="right", width=14)
    table.add_column("Progression", justify="right", width=14)
    table.add_column("Dropout Risk", justify="center", width=16)
    table.add_column("Status", justify="center", width=20)

    for client in clients:
        analysis = analyze_client(client)
        prediction = predict_dropout_risk(client, analysis, predictor)

        # Format values
        consistency_emoji = "✓" if analysis.consistency_score >= 80 else "⚠" if analysis.consistency_score >= 60 else "✗"
        consistency_str = f"{consistency_emoji} {analysis.consistency_score:.0f}%"

        prog_emoji = "📈" if analysis.progression_rate > 5 else "➡️" if analysis.progression_rate >= 0 else "📉"
        progression_str = f"{prog_emoji} {analysis.progression_rate:+.1f}%"

        risk_emoji = "🔴" if prediction.dropout_risk == "high" else "🟡" if prediction.dropout_risk == "medium" else "🟢"
        risk_str = f"{risk_emoji} {prediction.dropout_risk.upper()}"

        if prediction.intervention_needed:
            status = "[red]⚠ NEEDS ATTENTION[/red]"
        elif analysis.consistency_score > 80:
            status = "[green]✓ On Track[/green]"
        else:
            status = "[yellow]○ Monitoring[/yellow]"

        table.add_row(
            client.client_id,
            client.name,
            consistency_str,
            progression_str,
            risk_str,
            status
        )

    console.print(table)
    console.print()


def demo_detailed_analysis(client_id: str):
    """Show detailed analysis for a specific client"""
    client = data_manager.load_client(client_id)

    if not client:
        console.print(f"[red]Client {client_id} not found[/red]")
        return

    console.print("\n[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]")
    console.print(f"[bold cyan]       DETAILED ANALYSIS: {client.name}       [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]\n")

    # Validation
    validation = validate_client_data(client)

    if not validation.is_valid:
        console.print("[red]⚠ DATA VALIDATION ERRORS:[/red]")
        for error in validation.errors:
            console.print(f"  • {error}")
        return

    if validation.warnings:
        console.print("[yellow]⚠ WARNINGS:[/yellow]")
        for warning in validation.warnings[:3]:  # Show first 3
            console.print(f"  • {warning}")
        if len(validation.warnings) > 3:
            console.print(f"  ... and {len(validation.warnings) - 3} more warnings")
        console.print()

    # Analysis
    analysis = analyze_client(client)
    prediction = predict_dropout_risk(client, analysis, predictor)

    # Metrics table
    metrics_table = Table(title="Performance Metrics", box=box.SIMPLE)
    metrics_table.add_column("Metric", style="cyan", width=25)
    metrics_table.add_column("Value", justify="right", style="bold", width=15)

    metrics_table.add_row("Workout Consistency", f"{analysis.consistency_score:.1f}%")
    metrics_table.add_row("Workouts Completed", f"{analysis.actual_workouts}/{analysis.expected_workouts}")
    metrics_table.add_row("Missed Workouts", f"{analysis.missed_workouts_pct:.1f}%")
    metrics_table.add_row("Strength Progression", f"{analysis.progression_rate:+.1f}%")
    metrics_table.add_row("Nutrition Compliance", f"{analysis.nutrition_compliance:.1f}%")
    metrics_table.add_row("Strength Trend", analysis.strength_trend.upper())

    console.print(metrics_table)
    console.print()

    # Risk assessment
    risk_color = "red" if prediction.dropout_risk == "high" else "yellow" if prediction.dropout_risk == "medium" else "green"
    console.print(f"[bold]DROPOUT RISK:[/bold] [{risk_color}]{prediction.dropout_risk.upper()} ({prediction.dropout_risk_score:.0f}%)[/{risk_color}]")

    if prediction.plateau_detected:
        console.print(f"[yellow]⚠ Plateau detected: {prediction.weeks_at_plateau} weeks at same weight[/yellow]")

    if prediction.intervention_needed:
        console.print("[red]🚨 INTERVENTION RECOMMENDED[/red]")

    console.print()

    # Anomalies
    anomalies = detect_anomalies(client)
    if anomalies:
        console.print("[bold yellow]⚠ ANOMALIES DETECTED:[/bold yellow]")
        for anomaly in anomalies:
            console.print(f"  • {anomaly}")
        console.print()

    # Recommendations
    recommendations = generate_recommendations(client, analysis, prediction)
    recommendations = prioritize_recommendations(recommendations)

    console.print("[bold cyan]AI RECOMMENDATIONS:[/bold cyan]\n")

    for i, rec in enumerate(recommendations, 1):
        priority_emoji = "🔴" if rec.priority == "high" else "🟡" if rec.priority == "medium" else "🟢"
        console.print(f"{priority_emoji} [bold]Recommendation #{i}[/bold] [{rec.category.upper()}]")
        console.print(f"   {rec.suggestion}\n")
        console.print(f"   [dim]Reasoning:[/dim]")

        for line in rec.reasoning.split(". "):
            if line.strip():
                console.print(f"   • {line.strip('.')}.")

        approval_status = "⏳ PENDING COACH APPROVAL" if rec.requires_coach_approval else "✓ AUTO-APPROVED"
        console.print(f"   [dim]{approval_status}[/dim]\n")

    console.print("[dim]═══════════════════════════════════════════════════════[/dim]\n")


def demo_generate_reports():
    """Generate PDF reports and charts for all clients"""
    console.print("\n[bold cyan]📄 Generating Reports & Charts...[/bold cyan]\n")

    clients = data_manager.get_all_clients()

    for client in clients:
        try:
            console.print(f"Processing [bold]{client.name}[/bold]...")

            # Analysis
            analysis = analyze_client(client)
            prediction = predict_dropout_risk(client, analysis, predictor)
            recommendations = generate_recommendations(client, analysis, prediction)

            # Generate charts
            console.print("  • Generating charts...")
            chart_paths = generate_all_charts(client)
            console.print(f"    ✓ Created {len(chart_paths)} charts")

            # Generate PDF
            console.print("  • Creating PDF report...")
            pdf_path = pdf_generator.generate_client_report(
                client, analysis, prediction, recommendations
            )
            console.print(f"    ✓ PDF saved to: {pdf_path}")

        except Exception as e:
            console.print(f"  [red]✗ Error: {e}[/red]")

        console.print()

    console.print("[green]✓ All reports generated successfully![/green]\n")


def main():
    """Run the demo"""
    # Show dashboard
    demo_dashboard()

    # Show detailed analysis for each client
    console.print("\n[bold]═══ DETAILED CLIENT ANALYSES ═══[/bold]\n")
    for client_id in ["JS001", "SJ002", "MD003"]:
        demo_detailed_analysis(client_id)

    # Generate reports
    demo_generate_reports()

    # Summary
    console.print("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold green]✓ Demo Complete![/bold green]")
    console.print("\n[bold]What was generated:[/bold]")
    console.print("  • Client analyses for 3 demo clients")
    console.print("  • Dropout risk predictions")
    console.print("  • Personalized recommendations")
    console.print("  • Progress charts (in exports/charts/)")
    console.print("  • PDF reports (in exports/reports/)")
    console.print("\n[dim]To run the interactive CLI: python main.py[/dim]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]\n")


if __name__ == "__main__":
    main()
