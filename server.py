# server.py - Zero-dependency Python Web Server & SQLite API Gateway (With Chinese Translations & Filters)
import http.server
import socketserver
import urllib.parse
import json
import sqlite3
import os
import hashlib
import time
import gzip
from collections import OrderedDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", 8000))
DB_PATH = os.path.join(BASE_DIR, "db", "lego.db")
STATIC_DIR = BASE_DIR

API_CACHE_MAX_ITEMS = 256
API_CACHE_TTL_SECONDS = 300
SCAN_CANDIDATE_CACHE_TTL_SECONDS = 3600

API_CACHE = OrderedDict()
SCAN_CANDIDATE_CACHE = {"loaded_at": 0, "rows": None}

MINIFIG_EXCLUSION_SQL = """
  AND LOWER(m.name) NOT LIKE '%keychain%'
  AND LOWER(m.name) NOT LIKE '%key chain%'
  AND LOWER(m.name) NOT LIKE '%magnet%'
  AND LOWER(m.name) NOT LIKE '%watch%'
  AND LOWER(m.name) NOT LIKE '%clock%'
  AND LOWER(m.name) NOT LIKE '%book%'
  AND LOWER(m.name) NOT LIKE '%sticker%'
  AND LOWER(m.name) NOT LIKE '%card%'
  AND LOWER(m.name) NOT LIKE '%giant%'
  AND LOWER(m.name) NOT LIKE '%maxifigure%'
  AND LOWER(m.name) NOT LIKE '%brick-built%'
  AND LOWER(m.name) NOT LIKE '%pen%'
  AND LOWER(m.name) NOT LIKE '%torch%'
  AND LOWER(m.name) NOT LIKE '%light%'
  AND LOWER(m.name) NOT LIKE '%plush%'
  AND LOWER(m.name) NOT LIKE '%notebook%'
  AND LOWER(m.name) NOT LIKE '%tag%'
  AND LOWER(m.name) NOT LIKE '%bag%'
  AND LOWER(m.name) NOT LIKE '%frame%'
  AND LOWER(m.name) NOT LIKE '%display%'
  AND LOWER(m.name) NOT LIKE '%scale%'
"""

def open_db():
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=rw", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA cache_size = -32768")
    return conn

def get_cached_api_response(cache_key):
    cached = API_CACHE.get(cache_key)
    if not cached:
        return None
    expires_at, payload = cached
    if expires_at < time.time():
        API_CACHE.pop(cache_key, None)
        return None
    API_CACHE.move_to_end(cache_key)
    return payload

def set_cached_api_response(cache_key, payload):
    API_CACHE[cache_key] = (time.time() + API_CACHE_TTL_SECONDS, payload)
    API_CACHE.move_to_end(cache_key)
    while len(API_CACHE) > API_CACHE_MAX_ITEMS:
        API_CACHE.popitem(last=False)

TRANSLATION_MAP = {
    "黑武士": "darth vader",
    "达斯维达": "darth vader",
    "达斯·维达": "darth vader",
    "维达": "vader",
    "白兵": "stormtrooper",
    "风暴兵": "stormtrooper",
    "克隆兵": "clone trooper",
    "克隆人": "clone",
    "宇航员": "astronaut",
    "太空人": "space",
    "太空": "space",
    "钢铁侠": "iron man",
    "托尼": "tony",
    "蜘蛛侠": "spider-man",
    "蝙蝠侠": "batman",
    "哈利波特": "harry potter",
    "哈利": "harry",
    "罗恩": "ron",
    "赫敏": "hermione",
    "伏地魔": "voldemort",
    "城堡": "castle",
    "骑士": "knight",
    "星球大战": "star wars",
    "星战": "star wars",
    "忍者系列": "ninjago",
    "忍者": "ninjago",
    "绿巨人": "hulk",
    "美国队长": "captain america",
    "雷神": "thor",
    "超人": "superman",
    "卢克": "luke",
    "天行者": "skywalker",
    "皇帝": "emperor",
    "尤达": "yoda",
    "欧比旺": "obi-wan",
    "黄色": "yellow",
    "红色": "red",
    "蓝色": "blue",
    "黑色": "black",
    "白色": "white",
    "绿色": "green",
    "金色": "gold",
    "银色": "silver",
    
    # Weapons & Parts Chinese mappings
    "双筒望远镜": "binoculars",
    "望远镜": "binoculars",
    "对讲机": "radio",
    "手提箱": "suitcase",
    "蜘蛛网": "web",
    "爆能枪": "blaster",
    "双刃剑": "sword",
    "手头盔": "helmet",
    "头发": "hair",
    "发型": "hair",
    "胡子": "beard",
    "护甲": "armor",
    "肩甲": "armor",
    "手套": "glove",
    "弓箭": "bow",
    "战戟": "halberd",
    "水晶": "crystal",
    "金币": "coin",
    "硬币": "coin",
    "手铐": "handcuffs",
    "相机": "camera",
    "光剑": "lightsaber",
    "手枪": "pistol",
    "步枪": "rifle",
    "大剑": "sword",
    "宝剑": "sword",
    "盾牌": "shield",
    "长矛": "spear",
    "战斧": "axe",
    "斧子": "axe",
    "面罩": "mask",
    "面具": "mask",
    "披风": "cape",
    "斗篷": "cape",
    "翅膀": "wing",
    "帽子": "hat",
    "手杖": "staff",
    "魔杖": "wand",
    "权杖": "staff",
    "火焰": "fire",
    "钥匙": "key",
    "枪": "blaster",
    "剑": "sword",
    "盾": "shield",
    "矛": "spear",
    "斧": "axe",
    "弓": "bow",
    "书": "book"
}

EN_TO_ZH_MAP = {
    "darth vader": "达斯·维达 (黑武士)",
    "stormtrooper": "风暴兵 (白兵)",
    "clone trooper": "克隆人士兵",
    "astronaut": "经典太空宇航员",
    "spaceman": "经典太空人",
    "iron man": "钢铁侠",
    "tony stark": "托尼·斯塔克",
    "spider-man": "蜘蛛侠",
    "batman": "蝙蝠侠",
    "harry potter": "哈利·波特",
    "captain america": "美国队长",
    "thor": "雷神托尔",
    "yoda": "尤达大师",
    "obi-wan kenobi": "欧比旺·肯诺比",
    "emperor palpatine": "帕尔帕廷皇帝",
    "boba fett": "波巴·费特",
    "princess leia": "莱娅公主",
    "han solo": "韩·索罗",
    "anakin skywalker": "阿纳金·天行者",
    "luke skywalker": "卢克·天行者",
    "superman": "超人",
    "hulk": "绿巨人",
    "black widow": "黑寡妇",
    "hawkeye": "鹰眼",
    "pirate": "海盗",
    "knight": "骑士",
    "ninja": "忍者",
    "skeleton": "骷髅兵",
    "clown": "小丑",
    "policeman": "警察",
    "fireman": "消防员",
    "doctor": "医生",
    "farmer": "农夫",
    "chef": "厨师",
    "classic": "经典",
    "yellow": "黄色",
    "red": "红色",
    "blue": "蓝色",
    "black": "黑色",
    "white": "白色",
    "green": "绿色",
    "gold": "金色",
    "silver": "银色",
    
    # Weapons & Parts English to Chinese translations
    "lightsaber": "光剑",
    "blaster": "爆能枪",
    "sword": "宝剑",
    "shield": "盾牌",
    "spear": "长矛",
    "axe": "战斧",
    "cape": "披风",
    "mask": "面罩/面具",
    "helmet": "头盔",
    "wing": "翅膀",
    "wand": "魔杖",
    "staff": "手杖/权杖",
    "bow": "弓箭",
    "armor": "战甲/护甲",
    "hair": "发饰饰品",
    "torso": "躯干身体",
    "legs": "腿部关节",
    "death star": "死星",
    "imperial shuttle": "帝国穿梭机",
    "galaxy explorer": "银河探索号飞船",
    "mobile lab": "太空移动实验室",
    "hall of armor": "机甲陈列室",
    "endgame": "终局之战"
}

MINIFIG_ID_MAP = {
    "fig-016875": "sw1483", # Gingerbread Darth Vader
    "fig-000516": "sw0527", # Darth Vader with Scarred Cheek
    "fig-000581": "sw0218", # Chrome Black Darth Vader
    "fig-001106": "sw0599", # Santa Darth Vader
    "fig-001783": "sw0816", # Darth Vader - Light Nougat Head
    "fig-003660": "sw0117", # Light-Up Lightsaber Darth Vader
    "fig-011203": "sw1060", # Darth Vader with Medal
    "fig-010547": "sw1121", # Festive Red Sweater Darth Vader
    "fig-013054": "sw1224", # Sunset Vest Darth Vader
    "fig-014190": "sw1304", # Darth Vader - Two-Piece Helmet
    "fig-011126": "sw1117", # Darth Vader - Plain Arms
    "fig-010304": "sw1095"  # Darth Vader - Printed Arms
}

REVERSE_MINIFIG_MAP = {v: k for k, v in MINIFIG_ID_MAP.items()}

def resolve_minifig_id(m_id):
    if not m_id:
        return m_id
    m_id_lower = m_id.lower().strip()
    return REVERSE_MINIFIG_MAP.get(m_id_lower, m_id)

def translate_query(q):
    q_lower = q.lower()
    for zh, en in TRANSLATION_MAP.items():
        if zh in q_lower:
            q_lower = q_lower.replace(zh, en)
    return q_lower

# Pre-sort translation keys by length descending to match longest phrases first
SORTED_TRANSLATION_KEYS = sorted(EN_TO_ZH_MAP.keys(), key=len, reverse=True)

def translate_to_zh(name_en):
    import re
    if not name_en:
        return ""
    translated = name_en
    replaced = False
    for key in SORTED_TRANSLATION_KEYS:
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, translated, re.IGNORECASE):
            translated = re.sub(pattern, EN_TO_ZH_MAP[key], translated, flags=re.IGNORECASE)
            replaced = True
    if replaced:
        if translated.lower() == name_en.lower():
            return name_en
        return translated
    return name_en

def fuzzy_match_minifig(conn, name_en):
    import re
    # Normalize name
    name_clean = name_en.lower().replace("-", " ").replace(",", " ")
    words = [w.strip() for w in re.split(r'\s+', name_clean) if w.strip()]
    
    # Extract core name: split only by ' - ' (hyphen with spaces) or ','
    core_parts = re.split(r'\s+[-–]\s+|,', name_en)
    core_name = core_parts[0].strip().lower()
    
    # Remove parentheses and their contents from core name, e.g. "Luke Skywalker (Tatooine)" -> "Luke Skywalker"
    core_name = re.sub(r'\(.*?\)', '', core_name).strip()
    
    core_words = [w for w in re.split(r'\s+', core_name) if w]
    if len(core_words) > 3:
        core_query = " ".join(core_words[:2])
    else:
        core_query = core_name
        
    if not core_query:
        return None, 0
        
    stop_words = {
        'with', 'and', 'the', 'of', 'for', 'in', 'on', 'at', 'by', 'from',
        'a', 'an', 'to', 'with', 'without', 'or', 'but', 'is', 'are', 'was',
        'were', 'be', 'been', 'has', 'have', 'had', 'do', 'does', 'did',
        'traditional', 'starched', 'fabric', 'robe', 'hem', 'skin', 'head',
        'body', 'legs', 'torso', 'hair', 'helmet', 'cape', 'type', 'version'
    }
    
    descriptors = [w for w in words if w not in stop_words and len(w) > 2]
    
    cursor = conn.cursor()
    sql = "SELECT minifig_num, name, num_parts FROM minifigs WHERE 1=1"
    params = []
    
    for cw in core_words[:2]:
        # Replace non-alphanumeric with '%' for SQL wildcard match (e.g. spider-man -> spider%man)
        cleaned_cw = re.sub(r'[^a-zA-Z0-9]', '%', cw)
        cleaned_cw = re.sub(r'%+', '%', cleaned_cw)
        if len(cleaned_cw.replace('%', '')) > 1:
            sql += " AND name LIKE ?"
            params.append(f"%{cleaned_cw}%")
            
    if not params:
        sql += " AND name LIKE ?"
        params.append(f"%{core_query}%")
        
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    
    best_match = None
    best_score = -1
    
    for row in rows:
        cand_name = row["name"].lower()
        score = 0
        for desc in descriptors:
            # strip special characters from desc
            desc_clean = re.sub(r'[^a-zA-Z0-9]', '', desc)
            if not desc_clean:
                continue
            if desc_clean in cand_name.replace("-", "").replace(" ", ""):
                score += 1
                
        # Slight boost if core query matches closely
        cand_clean = cand_name.replace("-", "").replace(" ", "")
        core_clean = core_query.replace("-", "").replace(" ", "")
        if core_clean in cand_clean:
            score += 0.5
            
        if score > best_score:
            best_score = score
            best_match = row
            
    return best_match, best_score

class LegoAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def end_headers(self):
        # Add Cache-Control headers for static files to optimize page speed
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        if path.startswith("/api/"):
            self.send_header("Cache-Control", "public, max-age=300, stale-while-revalidate=600")
        elif path.endswith((".js", ".css")):
            self.send_header("Cache-Control", "public, max-age=3600")
        elif path.endswith((".png", ".jpg", ".jpeg", ".svg", ".ico", ".woff", ".woff2", ".webp")):
            self.send_header("Cache-Control", "public, max-age=604800")
        elif path.endswith((".html", "/")) or not "." in path:
            self.send_header("Cache-Control", "no-cache") # check for updates on HTML/entrypoints
        super().end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if path.startswith("/api/"):
            cache_key = parsed_url.path + "?" + parsed_url.query
            cached_payload = get_cached_api_response(cache_key)
            if cached_payload is not None:
                self.send_json_response(cached_payload)
                return
            self.handle_api(path, query_params, cache_key)
        else:
            super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        if path.startswith("/api/"):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8')) if post_data else {}
            except Exception:
                self.send_json_response({"error": "Invalid JSON"}, status=400)
                return
            
            self.handle_api_post(path, body)
        else:
            self.send_json_response({"error": "POST not supported for static files"}, status=405)

    def handle_api_post(self, path, body):
        if not os.path.exists(DB_PATH):
            self.send_json_response({"error": "Database not found. Please run db_builder.py first."}, status=500)
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            
            if path == "/api/register":
                username = body.get("username", "").strip()
                password = body.get("password", "").strip()
                if not username or not password:
                    self.send_json_response({"error": "用户名和密码不能为空！"}, status=400)
                    conn.close()
                    return
                
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    self.send_json_response({"error": "用户名已存在！"}, status=400)
                else:
                    pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                    cursor.execute("INSERT INTO users (username, password, preferences) VALUES (?, ?, ?)", 
                                   (username, pwd_hash, '{}'))
                    conn.commit()
                    self.send_json_response({"success": True, "message": "注册成功！"})
                    
            elif path == "/api/login":
                username = body.get("username", "").strip()
                password = body.get("password", "").strip()
                if not username or not password:
                    self.send_json_response({"error": "用户名和密码不能为空！"}, status=400)
                    conn.close()
                    return
                
                pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                cursor = conn.cursor()
                cursor.execute("SELECT preferences FROM users WHERE username = ? AND password = ?", (username, pwd_hash))
                user = cursor.fetchone()
                if not user:
                    self.send_json_response({"error": "用户名或密码错误！"}, status=400)
                else:
                    prefs = {}
                    try:
                        prefs = json.loads(user["preferences"]) if user["preferences"] else {}
                    except Exception:
                        pass
                    self.send_json_response({"success": True, "username": username, "preferences": prefs})
                    
            elif path == "/api/save-preferences":
                username = body.get("username", "").strip()
                preferences = body.get("preferences", {})
                if not username:
                    self.send_json_response({"error": "未指定用户名！"}, status=400)
                    conn.close()
                    return
                
                cursor = conn.cursor()
                prefs_str = json.dumps(preferences, ensure_ascii=False)
                cursor.execute("UPDATE users SET preferences = ? WHERE username = ?", (prefs_str, username))
                conn.commit()
                self.send_json_response({"success": True})
                
            elif path == "/api/scan-image":
                payload = self.api_scan_image(conn, body)
                if payload is not None:
                    self.send_json_response(payload)
                
            else:
                self.send_json_response({"error": "Endpoint not found"}, status=404)
                
            conn.close()
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def handle_api(self, path, params, cache_key=None):
        if not os.path.exists(DB_PATH):
            self.send_json_response({"error": "Database not found. Please run db_builder.py first."}, status=500)
            return

        try:
            conn = open_db()
            
            if path == "/api/search":
                payload = self.api_search(conn, params)
            elif path == "/api/gallery":
                payload = self.api_gallery(conn, params)
            elif path == "/api/scan":
                payload = self.api_scan(conn, params)
            elif path == "/api/minifig":
                payload = self.api_minifig_details(conn, params)
            elif path == "/api/shared-part":
                payload = self.api_shared_part(conn, params)
            else:
                self.send_json_response({"error": "Endpoint not found"}, status=404)
                conn.close()
                return
                
            if payload is None:
                conn.close()
                return
            if cache_key:
                set_cached_api_response(cache_key, payload)
            self.send_json_response(payload)
                
            conn.close()
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def api_gallery(self, conn, params):
        page = max(1, int(params.get("page", ["1"])[0]))
        limit = min(48, max(1, int(params.get("limit", ["24"])[0])))
        theme = params.get("theme", [""])[0].strip()
        sort = params.get("sort", ["num_parts_desc"])[0].strip()
        
        offset = (page - 1) * limit
        cursor = conn.cursor()
        
        sql_select = f"""
            SELECT m.minifig_num, m.name, m.num_parts
            FROM minifigs m
            WHERE m.num_parts BETWEEN 3 AND 12
              {MINIFIG_EXCLUSION_SQL}
              AND EXISTS (
                  SELECT 1
                  FROM inventories i
                  JOIN inventory_parts ip ON i.id = ip.inventory_id
                  JOIN parts p ON ip.part_num = p.part_num
                  WHERE i.set_num = m.minifig_num
                    AND p.part_cat_id IN (60, 61, 13)
                  LIMIT 1
              )
        """
        
        args = []
        if theme:
            translated_theme = translate_query(theme).lower()
            sql_select += " AND (LOWER(m.name) LIKE ? OR LOWER(m.minifig_num) LIKE ?)"
            args.extend([f"%{translated_theme}%", f"%{translated_theme}%"])
            
        order_by = {
            "num_parts_desc": "m.num_parts DESC",
            "num_parts_asc": "m.num_parts ASC",
            "minifig_num_asc": "m.minifig_num ASC",
        }.get(sort, "m.num_parts DESC")
        sql_select += f" ORDER BY {order_by} LIMIT ? OFFSET ?"
        args.extend([limit, offset])
        
        cursor.execute(sql_select, args)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            row_dict = dict(row)
            row_dict["name"] = translate_to_zh(row_dict["name"])
            
            sql_theme = """
                SELECT t.name 
                FROM inventory_minifigs im
                JOIN inventories i ON im.inventory_id = i.id
                JOIN sets s ON i.set_num = s.set_num
                JOIN themes t ON s.theme_id = t.id
                WHERE im.minifig_num = ?
                LIMIT 1
            """
            cursor.execute(sql_theme, (row_dict["minifig_num"],))
            theme_row = cursor.fetchone()
            row_dict["theme_name"] = translate_to_zh(theme_row["name"]) if theme_row else "收藏系列"
            row_dict["official_id"] = MINIFIG_ID_MAP.get(row_dict["minifig_num"], row_dict["minifig_num"])
            results.append(row_dict)
            
        return results

    def api_search(self, conn, params):
        query = params.get("q", [""])[0].strip()
        if not query:
            return []

        mapped_id = resolve_minifig_id(query)
        cursor = conn.cursor()

        if mapped_id != query:
            cursor.execute("SELECT minifig_num, name, num_parts FROM minifigs WHERE minifig_num = ?", (mapped_id,))
            rows = cursor.fetchall()
            results = []
            for row in rows:
                row_dict = dict(row)
                row_dict["name"] = translate_to_zh(row_dict["name"])
                row_dict["official_id"] = MINIFIG_ID_MAP.get(row_dict["minifig_num"], row_dict["minifig_num"])
                results.append(row_dict)
            return results

        translated_query = translate_query(query)
        like_query = f"%{translated_query}%"
        
        # Step 1: Find parts matching the query (limit to 200 parts to prevent parameter list overflow)
        cursor.execute("SELECT part_num FROM parts WHERE name LIKE ? OR part_num LIKE ? LIMIT 200", (like_query, like_query))
        parts = [r[0] for r in cursor.fetchall()]
        
        sets = []
        if parts:
            placeholders = ",".join(["?"] * len(parts))
            cursor.execute(f"""
                SELECT DISTINCT i.set_num
                FROM inventories i
                JOIN inventory_parts ip ON i.id = ip.inventory_id
                WHERE ip.part_num IN ({placeholders}) AND i.set_num LIKE 'fig-%'
                LIMIT 500
            """, parts)
            sets = [r[0] for r in cursor.fetchall()]
            
        # Step 2: Query minifigs matching either minifig attributes or containing matching parts
        args = [like_query, like_query]
        set_clause = ""
        if sets:
            placeholders_set = ",".join(["?"] * len(sets))
            set_clause = f"OR m.minifig_num IN ({placeholders_set})"
            args.extend(sets)
            
        sql = f"""
            SELECT m.minifig_num, m.name, m.num_parts 
            FROM minifigs m
            WHERE (m.minifig_num LIKE ? OR m.name LIKE ? {set_clause}) 
              AND m.num_parts BETWEEN 3 AND 12
              {MINIFIG_EXCLUSION_SQL}
              AND EXISTS (
                  SELECT 1
                  FROM inventories i
                  JOIN inventory_parts ip ON i.id = ip.inventory_id
                  JOIN parts p ON ip.part_num = p.part_num
                  WHERE i.set_num = m.minifig_num
                    AND p.part_cat_id IN (60, 61, 13)
                  LIMIT 1
              )
            ORDER BY m.num_parts DESC 
            LIMIT 15
        """
        cursor.execute(sql, args)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            row_dict = dict(row)
            row_dict["name"] = translate_to_zh(row_dict["name"])
            row_dict["official_id"] = MINIFIG_ID_MAP.get(row_dict["minifig_num"], row_dict["minifig_num"])
            results.append(row_dict)
            
        return results
            
    def api_scan(self, conn, params):
        target_color = params.get("color", ["ffffff"])[0].strip().lower()
        query = params.get("query", [""])[0].strip().lower()
        
        rows = self.get_scan_candidate_rows(conn)
        
        # Group by minifigure
        minifigs = {}
        for row in rows:
            num = row["minifig_num"]
            if num not in minifigs:
                minifigs[num] = {
                    "minifig_num": num,
                    "name": row["minifig_name"], # Keep original English name for matching
                    "num_parts": row["num_parts"],
                    "colors": [],
                    "img_url": f"https://cdn.rebrickable.com/media/sets/{num}.jpg"
                }
            rgb = row["rgb"]
            if rgb:
                minifigs[num]["colors"].append(rgb.lower())
                
        # Parse target RGB
        try:
            tr = int(target_color[0:2], 16)
            tg = int(target_color[2:4], 16)
            tb = int(target_color[4:6], 16)
        except:
            tr, tg, tb = 255, 255, 255
            
        matches = []
        for num, fig in minifigs.items():
            name_lower = fig["name"].lower()
            num_lower = fig["minifig_num"].lower()
            
            # Query keyword matching score
            query_score = 0
            official_id = MINIFIG_ID_MAP.get(num_lower, num_lower)
            if query and (query in name_lower or query in num_lower or query in official_id):
                query_score = 1000000  # huge boost
                
            # Color matching score
            min_color_dist = 3 * (255**2)
            for color_hex in fig["colors"]:
                try:
                    cr = int(color_hex[0:2], 16)
                    cg = int(color_hex[2:4], 16)
                    cb = int(color_hex[4:6], 16)
                    dist = (tr - cr)**2 + (tg - cg)**2 + (tb - cb)**2
                    if dist < min_color_dist:
                        min_color_dist = dist
                except:
                    continue
                    
            # Total distance metric (smaller is better)
            total_dist = min_color_dist - query_score
            matches.append((total_dist, fig))
            
        # Sort by distance
        matches.sort(key=lambda x: x[0])
        
        # Take top 3 and translate their names
        top_matches = []
        for m in matches[:3]:
            fig = m[1]
            fig["name"] = translate_to_zh(fig["name"])
            fig["official_id"] = MINIFIG_ID_MAP.get(fig["minifig_num"], fig["minifig_num"])
            top_matches.append(fig)
        return top_matches

    def get_scan_candidate_rows(self, conn):
        now = time.time()
        cached_rows = SCAN_CANDIDATE_CACHE["rows"]
        if cached_rows is not None and now - SCAN_CANDIDATE_CACHE["loaded_at"] < SCAN_CANDIDATE_CACHE_TTL_SECONDS:
            return cached_rows

        cursor = conn.cursor()
        sql = f"""
            SELECT m.minifig_num, m.name AS minifig_name, m.num_parts, c.rgb
            FROM minifigs m
            JOIN inventories i ON m.minifig_num = i.set_num
            JOIN inventory_parts ip ON i.id = ip.inventory_id
            JOIN colors c ON ip.color_id = c.id
            WHERE m.num_parts BETWEEN 3 AND 12
              AND m.minifig_num LIKE 'fig-%'
              {MINIFIG_EXCLUSION_SQL}
        """
        cursor.execute(sql)
        rows = [dict(row) for row in cursor.fetchall()]
        SCAN_CANDIDATE_CACHE["rows"] = rows
        SCAN_CANDIDATE_CACHE["loaded_at"] = now
        return rows

    def api_scan_image(self, conn, body):
        import urllib.request
        import urllib.error
        import base64
        import uuid
        import io
        from PIL import Image
        
        base64_image = body.get("image", "").strip()
        target_color = body.get("color", "ffffff").strip().lower()
        api_key = body.get("api_key", "").strip()
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            
        if not base64_image:
            self.send_json_response({
                "error": "INVALID_IMAGE",
                "message": "无有效的图像数据。"
            }, status=400)
            return

        # Extract mime type and raw base64 data
        mime_type = "image/jpeg"
        image_data = base64_image
        if "," in base64_image:
            header, image_data = base64_image.split(",", 1)
            if "image/png" in header:
                mime_type = "image/png"
            elif "image/webp" in header:
                mime_type = "image/webp"
            elif "image/gif" in header:
                mime_type = "image/gif"

        # Helper function to call Brickognize Predict API
        def call_brickognize(img_b64, m_type):
            try:
                raw_bytes = base64.b64decode(img_b64)
                bound = f"Boundary-{uuid.uuid4().hex}"
                body_parts = [
                    f"--{bound}".encode('utf-8'),
                    f'Content-Disposition: form-data; name="query_image"; filename="image.jpg"'.encode('utf-8'),
                    f'Content-Type: {m_type}'.encode('utf-8'),
                    b'',
                    raw_bytes,
                    f"--{bound}--".encode('utf-8'),
                    b''
                ]
                req_bytes = b'\r\n'.join(body_parts)
                req = urllib.request.Request(
                    "https://api.brickognize.com/predict/",
                    data=req_bytes,
                    headers={
                        'Content-Type': f'multipart/form-data; boundary={bound}',
                        'Accept': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    },
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    res = json.loads(response.read().decode('utf-8'))
                return res.get("items", [])
            except Exception as ex:
                print(f"Brickognize API call failed: {ex}")
                return []

        # Helper to lookup candidates in database
        def lookup_candidates(brick_items):
            matched_figs = []
            cursor = conn.cursor()
            for item in brick_items:
                itype = str(item.get("type", "")).strip().lower()
                
                # Option A: Direct minifigure match
                if itype in ("fig", "minifig") or item.get("id", "").startswith("fig-"):
                    candidates = {item.get("id", "").strip().lower()}
                    for ext in item.get("external_sites", []):
                        url = ext.get("url", "")
                        if "bricklink.com/" in url and ("?M=" in url or "&M=" in url or "?m=" in url or "&m=" in url):
                            import re
                            match = re.search(r'[?&][Mm]=([^&#]+)', url)
                            if match:
                                candidates.add(match.group(1).strip().lower())
                        if "rebrickable.com/minifigs/" in url:
                            parts = url.split("minifigs/")
                            if len(parts) > 1:
                                sub = parts[1].split("/")[0]
                                if sub:
                                    candidates.add(sub.strip().lower())
                                    
                    found_direct = False
                    for cand in candidates:
                        if not cand:
                            continue
                        resolved_cand = resolve_minifig_id(cand)
                        cursor.execute("SELECT minifig_num, name, num_parts FROM minifigs WHERE LOWER(minifig_num) = ?", (resolved_cand,))
                        row = cursor.fetchone()
                        if row:
                            matched_figs.append({
                                "minifig_num": row["minifig_num"],
                                "name": row["name"],
                                "num_parts": row["num_parts"],
                                "img_url": f"https://cdn.rebrickable.com/media/sets/{row['minifig_num']}.jpg",
                                "score": item.get("score", 0.9),
                                "official_id": MINIFIG_ID_MAP.get(row["minifig_num"], row["minifig_num"])
                            })
                            found_direct = True
                            
                    if not found_direct and item.get("name"):
                        matched_row, match_score = fuzzy_match_minifig(conn, item["name"])
                        if matched_row and match_score >= 0.5:
                            matched_figs.append({
                                "minifig_num": matched_row["minifig_num"],
                                "name": matched_row["name"],
                                "num_parts": matched_row["num_parts"],
                                "img_url": f"https://cdn.rebrickable.com/media/sets/{matched_row['minifig_num']}.jpg",
                                "score": item.get("score", 0.9) * 0.9,
                                "official_id": MINIFIG_ID_MAP.get(matched_row["minifig_num"], matched_row["minifig_num"])
                            })
                
                # Option B: Partial part match (torso, head, accessories)
                else:
                    part_candidates = {item.get("id", "").strip().lower()}
                    for ext in item.get("external_sites", []):
                        url = ext.get("url", "")
                        if "bricklink.com/" in url and ("?P=" in url or "&P=" in url or "?p=" in url or "&p=" in url):
                            import re
                            match = re.search(r'[?&][Pp]=([^&#]+)', url)
                            if match:
                                part_candidates.add(match.group(1).strip().lower())
                        if "rebrickable.com/parts/" in url:
                            parts = url.split("parts/")
                            if len(parts) > 1:
                                sub = parts[1].split("/")[0]
                                if sub:
                                    part_candidates.add(sub.strip().lower())
                                    
                    for pcand in part_candidates:
                        if not pcand:
                            continue
                        pcand_clean = pcand.replace("part-", "")
                        sql_figs_by_part = """
                            SELECT DISTINCT m.minifig_num, m.name, m.num_parts
                            FROM inventory_parts ip
                            JOIN inventories i ON ip.inventory_id = i.id
                            JOIN minifigs m ON i.set_num = m.minifig_num
                            WHERE (LOWER(ip.part_num) = ? OR LOWER(ip.part_num) = ?)
                              AND m.num_parts BETWEEN 3 AND 12
                              AND LOWER(m.name) NOT LIKE '%keychain%'
                              AND LOWER(m.name) NOT LIKE '%key chain%'
                              AND LOWER(m.name) NOT LIKE '%magnet%'
                              AND LOWER(m.name) NOT LIKE '%watch%'
                              AND LOWER(m.name) NOT LIKE '%clock%'
                              AND LOWER(m.name) NOT LIKE '%book%'
                              AND LOWER(m.name) NOT LIKE '%sticker%'
                              AND LOWER(m.name) NOT LIKE '%card%'
                              AND LOWER(m.name) NOT LIKE '%giant%'
                              AND LOWER(m.name) NOT LIKE '%maxifigure%'
                              AND LOWER(m.name) NOT LIKE '%brick-built%'
                              AND LOWER(m.name) NOT LIKE '%pen%'
                              AND LOWER(m.name) NOT LIKE '%torch%'
                              AND LOWER(m.name) NOT LIKE '%light%'
                              AND LOWER(m.name) NOT LIKE '%plush%'
                              AND LOWER(m.name) NOT LIKE '%notebook%'
                              AND LOWER(m.name) NOT LIKE '%tag%'
                              AND LOWER(m.name) NOT LIKE '%bag%'
                              AND LOWER(m.name) NOT LIKE '%frame%'
                              AND LOWER(m.name) NOT LIKE '%display%'
                              AND LOWER(m.name) NOT LIKE '%scale%'
                            LIMIT 12
                        """
                        cursor.execute(sql_figs_by_part, (pcand, pcand_clean))
                        rows = cursor.fetchall()
                        for row in rows:
                            matched_figs.append({
                                "minifig_num": row["minifig_num"],
                                "name": row["name"],
                                "num_parts": row["num_parts"],
                                "img_url": f"https://cdn.rebrickable.com/media/sets/{row['minifig_num']}.jpg",
                                "score": item.get("score", 0.8) * 0.8,
                                "official_id": MINIFIG_ID_MAP.get(row["minifig_num"], row["minifig_num"])
                            })
            
            # Deduplicate final list of matches
            unique_figs = []
            seen = set()
            for fig in matched_figs:
                if fig["minifig_num"] not in seen:
                    seen.add(fig["minifig_num"])
                    unique_figs.append(fig)
            return unique_figs

        # STEP 1: Attempt standard Brickognize scanning on original image
        brick_items = call_brickognize(image_data, mime_type)
        first_round_matches = lookup_candidates(brick_items)
        
        has_high_confidence = False
        if first_round_matches:
            first_round_matches.sort(key=lambda x: x.get("score", 0), reverse=True)
            if first_round_matches[0].get("score", 0) >= 0.85:
                has_high_confidence = True

        # STEP 2: If low confidence or no matches, use Gemini to detect bounding box, crop & retry!
        cropped_image_data = None
        gemini_box = None
        gemini_keywords = []
        ai_desc = ""

        if not has_high_confidence and api_key:
            print("Confidence is low or no matches found. Initiating Gemini crop & retry sequence...")
            # We call Gemini to find the bounding box
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            prompt = (
                "Analyze the Lego minifigure (or Lego part) in this image. We need to crop it to improve matching.\n"
                "1. Detect the bounding box of the main LEGO minifigure (or prominent LEGO part/piece). Return coordinates as [ymin, xmin, ymax, xmax] normalized on a 0-1000 scale.\n"
                "2. Provide 3-6 English keywords describing its visual attributes (e.g. torso prints, helmet color, legs).\n"
                "3. Provide a brief description of the minifigure in Chinese (within 60 characters) describing who/what it is.\n"
                "Return STRICTLY JSON format:\n"
                "{\n"
                "  \"box\": [ymin, xmin, ymax, xmax],\n"
                "  \"keywords\": [\"keyword1\", \"keyword2\", ...],\n"
                "  \"description\": \"Chinese description\"\n"
                "}"
            )
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inlineData": {"mimeType": mime_type, "data": image_data}}
                    ]
                }],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            try:
                req = urllib.request.Request(
                    gemini_url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=15) as response:
                    res_body = json.loads(response.read().decode('utf-8'))
                
                text_resp = res_body["candidates"][0]["content"]["parts"][0]["text"].strip()
                if text_resp.startswith("```json"):
                    text_resp = text_resp[7:]
                if text_resp.endswith("```"):
                    text_resp = text_resp[:-3]
                text_resp = text_resp.strip()
                
                ai_data = json.loads(text_resp)
                gemini_box = ai_data.get("box")
                gemini_keywords = ai_data.get("keywords", [])
                ai_desc = ai_data.get("description", "")
                
                if gemini_box and len(gemini_box) == 4:
                    # Perform image crop using Pillow
                    try:
                        raw_bytes = base64.b64decode(image_data)
                        img = Image.open(io.BytesIO(raw_bytes))
                        width, height = img.size
                        ymin, xmin, ymax, xmax = gemini_box
                        
                        # Convert to absolute pixels
                        left = int(xmin * width / 1000.0)
                        top = int(ymin * height / 1000.0)
                        right = int(xmax * width / 1000.0)
                        bottom = int(ymax * height / 1000.0)
                        
                        # Apply 15% padding
                        w_pad = int((right - left) * 0.15)
                        h_pad = int((bottom - top) * 0.15)
                        
                        left = max(0, left - w_pad)
                        top = max(0, top - h_pad)
                        right = min(width, right + w_pad)
                        bottom = min(height, bottom + h_pad)
                        
                        if right > left and bottom > top:
                            cropped_img = img.crop((left, top, right, bottom))
                            # Resize 1.5x for higher detail matching resolution
                            cropped_img = cropped_img.resize(
                                (int((right - left) * 1.5), int((bottom - top) * 1.5)), 
                                Image.Resampling.LANCZOS
                            )
                            buffered = io.BytesIO()
                            cropped_img.save(buffered, format="JPEG", quality=85)
                            cropped_image_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
                            print("Successfully cropped and zoomed image using Gemini coordinates.")
                    except Exception as crop_err:
                        print(f"PIL Image cropping failed: {crop_err}")
            except Exception as gemini_err:
                print(f"Gemini coordinate extraction failed: {gemini_err}")

        # STEP 3: If we have a cropped image, perform a second-round Brickognize match
        second_round_matches = []
        if cropped_image_data:
            brick_items_retry = call_brickognize(cropped_image_data, "image/jpeg")
            second_round_matches = lookup_candidates(brick_items_retry)
            if second_round_matches:
                print(f"Second-round match succeeded! Found {len(second_round_matches)} candidate figures.")

        # Combine results from both rounds
        all_matches = []
        seen = set()
        
        # Prioritize second-round cropped matches, as they are cleaner
        for fig in (second_round_matches + first_round_matches):
            if fig["minifig_num"] not in seen:
                seen.add(fig["minifig_num"])
                all_matches.append(fig)

        # STEP 4: Call Gemini for final visual confirmation and Chinese report if we have matches but no AI description
        if all_matches and api_key and not ai_desc:
            try:
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                best_match_name = all_matches[0]["name"]
                prompt = (
                    f"We matched this LEGO image with candidate character: '{best_match_name}'.\n"
                    "Provide a brief description of the minifigure in Chinese (within 60 characters) describing who it is and its key visual features.\n"
                    "Return STRICTLY JSON format:\n"
                    "{\n"
                    "  \"description\": \"Chinese description\"\n"
                    "}"
                )
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {"inlineData": {"mimeType": mime_type, "data": image_data}}
                        ]
                    }],
                    "generationConfig": {"responseMimeType": "application/json"}
                }
                req = urllib.request.Request(
                    gemini_url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    res_body = json.loads(response.read().decode('utf-8'))
                
                text_resp = res_body["candidates"][0]["content"]["parts"][0]["text"].strip()
                if text_resp.startswith("```json"):
                    text_resp = text_resp[7:]
                if text_resp.endswith("```"):
                    text_resp = text_resp[:-3]
                text_resp = text_resp.strip()
                
                ai_desc = json.loads(text_resp).get("description", "")
            except Exception as desc_err:
                print(f"Gemini confirmation report failed: {desc_err}")

        # Translate names for top matches
        top_matches = all_matches[:3]
        for fig in top_matches:
            fig["name"] = translate_to_zh(fig["name"])

        # If any matches are found, return them!
        if top_matches:
            if not ai_desc:
                ai_desc = f"已通过双通道智能影像识别，匹配置信度 {(top_matches[0].get('score', 0.9)*100):.1f}%"
                if second_round_matches:
                    ai_desc += "（触发 Gemini 精细裁切识别）"
            self.send_json_response({
                "description": ai_desc,
                "results": top_matches
            })
            return

        # STEP 5: Graceful Fallback if still no matches found
        print("Dual-pipeline returned no matches in database. Falling back to traditional color distance match...")
        params = {"color": [target_color], "query": [""]}
        color_matches = self.api_scan(conn, params)
        
        # Extract keywords to construct an AI-fallback description if keywords exist
        if gemini_keywords:
            fallback_desc = f"⚠️ 图像未能精准匹配，为您推荐与视觉特征 {' '.join(gemini_keywords[:3])} 及主色相近的经典人仔。"
        else:
            fallback_desc = "⚠️ 图像未能精准匹配，已为您推荐主颜色最相近的经典乐高人仔。"

        self.send_json_response({
            "description": fallback_desc,
            "results": color_matches
        })

    def api_minifig_details(self, conn, params):
        minifig_id = params.get("id", [""])[0].strip()
        if not minifig_id:
            self.send_json_response({"error": "Missing 'id' parameter"}, status=400)
            return None

        cursor = conn.cursor()
        
        minifig_id = resolve_minifig_id(minifig_id)
        norm_id = minifig_id.lower()
        norm_id_suffix = f"{norm_id}-1" if "-" not in norm_id else norm_id

        sql_minifig = """
            SELECT minifig_num, name, num_parts 
            FROM minifigs 
            WHERE minifig_num = ? OR minifig_num = ?
        """
        cursor.execute(sql_minifig, (norm_id, norm_id_suffix))
        minifig_row = cursor.fetchone()
        
        if not minifig_row:
            self.send_json_response({"error": "Minifigure not found"}, status=404)
            return None
            
        minifig_data = dict(minifig_row)
        minifig_data["name"] = translate_to_zh(minifig_data["name"])
        minifig_num = minifig_data["minifig_num"]
        minifig_data["official_id"] = MINIFIG_ID_MAP.get(minifig_num, minifig_num)

        # Get parts list
        cursor.execute("SELECT id FROM inventories WHERE set_num = ?", (minifig_num,))
        inventory_row = cursor.fetchone()
        
        parts_list = []
        if inventory_row:
            inv_id = inventory_row["id"]
            
            sql_parts = """
                SELECT ip.part_num, ip.color_id, ip.quantity, p.name AS part_name, 
                       c.name AS color_name, c.rgb AS color_rgb, ip.img_url, p.part_cat_id,
                       (SELECT element_id FROM elements WHERE part_num = ip.part_num AND color_id = ip.color_id LIMIT 1) AS element_id
                FROM inventory_parts ip
                JOIN parts p ON ip.part_num = p.part_num
                JOIN colors c ON ip.color_id = c.id
                WHERE ip.inventory_id = ?
            """
            cursor.execute(sql_parts, (inv_id,))
            for row in cursor.fetchall():
                row_dict = dict(row)
                row_dict["part_name"] = translate_to_zh(row_dict["part_name"])
                row_dict["color_name"] = translate_to_zh(row_dict["color_name"])
                parts_list.append(row_dict)

        # Get Sets containing minifig
        sql_sets = """
            SELECT s.set_num, s.name AS set_name, s.year, s.theme_id, s.num_parts, s.img_url, t.name AS theme_name
            FROM inventory_minifigs im
            JOIN inventories i ON im.inventory_id = i.id
            JOIN sets s ON i.set_num = s.set_num
            JOIN themes t ON s.theme_id = t.id
            WHERE im.minifig_num = ?
        """
        cursor.execute(sql_sets, (minifig_num,))
        sets_list = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            row_dict["set_name"] = translate_to_zh(row_dict["set_name"])
            row_dict["theme_name"] = translate_to_zh(row_dict["theme_name"])
            sets_list.append(row_dict)

        # Get compatible weapons list (from co-occurring sets)
        sql_weapons = """
            SELECT DISTINCT ip.part_num, ip.color_id, p.name AS part_name, c.name AS color_name, c.rgb AS color_rgb, ip.img_url, p.part_cat_id
            FROM inventory_minifigs im
            JOIN inventories i_set ON im.inventory_id = i_set.id
            JOIN inventory_parts ip ON i_set.id = ip.inventory_id
            JOIN parts p ON ip.part_num = p.part_num
            JOIN colors c ON ip.color_id = c.id
            WHERE im.minifig_num = ? 
              AND (p.part_cat_id = 73 OR p.name LIKE '%Weapon%' OR p.name LIKE '%Sword%' OR p.name LIKE '%Blaster%' OR p.name LIKE '%Lightsaber%' OR p.name LIKE '%Shield%' OR p.name LIKE '%Bow%' OR p.name LIKE '%Dagger%' OR p.name LIKE '%Axe%' OR p.name LIKE '%Spear%' OR p.name LIKE '%Gun%' OR p.name LIKE '%Pistol%' OR p.name LIKE '%Rifle%')
              AND LOWER(p.name) NOT LIKE '%tile%'
              AND LOWER(p.name) NOT LIKE '%book%'
              AND LOWER(p.name) NOT LIKE '%sticker%'
              AND LOWER(p.name) NOT LIKE '%magnet%'
              AND LOWER(p.name) NOT LIKE '%keychain%'
              AND LOWER(p.name) NOT LIKE '%keyring%'
              AND LOWER(p.name) NOT LIKE '%poster%'
              AND LOWER(p.name) NOT LIKE '%card%'
              AND LOWER(p.name) NOT LIKE '%wear%'
            LIMIT 12
        """
        cursor.execute(sql_weapons, (minifig_num,))
        weapons_list = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            row_dict["part_name"] = translate_to_zh(row_dict["part_name"])
            row_dict["color_name"] = translate_to_zh(row_dict["color_name"])
            weapons_list.append(row_dict)

        return {
            "minifig": minifig_data,
            "parts": parts_list,
            "sets": sets_list,
            "weapons": weapons_list
        }

    def api_shared_part(self, conn, params):
        part_num = params.get("part_num", [""])[0].strip()
        color_id = params.get("color_id", [""])[0].strip()
        exclude_id = params.get("exclude", [""])[0].strip()

        if not part_num or not color_id:
            self.send_json_response({"error": "Missing 'part_num' or 'color_id'"}, status=400)
            return None

        cursor = conn.cursor()
        
        # Exclude non-minifigures in shared parts check as well!
        sql_shared = """
            SELECT DISTINCT m.minifig_num, m.name, ip.img_url
            FROM inventory_parts ip
            JOIN inventories i ON ip.inventory_id = i.id
            JOIN minifigs m ON i.set_num = m.minifig_num
            WHERE ip.part_num = ? AND ip.color_id = ? AND LOWER(m.minifig_num) != ?
              AND m.num_parts BETWEEN 3 AND 12
              AND LOWER(m.name) NOT LIKE '%keychain%'
              AND LOWER(m.name) NOT LIKE '%key chain%'
              AND LOWER(m.name) NOT LIKE '%magnet%'
              AND LOWER(m.name) NOT LIKE '%watch%'
              AND LOWER(m.name) NOT LIKE '%clock%'
              AND LOWER(m.name) NOT LIKE '%book%'
              AND LOWER(m.name) NOT LIKE '%sticker%'
              AND LOWER(m.name) NOT LIKE '%card%'
              AND LOWER(m.name) NOT LIKE '%giant%'
              AND LOWER(m.name) NOT LIKE '%maxifigure%'
              AND LOWER(m.name) NOT LIKE '%brick-built%'
              AND LOWER(m.name) NOT LIKE '%pen%'
              AND LOWER(m.name) NOT LIKE '%torch%'
              AND LOWER(m.name) NOT LIKE '%light%'
              AND LOWER(m.name) NOT LIKE '%plush%'
              AND LOWER(m.name) NOT LIKE '%notebook%'
              AND LOWER(m.name) NOT LIKE '%tag%'
              AND LOWER(m.name) NOT LIKE '%bag%'
              AND LOWER(m.name) NOT LIKE '%frame%'
              AND LOWER(m.name) NOT LIKE '%display%'
              AND LOWER(m.name) NOT LIKE '%scale%'
            LIMIT 10
        """
        cursor.execute(sql_shared, (part_num, int(color_id), exclude_id.lower()))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            row_dict = dict(row)
            row_dict["name"] = translate_to_zh(row_dict["name"])
            row_dict["official_id"] = MINIFIG_ID_MAP.get(row_dict["minifig_num"], row_dict["minifig_num"])
            results.append(row_dict)
            
        return results

    def send_json_response(self, data, status=200):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        accepts_gzip = "gzip" in self.headers.get("Accept-Encoding", "")
        if accepts_gzip and len(payload) > 1024:
            payload = gzip.compress(payload, compresslevel=5)
            use_gzip = True
        else:
            use_gzip = False

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        if use_gzip:
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Vary", "Accept-Encoding")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

def init_users_db():
    try:
        # DB_PATH dir must exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            preferences TEXT
        )""")
        cursor.executescript("""
        CREATE INDEX IF NOT EXISTS idx_minifigs_num_parts ON minifigs(num_parts);
        CREATE INDEX IF NOT EXISTS idx_inventory_parts_part_color_inv ON inventory_parts(part_num, color_id, inventory_id);
        CREATE INDEX IF NOT EXISTS idx_inventory_parts_color_part_inv ON inventory_parts(color_id, part_num, inventory_id);
        CREATE INDEX IF NOT EXISTS idx_parts_cat_part ON parts(part_cat_id, part_num);
        CREATE INDEX IF NOT EXISTS idx_sets_theme ON sets(theme_id);
        """)
        conn.commit()
        conn.close()
        print("[Database] Users table initialized successfully.")
    except Exception as e:
        print(f"[Database Error] Failed to initialize users table: {e}")

def main():
    init_users_db()
    handler = LegoAPIHandler
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), handler) as httpd:
        print(f"[Server] BrickFinder Backend API Gateway running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Server] Shutting down server...")

if __name__ == "__main__":
    main()
