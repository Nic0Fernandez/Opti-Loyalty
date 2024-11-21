import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

conn.close()


tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(pizzas_df['ingredients'])


cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

import pickle

# Chemins pour sauvegarder les objets
tfidf_path = "tfidf_vectorizer.pkl"
cosine_sim_path = "cosine_similarity.pkl"

# Sauvegarder TfidfVectorizer
with open(tfidf_path, 'wb') as f:
    pickle.dump(tfidf_vectorizer, f)

# Sauvegarder la matrice de similarité
with open(cosine_sim_path, 'wb') as f:
    pickle.dump(cosine_sim, f)