import sqlite3
import os
import pandas as pd
import surprise
from surprise import Dataset, Reader, SVD
from sklearn.model_selection import train_test_split
import joblib

import os

current_dir = os.path.dirname(os.path.abspath(__file__))  
db_path = os.path.join(current_dir, '../../../db.sqlite3') 
conn = sqlite3.connect(db_path)


query = """
SELECT 
    main_order.client_id,
    main_pizza.name AS pizza_name
FROM 
    main_order
JOIN 
    main_pizza
ON 
    main_order.pizza_id = main_pizza.pizza_id
"""
data = pd.read_sql_query(query, conn)
conn.close()

client_ids = data['client_id'].unique()

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

# Entraîner le modèle avec data train
algo = SVD(n_factors=50, reg_all=0.1)
algo.fit(trainset)


collaborative_model_path = 'models/collaborative_model.joblib'
joblib.dump(algo, collaborative_model_path)
