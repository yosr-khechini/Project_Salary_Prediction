import os
from dotenv import load_dotenv

load_dotenv()

print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"FLASK_DEBUG: {os.getenv('FLASK_DEBUG')}")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")