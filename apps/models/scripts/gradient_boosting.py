import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import warnings
warnings.filterwarnings("ignore")

import os

# Chemin absolu vers la base de données
current_dir = os.path.dirname(os.path.abspath(__file__))  
db_path = os.path.join(current_dir, '../../../db.sqlite3') 
conn = sqlite3.connect(db_path)

# Chargement des données
menu = pd.read_sql_query("SELECT * FROM main_pizza", conn)
orders = pd.read_sql_query("SELECT * FROM main_order", conn)

# Fermer la connexion
conn.close()

# Jointure pour obtenir les noms des pizzas
order_data = orders.merge(menu, on='pizza_id')

# Remplacer pizza_id par name
order_data_grouped = order_data.groupby(['client_id', 'name'])['name'].count().unstack(fill_value=0)

# Création des labels pour recommandation
# La pizza la plus commandée pour chaque client devient la cible
order_data_grouped['most_ordered'] = order_data_grouped.idxmax(axis=1)
target = order_data_grouped['most_ordered']
features = order_data_grouped.drop(columns=['most_ordered'])

# Encodage des pizzas
features_encoded = features  # Pas besoin d'encodage pour les noms dans ce cas
target_encoded = target.astype('category').cat.codes
pizza_name_mapping = dict(enumerate(target.astype('category').cat.categories))  # Pour décoder plus tard


# Séparation des données pour entraînement et test
X_train, X_test, y_train, y_test = train_test_split(features_encoded, target_encoded, test_size=0.2, random_state=42)

# Entraînement du modèle Gradient Boosting
model = GradientBoostingClassifier(n_estimators=40, learning_rate=0.2, random_state=42, max_depth=3, subsample=0.8)
model.fit(X_train, y_train)


import joblib

# Chemin pour sauvegarder le modèle
gradient_boosting_model_path = "models/gradient_boosting_model.joblib"

# Sauvegarder le modèle
joblib.dump(model, gradient_boosting_model_path)


print(f"Modèle sauvegardé dans {gradient_boosting_model_path}")
