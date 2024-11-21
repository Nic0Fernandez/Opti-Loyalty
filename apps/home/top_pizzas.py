import sqlite3
import pandas as pd

# Requête SQL pour récupérer les 5 pizzas les plus populaires du mois dernier
query_best_sold = """
    SELECT name, unit_price, ingredients, image,strftime('%Y-%m', order_date) AS order_month, COUNT(*) AS order_count
    FROM main_order o
    JOIN main_pizza p ON o.pizza_id = p.pizza_id
    WHERE order_date >= date('now', 'start of month', '-1 month')  
    AND order_date < date('now', 'start of month')      
    AND unit_price = (
            SELECT MIN(mp.unit_price)
            FROM main_pizza mp
            WHERE mp.name = p.name
        )        
    GROUP BY name, order_month
    ORDER BY order_count DESC
    LIMIT 5;
"""




def best_sold(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query_best_sold, conn)
    conn.close()
    result = df.to_dict(orient='records')
    return result

def get_info_pizza(db_path,recommendations):
    placeholders = ', '.join(['?'] * len(recommendations))  
    query_info_recommendations = f"""
        SELECT p.name, p.unit_price, p.ingredients, p.image
        FROM main_pizza p
        WHERE p.name IN ({placeholders})
        AND p.unit_price = (
            SELECT MIN(mp.unit_price)
            FROM main_pizza mp
            WHERE mp.name = p.name
        )
        GROUP BY p.name
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query_info_recommendations, conn,params=recommendations)
    conn.close()
    result = df.to_dict(orient='records')
    return result


