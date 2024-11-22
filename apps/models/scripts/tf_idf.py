import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

def get_tfidf_recommendations(client_id, db_path, num_recommendations=10):
    conn = sqlite3.connect(db_path)

    query_pizzas = """
    SELECT pizza_id, name, ingredients
    FROM main_pizza;
    """
    pizzas_df = pd.read_sql_query(query_pizzas, conn)

    query_user_orders = f"""
    SELECT pizza_id
    FROM main_order
    WHERE client_id = {client_id};
    """
    user_orders_df = pd.read_sql_query(query_user_orders, conn)

    conn.close()

    if user_orders_df.empty:
        return pizzas_df['name'].head(num_recommendations).tolist()

    user_pizza_ids = user_orders_df['pizza_id'].unique()

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(pizzas_df['ingredients'])

    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    pizza_id_to_index = pd.Series(pizzas_df.index, index=pizzas_df['pizza_id']).drop_duplicates()
    index_to_pizza_id = pd.Series(pizzas_df['pizza_id'], index=pizzas_df.index)

    user_pizza_indices = pizza_id_to_index[user_pizza_ids]

    sim_scores = cosine_sim[user_pizza_indices].mean(axis=0)
    sim_scores = list(enumerate(sim_scores))
    sim_scores = [ (i, score) for i, score in sim_scores if index_to_pizza_id[i] not in user_pizza_ids ]

    # Trier les pizzas en fonction des scores de similarité
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    recommended_pizzas = []
    for i, score in sim_scores[:num_recommendations]:
        pizza_name = pizzas_df.iloc[i]['name']
        recommended_pizzas.append(pizza_name)

    return recommended_pizzas

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, '../../../db.sqlite3')

    client_id = 1  # Exemple de client_id
    recommendations = get_tfidf_recommendations(client_id, db_path)
