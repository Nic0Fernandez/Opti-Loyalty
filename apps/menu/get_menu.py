import sqlite3
import pandas as pd

query = """
    SELECT *
    FROM main_pizza
    
"""

def get_menu(db_path):
    conn = sqlite3.connect(db_path)
    
    df = pd.read_sql_query(query, conn)
    
    conn.close()
    
    result = df.to_dict(orient='records')
    return result
