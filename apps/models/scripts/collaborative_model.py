import sqlite3
import os
import pandas as pd
from surprise import Dataset, Reader, SVD
from sklearn.model_selection import train_test_split
import pickle

import os

# Chemin absolu vers la base de données
current_dir = os.path.dirname(os.path.abspath(__file__))  
db_path = os.path.join(current_dir, '../../../db.sqlite3') 
conn = sqlite3.connect(db_path)


query = """
SELECT 
    orders.client_id,
    menu.name AS pizza_name
FROM 
    orders
JOIN 
    menu
ON 
    orders.pizza_id = menu.pizza_id
"""
data = pd.read_sql_query(query, conn)

# Fermer la connexion
conn.close()

# Récupérer tous les clients
client_ids = data['client_id'].unique()

# Split des clients en 80% train, 20% test
train_clients, test_clients = train_test_split(client_ids, test_size=0.2, random_state=42)

# Dataset d'entraînement
train_data = data[data['client_id'].isin(train_clients)]

# Dataset de test
test_data = data[data['client_id'].isin(test_clients)]

# Calculer le nombre de commandes par client et pizza (fréquence comme score)
train_pizza_counts = train_data.groupby(['client_id', 'pizza_name']).size().reset_index(name='rating')
test_pizza_counts = test_data.groupby(['client_id', 'pizza_name']).size().reset_index(name='rating')

reader = Reader(rating_scale=(train_pizza_counts['rating'].min(), train_pizza_counts['rating'].max()))
trainset = Dataset.load_from_df(train_pizza_counts[['client_id', 'pizza_name', 'rating']], reader).build_full_trainset()
testset = Dataset.load_from_df(test_pizza_counts[['client_id', 'pizza_name', 'rating']], reader).build_full_trainset()

# Entraîner un modèle SVD sur l'ensemble d'entraînement
algo = SVD(n_factors=50, reg_all=0.1)
algo.fit(trainset)


# Chemin pour sauvegarder le modèle
collaborative_model_path = '../collaborative_model.pkl'

# Sauvegarder le modèle
with open(collaborative_model_path, 'wb') as f:
    pickle.dump(algo, f)

print(f"Modèle sauvegardé dans {collaborative_model_path}")