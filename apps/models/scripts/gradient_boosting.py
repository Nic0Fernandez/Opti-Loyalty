import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
import warnings
warnings.filterwarnings("ignore")
import os

def get_boosting_recommendations(client_id, db_path):
    conn = sqlite3.connect(db_path)

    menu = pd.read_sql_query("SELECT * FROM main_pizza", conn)
    orders = pd.read_sql_query("SELECT * FROM main_order", conn)

    conn.close()

    order_data = orders.merge(menu, on='pizza_id')
    order_data_grouped = order_data.groupby(['client_id', 'name'])['name'].count().unstack(fill_value=0)

    # La pizza la plus commandée pour chaque client devient la cible
    order_data_grouped['most_ordered'] = order_data_grouped.idxmax(axis=1)
    target = order_data_grouped['most_ordered']
    features = order_data_grouped.drop(columns=['most_ordered'])

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

    model = GradientBoostingClassifier(n_estimators=30, learning_rate=0.2, random_state=42, max_depth=3, subsample=0.8)
    model.fit(X_train, y_train)



    if client_id in features.index:
        user_features = features.loc[[client_id]]
    else:
        user_features = pd.DataFrame(0, index=[client_id], columns=features.columns)

    # Prédire les probabilités pour toutes les classes (pizzas)
    predictions_proba = model.predict_proba(user_features)[0]
    pizza_names = model.classes_


    pizza_probabilities = list(zip(pizza_names, predictions_proba))
    pizza_probabilities.sort(key=lambda x: x[1], reverse=True)
    top_recommendations = pizza_probabilities[:10]
    recommendations = [pizza for pizza, prob in top_recommendations]

    return recommendations
