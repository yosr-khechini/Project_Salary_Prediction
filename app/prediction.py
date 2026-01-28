import pandas as pd
import numpy as np
from app.model_loader import get_model, get_scaler

def validate_inputs(start_year, end_year, recruitments, departures, initial_employees):
    """Valide les paramètres d'entrée"""
    if start_year < 2000 or start_year > 2100:
        return False, "Année de début invalide (2000-2100)"

    if end_year <= start_year:
        return False, "L'année de fin doit être supérieure à l'année de début"

    if end_year - start_year > 20:
        return False, "Plage maximale: 20 ans"

    if recruitments < 0 or departures < 0 or initial_employees < 0:
        return False, "Les valeurs doivent être positives"

    if initial_employees == 0:
        return False, "L'effectif initial ne peut pas être zéro"

    return True, None

def predict_salaries(start_year, end_year, recruitments, departures, initial_employees):
    """
    Prédit la masse salariale pour chaque année
    Retourne: (monthly_df, yearly_df)
    """
    try:
        model = get_model()
        scaler = get_scaler()

        if model is None or scaler is None:
            raise ValueError("Modèle ou scaler non chargé")

        monthly_predictions = []
        yearly_predictions = []
        current_employees = float(initial_employees)

        for year in range(start_year, end_year + 1):
            yearly_salary = 0
            year_start_employees = current_employees

            # Prédire pour chaque mois
            for month in range(1, 13):
                # Calcul de l'effectif du mois
                monthly_recruitment = recruitments / 12
                monthly_departures = departures / 12
                month_employees = year_start_employees + (monthly_recruitment * (month - 1)) - (monthly_departures * (month - 1))

                # Empêcher les effectifs négatifs
                month_employees = max(1, month_employees)

                # Préparer les features pour le modèle
                input_data = {
                    'Year': year,
                    'Month': month,
                    'nb_departures': monthly_departures,
                    'monthly_recruitment_effect': monthly_recruitment,
                    'nbemp': month_employees
                }

                df = pd.DataFrame([input_data])
                df = df[['Year', 'Month', 'nb_departures', 'monthly_recruitment_effect', 'nbemp']]

                # Normaliser et prédire
                scaled_data = scaler.transform(df)
                monthly_prediction = model.predict(scaled_data)[0]

                # S'assurer que la prédiction est positive
                monthly_prediction = max(0, monthly_prediction)

                yearly_salary += monthly_prediction

                # Stocker les données mensuelles
                monthly_predictions.append({
                    'Year': year,
                    'Month': month,
                    'Month_Name': pd.to_datetime(f'{year}-{month:02d}-01').strftime('%B'),
                    'Predicted_Salary': round(monthly_prediction, 2),
                    'Employees': int(round(month_employees))
                })

            # Calculer l'effectif de fin d'année
            end_year_employees = year_start_employees + recruitments - departures
            end_year_employees = max(0, end_year_employees)

            # Stocker le résumé annuel
            yearly_predictions.append({
                'Year': year,
                'Total_Salary': round(yearly_salary, 2),
                'End_Employees': int(round(end_year_employees))
            })

            # Mettre à jour l'effectif pour l'année suivante
            current_employees = end_year_employees

            print(f"Année {year}: Masse salariale totale = {yearly_salary:,.2f} €, Effectif fin = {int(end_year_employees)}")

        monthly_df = pd.DataFrame(monthly_predictions)
        yearly_df = pd.DataFrame(yearly_predictions)

        return monthly_df, yearly_df

    except Exception as e:
        print(f"Erreur dans predict_salaries: {e}")
        import traceback
        traceback.print_exc()
        raise

def generate_graph(monthly_df):
    """Génère le graphique mensuel de prédiction"""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import io
        import base64

        plt.figure(figsize=(14, 6))

        # Créer les labels de l'axe X (format Année-Mois)
        monthly_df['Period'] = monthly_df['Year'].astype(str) + '-' + monthly_df['Month'].astype(str).str.zfill(2)

        # Tracer les prédictions mensuelles
        plt.plot(range(len(monthly_df)),
                 monthly_df['Predicted_Salary'],
                 marker='o', linewidth=2, markersize=6,
                 label='Masse Salariale Mensuelle', color='#4CAF50')

        plt.xlabel('Période (Année-Mois)', fontsize=12)
        plt.ylabel('Masse Salariale (€)', fontsize=12)
        plt.title('Prédiction Mensuelle de la Masse Salariale', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.legend(fontsize=10)

        # Formater l'axe Y
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f} €'))

        # Afficher moins de labels sur l'axe X (tous les 3 mois)
        step = max(1, len(monthly_df) // 12)  # Ajuster selon le nombre de points
        tick_positions = range(0, len(monthly_df), step)
        tick_labels = [monthly_df['Period'].iloc[i] if i < len(monthly_df) else ''
                       for i in tick_positions]
        plt.xticks(tick_positions, tick_labels, rotation=45, ha='right', fontsize=9)

        plt.tight_layout()

        # Convertir en base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        graph_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()

        return f'data:image/png;base64,{graph_base64}'

    except Exception as e:
        print(f"Erreur génération graphique: {e}")
        import traceback
        traceback.print_exc()
        raise ValueError(f"Erreur graphique: {str(e)}")