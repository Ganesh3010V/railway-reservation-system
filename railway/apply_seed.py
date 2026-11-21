import mysql.connector
from mysql.connector import Error

PASSWORDS = ["", "Ganesh@3018"]

def get_connection():
    for pwd in PASSWORDS:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password=pwd,
                database="railway_db"
            )
            print(f"Connected to MySQL successfully (password: '{pwd}')")
            return conn
        except Error:
            continue
    raise Exception("Could not connect to MySQL with tested passwords.")

def run_seed():
    conn = get_connection()
    cur = conn.cursor(buffered=True)
    with open("railway/demo_sample_data.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split statements by semicolon
    statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
    for stmt in statements:
        # Skip pure comments or USE statements
        clean_lines = [l for l in stmt.split("\n") if not l.strip().startswith("--")]
        clean_stmt = "\n".join(clean_lines).strip()
        if not clean_stmt or clean_stmt.upper().startswith("USE "):
            continue
        # Skip SELECT queries at the bottom intended for manual inspection
        if clean_stmt.upper().startswith("SELECT "):
            continue
        try:
            cur.execute(clean_stmt)
            conn.commit()
        except Error as e:
            print(f"Notice on statement: {e}")
    cur.close()
    conn.close()
    print("Sample data successfully applied to railway_db!")

if __name__ == "__main__":
    run_seed()
