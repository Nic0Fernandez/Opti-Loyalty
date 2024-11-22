import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings("ignore")

import os

def get_forest_recommendations(client_id, db_path):
    conn = sqlite3.connect(db_path)

    menu = pd.read_sql_query("SELECT * FROM main_pizza", conn)
    orders = pd.read_sql_query("SELECT * FROM main_order", conn)

    conn.close()

    order_data = orders.merge(menu, on='pizza_id')

    # Créer un pivot pour les clients et les pizzas
    order_data_grouped = order_data.groupby(['client_id', 'name'])['name'].count().unstack(fill_value=0)

    order_data_grouped['most_ordered'] = order_data_grouped.idxmax(axis=1)
    target = order_data_grouped['most_ordered']
    features = order_data_grouped.drop(columns=['most_ordered'])

    X = features
    y = target

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    if client_id in X.index:
        user_features = X.loc[[client_id]]
    else:
        user_features = pd.DataFrame(0, index=[client_id], columns=X.columns)

    # Prédire les probabilités pour toutes les classes (pizzas)
    predictions_proba = model.predict_proba(user_features)[0]
    pizza_names = model.classes_

    pizza_probabilities = list(zip(pizza_names, predictions_proba))
    pizza_probabilities.sort(key=lambda x: x[1], reverse=True)
    top_recommendations = pizza_probabilities[:10]
    recommendations = [pizza for pizza, prob in top_recommendations]

    return recommendations

