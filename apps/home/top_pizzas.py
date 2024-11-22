import sqlite3
import pandas as pd
from datetime import datetime

# Requête SQL pour récupérer les 5 pizzas les plus populaires du mois dernier (ie 30 derniers jours)
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



#Recommandations personnalisées
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




#Pizzas de saison
query_pizzas = """
    SELECT p.name,ingredients,image,unit_price
    FROM main_pizza p
    WHERE unit_price = (
            SELECT MIN(mp.unit_price)
            FROM main_pizza mp
            WHERE mp.name = p.name
        )    
    GROUP BY name
"""



def pizzas_season(db_path):
    """
    Calcul d'un score de saisonnalité pour chaque pizza, 
    2 points par ingrédient de saison, 1 point par ingrédient qui n'est pas un légume et 0 pour un ingrédient pas de saison
    Pizzas sans légumes ne peuvent pas être de saison
    
    """
    conn = sqlite3.connect(db_path)
    df_pizzas = pd.read_sql_query(query_pizzas, conn)
    df_pizzas['score_seasonnality'] = 0.0
    for _,pizza in df_pizzas.iterrows():
        score_seasonnality=0
        ingredients = pizza['ingredients'].split(',')  
        ingredients = [ingredient.strip() for ingredient in ingredients]
        
        #Récupérer les légumes parmi les ingrédients
        cursor = conn.cursor() 
        like_conditions = [
            f"(LOWER(vegetable) LIKE '%' || LOWER(?) || '%' OR LOWER(?) LIKE '%' || LOWER(vegetable) || '%')"
            for _ in ingredients
        ]
        where_clause = " OR ".join(like_conditions)
        query_at_least_one_vegetable = f"""
            SELECT vegetable
            FROM seasonnality
            WHERE {where_clause}
        """
        params = [(ingredient, '%' + ingredient + '%') for ingredient in ingredients]
        params = [param for sublist in params for param in sublist]
        cursor.execute(query_at_least_one_vegetable, params)
        present_ingredients = {row[0] for row in cursor.fetchall()}
        #Exclusion des pizzas sans légumes
        if len(present_ingredients)==0:
            continue
        
        #Calcul du score
        for ingredient in ingredients:
            # Ingrédient pas légume
            if ingredient not in present_ingredients:
                score_seasonnality+=1
            else:
                today = datetime.now()
                current_day = today.day
                current_month = today.month
                
                #Requête pour vérifier la saisonnalité de l'ingrédient (correspondance des dates de consommation avec date du jour)
                cursor = conn.cursor()
                query_ingredients=f"""
                    SELECT COUNT(*)
                    FROM seasonnality
                    WHERE vegetable LIKE "%{ingredient}%"
                    AND  
                    (
                    ((start_month < end_month OR (start_month = end_month AND start_day <= end_day))
                    AND
                    (({current_month} > start_month OR ({current_month} = start_month AND {current_day} >= start_day))
                    AND
                    ({current_month} < end_month OR ({current_month} = end_month AND {current_day} <= end_day))))
                    OR
                    ((start_month > end_month)
                    AND
                    (({current_month} > start_month OR ({current_month} = start_month AND {current_day} >= start_day))
                    OR
                    ({current_month} < end_month OR ({current_month} = end_month AND {current_day} <= end_day))))
                    );
                """
                cursor.execute(query_ingredients)
                #2 points si ingrédient de saison
                score_seasonnality += 2*cursor.fetchone()[0] 
                
        #Normalisation du score
        normalized_score=score_seasonnality/len(df_pizzas['ingredients'])    
        df_pizzas.loc[df_pizzas['name'] == pizza['name'], 'score_seasonnality'] = normalized_score

    conn.close()
    result = df_pizzas.sort_values(by='score_seasonnality', ascending=False).head(5)
    result=result.to_dict(orient='records')
    return result

