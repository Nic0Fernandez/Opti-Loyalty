import sqlite3
import pandas as pd
from collections import Counter

conn = sqlite3.connect('../db.sqlite3')

query = """
SELECT name, strftime('%Y-%m', order_date) AS order_month
FROM orders JOIN menu ON orders.pizza_id=menu.pizza_id;
"""

df = pd.read_sql_query(query, conn)

if df.empty:
    print("Aucune donnée récupérée de la base de données.")
else:
    top_pizzas_by_month = (
        df.groupby('order_month')['name']
        .apply(lambda x: Counter(x).most_common(3))  
        .reset_index(name='top_pizzas')
    )
    
    print("Top 3 des pizzas les plus vendues par mois :")
    print(top_pizzas_by_month)

conn.close()
