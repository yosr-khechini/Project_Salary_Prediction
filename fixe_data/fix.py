import pandas as pd
import glob
import os

# 🔹 Step 1: Set the folder path
folder_path = r"C:\L2 DSI\Stage\Project_Salary_Prediction\fixe_data"

# 🔹 Step 2: Find all CSV files
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
print("Found files:", csv_files)

# 🔹 Step 3: Load and merge only selected columns
required_columns = ['codetab', 'mat', 'mois', 'annee', 'cod1', 'cod2', 'cod3', 'sulbrut']
df_list = [pd.read_csv(file, sep=";", usecols=lambda col: col in required_columns, low_memory=False) for file in csv_files]
merged_df = pd.concat(df_list, ignore_index=True)

# 🔹 Step 4: Compute real salary per employee per month
employee_monthly = merged_df.groupby(['mat', 'mois', 'annee'], as_index=False).agg({
    'cod3': 'sum',
    'sulbrut': 'sum'
})
employee_monthly['real_salary'] = employee_monthly['cod3'] + employee_monthly['sulbrut']

# 🔹 Step 5: Aggregate per month across all employees
monthly_summary = employee_monthly.groupby(['annee', 'mois'], as_index=False).agg({
    'real_salary': 'sum',
    'mat': 'nunique'
})
monthly_summary.rename(columns={
    'real_salary': 'mass_salary',
    'mat': 'nbemp'
}, inplace=True)

# 🔹 Step 6: Save the result
output_path = os.path.join(folder_path, "anne_mois_MS_nbemp.csv")
monthly_summary.to_csv(output_path, index=False)
print(f"Summary saved to: {output_path}")
