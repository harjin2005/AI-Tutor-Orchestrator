from dotenv import load_dotenv
load_dotenv()

import os
import psycopg2
from urllib.parse import urlparse

def test_direct_connection():
    """Test direct psycopg2 connection to Supabase"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    print(f"🔗 Testing connection to: {database_url.split('@')[1] if '@' in database_url else 'Unknown'}")
    
    try:
        # Parse the DATABASE_URL
        parsed = urlparse(database_url)
        
        # Connect using psycopg2 directly
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password,
            sslmode='require',
            connect_timeout=10
        )
        
        # Test a simple query
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        
        print("✅ Direct psycopg2 connection successful!")
        print(f"📊 PostgreSQL version: {version[0][:50]}...")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection"""
    try:
        from schemas.database import test_database_connection
        return test_database_connection()
    except Exception as e:
        print(f"❌ SQLAlchemy test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Supabase Database Connection...")
    print("=" * 50)
    
    # Test direct connection first
    direct_success = test_direct_connection()
    print()
    
    # Test SQLAlchemy connection
    if direct_success:
        print("🧪 Testing SQLAlchemy connection...")
        sqlalchemy_success = test_sqlalchemy_connection()
    
    print("=" * 50)
    if direct_success:
        print("✅ All tests passed! Your database is ready.")
    else:
        print("❌ Connection tests failed. Check your DATABASE_URL and network.")
