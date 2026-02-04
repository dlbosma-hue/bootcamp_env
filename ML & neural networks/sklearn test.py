"""
TITANIC SURVIVAL PREDICTION - LOGISTIC REGRESSION CLASSIFIER
=============================================================
This script walks you through building a classification model step-by-step.
Each section explains the ROLE (why we do it) before the code (how we do it).

Author: Built as a learning tutorial for Dina
Dataset: Titanic passenger data (891 passengers)
Goal: Predict whether a passenger survived (1) or not (0)
"""

# =============================================================================
# STEP 1: IMPORT REQUIRED LIBRARIES
# =============================================================================
"""
ROLE: Libraries are pre-built toolkits that save us from writing code from scratch.
Think of them like apps on your phone - each one does something specific.
We import them at the top so they're available throughout our script.
"""

# pandas: The main tool for working with tabular data (like Excel spreadsheets)
# We nickname it 'pd' so we don't have to type 'pandas' every time
import pandas as pd

# numpy: Handles mathematical operations on arrays of numbers
# Essential for statistical calculations
import numpy as np

# sklearn (scikit-learn): The machine learning library
# We import specific tools we need for each task:

# train_test_split: Splits data into training and testing portions
from sklearn.model_selection import train_test_split

# LogisticRegression: The algorithm we'll use for classification
from sklearn.linear_model import LogisticRegression

# StandardScaler: Standardizes features to have mean=0 and std=1
from sklearn.preprocessing import StandardScaler

# f1_score: Measures how well our model performs
from sklearn.metrics import f1_score, classification_report, confusion_matrix

# warnings: Suppresses unnecessary warning messages for cleaner output
import warnings
warnings.filterwarnings('ignore')

print("✓ Step 1 Complete: All libraries imported successfully!\n")


# =============================================================================
# STEP 2: IMPORT AND VERIFY THE DATASET
# =============================================================================
"""
ROLE: We need data to train our model. This step loads the Titanic dataset from
your uploaded file and checks that it loaded correctly. Verification catches 
problems early before we waste time on broken data.
"""

# Load the dataset from your uploaded file into a pandas DataFrame
# A DataFrame is like a spreadsheet - rows of data with named columns
df = pd.read_csv('/mnt/user-data/uploads/titanic.csv')

# Verification checks to ensure data loaded correctly
print("=" * 60)
print("STEP 2: DATASET VERIFICATION")
print("=" * 60)

# Check 1: Dataset dimensions (rows x columns)
# We expect 891 passengers with 12 features about each
print(f"\nDataset shape: {df.shape[0]} rows × {df.shape[1]} columns")

# Check 2: Preview the first few rows to see what the data looks like
print("\nFirst 5 rows of data:")
print(df.head())

# Check 3: Column names and data types
# This shows us what information we have about each passenger
print("\nColumn names and data types:")
print(df.dtypes)

# Check 4: Basic statistics for numeric columns
# Helps us understand the range and distribution of values
print("\nBasic statistics:")
print(df.describe())

# Check 5: Check for missing values in each column
# Missing data is common and needs to be handled
print("\nMissing values per column:")
print(df.isnull().sum())

print("\n✓ Step 2 Complete: Dataset loaded and verified!\n")


# =============================================================================
# STEP 3: DATA PREPROCESSING
# =============================================================================
"""
ROLE: Raw data is messy. Machine learning models need clean, numeric data.
Preprocessing transforms our raw data into a format the model can understand.
Think of it like preparing ingredients before cooking - essential for a good result.
"""

print("=" * 60)
print("STEP 3: DATA PREPROCESSING")
print("=" * 60)

# -------------------------------------------------------------------------
# STEP 3a: Separate Features (X) from Target (y)
# -------------------------------------------------------------------------
"""
ROLE: We need to separate what we're trying to predict (Survived) from the
information we'll use to make predictions (all other columns).
- X = Features (input variables) - the information about each passenger
- y = Target (output variable) - what we want to predict (survived or not)
"""

# 'Survived' is our target - remove it from features
y = df['Survived']  # Target: 0 = died, 1 = survived
X = df.drop('Survived', axis=1)  # Features: everything except 'Survived'

print(f"\n3a. Separated features (X) and target (y)")
print(f"    Features shape: {X.shape}")
print(f"    Target distribution: {y.value_counts().to_dict()}")


# -------------------------------------------------------------------------
# STEP 3b: Remove Zero Variance Columns
# -------------------------------------------------------------------------
"""
ROLE: A column with zero variance has the same value for every row.
If everyone has the same value, that feature provides no useful information
for distinguishing survivors from non-survivors. We remove these to simplify
our model and avoid potential computational issues.
"""

# Calculate variance for numeric columns only
numeric_cols = X.select_dtypes(include=[np.number]).columns
variances = X[numeric_cols].var()

# Find columns where variance is zero (or very close to zero)
zero_variance_cols = variances[variances == 0].index.tolist()

if zero_variance_cols:
    print(f"\n3b. Removing zero variance columns: {zero_variance_cols}")
    X = X.drop(columns=zero_variance_cols)
else:
    print(f"\n3b. No zero variance columns found - all columns have variation")

print(f"    Remaining columns: {X.shape[1]}")


# -------------------------------------------------------------------------
# STEP 3c: Drop Rows with Missing Values
# -------------------------------------------------------------------------
"""
ROLE: Most algorithms can't handle missing values (NaN/null). We have options:
1. Drop rows with missing data (simple but loses information)
2. Fill in missing values (imputation)

Here we're dropping rows to keep things simple. In practice, you might
impute values for columns with few missing entries (like Age).
"""

# Count missing values before dropping
missing_before = X.isnull().sum().sum()
rows_before = X.shape[0]

# Drop rows where ANY column has a missing value
# We need to drop from both X and y to keep them aligned
X = X.dropna()
y = y.loc[X.index]  # Keep only the y values for rows that remain in X

rows_after = X.shape[0]
rows_dropped = rows_before - rows_after

print(f"\n3c. Dropped rows with missing values")
print(f"    Rows before: {rows_before}")
print(f"    Rows after: {rows_after}")
print(f"    Rows dropped: {rows_dropped} ({100*rows_dropped/rows_before:.1f}%)")


# -------------------------------------------------------------------------
# STEP 3d: Drop Non-Predictive Columns
# -------------------------------------------------------------------------
"""
ROLE: Some columns don't help predict survival:
- PassengerId: Just a row number, no predictive value
- Name: Each name is unique, can't generalize from it
- Ticket: Mostly unique identifiers
- Cabin: Too many missing values and unique categories

Keeping these would add noise or cause issues with encoding.
"""

# Columns to drop (identifiers and high-cardinality features)
cols_to_drop = ['PassengerId', 'Name', 'Ticket', 'Cabin']

# Only drop columns that exist (some might already be removed)
cols_to_drop = [col for col in cols_to_drop if col in X.columns]

X = X.drop(columns=cols_to_drop)

print(f"\n3d. Dropped non-predictive columns: {cols_to_drop}")
print(f"    Remaining features: {list(X.columns)}")


# -------------------------------------------------------------------------
# STEP 3e: Convert Text to Numbers (Dummify/One-Hot Encoding)
# -------------------------------------------------------------------------
"""
ROLE: Machine learning models only understand numbers, not text. We convert
categorical text columns (like 'Sex' and 'Embarked') into numeric format
using "one-hot encoding" (also called "dummifying").

Example: Sex column becomes two columns:
- Sex_female: 1 if female, 0 otherwise
- Sex_male: 1 if male, 0 otherwise

We use drop_first=True to avoid redundancy (if not female, must be male).
"""

# Identify categorical (text) columns
categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
print(f"\n3e. Converting categorical columns to numbers: {categorical_cols}")

# One-hot encode: creates new binary columns for each category
# drop_first=True removes one column per category to avoid multicollinearity
X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

print(f"    Features after encoding: {list(X.columns)}")
print(f"    New shape: {X.shape}")


# -------------------------------------------------------------------------
# STEP 3f: Check and Remove Highly Correlated Features
# -------------------------------------------------------------------------
"""
ROLE: Correlation measures how much two features move together.
If two features are highly correlated (e.g., >0.9), they provide redundant
information. This is called "multicollinearity" and can:
1. Make the model unstable
2. Make it hard to interpret which features are important

We remove one of each highly correlated pair to keep the model clean.
"""

# Calculate the correlation matrix for all numeric features
correlation_matrix = X.corr().abs()  # abs() because we care about strength, not direction

# Create a mask for the upper triangle (to avoid checking pairs twice)
# We only look at upper triangle because correlation(A,B) = correlation(B,A)
upper_triangle = np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
upper_corr = correlation_matrix.where(upper_triangle)

# Find columns with correlation > 0.9 (highly correlated)
threshold = 0.9
high_corr_cols = [column for column in upper_corr.columns 
                  if any(upper_corr[column] > threshold)]

print(f"\n3f. Checking for highly correlated features (threshold > {threshold})")

if high_corr_cols:
    print(f"    Removing highly correlated columns: {high_corr_cols}")
    X = X.drop(columns=high_corr_cols)
else:
    print(f"    No highly correlated features found")

# Show the correlation matrix for remaining features
print(f"\n    Correlation matrix of final features:")
print(X.corr().round(2))


# -------------------------------------------------------------------------
# STEP 3g: Split Data into Training and Testing Sets
# -------------------------------------------------------------------------
"""
ROLE: We need to test our model on data it hasn't seen during training.
This tells us how well it will perform on new, real-world data.

- Training set (80%): Used to teach the model patterns
- Testing set (20%): Held back to evaluate performance

random_state=42 ensures we get the same split every time (reproducibility).
"""

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2,      # 20% for testing
    random_state=42,    # For reproducibility
    stratify=y          # Keeps same proportion of survivors in both sets
)

print(f"\n3g. Split data into training and testing sets")
print(f"    Training set: {X_train.shape[0]} samples")
print(f"    Testing set: {X_test.shape[0]} samples")
print(f"    Training survival rate: {y_train.mean():.2%}")
print(f"    Testing survival rate: {y_test.mean():.2%}")


# -------------------------------------------------------------------------
# STEP 3h: Standardize the Features
# -------------------------------------------------------------------------
"""
ROLE: Standardization transforms each feature to have mean=0 and std=1.
This is important because:
1. Features are on different scales (Age: 0-80, Fare: 0-500)
2. Logistic regression uses gradient descent, which works better when
   features are on similar scales
3. Prevents features with large values from dominating the model

IMPORTANT: We fit the scaler on training data only, then transform both.
This prevents "data leakage" - using test data information during training.
"""

# Create the StandardScaler object
scaler = StandardScaler()

# Fit on training data (learns mean and std) and transform it
X_train_scaled = scaler.fit_transform(X_train)

# Transform test data using the SAME mean and std from training
# (never fit on test data!)
X_test_scaled = scaler.transform(X_test)

# Convert back to DataFrame for easier viewing (optional)
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)

print(f"\n3h. Standardized features (mean=0, std=1)")
print(f"    Training data statistics after scaling:")
print(f"    Mean: {X_train_scaled.mean().mean():.6f} (should be ~0)")
print(f"    Std:  {X_train_scaled.std().mean():.6f} (should be ~1)")

print("\n✓ Step 3 Complete: Data preprocessing finished!\n")


# =============================================================================
# STEP 4: BUILD THE LOGISTIC REGRESSION MODEL
# =============================================================================
"""
ROLE: Now we create and train our classification model.
Logistic Regression predicts the probability of belonging to a class (survived/died).
Despite its name, it's used for CLASSIFICATION, not regression.

How it works:
1. Learns weights for each feature
2. Combines features into a score
3. Passes score through sigmoid function to get probability (0-1)
4. If probability > 0.5, predicts "survived"
"""

print("=" * 60)
print("STEP 4: BUILD LOGISTIC REGRESSION MODEL")
print("=" * 60)

# Create the logistic regression model
# max_iter=1000 allows enough iterations for the algorithm to converge
model = LogisticRegression(max_iter=1000, random_state=42)

# Train the model on the training data
# This is where the model learns patterns from the data
model.fit(X_train_scaled, y_train)

print(f"\nModel trained successfully!")
print(f"\nModel coefficients (feature weights):")
print("-" * 40)

# Display feature importance (coefficients)
# Positive coefficient = increases survival probability
# Negative coefficient = decreases survival probability
feature_importance = pd.DataFrame({
    'Feature': X_train.columns,
    'Coefficient': model.coef_[0]
}).sort_values('Coefficient', ascending=False)

for _, row in feature_importance.iterrows():
    direction = "↑ survival" if row['Coefficient'] > 0 else "↓ survival"
    print(f"  {row['Feature']:15} : {row['Coefficient']:+.4f} ({direction})")

print(f"\nIntercept: {model.intercept_[0]:.4f}")

print("\n✓ Step 4 Complete: Model built and trained!\n")


# =============================================================================
# STEP 5: MAKE PREDICTIONS
# =============================================================================
"""
ROLE: Now we use our trained model to predict survival on the test data.
The model has never seen this data, so this simulates real-world performance.

We get two types of predictions:
1. Class predictions (0 or 1) - the final decision
2. Probability predictions (0.0 to 1.0) - confidence level
"""

print("=" * 60)
print("STEP 5: MAKE PREDICTIONS")
print("=" * 60)

# Make predictions on the test set
y_pred = model.predict(X_test_scaled)

# Get probability predictions (useful for understanding confidence)
y_pred_proba = model.predict_proba(X_test_scaled)

print(f"\nPredictions made on {len(y_pred)} test samples")
print(f"\nPrediction distribution:")
print(f"  Predicted to die (0):    {(y_pred == 0).sum()} passengers")
print(f"  Predicted to survive (1): {(y_pred == 1).sum()} passengers")

# Show a few example predictions with their probabilities
print(f"\nSample predictions (first 10):")
print("-" * 50)
print(f"{'Actual':<10} {'Predicted':<12} {'P(Die)':<10} {'P(Survive)':<10}")
print("-" * 50)

# Reset index to access by position
y_test_reset = y_test.reset_index(drop=True)

for i in range(min(10, len(y_pred))):
    actual = "Survived" if y_test_reset.iloc[i] == 1 else "Died"
    predicted = "Survived" if y_pred[i] == 1 else "Died"
    match = "✓" if y_test_reset.iloc[i] == y_pred[i] else "✗"
    print(f"{actual:<10} {predicted:<12} {y_pred_proba[i][0]:.2%}     {y_pred_proba[i][1]:.2%}    {match}")

print("\n✓ Step 5 Complete: Predictions made!\n")


# =============================================================================
# STEP 6: EVALUATE THE MODEL USING F1 SCORE
# =============================================================================
"""
ROLE: We need to measure how well our model performs. F1 Score is ideal for
classification because it balances two important metrics:

- Precision: Of all passengers we predicted would survive, how many actually did?
  (Are our positive predictions reliable?)

- Recall: Of all passengers who actually survived, how many did we correctly identify?
  (Are we finding all the survivors?)

F1 Score = 2 × (Precision × Recall) / (Precision + Recall)

It ranges from 0 (worst) to 1 (perfect). It's especially useful when
classes are imbalanced (more deaths than survivors in Titanic data).
"""

print("=" * 60)
print("STEP 6: MODEL EVALUATION")
print("=" * 60)

# Calculate F1 Score
f1 = f1_score(y_test, y_pred)

print(f"\n★ F1 SCORE: {f1:.4f} ★")
print(f"\nInterpretation: Our model achieves {f1:.1%} F1 score.")

if f1 >= 0.7:
    print("This is a reasonably good performance for the Titanic dataset!")
elif f1 >= 0.5:
    print("This is moderate performance - there's room for improvement.")
else:
    print("This suggests the model is struggling - consider more feature engineering.")

# Detailed classification report
print(f"\nDetailed Classification Report:")
print("-" * 50)
print(classification_report(y_test, y_pred, target_names=['Died (0)', 'Survived (1)']))

# Confusion Matrix - shows where the model is right and wrong
print(f"Confusion Matrix:")
print("-" * 30)
cm = confusion_matrix(y_test, y_pred)
print(f"                 Predicted")
print(f"                 Die    Survive")
print(f"Actual Die      {cm[0][0]:4}    {cm[0][1]:4}")
print(f"Actual Survive  {cm[1][0]:4}    {cm[1][1]:4}")

# Explain the confusion matrix
print(f"\nConfusion Matrix Breakdown:")
print(f"  True Negatives (correctly predicted death):     {cm[0][0]}")
print(f"  False Positives (predicted survive, but died):  {cm[0][1]}")
print(f"  False Negatives (predicted die, but survived):  {cm[1][0]}")
print(f"  True Positives (correctly predicted survival):  {cm[1][1]}")

# Calculate accuracy for comparison
accuracy = (y_pred == y_test).mean()
print(f"\nOverall Accuracy: {accuracy:.2%}")

print("\n✓ Step 6 Complete: Model evaluated!\n")


# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 60)
print("SUMMARY: COMPLETE PIPELINE OVERVIEW")
print("=" * 60)

print("""
What we accomplished:

1. IMPORTED LIBRARIES
   → Loaded tools for data handling (pandas), math (numpy), 
     and machine learning (sklearn)

2. LOADED & VERIFIED DATA
   → Imported Titanic dataset with 891 passengers
   → Checked structure, types, and missing values

3. PREPROCESSED DATA
   a) Separated features (X) from target (y)
   b) Removed zero variance columns (no useful information)
   c) Dropped rows with missing values
   d) Removed non-predictive columns (IDs, names)
   e) Converted text to numbers (one-hot encoding)
   f) Removed highly correlated features (reduce redundancy)
   g) Split into training (80%) and testing (20%) sets
   h) Standardized features (mean=0, std=1)

4. BUILT MODEL
   → Created and trained Logistic Regression classifier
   → Model learned which features predict survival

5. MADE PREDICTIONS
   → Applied model to unseen test data
   → Got survival predictions for each passenger

6. EVALUATED PERFORMANCE
   → Measured F1 Score to assess model quality
   → Analyzed precision, recall, and confusion matrix
""")

print(f"FINAL RESULT: F1 Score = {f1:.4f}")
print("=" * 60)
