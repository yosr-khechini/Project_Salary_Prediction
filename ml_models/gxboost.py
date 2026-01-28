import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBRegressor
import joblib

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

    # Merge all data
    merged = df1.merge(df2, on=["Year", "Month"], how="left").merge(df3, on=["Year", "Month"], how="left")

    # Fill missing recruitments with 0 (only January has recruitments)
    merged["Recruitments"] = merged["Recruitments"].fillna(0)

    # Remove rows with missing critical data
    merged = merged.dropna(subset=["mass_salary", "nbemp"])

    print(f"Total rows after merge: {len(merged)}")
    print("Missing values:\n", merged.isna().sum())

    return merged

# -----------------------------
# Step 2: Preprocess Data
# -----------------------------
def preprocess(df):
    # Create features including cumulative recruitments for the year
    df = df.sort_values(["Year", "Month"])

    # For each month, use the cumulative effect of January's recruitments
    df["cumulative_recruitments"] = df.groupby("Year")["Recruitments"].transform("sum")

    # Create monthly recruitment feature (spread yearly recruitments across months)
    df["monthly_recruitment_effect"] = df["cumulative_recruitments"] / 12

    # Features to use
    feature_cols = ["Year", "Month", "nb_departures", "monthly_recruitment_effect", "nbemp"]
    X = df[feature_cols]
    y = df["mass_salary"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, scaler, X.columns, df

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
# Step 4: Evaluate Model (Monthly)
# -----------------------------
def evaluate_model_monthly(model, X_test, y_test):
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n--- XGBoost Monthly Accuracy ---")
    print(f"MSE: {mse:.2f}")
    print(f"R²: {r2:.2f}")
    return y_pred

# -----------------------------
# Step 5: Aggregate to Yearly Predictions
# -----------------------------
def aggregate_to_yearly(df_with_predictions):
    yearly = df_with_predictions.groupby("Year").agg({
        "mass_salary": "sum",
        "predicted_salary": "sum"
    }).reset_index()
    yearly.columns = ["Year", "actual_yearly_salary", "predicted_yearly_salary"]

    # Calculate yearly metrics
    mse_yearly = mean_squared_error(yearly["actual_yearly_salary"], yearly["predicted_yearly_salary"])
    r2_yearly = r2_score(yearly["actual_yearly_salary"], yearly["predicted_yearly_salary"])

    print("\n--- XGBoost Yearly Accuracy ---")
    print(f"MSE: {mse_yearly:.2f}")
    print(f"R²: {r2_yearly:.2f}")

    return yearly, mse_yearly, r2_yearly

# -----------------------------
# Step 6: Predict Future Years
# -----------------------------
def predict_future_years(model, scaler, feature_names, start_year, end_year,
                        annual_recruitments, monthly_departures, initial_employees):
    """
    Predict future years month by month, then aggregate to yearly totals.
    """
    predictions = []
    current_employees = initial_employees

    for year in range(start_year, end_year + 1):
        yearly_sum = 0

        for month in range(1, 13):
            # Recruitments only happen in January
            monthly_recruitment = annual_recruitments if month == 1 else 0
            recruitment_effect = annual_recruitments / 12

            # Create features
            features = pd.DataFrame([{
                "Year": year,
                "Month": month,
                "nb_departures": monthly_departures,
                "monthly_recruitment_effect": recruitment_effect,
                "nbemp": current_employees
            }])

            # Scale and predict
            features_scaled = scaler.transform(features)
            monthly_prediction = model.predict(features_scaled)[0]
            yearly_sum += monthly_prediction

            # Update employee count
            if month == 1:
                current_employees += monthly_recruitment
            current_employees -= monthly_departures

        # Store yearly prediction
        avg_monthly = yearly_sum / 12
        predictions.append({
            "Year": year,
            "total_yearly_salary": yearly_sum,
            "avg_monthly_salary": avg_monthly,
            "employees_end_of_year": current_employees
        })

        print(f"Year {year}: Total Salary = {yearly_sum:,.2f}, Avg Monthly = {avg_monthly:,.2f}, Employees = {current_employees}")

    return pd.DataFrame(predictions)

# -----------------------------
# Step 7: Save Model
# -----------------------------
def save_model(model, scaler, feature_names):
    """Save model, scaler, and feature names"""
    import os
    os.makedirs("artifacts", exist_ok=True)

    joblib.dump(model, "artifacts/xgb_model.pkl")
    joblib.dump(scaler, "artifacts/scaler.pkl")
    joblib.dump(feature_names, "artifacts/feature_names.pkl")

    print("✅ Model, scaler, and features saved to artifacts/")
# -----------------------------
# Step 8: Main Workflow
# -----------------------------
if __name__ == "__main__":
    # Load and preprocess data
    df = load_data()
    X_scaled, y, scaler, feature_names, df_full = preprocess(df)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, shuffle=False  # Keep temporal order
    )

    # Train model
    print("\n🚀 Training XGBoost model...")
    xgb_model = train_xgboost(X_train, y_train)

    # Evaluate on monthly predictions
    monthly_predictions = evaluate_model_monthly(xgb_model, X_test, y_test)

    # Add predictions to dataframe for yearly aggregation
    df_test = df_full.iloc[-len(y_test):].copy()
    df_test["predicted_salary"] = monthly_predictions

    # Aggregate to yearly
    yearly_results, mse_yearly, r2_yearly = aggregate_to_yearly(df_test)
    print("\n📊 Yearly Results:")
    print(yearly_results)

    # Plot results
    plot_predictions(y_test, monthly_predictions, "XGBoost Monthly")
    plot_feature_importance(xgb_model, feature_names)

    # Save model
    save_model(xgb_model, scaler, feature_names)

    # Example: Predict future years
    print("\n🔮 Predicting future years...")
    future_predictions = predict_future_years(
        model=xgb_model,
        scaler=scaler,
        feature_names=feature_names,
        start_year=2025,
        end_year=2027,
        annual_recruitments=100,  # Total recruitments in January
        monthly_departures=5,      # Average monthly departures
        initial_employees=5431     # From last known value (2020)
    )

    print("\n📈 Future Predictions:")
    print(future_predictions)