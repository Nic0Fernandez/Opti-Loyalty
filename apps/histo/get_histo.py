import sqlite3
import pandas as pd
from datetime import datetime

query = """
    SELECT name, ingredients, size,unit_price, order_date 
    FROM main_order
    JOIN main_pizza
    ON main_order.pizza_id=main_pizza.pizza_id
    WHERE client_id= ?
    ORDER BY order_date DESC
"""

def get_histo(db_path, client_id):
    conn = sqlite3.connect(db_path)
    
    df = pd.read_sql_query(query, conn, params=(client_id,))
    
    conn.close()
    
    records=df.to_dict(orient='records')
    for record in records:
        order_date = record['order_date']
        
        dt_obj = datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S.%f")
        
        formatted_date = dt_obj.strftime("%d-%m-%Y")  
        formatted_time = dt_obj.strftime("%H:%M:%S")  
        
        record['formatted_date'] = formatted_date
        record['formatted_time'] = formatted_time
    
    return records
