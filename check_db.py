import sqlite3
import json

def check_db():
    try:
        conn = sqlite3.connect("mcp.db")
        cursor = conn.cursor()
        
        print("--- Gateways ---")
        cursor.execute("SELECT name, url FROM gateways")
        for row in cursor.fetchall():
            print(f"Gateway: {row[0]} ({row[1]})")
            
        print("\n--- Virtual Servers ---")
        cursor.execute("SELECT name FROM servers")
        for row in cursor.fetchall():
            print(f"Server: {row[0]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
