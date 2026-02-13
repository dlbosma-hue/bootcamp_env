"""
Interactive CLI interface
"""

import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from datetime import datetime, timedelta
from typing import Optional, List

from models import Client, WorkoutEntry, NutritionEntry
from data_manager import DataManager
from analysis import analyze_client, validate_client_data
from predictions import predict_dropout_risk, DropoutPredictor, detect_anomalies
from recommendations import generate_recommendations, prioritize_recommendations, format_recommendation_for_display
from reports import PDFReportGenerator
from visualizations import generate_all_charts

console = Console()
data_manager = DataManager()
predictor = DropoutPredictor()
pdf_generator = PDFReportGenerator()


def display_header():
    """Display application header"""
    console.print(Panel.fit(
        "[bold cyan]FITNESS COACH AI ASSISTANT[/bold cyan]\n"
        "[dim]Intelligent client management & performance analysis[/dim]",
        border_style="cyan"
    ))
    console.print()


def main_menu() -> str:
    """Display main menu and get user choice"""
    choices = [
        "📊 View All Clients Dashboard",
        "👤 Manage Individual Client",
        "➕ Add New Client",
        "📈 Generate Client Report",
        "📁 Import/Export Data",
        "🔧 Settings",
        "❌ Exit"
    ]

    choice = questionary.select(
        "What would you like to do?",
        choices=choices
    ).ask()

    return choice


def client_menu(client: Client) -> str:
    """Display client-specific menu"""
    choices = [
        "📊 View Analysis & Recommendations",
        "💪 Add Workout Entry",
        "🥗 Add Nutrition Entry",
        "📈 View Progress Charts",
        "📄 Generate PDF Report",
        "✏️  Edit Client Info",
        "🗑️  Delete Client",
        "⬅️  Back to Main Menu"
    ]

    choice = questionary.select(
        f"Managing: {client.name} ({client.client_id})",
        choices=choices
    ).ask()

    return choice


def display_all_clients_dashboard():
    """Display dashboard with all clients"""
    console.clear()
    display_header()

    clients = data_manager.get_all_clients()

    if not clients:
        console.print("[yellow]No clients found. Add a new client to get started.[/yellow]")
        return

    console.print(f"[bold]Total Clients: {len(clients)}[/bold]\n")

    table = Table(title="Client Dashboard", box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Consistency", justify="right")
    table.add_column("Progression", justify="right")
    table.add_column("Dropout Risk", justify="center")
    table.add_column("Status", justify="center")

    for client in clients:
        try:
            analysis = analyze_client(client)
            prediction = predict_dropout_risk(client, analysis, predictor)

            # Format consistency
            consistency_emoji = "✓" if analysis.consistency_score >= 80 else "⚠" if analysis.consistency_score >= 60 else "✗"
            consistency_str = f"{consistency_emoji} {analysis.consistency_score:.0f}%"

            # Format progression
            prog_emoji = "📈" if analysis.progression_rate > 5 else "➡️" if analysis.progression_rate >= 0 else "📉"
            progression_str = f"{prog_emoji} {analysis.progression_rate:+.1f}%"

            # Format risk
            risk_emoji = "🔴" if prediction.dropout_risk == "high" else "🟡" if prediction.dropout_risk == "medium" else "🟢"
            risk_str = f"{risk_emoji} {prediction.dropout_risk.upper()}"

            # Status
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
        except Exception as e:
            console.print(f"[red]Error analyzing {client.name}: {e}[/red]")

    console.print(table)
    console.print()
    input("Press Enter to continue...")


def select_client() -> Optional[Client]:
    """Prompt user to select a client"""
    clients = data_manager.get_all_clients()

    if not clients:
        console.print("[yellow]No clients found.[/yellow]")
        return None

    choices = [f"{c.name} ({c.client_id})" for c in clients]
    choices.append("← Cancel")

    choice = questionary.select(
        "Select a client:",
        choices=choices
    ).ask()

    if choice == "← Cancel":
        return None

    # Extract client_id from choice
    client_id = choice.split("(")[1].strip(")")
    return data_manager.load_client(client_id)


def add_new_client():
    """Add a new client"""
    console.clear()
    display_header()
    console.print("[bold cyan]Add New Client[/bold cyan]\n")

    name = questionary.text("Client Name:").ask()
    client_id = questionary.text(
        "Client ID (leave blank for auto-generate):",
        default=""
    ).ask()

    if not client_id:
        # Auto-generate ID from name
        client_id = name.replace(" ", "").upper()[:3] + datetime.now().strftime("%Y%m%d")

    email = questionary.text("Email (optional):").ask()
    phone = questionary.text("Phone (optional):").ask()

    target_workouts = questionary.text(
        "Target workouts per week:",
        default="3"
    ).ask()

    target_calories = questionary.text(
        "Target daily calories:",
        default="2000"
    ).ask()

    target_protein = questionary.text(
        "Target daily protein (g):",
        default="150"
    ).ask()

    client = Client(
        name=name,
        client_id=client_id,
        start_date=datetime.now().isoformat(),
        email=email,
        phone=phone,
        target_workouts_per_week=int(target_workouts),
        target_calories=int(target_calories),
        target_protein=int(target_protein)
    )

    if data_manager.save_client(client):
        console.print(f"\n[green]✓ Client {name} added successfully![/green]")
    else:
        console.print(f"\n[red]✗ Failed to save client.[/red]")

    input("\nPress Enter to continue...")


def add_workout_entry(client: Client):
    """Add a workout entry for a client"""
    console.clear()
    console.print(f"[bold cyan]Add Workout Entry for {client.name}[/bold cyan]\n")

    date_input = questionary.text(
        "Date (YYYY-MM-DD, or leave blank for today):",
        default=""
    ).ask()

    if not date_input:
        workout_date = datetime.now()
    else:
        workout_date = datetime.fromisoformat(date_input)

    exercise = questionary.text("Exercise name:").ask()
    sets = int(questionary.text("Sets:").ask())
    reps = int(questionary.text("Reps:").ask())
    weight = float(questionary.text("Weight (lbs):").ask())
    form_notes = questionary.text("Form notes (optional):").ask()

    workout = WorkoutEntry.from_datetime(
        date=workout_date,
        exercise=exercise,
        sets=sets,
        reps=reps,
        weight=weight,
        form_notes=form_notes,
        completed=True
    )

    client.workout_logs.append(workout)

    if data_manager.save_client(client):
        console.print(f"\n[green]✓ Workout entry added![/green]")
    else:
        console.print(f"\n[red]✗ Failed to save workout.[/red]")

    # Ask if they want to add another
    add_more = questionary.confirm("Add another workout entry?").ask()
    if add_more:
        add_workout_entry(client)
    else:
        input("\nPress Enter to continue...")


def add_nutrition_entry(client: Client):
    """Add a nutrition entry for a client"""
    console.clear()
    console.print(f"[bold cyan]Add Nutrition Entry for {client.name}[/bold cyan]\n")

    date_input = questionary.text(
        "Date (YYYY-MM-DD, or leave blank for today):",
        default=""
    ).ask()

    if not date_input:
        nutrition_date = datetime.now()
    else:
        nutrition_date = datetime.fromisoformat(date_input)

    calories = int(questionary.text("Calories:").ask())
    protein = int(questionary.text("Protein (g):").ask())
    carbs = int(questionary.text("Carbs (g):").ask())
    fats = int(questionary.text("Fats (g):").ask())
    meals_logged = int(questionary.text("Meals logged:").ask())
    compliance_note = questionary.text("Compliance note (optional):").ask()

    nutrition = NutritionEntry.from_datetime(
        date=nutrition_date,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fats=fats,
        meals_logged=meals_logged,
        compliance_note=compliance_note
    )

    client.nutrition_logs.append(nutrition)

    if data_manager.save_client(client):
        console.print(f"\n[green]✓ Nutrition entry added![/green]")
    else:
        console.print(f"\n[red]✗ Failed to save nutrition entry.[/red]")

    input("\nPress Enter to continue...")


def view_client_analysis(client: Client):
    """Display comprehensive analysis for a client"""
    console.clear()
    display_header()

    console.print(f"[bold cyan]Analysis Report: {client.name}[/bold cyan]")
    console.print(f"Client ID: {client.client_id}")
    console.print(f"Weeks Active: {(datetime.now() - client.start_date_obj).days // 7}\n")

    # Validation
    validation = validate_client_data(client)
    if not validation.is_valid:
        console.print("[red]⚠ DATA VALIDATION ERRORS:[/red]")
        for error in validation.errors:
            console.print(f"  • {error}")
        input("\nPress Enter to continue...")
        return

    if validation.warnings:
        console.print("[yellow]⚠ WARNINGS:[/yellow]")
        for warning in validation.warnings[:5]:  # Show first 5 warnings
            console.print(f"  • {warning}")
        console.print()

    # Analysis
    analysis = analyze_client(client)
    prediction = predict_dropout_risk(client, analysis, predictor)

    # Display metrics table
    metrics_table = Table(title="Performance Metrics", box=box.ROUNDED)
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", justify="right", style="bold")

    metrics_table.add_row("Workout Consistency", f"{analysis.consistency_score:.1f}%")
    metrics_table.add_row("Workouts Completed", f"{analysis.actual_workouts}/{analysis.expected_workouts}")
    metrics_table.add_row("Missed Workouts", f"{analysis.missed_workouts_pct:.1f}%")
    metrics_table.add_row("Strength Progression", f"{analysis.progression_rate:+.1f}%")
    metrics_table.add_row("Nutrition Compliance", f"{analysis.nutrition_compliance:.1f}%")
    metrics_table.add_row("Strength Trend", analysis.strength_trend.upper())

    console.print(metrics_table)
    console.print()

    # Predictions
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

    console.print("[bold cyan]AI RECOMMENDATIONS:[/bold cyan]")
    for i, rec in enumerate(recommendations, 1):
        formatted = format_recommendation_for_display(rec, i)
        console.print(formatted)

    input("\nPress Enter to continue...")


def generate_report(client: Client):
    """Generate PDF report for client"""
    console.clear()
    console.print(f"[bold cyan]Generating Report for {client.name}...[/bold cyan]\n")

    try:
        # Run analysis
        validation = validate_client_data(client)
        if not validation.is_valid:
            console.print("[red]Cannot generate report: Invalid data[/red]")
            input("\nPress Enter to continue...")
            return

        analysis = analyze_client(client)
        prediction = predict_dropout_risk(client, analysis, predictor)
        recommendations = generate_recommendations(client, analysis, prediction)
        recommendations = prioritize_recommendations(recommendations)

        # Generate PDF
        with console.status("[bold green]Creating PDF report..."):
            pdf_path = pdf_generator.generate_client_report(
                client, analysis, prediction, recommendations
            )

        console.print(f"\n[green]✓ PDF report generated successfully![/green]")
        console.print(f"Location: {pdf_path}")

        # Generate charts
        if questionary.confirm("Generate performance charts?", default=True).ask():
            with console.status("[bold green]Creating charts..."):
                chart_paths = generate_all_charts(client)

            console.print(f"\n[green]✓ Generated {len(chart_paths)} charts![/green]")
            for path in chart_paths:
                console.print(f"  • {path}")

    except Exception as e:
        console.print(f"[red]Error generating report: {e}[/red]")

    input("\nPress Enter to continue...")


def run():
    """Main application loop"""
    while True:
        console.clear()
        display_header()

        choice = main_menu()

        if "View All Clients Dashboard" in choice:
            display_all_clients_dashboard()

        elif "Manage Individual Client" in choice:
            client = select_client()
            if client:
                manage_client(client)

        elif "Add New Client" in choice:
            add_new_client()

        elif "Generate Client Report" in choice:
            client = select_client()
            if client:
                generate_report(client)

        elif "Import/Export Data" in choice:
            import_export_menu()

        elif "Exit" in choice:
            console.print("\n[cyan]Thanks for using Fitness Coach AI! 💪[/cyan]")
            break


def manage_client(client: Client):
    """Manage a specific client"""
    while True:
        console.clear()
        display_header()

        choice = client_menu(client)

        if "View Analysis" in choice:
            view_client_analysis(client)

        elif "Add Workout Entry" in choice:
            add_workout_entry(client)
            # Reload client to get updated data
            client = data_manager.load_client(client.client_id)

        elif "Add Nutrition Entry" in choice:
            add_nutrition_entry(client)
            # Reload client
            client = data_manager.load_client(client.client_id)

        elif "View Progress Charts" in choice:
            console.clear()
            with console.status("[bold green]Generating charts..."):
                chart_paths = generate_all_charts(client)
            console.print(f"[green]✓ Generated {len(chart_paths)} charts![/green]")
            for path in chart_paths:
                console.print(f"  • {path}")
            input("\nPress Enter to continue...")

        elif "Generate PDF Report" in choice:
            generate_report(client)

        elif "Delete Client" in choice:
            confirm = questionary.confirm(
                f"Are you sure you want to delete {client.name}? This cannot be undone."
            ).ask()
            if confirm:
                if data_manager.delete_client(client.client_id):
                    console.print(f"[green]✓ Client deleted.[/green]")
                    input("\nPress Enter to continue...")
                    break

        elif "Back to Main Menu" in choice:
            break


def import_export_menu():
    """Import/Export data menu"""
    choices = [
        "📤 Export Client to CSV",
        "📥 Import Workouts from CSV",
        "📥 Import Nutrition from CSV",
        "💾 Backup All Data",
        "⬅️ Back"
    ]

    choice = questionary.select("Import/Export Options:", choices=choices).ask()

    if "Export Client to CSV" in choice:
        client = select_client()
        if client:
            if data_manager.export_client_to_csv(client):
                console.print(f"[green]✓ Exported {client.name} to CSV![/green]")
            input("\nPress Enter to continue...")

    elif "Backup All Data" in choice:
        if data_manager.backup_all_data():
            console.print("[green]✓ Backup created successfully![/green]")
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    run()
