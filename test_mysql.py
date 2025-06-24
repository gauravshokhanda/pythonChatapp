from app.db import get_connection

conn = get_connection()
if conn:
    print("✅ Connected to MySQL!")
else:
    print("❌ Connection failed.")
