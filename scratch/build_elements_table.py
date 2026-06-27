import os
import urllib.request
import gzip
import csv
import sqlite3
import time

DB_PATH = "/Users/xiaozhi/Desktop/find/db/lego.db"
URL = "https://cdn.rebrickable.com/media/downloads/elements.csv.gz"
GZ_PATH = "/Users/xiaozhi/Desktop/find/db/elements.csv.gz"

def test_download_and_build():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS elements")
        cursor.execute("""
            CREATE TABLE elements (
                element_id TEXT PRIMARY KEY,
                part_num TEXT,
                color_id INTEGER
            )
        """)
        
        print("Importing CSV into elements table...")
        start = time.time()
        with gzip.open(GZ_PATH, 'rt', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # element_id, part_num, color_id, design_id
            print(f"CSV Header: {header}")
            
            batch = []
            count = 0
            for row in reader:
                if len(row) >= 3:
                    batch.append((row[0], row[1], int(row[2])))
                    count += 1
                if len(batch) >= 50000:
                    cursor.executemany("INSERT OR REPLACE INTO elements VALUES (?, ?, ?)", batch)
                    batch = []
            if batch:
                cursor.executemany("INSERT OR REPLACE INTO elements VALUES (?, ?, ?)", batch)
        
        conn.commit()
        print(f"Imported {count} rows in {time.time() - start:.2f} seconds.")
        
        print("Creating index for fast queries...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_elements_part_color ON elements(part_num, color_id)")
        conn.commit()
        
        print("\nTesting query for Gingerbread parts:")
        cursor.execute("""
            SELECT e.element_id, e.part_num, e.color_id, p.name 
            FROM elements e 
            JOIN parts p ON e.part_num = p.part_num
            WHERE p.name LIKE '%Gingerbread%'
            LIMIT 10
        """)
        print(cursor.fetchall())
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_download_and_build()
