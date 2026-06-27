# db_builder.py - Download and build full Lego SQLite database from Rebrickable GZ dumps
import os
import urllib.request
import gzip
import csv
import sqlite3
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "lego.db")

CSV_FILES = {
    "colors.csv.gz": "https://cdn.rebrickable.com/media/downloads/colors.csv.gz",
    "themes.csv.gz": "https://cdn.rebrickable.com/media/downloads/themes.csv.gz",
    "minifigs.csv.gz": "https://cdn.rebrickable.com/media/downloads/minifigs.csv.gz",
    "sets.csv.gz": "https://cdn.rebrickable.com/media/downloads/sets.csv.gz",
    "inventories.csv.gz": "https://cdn.rebrickable.com/media/downloads/inventories.csv.gz",
    "inventory_minifigs.csv.gz": "https://cdn.rebrickable.com/media/downloads/inventory_minifigs.csv.gz",
    "inventory_parts.csv.gz": "https://cdn.rebrickable.com/media/downloads/inventory_parts.csv.gz",
    "parts.csv.gz": "https://cdn.rebrickable.com/media/downloads/parts.csv.gz",
    "elements.csv.gz": "https://cdn.rebrickable.com/media/downloads/elements.csv.gz"
}

def setup_db(conn):
    cursor = conn.cursor()
    
    # 1. Colors
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS colors (
        id INTEGER PRIMARY KEY,
        name TEXT,
        rgb TEXT,
        is_trans TEXT
    )""")
    
    # 2. Themes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS themes (
        id INTEGER PRIMARY KEY,
        name TEXT,
        parent_id INTEGER
    )""")
    
    # 3. Minifigs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS minifigs (
        minifig_num TEXT PRIMARY KEY,
        name TEXT,
        num_parts INTEGER
    )""")
    
    # 4. Sets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sets (
        set_num TEXT PRIMARY KEY,
        name TEXT,
        year INTEGER,
        theme_id INTEGER,
        num_parts INTEGER,
        img_url TEXT
    )""")
    
    # 5. Inventories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventories (
        id INTEGER PRIMARY KEY,
        version INTEGER,
        set_num TEXT
    )""")
    
    # 6. Inventory Minifigs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_minifigs (
        inventory_id INTEGER,
        minifig_num TEXT,
        quantity INTEGER
    )""")
    
    # 7. Inventory Parts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_parts (
        inventory_id INTEGER,
        part_num TEXT,
        color_id INTEGER,
        quantity INTEGER,
        is_spare TEXT,
        img_url TEXT
    )""")
    
    # 8. Parts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parts (
        part_num TEXT PRIMARY KEY,
        name TEXT,
        part_cat_id INTEGER,
        part_material_id INTEGER
    )""")
    
    # 9. Elements (official LEGO Element IDs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS elements (
        element_id TEXT PRIMARY KEY,
        part_num TEXT,
        color_id INTEGER
    )""")
    
    conn.commit()

def download_file(filename, url):
    local_path = os.path.join(DB_DIR, filename)
    if os.path.exists(local_path):
        print(f"[Info] File {filename} already exists, skipping download.")
        return local_path
    
    print(f"[Download] Downloading {filename} from {url}...")
    start_time = time.time()
    
    # Custom User-Agent to prevent bot-detection issues
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    )
    
    with urllib.request.urlopen(req) as response, open(local_path, 'wb') as out_file:
        out_file.write(response.read())
        
    print(f"[Download] Completed in {time.time() - start_time:.2f} seconds.")
    return local_path

def import_csv_to_table(conn, file_path, table_name, num_fields):
    print(f"[Import] Importing {os.path.basename(file_path)} into SQLite table '{table_name}'...")
    start_time = time.time()
    
    cursor = conn.cursor()
    # Read Gzipped CSV
    with gzip.open(file_path, mode='rt', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) # skip header
        
        placeholders = ",".join(["?"] * num_fields)
        insert_query = f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})"
        
        # Batch insert for extreme speed
        batch = []
        batch_size = 50000
        count = 0
        
        for row in reader:
            # Handle row size mismatch just in case
            if len(row) > num_fields:
                row = row[:num_fields]
            elif len(row) < num_fields:
                row = row + [""] * (num_fields - len(row))
                
            batch.append(row)
            count += 1
            if len(batch) >= batch_size:
                cursor.executemany(insert_query, batch)
                batch = []
                
        if batch:
            cursor.executemany(insert_query, batch)
            
    conn.commit()
    print(f"[Import] Finished {count} rows in {time.time() - start_time:.2f} seconds.")

def create_indexes(conn):
    print("[Index] Creating indexes for query optimization...")
    start_time = time.time()
    cursor = conn.cursor()
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_set ON inventories(set_num)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_parts_id ON inventory_parts(inventory_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_parts_part ON inventory_parts(part_num)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_minifigs_num ON inventory_minifigs(minifig_num)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_minifigs_id ON inventory_minifigs(inventory_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_elements_part_color ON elements(part_num, color_id)")
    
    conn.commit()
    print(f"[Index] Completed in {time.time() - start_time:.2f} seconds.")

def main():
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    
    # SQLite optimization pragmas for faster bulk inserts
    cursor = conn.cursor()
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("PRAGMA cache_size = 100000")
    
    setup_db(conn)
    
    # Download and import each CSV file
    # Format: (filename, url, table_name, number of fields)
    import_tasks = [
        ("colors.csv.gz", CSV_FILES["colors.csv.gz"], "colors", 4),
        ("themes.csv.gz", CSV_FILES["themes.csv.gz"], "themes", 3),
        ("minifigs.csv.gz", CSV_FILES["minifigs.csv.gz"], "minifigs", 3),
        ("sets.csv.gz", CSV_FILES["sets.csv.gz"], "sets", 6),
        ("inventories.csv.gz", CSV_FILES["inventories.csv.gz"], "inventories", 3),
        ("inventory_minifigs.csv.gz", CSV_FILES["inventory_minifigs.csv.gz"], "inventory_minifigs", 3),
        ("inventory_parts.csv.gz", CSV_FILES["inventory_parts.csv.gz"], "inventory_parts", 6),
        ("parts.csv.gz", CSV_FILES["parts.csv.gz"], "parts", 4),
        ("elements.csv.gz", CSV_FILES["elements.csv.gz"], "elements", 3)
    ]
    
    total_start = time.time()
    
    for filename, url, table_name, num_fields in import_tasks:
        try:
            local_file = download_file(filename, url)
            import_csv_to_table(conn, local_file, table_name, num_fields)
        except Exception as e:
            print(f"[Error] Failed task for {filename}: {e}")
            
    create_indexes(conn)
    
    conn.close()
    print(f"\n[Success] SQLite Database successfully built at {DB_PATH}!")
    print(f"[Success] Total execution time: {time.time() - total_start:.2f} seconds.")

if __name__ == "__main__":
    main()
