from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        result = db.session.execute(text('SELECT 1'))
        print("✅ Connexion MySQL réussie")

        result = db.session.execute(text('SHOW TABLES'))
        tables = result.fetchall()
        print(f"📋 Tables trouvées : {[t[0] for t in tables]}")
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")