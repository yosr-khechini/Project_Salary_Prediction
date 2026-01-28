import sys
import os
import pandas as pd
import numpy as np

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.model_loader import get_model, get_scaler, get_feature_names

def inspect_model_and_scaler():
    """Inspecte le modèle et le scaler pour diagnostiquer le problème"""

    print("=" * 80)
    print("INSPECTION DU MODÈLE ET DU SCALER")
    print("=" * 80)

    try:
        # Charger le modèle
        model = get_model()
        print("\n✅ Modèle chargé avec succès")
        print(f"Type de modèle: {type(model).__name__}")
        print(f"Nombre de features attendues: {model.n_features_in_}")

        # Vérifier si c'est un modèle linéaire
        if hasattr(model, 'coef_'):
            print(f"\nCoefficients du modèle:")
            for i, coef in enumerate(model.coef_):
                print(f"  Feature {i}: {coef:.6f}")
            print(f"Intercept: {model.intercept_:.2f}")

        # Charger le scaler
        scaler = get_scaler()
        print("\n✅ Scaler chargé avec succès")
        print(f"Type de scaler: {type(scaler).__name__}")

        if hasattr(scaler, 'mean_'):
            print(f"\nMoyennes (mean) utilisées pour le scaling:")
            for i, mean in enumerate(scaler.mean_):
                print(f"  Feature {i}: {mean:.2f}")

        if hasattr(scaler, 'scale_'):
            print(f"\nÉcarts-types (scale) utilisés pour le scaling:")
            for i, scale in enumerate(scaler.scale_):
                print(f"  Feature {i}: {scale:.2f}")

        if hasattr(scaler, 'var_'):
            print(f"\nVariances:")
            for i, var in enumerate(scaler.var_):
                print(f"  Feature {i}: {var:.2f}")

        # Charger les noms de features
        feature_names = get_feature_names()
        print(f"\n✅ Noms des features: {feature_names}")

        # Test avec des données réalistes
        print("\n" + "=" * 80)
        print("TEST AVEC DES DONNÉES RÉALISTES")
        print("=" * 80)

        test_cases = [
            {'Year': 2025, 'Month': 1, 'nb_departures': 60, 'Recruitments': 100, 'nbemp': 500000},
            {'Year': 2025, 'Month': 1, 'nb_departures': 60, 'Recruitments': 100, 'nbemp': 1000},
            {'Year': 2025, 'Month': 1, 'nb_departures': 5, 'Recruitments': 10, 'nbemp': 100},
        ]

        for idx, test_data in enumerate(test_cases, 1):
            print(f"\nTest {idx}: {test_data}")
            df = pd.DataFrame([test_data])[feature_names]

            print("Données brutes:")
            print(df.to_string())

            scaled_data = scaler.transform(df)
            print(f"Données après scaling: {scaled_data}")

            prediction = model.predict(scaled_data)[0]
            print(f"Prédiction: {prediction:,.2f}")

        # Tester l'impact de chaque feature
        print("\n" + "=" * 80)
        print("ANALYSE DE L'IMPACT DES FEATURES")
        print("=" * 80)

        base_data = {'Year': 2025, 'Month': 1, 'nb_departures': 5, 'Recruitments': 10, 'nbemp': 1000}

        for feature in feature_names:
            print(f"\nVariation de {feature}:")

            for multiplier in [0.5, 1.0, 2.0]:
                test_data = base_data.copy()
                test_data[feature] = base_data[feature] * multiplier

                df = pd.DataFrame([test_data])[feature_names]
                scaled = scaler.transform(df)
                pred = model.predict(scaled)[0]

                print(f"  {feature}={test_data[feature]:.0f} → Prédiction: {pred:,.2f}")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_model_and_scaler()