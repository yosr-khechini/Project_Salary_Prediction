from flask import Blueprint, render_template, request, jsonify, current_app
from app.prediction import predict_salaries, generate_graph, validate_inputs
from app.model_loader import get_model, get_scaler, get_model_metrics
from flask_login import login_required, current_user
import pandas as pd
from app import db
from app.models import PredictionHistory
import json



# Créer le blueprint
prediction_bp = Blueprint('prediction', __name__, url_prefix='/prediction')

@prediction_bp.route('/')
@login_required
def prediction_page():
    """Page d'accueil avec le formulaire de prédiction"""
    return render_template('prediction.html')

@prediction_bp.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint JSON pour les requêtes AJAX
    Retourne JSON au lieu de HTML
    """
    try:
        # Récupérer les données JSON de la requête
        data = request.get_json()

        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Aucune donnée JSON reçue'
            }), 400

        # Valider les champs requis
        required_fields = ['start_year', 'end_year', 'recruitments', 'departures', 'initial_employees']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]

        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400

        # Convertir avec gestion d'erreur
        try:
            start_year = int(data['start_year'])
            end_year = int(data['end_year'])
            recruitments = int(data['recruitments'])
            departures = int(data['departures'])
            initial_employees = int(data['initial_employees'])
        except (ValueError, TypeError) as ve:
            current_app.logger.error(f"Erreur de conversion: {ve}")
            return jsonify({
                'status': 'error',
                'message': 'Valeurs numériques invalides'
            }), 400

        # Validation métier
        is_valid, error_msg = validate_inputs(start_year, end_year, recruitments, departures, initial_employees)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 400

        # Obtenir les prédictions (retourne DEUX dataframes)
        monthly_df, yearly_df = predict_salaries(start_year, end_year, recruitments, departures, initial_employees)

        # Générer le graphique à partir des données MENSUELLES
        graph_base64 = generate_graph(monthly_df)

        # Obtenir les métriques du modèle
        try:
            model_metrics = get_model_metrics()
            metrics_data = {
                'r2_score': round(model_metrics.get('r2', 0.0), 4),
                'mse': round(model_metrics.get('mse', 0.0), 2)
            }
        except Exception as me:
            current_app.logger.warning(f"Impossible de récupérer les métriques: {me}")
            metrics_data = {
                'r2_score': 0.0,
                'mse': 0.0
            }

        # Convertir le dataframe annuel en liste de dictionnaires
        predictions_list = yearly_df.to_dict('records')

        # Construire la réponse JSON
        response = {
            'status': 'success',
            'predictions': predictions_list,
            'graph': graph_base64,
            'metrics': metrics_data
        }

        if current_user.is_authenticated:
            history = PredictionHistory(
                user_id=current_user.id,
                start_year=start_year,
                end_year=end_year,
                recruitments=recruitments,
                departures=departures,
                initial_employees=initial_employees,
                result_json=json.dumps(response)
            )
            db.session.add(history)
            db.session.commit()

        return jsonify(response), 200

    except Exception as e:
        current_app.logger.error(f"Erreur API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Erreur serveur: {str(e)}'
        }), 500

@prediction_bp.route('/api/predict', methods=['POST'])
def api_predict():
    """Endpoint API alternatif (identique à /predict)"""
    return predict()

@prediction_bp.route('/health')
def health():
    """Endpoint de vérification de santé de l'API"""
    try:
        model = get_model()
        scaler = get_scaler()
        model_loaded = model is not None and scaler is not None

        response = {
            'status': 'ok',
            'message': 'API opérationnelle',
            'model_loaded': model_loaded
        }

        if model_loaded:
            try:
                model_metrics = get_model_metrics()
                response['metrics'] = {
                    'r2_score': round(model_metrics.get('r2', 0.0), 4),
                    'mse': round(model_metrics.get('mse', 0.0), 2)
                }
            except Exception as me:
                current_app.logger.warning(f"Métriques non disponibles: {me}")

        return jsonify(response), 200

    except Exception as e:
        current_app.logger.error(f"Erreur health check: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@prediction_bp.route('/metrics', methods=['GET'])
def get_metrics_route():
    """Obtenir les métriques du modèle"""
    try:
        model_metrics = get_model_metrics()
        return jsonify({
            'status': 'success',
            'metrics': {
                'r2_score': round(model_metrics.get('r2', 0.0), 4),
                'mse': round(model_metrics.get('mse', 0.0), 2)
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Erreur récupération métriques: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500