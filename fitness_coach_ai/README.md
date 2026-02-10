# Fitness Coach AI Assistant 💪

An intelligent client management system for fitness coaches that uses machine learning to analyze client performance, predict dropout risk, and generate personalized recommendations.

## Features

### 🎯 Core Functionality
- **Client Management**: Track multiple clients with detailed workout and nutrition logs
- **Performance Analysis**: Automated analysis of strength progression, consistency, and nutrition compliance
- **ML-Powered Predictions**: Predict client dropout risk using machine learning models
- **Smart Recommendations**: AI-generated coaching suggestions prioritized by urgency
- **Data Visualization**: Beautiful charts showing progress trends over time
- **PDF Reports**: Generate comprehensive client reports with charts and recommendations

### 📊 Analysis Capabilities
- Strength progression tracking (per exercise and overall)
- Workout consistency scoring
- Nutrition compliance analysis
- Plateau detection (identifies when clients are stuck)
- Anomaly detection (sudden behavior changes)
- Dropout risk prediction (low/medium/high)

### 📈 Visualizations
- Strength progression charts (by exercise)
- Workout consistency graphs
- Nutrition compliance trends
- Multi-exercise comparisons
- Training volume analysis

### 💾 Data Management
- JSON-based storage (easily human-readable)
- CSV import/export for integration with other tools
- Automatic backup functionality
- Data validation and error checking

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Navigate to the project directory**:
```bash
cd fitness_coach_ai
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Generate demo data** (optional but recommended for first run):
```bash
python main.py --demo
```

4. **Run the application**:
```bash
python main.py
```

## Usage

### Starting the Application

```bash
python main.py
```

This launches the interactive CLI with a beautiful menu interface.

### Main Menu Options

1. **📊 View All Clients Dashboard**
   - See overview of all clients
   - Quick status indicators for each client
   - Dropout risk levels and performance metrics

2. **👤 Manage Individual Client**
   - View detailed analysis and recommendations
   - Add workout entries
   - Add nutrition entries
   - Generate progress charts
   - Create PDF reports

3. **➕ Add New Client**
   - Create new client profile
   - Set goals and targets
   - Auto-generates client ID

4. **📈 Generate Client Report**
   - Comprehensive PDF report
   - Includes all charts and analysis
   - Professional format for sharing

5. **📁 Import/Export Data**
   - Export client data to CSV
   - Import workouts/nutrition from CSV
   - Create backups

### Adding Data

#### Manual Entry (via CLI)
1. Select "Manage Individual Client"
2. Choose "Add Workout Entry" or "Add Nutrition Entry"
3. Fill in the prompted information

#### Bulk Import (via CSV)
1. Create a CSV file with the appropriate format
2. Use "Import/Export Data" menu
3. Select "Import Workouts from CSV"

### Generating Reports

1. Select "Generate Client Report" from main menu
2. Choose the client
3. The system will:
   - Analyze all client data
   - Generate predictions
   - Create recommendations
   - Produce PDF report with charts
   - Save to `exports/reports/` directory

## Project Structure

```
fitness_coach_ai/
├── main.py                 # Entry point
├── cli.py                  # Interactive CLI interface
├── models.py               # Data models (Client, Workout, Nutrition)
├── data_manager.py         # Data persistence (save/load)
├── analysis.py             # Performance analysis functions
├── predictions.py          # ML prediction models
├── recommendations.py      # Recommendation engine
├── visualizations.py       # Chart generation
├── reports.py              # PDF report generation
├── requirements.txt        # Python dependencies
└── data/
    └── clients/            # Client JSON files
```

## Understanding the Analysis

### Metrics Explained

- **Workout Consistency**: Percentage of planned workouts completed
  - 80%+: Excellent ✓
  - 60-79%: Needs improvement ⚠
  - <60%: Poor ✗

- **Strength Progression**: Percentage change in weights lifted
  - 5%+: Great progress 📈
  - 0-5%: Slow progress ➡️
  - Negative: Declining 📉

- **Nutrition Compliance**: Combined score based on:
  - Hitting calorie targets
  - Hitting protein targets
  - Meal tracking consistency

- **Dropout Risk**: Probability of client quitting
  - Low (0-35%): Client engaged 🟢
  - Medium (35-60%): Warning signs 🟡
  - High (60%+): Intervention needed 🔴

### Recommendations Priority

- **🔴 High Priority**: Urgent action needed (dropout risk, declining performance)
- **🟡 Medium Priority**: Should address soon (consistency issues, nutrition)
- **🟢 Low Priority**: Nice to have (optimization, positive reinforcement)

## ML Models

### Dropout Prediction Model

The system uses a **Logistic Regression** model that considers:
- Missed workout percentage
- Nutrition compliance
- Strength progression rate
- Workout consistency
- Length of plateau
- Total engagement history

**Note**: With <5 clients, the system uses a rule-based fallback. With 5+ clients, it trains an ML model for more accurate predictions.

### Performance Prediction

Uses **Linear Regression** to forecast future strength progression based on historical trends.

## Data Privacy & Security

- All data stored locally on your machine
- No cloud sync or external data sharing
- Client data in easily-auditable JSON format
- Regular backups recommended (use built-in backup feature)

## Tips for Best Results

1. **Consistent Data Entry**: Enter workout/nutrition data regularly (weekly minimum)
2. **Detailed Form Notes**: Include notes about form issues - the AI uses these for recommendations
3. **Review Recommendations**: AI suggestions require coach approval before implementation
4. **Regular Reports**: Generate monthly reports to track long-term trends
5. **Backup Data**: Use the backup feature weekly

## Customization

### Adjusting Targets

You can customize per client:
- Target workouts per week
- Target daily calories
- Target daily protein

### Adding New Exercises

Simply enter new exercise names when logging workouts. The system automatically tracks all unique exercises.

## Troubleshooting

### Issue: "No clients found"
- **Solution**: Generate demo data with `python main.py --demo` or add a new client

### Issue: Charts not generating
- **Solution**: Ensure matplotlib and seaborn are installed correctly
- Check that you have sufficient workout data (minimum 3 workouts per exercise)

### Issue: PDF generation fails
- **Solution**: Ensure reportlab is installed
- Check you have write permissions in exports/reports/ directory

## Future Enhancements

Potential features for future versions:
- Mobile app integration
- Automated client email reports
- Video form analysis integration
- Advanced periodization suggestions
- Multi-coach collaboration features
- Cloud sync (optional)

## Support

For issues or questions:
1. Check this README
2. Review demo data examples
3. Check error messages in terminal

## License

This project is for personal use. Modify as needed for your coaching business.

---

**Built with**: Python, scikit-learn, matplotlib, rich, questionary, reportlab

**Perfect for**: Personal trainers, strength coaches, online fitness coaches
