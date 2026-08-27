import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

user = os.getenv('MINI_MART_MYSQL_USER')
pwd = os.getenv('MINI_MART_MYSQL_PWD')
host = os.getenv('MINI_MART_MYSQL_HOST')
db = os.getenv('MINI_MART_MYSQL_DB')

uri = f"mysql+pymysql://{user}:{pwd}@{host}/{db}"
engine = create_engine(uri)

# --- EDIT THIS LINE to the email you registered on your frontend ---
TARGET_EMAIL = "eresecaleb012@gmail.com"

with engine.connect() as conn:
    print("Connecting to Aiven Cloud Database...")
    result = conn.execute(text(f"UPDATE users SET is_admin = 1, is_super_admin = 1 WHERE email = '{TARGET_EMAIL}';"))
    conn.commit()
    
    if result.rowcount > 0:
        print(f"✅ Success! {TARGET_EMAIL} now has full Admin Rights.")
    else:
        print(f"❌ ERROR: The email '{TARGET_EMAIL}' was NOT found in the database. Did you register it successfully on the frontend first?")
