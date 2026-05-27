import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase URL or Key is missing in .env")

supabase: Client = create_client(url, key)

def get_user(user_id):
    res = supabase.table('users').select("*").eq('user_id', user_id).execute()
    return res.data[0] if res.data else None

def add_user(user_id, full_name, phone_number):
    data = {
        "user_id": user_id,
        "full_name": full_name,
        "phone_number": phone_number
    }
    supabase.table('users').upsert(data).execute()

def add_payment(user_id, course_name):
    data = {
        "user_id": user_id,
        "course_name": course_name,
        "status": "pending"
    }
    res = supabase.table('payments').insert(data).execute()
    return res.data[0]['id'] if res.data else None

def update_payment_status(payment_id, status):
    supabase.table('payments').update({"status": status}).eq('id', payment_id).execute()

def get_payment(payment_id):
    res = supabase.table('payments').select("*").eq('id', payment_id).execute()
    return res.data[0] if res.data else None

def get_latest_payment(user_id):
    res = supabase.table('payments').select("*").eq('user_id', user_id).order('id', desc=True).limit(1).execute()
    return res.data[0] if res.data else None

def get_statistics():
    users_res = supabase.table('users').select("*", count='exact').execute()
    total_users = users_res.count if hasattr(users_res, 'count') and users_res.count else len(users_res.data)
    
    appr_res = supabase.table('payments').select("*", count='exact').eq('status', 'approved').execute()
    total_approved = appr_res.count if hasattr(appr_res, 'count') and appr_res.count else len(appr_res.data)
    
    beg_res = supabase.table('payments').select("*", count='exact').eq('status', 'approved').eq('course_name', 'Beginner Kanal').execute()
    beginner_users = beg_res.count if hasattr(beg_res, 'count') and beg_res.count else len(beg_res.data)
    
    prem_res = supabase.table('payments').select("*", count='exact').eq('status', 'approved').eq('course_name', 'Premium Kanal').execute()
    premium_users = prem_res.count if hasattr(prem_res, 'count') and prem_res.count else len(prem_res.data)
    
    return total_users, total_approved, beginner_users, premium_users
