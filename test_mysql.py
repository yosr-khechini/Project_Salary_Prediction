import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
print(f"🔗 Tentative de connexion à: {DATABASE_URL}")

try:
    # Suppression de auth_plugin_map car on a configuré MySQL correctement
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        result = conn.execute(text('SHOW TABLES'))
        tables = [row[0] for row in result]
        print(f"✅ Connexion réussie !")
        print(f"📊 Tables trouvées: {tables}")
except Exception as e:
    print(f"❌ Erreur de connexion: {e}")

# Affichez les colonnes de chaque table
from sqlalchemy import inspect

inspector = inspect(engine)
for table_name in inspector.get_table_names():
    print(f"\n📋 Table: {table_name}")
    for column in inspector.get_columns(table_name):
        print(f"  - {column['name']}: {column['type']}")
