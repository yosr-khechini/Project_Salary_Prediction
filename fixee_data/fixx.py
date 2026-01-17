import pandas as pd

# 🔹 Step 1: Load your departure data
file_path = r"C:\L2 DSI\Stage\Project_Salary_Prediction\fixee_data\depart.csv"
df = pd.read_csv(file_path, sep=";", low_memory=False)

# 🔹 Step 2: Keep only relevant columns
df_filtered = df[['DEP_ANNEE', 'DEP_MOIS', 'DEP_ETABR']]

# 🔹 Step 3: Count number of departures per (year, month)
monthly_departures = df_filtered.groupby(['DEP_ANNEE', 'DEP_MOIS']).size().reset_index(name='nb_departures')

# 🔹 Step 4: Save to CSV
monthly_departures.to_csv("monthly_departures.csv", index=False)

# 🔹 Optional: Preview
print(monthly_departures.head())
res = pd.read_csv("monthly_departures.csv")
print(res.head())
print(res.shape)