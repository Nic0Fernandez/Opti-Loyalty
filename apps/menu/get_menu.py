import sqlite3
import pandas as pd

# Requête SQL pour récupérer les 5 pizzas les plus populaires du mois dernier
query = """
    SELECT DISTINCT name, ingredients, image
    FROM main_pizza
"""

def get_menu(db_path):
    # Connexion à la base de données SQLite
    conn = sqlite3.connect(db_path)
    
    # Exécution de la requête et stockage du résultat dans un DataFrame Pandas
    df = pd.read_sql_query(query, conn)
    
    # Fermeture de la connexion à la base de données
    conn.close()
    
    # Conversion du DataFrame en une liste de dictionnaires
    result = df.to_dict(orient='records')
    
    return result
