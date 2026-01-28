
import joblib
import os
import pickle

# Chemins vers les artefacts du modèle
ARTIFACTS_DIR = os.path.join('ml_models', 'artifacts')
MODEL_PATH = os.path.join(ARTIFACTS_DIR, 'xgb_model.pkl')
SCALER_PATH = os.path.join(ARTIFACTS_DIR, 'scaler.pkl')
FEATURE_NAMES_PATH = os.path.join(ARTIFACTS_DIR, 'feature_names.pkl')
METRICS_PATH = os.path.join(ARTIFACTS_DIR, 'metrics.pkl')

# Cache pour éviter de recharger les artefacts à chaque prédiction
_model_cache = None
_scaler_cache = None
_feature_names_cache = None
_metrics_cache = None

def get_model():
    """Charge et retourne le modèle ML"""
    global _model_cache
    if _model_cache is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Modèle non trouvé: {MODEL_PATH}. Exécutez d'abord export_model.py")
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache

def get_scaler():
    """Charge et retourne le scaler"""
    global _scaler_cache
    if _scaler_cache is None:
        if not os.path.exists(SCALER_PATH):
            raise FileNotFoundError(f"Scaler non trouvé: {SCALER_PATH}. Exécutez d'abord export_model.py")
        _scaler_cache = joblib.load(SCALER_PATH)
    return _scaler_cache

def get_feature_names():
    """Charge et retourne la liste des noms de features"""
    global _feature_names_cache
    if _feature_names_cache is None:
        if not os.path.exists(FEATURE_NAMES_PATH):
            raise FileNotFoundError(f"Features non trouvées: {FEATURE_NAMES_PATH}. Exécutez d'abord export_model.py")
        _feature_names_cache = joblib.load(FEATURE_NAMES_PATH)
    return _feature_names_cache

def get_model_metrics():
    """
    Récupère les métriques du modèle (R², MSE, etc.)
    """
    global _metrics_cache

    if _metrics_cache is None:
        try:
            if os.path.exists(METRICS_PATH):
                _metrics_cache = joblib.load(METRICS_PATH)
            else:
                print(f"⚠️ Fichier de métriques non trouvé: {METRICS_PATH}")
                _metrics_cache = {'r2': 0.0, 'mse': 0.0}
        except Exception as e:
            print(f"❌ Erreur lors du chargement des métriques: {e}")
            _metrics_cache = {'r2': 0.0, 'mse': 0.0}

    return _metrics_cache

def reload_model():
    """Force le rechargement de tous les artefacts (utile après un réentraînement)"""
    global _model_cache, _scaler_cache, _feature_names_cache, _metrics_cache
    _model_cache = None
    _scaler_cache = None
    _feature_names_cache = None
    _metrics_cache = None
    print("✅ Cache des modèles vidé. Prochain appel rechargera les artefacts.")