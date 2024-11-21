import pandas as pd
import sqlite3

def load_pizza_data():
    df = pd.read_excel("data/Pizza_Sales.xlsx")

    required_columns = ['pizza_id', 'unit_price','pizza_name', 'pizza_ingredients', 'pizza_category', 'pizza_size']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Le fichier Excel doit contenir les colonnes suivantes : {', '.join(required_columns)}")
    
    return df

def create_menu_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main_pizza (
            pizza_id TEXT PRIMARY KEY,
            unit_price REAL NOT NULL,
            name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            category TEXT NOT NULL,
            size TEXT NOT NULL
        )
    ''')
    conn.commit()

def insert_pizza_data(conn, df):
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO menu (pizza_id, unit_price, name, ingredients, category, size)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (row['pizza_id'], row['unit_price'], row['pizza_name'], row['pizza_ingredients'], row['pizza_category'], row['pizza_size']))
    conn.commit()

def main(): 
    db_file = '../db.sqlite3'  

    df = load_pizza_data()

    conn = sqlite3.connect(db_file)

    create_menu_table(conn)

    insert_pizza_data(conn, df)

    conn.close()

    print(f"Les données ont été insérées dans la base de données '{db_file}'.")

if __name__ == "__main__":
    main()
