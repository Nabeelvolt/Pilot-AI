import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import settings
    from services.supabase_client import get_supabase
    
    print("Testing Supabase connection...")
    print(f"URL: {settings.SUPABASE_URL}")
    
    client = get_supabase()
    res = client.table("documents").select("doc_id").limit(1).execute()
    print("Supabase connection SUCCESSFUL.")
    print("Result:", res)
except Exception as e:
    import traceback
    print("Supabase connection ERROR:")
    traceback.print_exc()
