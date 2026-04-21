import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_TO


def _shopping_list_html(shopping_list: dict, label: str) -> str:
    html = f"<h2>🛒 Einkaufsliste {label}</h2>"
    for category, items in shopping_list.items():
        html += f"<h3>{category}</h3><ul>"
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    name = item.get("name", item.get("Zutat", str(item)))
                    qty = item.get("quantity", item.get("Menge", ""))
                    store = item.get("store", item.get("Supermarkt", ""))
                    alt = item.get("alternative", item.get("Alternative", ""))
                    line = f"<strong>{name}</strong> — {qty}"
                    if store:
                        line += f" <em>({store})</em>"
                    if alt:
                        line += f" <br><small>💡 Alternative: {alt}</small>"
                    html += f"<li>{line}</li>"
                else:
                    html += f"<li>{item}</li>"
        html += "</ul>"
    return html


def _recipe_card_html(recipe: dict) -> str:
    name = recipe.get("name", "Rezept")
    url = recipe.get("source_url", "#")
    prep = recipe.get("prep_time_minutes", "?")
    calories = recipe.get("calories_per_adult", "?")
    protein = recipe.get("protein_per_adult_g", "?")
    child_note = recipe.get("child_adaptation", "")
    safe = recipe.get("pregnancy_safe", True)
    ingredients = recipe.get("ingredients", [])
    steps = recipe.get("steps", [])

    safety_badge = (
        '<span style="color:green">✅ Schwangerschaftssicher</span>'
        if safe
        else '<span style="color:red">⚠️ Nicht schwangerschaftssicher</span>'
    )

    ing_html = "".join(
        f"<li>{i if isinstance(i, str) else i.get('name','') + ' — ' + str(i.get('quantity',''))}</li>"
        for i in ingredients
    )
    steps_html = "".join(f"<li>{s}</li>" for s in steps)
    child_html = f'<p><strong>👶 Für das Kind:</strong> {child_note}</p>' if child_note else ""

    return f"""
<div style="border:1px solid #ddd;border-radius:8px;padding:16px;margin-bottom:16px;">
  <h3><a href="{url}">{name}</a></h3>
  <p>⏱ {prep} Min &nbsp;|&nbsp; 🔥 {calories} kcal &nbsp;|&nbsp; 💪 {protein}g Protein &nbsp;|&nbsp; {safety_badge}</p>
  <h4>Zutaten</h4><ul>{ing_html}</ul>
  <h4>Zubereitung</h4><ol>{steps_html}</ol>
  {child_html}
</div>
"""


def _weekly_overview_html(meal_plan: list[dict]) -> str:
    rows = ""
    for day in meal_plan:
        rows += f"""
<tr>
  <td><strong>{day.get('day','')}</strong></td>
  <td>{day.get('lunch_option_1','')}<br><small>{day.get('lunch_option_2','')}</small></td>
  <td>{day.get('dinner_option_1','')}<br><small>{day.get('dinner_option_2','')}</small></td>
</tr>"""

    return f"""
<h2>📅 Wochenübersicht</h2>
<table style="width:100%;border-collapse:collapse;">
  <thead>
    <tr style="background:#f5f5f5;">
      <th style="padding:8px;text-align:left;border:1px solid #ddd;">Tag</th>
      <th style="padding:8px;text-align:left;border:1px solid #ddd;">Mittagessen</th>
      <th style="padding:8px;text-align:left;border:1px solid #ddd;">Abendessen</th>
    </tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
"""


def render_email(plan_data: dict) -> str:
    meal_plan = plan_data.get("meal_plan", [])
    recipes = plan_data.get("recipes", [])
    sl1 = plan_data.get("shopping_list_1", {})
    sl2 = plan_data.get("shopping_list_2", {})

    recipe_cards = "".join(_recipe_card_html(r) for r in recipes)

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px; color: #333; }}
    h1 {{ color: #2d6a4f; }}
    h2 {{ color: #40916c; border-bottom: 2px solid #40916c; padding-bottom: 4px; }}
    h3 {{ color: #52b788; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 8px; border: 1px solid #ddd; vertical-align: top; }}
    a {{ color: #40916c; }}
    footer {{ text-align: center; color: #999; margin-top: 40px; font-size: 12px; }}
  </style>
</head>
<body>
  <h1>🥗 Dein Familien-Wochenplan</h1>

  {_weekly_overview_html(meal_plan)}

  <h2>📖 Rezeptkarten</h2>
  {recipe_cards}

  {_shopping_list_html(sl1, "Montag – Mittwoch")}
  {_shopping_list_html(sl2, "Donnerstag – Sonntag")}

  <footer>Erstellt von deinem Familien-Mahlzeitenplaner 🥦</footer>
</body>
</html>"""
    return html


def send_email(html_content: str, subject: str = "🥗 Dein Wochenplan ist da!") -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, EMAIL_TO, msg.as_string())
    print(f"E-Mail gesendet an {EMAIL_TO}")
