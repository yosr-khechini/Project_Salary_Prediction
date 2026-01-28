document.addEventListener('DOMContentLoaded', function() {
    console.log('JavaScript chargé');

    const form = document.getElementById('predictionForm');

    if (!form) {
        console.error('Formulaire introuvable');
        return;
    }

    console.log('Formulaire trouvé');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Soumission du formulaire...');

        const loadingSpinner = document.getElementById('loadingSpinner');
        const errorAlert = document.getElementById('errorAlert');
        const resultsSection = document.getElementById('resultsSection');

        // Afficher le spinner
        if (loadingSpinner) loadingSpinner.style.display = 'block';
        if (errorAlert) errorAlert.style.display = 'none';
        if (resultsSection) resultsSection.style.display = 'none';

        const formData = {
            start_year: parseInt(document.getElementById('start_year').value),
            end_year: parseInt(document.getElementById('end_year').value),
            recruitments: parseInt(document.getElementById('recruitments').value),
            departures: parseInt(document.getElementById('departures').value),
            initial_employees: parseInt(document.getElementById('initial_employees').value)
        };

        console.log('Données envoyées:', formData);

        try {
            // Fixed URL - use relative path to /predict endpoint
            const url = '/prediction/predict';
            console.log('URL appelée:', url);

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            console.log('Réponse reçue:', response.status);

            const data = await response.json();
            console.log('Données reçues:', data);

            if (!response.ok || data.status === 'error') {
                showError(data.message || 'Erreur de prédiction');
                return;
            }

            displayResults(data);

        } catch (error) {
            console.error('Erreur détaillée:', error);
            showError('Erreur de connexion au serveur. Vérifiez que le serveur est démarré');
        } finally {
            if (loadingSpinner) loadingSpinner.style.display = 'none';
        }
    });
});

function showError(message) {
    console.error('Erreur affichée:', message);
    const errorAlert = document.getElementById('errorAlert');
    if (errorAlert) {
        errorAlert.textContent = message;
        errorAlert.style.display = 'block';
    }
}

function displayResults(data) {
    console.log('Affichage des résultats...');
    const resultsSection = document.getElementById('resultsSection');
    if (!resultsSection) {
        console.error('Section results introuvable');
        return;
    }

    // Afficher le graphique
    const graphImage = document.getElementById('graphImage');
    if (graphImage && data.graph) {
        graphImage.src = data.graph;
        console.log('Graphique affiché');
    } else {
        console.warn('Pas de graphique ou élément img manquant');
    }

    // Afficher les métriques si disponibles
    const metricsDiv = document.getElementById('modelMetrics');
    if (metricsDiv && data.metrics) {
        metricsDiv.textContent = `R2 Score: ${data.metrics.r2_score} | MSE: ${data.metrics.mse.toFixed(2)}`;
        metricsDiv.style.display = 'block';
        console.log('Métriques affichées');
    }

    // Remplir le tableau
    const tbody = document.getElementById('predictionsTable');
    if (tbody && data.predictions) {
        tbody.innerHTML = '';

        data.predictions.forEach(pred => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${pred.Year}</td>
                <td>${pred.Total_Salary.toLocaleString('fr-FR', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })}</td>
                <td>${pred.End_Employees}</td>
            `;
        });

        console.log(`${data.predictions.length} lignes ajoutées au tableau`);
    } else {
        console.error('Pas de prédictions ou tableau manquant');
    }

    resultsSection.style.display = 'block';
    console.log('Section results affichée');
}