import pandas as pd
import sqlite3



def load_pizza_data():
    df = pd.read_csv('data/consumer_data.csv')

    required_columns = ['client_id','pizza_id','order_date']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Le fichier Excel doit contenir les colonnes suivantes : {', '.join(required_columns)}")
    
    return df

def create_menu_table(conn):
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS orders')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            pizza_id TEXT,
            order_date DATE NOT NULL,
            FOREIGN KEY (pizza_id) REFERENCES menu (pizza_id)
        )
    ''')
    conn.commit()

def insert_pizza_data(conn, df):
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO orders (pizza_id, client_id,  order_date)
            VALUES (?, ?, ?)
        ''', (row['pizza_id'], row['client_id'], row['order_date']))
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
