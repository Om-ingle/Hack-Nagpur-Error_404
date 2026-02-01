import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

# Test connection
def test_connection():
    try:
        result = supabase.table('doctors').select("*").execute()
        print(f"[OK] Database connected! Found {len(result.data)} doctors")
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()