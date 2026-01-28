import joblib
import os

METRICS_PATH = os.path.join("ml_models", "artifacts", "metrics.pkl")

try:
    metrics = joblib.load(METRICS_PATH)
    print("✅ Contenu de metrics.pkl:")
    print(metrics)
    print("\n📋 Clés disponibles:")
    print(list(metrics.keys()) if isinstance(metrics, dict) else "Pas un dictionnaire")
except Exception as e:
    print(f"❌ Erreur: {e}")