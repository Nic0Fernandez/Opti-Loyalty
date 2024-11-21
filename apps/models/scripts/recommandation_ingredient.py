import sqlite3
import pandas as pd
import numpy as np

import os

# Chemin absolu vers la base de données
current_dir = os.path.dirname(os.path.abspath(__file__))  
db_path = os.path.join(current_dir, '../../../db.sqlite3') 
conn = sqlite3.connect(db_path)

query_pizzas = """
SELECT pizza_id, name, size, ingredients
FROM menu;
"""
pizzas_df = pd.read_sql_query(query_pizzas, conn)

query_orders = """
SELECT client_id, pizza_id, order_date
FROM orders;
"""
orders_df = pd.read_sql_query(query_orders, conn)
orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])

conn.close()


def get_pizza_ingredients(pizza_id, pizzas_df):
    """Retourne les ingrédients d'une pizza donnée par son pizza_id."""
    return pizzas_df[pizzas_df['pizza_id'] == pizza_id]['ingredients'].iloc[0].split(', ')

def recommend_pizzas_based_on_ingredients(client_pizzas, pizzas_df, top_k=1):
    """
    Recommande des pizzas basées sur les ingrédients des pizzas commandées par le client.
    
    Parameters:
        client_pizzas (List[str]): Liste des pizza_ids des pizzas commandées par le client.
        similarity_matrix (array): Matrice de similarité entre les pizzas.
        pizzas_df (DataFrame): Informations sur les pizzas.
        top_k (int): Nombre de recommandations.
    
    Returns:
        List[Tuple[str, float]]: Liste des recommandations avec scores.
    """
    # Extraire les ingrédients des pizzas commandées par le client
    client_ingredients = []
    for pizza_id in client_pizzas:
        client_ingredients.extend(get_pizza_ingredients(pizza_id, pizzas_df))
    client_ingredients = set(client_ingredients)  # Éviter les doublons
    
    # Calculer la similarité avec les autres pizzas basées sur les ingrédients partagés
    similarities = []
    for idx, pizza in pizzas_df.iterrows():
        pizza_ingredients = set(pizza['ingredients'].split(', '))
        common_ingredients = len(client_ingredients.intersection(pizza_ingredients))
        total_ingredients = len(client_ingredients.union(pizza_ingredients))
        similarity_score = common_ingredients / total_ingredients if total_ingredients > 0 else 0
        similarities.append((pizza['pizza_id'], similarity_score))
    
    # Trier les pizzas par similarité décroissante et retourner les k premières
    recommendations = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    recommended_pizzas = [pizza[0] for pizza in recommendations]
    
    return recommended_pizzas


def precision_recall_at_k(recommended_pizzas, relevant_pizzas, k=1):
    recommended_set = set(recommended_pizzas[:k])  # Top-k recommandations
    relevant_set = set(relevant_pizzas)  # Pizzas réellement commandées
    hits = recommended_set.intersection(relevant_set)
    
    precision = len(hits) / k
    recall = len(hits) / len(relevant_set) if len(relevant_set) > 0 else 0
    return precision, recall

# Liste de tous les clients à évaluer
clients = orders_df['client_id'].unique()

precisions, recalls, f1_scores = [], [], []

for client_id in clients:
    # Pizzas commandées dans l'ensemble complet (pizzas pertinentes)
    relevant_pizzas = orders_df[orders_df['client_id'] == client_id]['pizza_id'].tolist()
    relevant_pizzas = pizzas_df[pizzas_df['pizza_id'].isin(relevant_pizzas)]['name'].tolist()
    
    # Pizzas commandées par le client (pour l'historique de recommandations)
    client_pizzas = orders_df[orders_df['client_id'] == client_id]['pizza_id'].tolist()
    
    # Recommandation de pizzas en fonction des ingrédients des pizzas commandées par le client
    recommended_pizzas = recommend_pizzas_based_on_ingredients(client_pizzas, pizzas_df, top_k=1)
    recommended_pizzas_names = pizzas_df[pizzas_df['pizza_id'].isin(recommended_pizzas)]['name'].tolist()
    
    print(f"Client {client_id} :")
    print(f"Recommandations : {recommended_pizzas_names}")
    print(f"Pizzas pertinentes : {relevant_pizzas}")
    
    # Calcul de la précision, du rappel et du F1-score
    precision, recall = precision_recall_at_k(recommended_pizzas_names, relevant_pizzas, k=1)
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    precisions.append(precision)
    recalls.append(recall)
    f1_scores.append(f1_score)

# Affichage des résultats
print(f"Précision moyenne : {sum(precisions)/len(precisions):.2f}")
print(f"Rappel moyen : {sum(recalls)/len(recalls):.2f}")
print(f"F1-Score moyen : {sum(f1_scores)/len(f1_scores):.2f}")



