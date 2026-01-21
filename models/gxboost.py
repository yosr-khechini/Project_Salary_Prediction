import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBRegressor
import shap

# -----------------------------
# Plotting functions
# -----------------------------
def plot_predictions(y_true, y_pred, model_name):
    plt.figure(figsize=(6,6))
    sns.scatterplot(x=y_true, y=y_pred, alpha=0.7)
    plt.plot([y_true.min(), y_true.max()],
             [y_true.min(), y_true.max()],
             'r--', lw=2)
    plt.xlabel("Actual Salary")
    plt.ylabel("Predicted Salary")
    plt.title(f"Predicted vs Actual - {model_name}")
    plt.tight_layout()
    plt.show()

def plot_feature_importance(model, feature_names):
    importance = model.feature_importances_
    sorted_idx = importance.argsort()[::-1]
    plt.figure(figsize=(8,5))
    sns.barplot(x=importance[sorted_idx],
                y=[feature_names[i] for i in sorted_idx],
                palette="viridis")
    plt.title("Feature Importance - XGBoost")
    plt.xlabel("Importance Score")
    plt.ylabel("Features")
    plt.tight_layout()
    plt.show()

# -----------------------------
# Clean keys
# -----------------------------
def clean_keys(df):
    df["Year"] = pd.to_numeric(df["Year"].astype(str).str.strip(), errors="coerce")
    df["Month"] = pd.to_numeric(df["Month"].astype(str).str.strip(), errors="coerce")
    df = df.dropna(subset=["Year", "Month"])
    df["Year"] = df["Year"].astype(int)
    df["Month"] = df["Month"].astype(int)
    return df

# -----------------------------
# Step 1: Load Data
# -----------------------------
def load_data():
    df1 = pd.read_csv(r"C:\L2 DSI\Stage\Project_Salary_Prediction\data\processed\monthly_departures.csv")
    df2 = pd.read_csv(r"C:\L2 DSI\Stage\Project_Salary_Prediction\data\processed\recruitments_by_year_month.csv")
    df3 = pd.read_csv(r"C:\L2 DSI\Stage\Project_Salary_Prediction\data\processed\anne_mois_MS_nbemp.csv")

    df1 = clean_keys(df1)
    df2 = clean_keys(df2)
    df3 = clean_keys(df3)

    print("Missing values in df1:\n", df1.isna().sum())

    merged = df1.merge(df2, on=["Year", "Month"]).merge(df3, on=["Year", "Month"])
    return merged

# -----------------------------
# Step 2: Preprocess Data
# -----------------------------
def preprocess(df):
    X = df.drop("mass_salary", axis=1)   # replace with your target column
    y = df["mass_salary"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, y, scaler, X.columns

# -----------------------------
# Step 3: Train XGBoost
# -----------------------------
def train_xgboost(X_train, y_train):
    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    return model

# -----------------------------
# Step 4: Evaluate Model
# -----------------------------
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n--- XGBoost Accuracy ---")
    print(f"MSE: {mse:.2f}")
    print(f"R²: {r2:.2f}")
    return y_pred, mse, r2

# -----------------------------
# Step 5: SHAP Analysis
# -----------------------------
def shap_analysis(model, X_train, X_test, feature_names):
    explainer = shap.Explainer(model, X_train)
    shap_values = explainer(X_test)

    # Global summary plot
    shap.summary_plot(shap_values, X_test, feature_names=feature_names)

    # Example: force plot for first prediction
    shap.plots.force(shap_values[0])

    # Example: dependence plot for nbemp
    shap.dependence_plot("nbemp", shap_values.values, X_test, feature_names=feature_names)

# -----------------------------
# Step 6: Main Workflow
# -----------------------------
if __name__ == "__main__":
    df = load_data()
    X_scaled, y, scaler, feature_names = preprocess(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    xgb_model = train_xgboost(X_train, y_train)
    predictions, mse, r2 = evaluate_model(xgb_model, X_test, y_test)

    # Plot results
    plot_predictions(y_test, predictions, "XGBoost")
    plot_feature_importance(xgb_model, feature_names)

    # SHAP analysis
    shap_analysis(xgb_model, X_train, X_test, feature_names)