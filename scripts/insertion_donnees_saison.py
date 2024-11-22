import pandas as pd
import sqlite3



def load_vegetables_data():
    df = pd.read_csv('data/vegetables Dataset.csv')

    required_columns = ['Name','Season']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Le fichier csv doit contenir les colonnes suivantes : {';'.join(required_columns)}")
    
    return df

def create_seasonnality_table(conn):
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS seasonnality')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seasonnality (
            vegetable TEXT PRIMARY KEY,
            start_day INTEGER NOT NULL,
            start_month INTEGER NOT NULL,
            end_day INTEGER NOT NULL,
            end_month INTEGER NOT NULL
        )
    ''')
    conn.commit()

def insert_vegetables_data(conn, df):
    cursor = conn.cursor()
    for _, row in df.iterrows():
        print(row)
        start_day,start_month,end_day,end_month=convert_season_to_dates(row['Season'])
        cursor.execute('''
            INSERT INTO seasonnality (vegetable,start_day,start_month,end_day,end_month)
            VALUES (?, ?, ?, ?, ?)
        ''', (row['Name'], start_day,start_month,end_day,end_month))
    conn.commit()
    
def convert_season_to_dates(season):
    if season=='Winter':
        start_day=21
        start_month=12
        end_day=20
        end_month=3
    elif season=='Fall':
        start_day=22
        start_month=9
        end_day=20
        end_month=12
    elif season=='Summer':
        start_day=22
        start_month=6
        end_day=21
        end_month=9
    elif season=="Spring":
        start_day=21
        start_month=3
        end_day=21
        end_month=6
    elif season=="Spring/Summer":
        start_day=21
        start_month=3
        end_day=21
        end_month=9
    else:
        start_day=22
        start_month=9
        end_day=20
        end_month=3
    return start_day,start_month,end_day,end_month
        

def main(): 
    db_file = '../db.sqlite3'  

    df = load_vegetables_data()

    conn = sqlite3.connect(db_file)
    

    create_seasonnality_table(conn)

    insert_vegetables_data(conn, df)

    conn.close()

    print(f"Les données ont été insérées dans la base de données '{db_file}'.")

if __name__ == "__main__":
    main()
