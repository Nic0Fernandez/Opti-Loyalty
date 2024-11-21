import sqlite3
import pandas as pd
import numpy as np
import os

# Chemin absolu vers la base de données
def get_database_connection():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, '../../../db.sqlite3')
    return sqlite3.connect(db_path)

# Charger les données nécessaires
def load_data():
    conn = get_database_connection()

    query_pizzas = """
    SELECT pizza_id, name, size, ingredients
    FROM main_pizza;
    """
    pizzas_df = pd.read_sql_query(query_pizzas, conn)

    query_orders = """
    SELECT client_id, pizza_id, order_date
    FROM orders;
    """
    orders_df = pd.read_sql_query(query_orders, conn)
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])

    conn.close()

    return pizzas_df, orders_df

# Fonctions utilitaires
def get_pizza_ingredients(pizza_id, pizzas_df):
    """Retourne les ingrédients d'une pizza donnée par son pizza_id."""
    return pizzas_df[pizzas_df['pizza_id'] == pizza_id]['ingredients'].iloc[0].split(', ')

def recommend_pizzas_based_on_ingredients(client_pizzas, pizzas_df, top_k=1):
    """Recommande des pizzas basées sur les ingrédients des pizzas commandées par le client."""
    client_ingredients = []
    for pizza_id in client_pizzas:
        client_ingredients.extend(get_pizza_ingredients(pizza_id, pizzas_df))
    client_ingredients = set(client_ingredients)

    similarities = []
    for idx, pizza in pizzas_df.iterrows():
        pizza_ingredients = set(pizza['ingredients'].split(', '))
        common_ingredients = len(client_ingredients.intersection(pizza_ingredients))
        total_ingredients = len(client_ingredients.union(pizza_ingredients))
        similarity_score = common_ingredients / total_ingredients if total_ingredients > 0 else 0
        similarities.append((pizza['pizza_id'], similarity_score))
    
    similarities.sort(key=lambda x: x[1], reverse=True)

    recommendations = []
    for i in range(len(similarities)):
        recommanded_pizza_idx = similarities[i][0]
        recommanded_pizza = pizzas_df.loc[pizzas_df['pizza_id'] == recommanded_pizza_idx].iloc[0]
        
        if recommanded_pizza["name"] not in recommendations:
            recommendations.append(recommanded_pizza["name"])
            
        if len(recommendations) == top_k : 
            break
    
    return recommendations

def precision_recall_at_k(recommended_pizzas, relevant_pizzas, k=1):
    recommended_set = set(recommended_pizzas[:k])
    relevant_set = set(relevant_pizzas)
    hits = recommended_set.intersection(relevant_set)
    
    precision = len(hits) / k
    recall = len(hits) / len(relevant_set) if len(relevant_set) > 0 else 0
    return precision, recall

# Fonction d'évaluation
def evaluate_model():
    pizzas_df, orders_df = load_data()
    clients = orders_df['client_id'].unique()

    precisions, recalls, f1_scores = [], [], []

    for client_id in clients:
        relevant_pizzas = orders_df[orders_df['client_id'] == client_id]['pizza_id'].tolist()
        relevant_pizzas = pizzas_df[pizzas_df['pizza_id'].isin(relevant_pizzas)]['name'].tolist()
        
        client_pizzas = orders_df[orders_df['client_id'] == client_id]['pizza_id'].tolist()
        recommended_pizzas = recommend_pizzas_based_on_ingredients(client_pizzas, pizzas_df, top_k=1)
        recommended_pizzas_names = pizzas_df[pizzas_df['pizza_id'].isin(recommended_pizzas)]['name'].tolist()
        
        print(f"Client {client_id} :")
        print(f"Recommandations : {recommended_pizzas_names}")
        print(f"Pizzas pertinentes : {relevant_pizzas}")
        
        precision, recall = precision_recall_at_k(recommended_pizzas_names, relevant_pizzas, k=1)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1_score)

    print(f"Précision moyenne : {sum(precisions)/len(precisions):.2f}")
    print(f"Rappel moyen : {sum(recalls)/len(recalls):.2f}")
    print(f"F1-Score moyen : {sum(f1_scores)/len(f1_scores):.2f}")
