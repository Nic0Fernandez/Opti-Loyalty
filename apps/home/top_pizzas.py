import sqlite3
import pandas as pd

# Requête SQL pour récupérer les 5 pizzas les plus populaires du mois dernier
query = """
    SELECT name, unit_price, ingredients, image,strftime('%Y-%m', order_date) AS order_month, COUNT(*) AS order_count
    FROM main_order
    JOIN main_pizza ON main_order.pizza_id = main_pizza.pizza_id
    WHERE order_date >= date('now', 'start of month', '-1 month')  
    AND order_date < date('now', 'start of month')              
    GROUP BY name, order_month
    ORDER BY order_count DESC
    LIMIT 5;
"""

def top_5_pizzas(db_path):
    # Connexion à la base de données SQLite
    conn = sqlite3.connect(db_path)
    
    # Exécution de la requête et stockage du résultat dans un DataFrame Pandas
    df = pd.read_sql_query(query, conn)
    
    # Fermeture de la connexion à la base de données
    conn.close()
    
    # Conversion du DataFrame en une liste de dictionnaires
    result = df.to_dict(orient='records')
    
    return result
