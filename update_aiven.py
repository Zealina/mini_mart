import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv('MINI_MART_MYSQL_USER')
PWD = os.getenv('MINI_MART_MYSQL_PWD')
HOST = os.getenv('MINI_MART_MYSQL_HOST')
DB = os.getenv('MINI_MART_MYSQL_DB')

if not all([USER, PWD, HOST, DB]):
    raise ValueError("Set all DB env variables before running this script.")

# PyMySQL does not support the ssl_mode query parameter used by some other
# drivers. Use a plain Aiven-compatible connection string instead.
uri = f"mysql+pymysql://{quote_plus(USER)}:{quote_plus(PWD)}@{HOST}/{DB}"

print(f"Connecting to Aiven Database at {HOST}...")
try:
    engine = create_engine(uri, pool_pre_ping=True)
    with engine.connect() as conn:
        print("Adding delivery_address column...")
        try:
            conn.execute(text("ALTER TABLE orders ADD COLUMN delivery_address VARCHAR(255);"))
            print("✅ Success!")
        except Exception as e:
            print(f"⚠️ Notice: {e}")

        print("Adding contact_phone column...")
        try:
            conn.execute(text("ALTER TABLE orders ADD COLUMN contact_phone VARCHAR(50);"))
            print("✅ Success!")
        except Exception as e:
            print(f"⚠️ Notice: {e}")
            
        conn.commit()
    print("\n🎉 Aiven Database successfully updated to accept Delivery Data!")
except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")