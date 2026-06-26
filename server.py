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
    "忍者": "ninja",
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
    "银色": "silver"
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
    "helmet": "头盔",
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
        return f"{translated} [{name_en}]"
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
            results.append(row_dict)
            
        return results

    def api_search(self, conn, params):
        query = params.get("q", [""])[0].strip()
        if not query:
            return []

        translated_query = translate_query(query)
        cursor = conn.cursor()
        
        # Search query strictly excluding gear, keychains, clocks, magnets, books, stickers, etc.
        # Must have standard torso (60) or legs (61) and have a reasonable part count (3-12 parts)
        sql = f"""
            SELECT m.minifig_num, m.name, m.num_parts 
            FROM minifigs m
            WHERE (m.minifig_num LIKE ? OR m.name LIKE ?) 
              AND m.num_parts BETWEEN 3 AND 12
              {MINIFIG_EXCLUSION_SQL}
              AND EXISTS (
                  SELECT 1
                  FROM inventories i
                  JOIN inventory_parts ip ON i.id = ip.inventory_id
                  JOIN parts p ON ip.part_num = p.part_num
                  WHERE i.set_num = m.minifig_num
                    AND p.part_cat_id IN (60, 61)
                  LIMIT 1
              )
            ORDER BY m.num_parts DESC 
            LIMIT 15
        """
        like_query = f"%{translated_query}%"
        cursor.execute(sql, (like_query, like_query))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            row_dict = dict(row)
            row_dict["name"] = translate_to_zh(row_dict["name"])
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
            if query and (query in name_lower or query in num_lower):
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
        
        base64_image = body.get("image", "").strip()
        target_color = body.get("color", "ffffff").strip().lower()
        api_key = body.get("api_key", "").strip()
        
        if not base64_image:
            self.send_json_response({
                "error": "INVALID_IMAGE",
                "message": "无有效的图像数据。"
            }, status=400)
            return

        # 2. Extract mime type and raw base64 data
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
                
        # Try calling Brickognize first
        try:
            import base64
            import uuid
            
            raw_image_bytes = base64.b64decode(image_data)
            boundary = f"Boundary-{uuid.uuid4().hex}"
            
            # Construct multipart form-data body
            body_parts = []
            body_parts.append(f"--{boundary}".encode('utf-8'))
            body_parts.append(f'Content-Disposition: form-data; name="query_image"; filename="image.jpg"'.encode('utf-8'))
            body_parts.append(f'Content-Type: {mime_type}'.encode('utf-8'))
            body_parts.append(b'')
            body_parts.append(raw_image_bytes)
            body_parts.append(f"--{boundary}--".encode('utf-8'))
            body_parts.append(b'')
            body_bytes = b'\r\n'.join(body_parts)
            
            brickognize_url = "https://api.brickognize.com/predict/"
            req = urllib.request.Request(
                brickognize_url,
                data=body_bytes,
                headers={
                    'Content-Type': f'multipart/form-data; boundary={boundary}',
                    'Accept': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                },
                method='POST'
            )
            
            print("Calling Brickognize predict API...")
            # Set a moderate timeout (6 seconds) to prevent hanging
            with urllib.request.urlopen(req, timeout=6) as response:
                res_body = json.loads(response.read().decode('utf-8'))
                
            brick_items = res_body.get("items", [])
            matched_figs = []
            cursor = conn.cursor()
            
            for item in brick_items:
                itype = str(item.get("type", "")).strip().lower()
                if itype in ("fig", "minifig") or item.get("id", "").startswith("fig-"):
                    candidates = set()
                    candidates.add(item.get("id", "").strip().lower())
                    
                    # Also extract from external sites
                    for ext in item.get("external_sites", []):
                        url = ext.get("url", "")
                        # 1. Parse BrickLink ID (M parameter)
                        if "bricklink.com/" in url and ("?M=" in url or "&M=" in url or "?m=" in url or "&m=" in url):
                            import re
                            match = re.search(r'[?&][Mm]=([^&#]+)', url)
                            if match:
                                candidates.add(match.group(1).strip().lower())
                        # 2. Parse Rebrickable ID
                        if "rebrickable.com/minifigs/" in url:
                            parts = url.split("minifigs/")
                            if len(parts) > 1:
                                sub = parts[1].split("/")[0]
                                if sub:
                                    candidates.add(sub.strip().lower())
                                    
                    # Query candidates in our local database
                    found_direct = False
                    for cand in candidates:
                        if not cand:
                            continue
                        cursor.execute("SELECT minifig_num, name, num_parts FROM minifigs WHERE LOWER(minifig_num) = ?", (cand,))
                        row = cursor.fetchone()
                        if row:
                            matched_figs.append({
                                "minifig_num": row["minifig_num"],
                                "name": row["name"],
                                "num_parts": row["num_parts"],
                                "img_url": f"https://cdn.rebrickable.com/media/sets/{row['minifig_num']}.jpg",
                                "score": item.get("score", 0.9)
                            })
                            found_direct = True
                            
                    # If not found directly, do a fuzzy name match
                    if not found_direct and item.get("name"):
                        matched_row, match_score = fuzzy_match_minifig(conn, item["name"])
                        if matched_row and match_score >= 0.5:
                            matched_figs.append({
                                "minifig_num": matched_row["minifig_num"],
                                "name": matched_row["name"],
                                "num_parts": matched_row["num_parts"],
                                "img_url": f"https://cdn.rebrickable.com/media/sets/{matched_row['minifig_num']}.jpg",
                                "score": item.get("score", 0.9)
                            })
                            
            if matched_figs:
                # Deduplicate matches
                seen = set()
                unique_matches = []
                for fig in matched_figs:
                    if fig["minifig_num"] not in seen:
                        seen.add(fig["minifig_num"])
                        unique_matches.append(fig)
                        
                # Sort unique matches by score descending
                unique_matches.sort(key=lambda x: x.get("score", 0), reverse=True)
                top_matches = unique_matches[:3]
                
                # Translate names for top matches
                for fig in top_matches:
                    fig["name"] = translate_to_zh(fig["name"])
                    
                self.send_json_response({
                    "description": f"已通过 Brickognize 智能引擎精准比对，匹配置信度 {(top_matches[0]['score']*100):.1f}%",
                    "results": top_matches
                })
                print(f"Brickognize successfully identified minifigure: {[f['minifig_num'] for f in top_matches]}")
                return
                
            print("Brickognize succeeded but returned no matching minifigures in local database. Falling back to Gemini...")
        except Exception as e:
            print(f"Brickognize API call failed or timed out (error: {str(e)}). Falling back to Gemini...")
            
        # 3. Call Gemini API
        if not api_key:
            print("Gemini API key is missing. Falling back to traditional color distance search...")
            params = {"color": [target_color], "query": [""]}
            color_matches = self.api_scan(conn, params)
            self.send_json_response({
                "description": "⚠️ 图像未能通过 Brickognize 引擎精确匹配，已为您推荐颜色最相近的经典人仔。",
                "results": color_matches
            })
            return
            
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        prompt = (
            "Analyze the Lego minifigure in the image and extract its visual attributes to match a database name.\n"
            "1. Identify the character name (e.g. 'Darth Vader', 'Luke Skywalker', 'Iron Man', 'Boba Fett').\n"
            "2. Identify unique features shown in the image, such as:\n"
            "   - Skin color (e.g., 'Yellow', 'Light Nougat', 'White').\n"
            "   - Helmet/Hair color and type (e.g., 'Chrome Black', 'Gold Helmet', 'Brown Hair').\n"
            "   - Specific suit/armor printing details (e.g., 'Imperial Inspection', 'Quantum Suit', 'Oni Mask', 'Printed Arms').\n"
            "   - Key accessories (e.g., 'Cape', 'Lightsaber', 'Pauldrons', 'Visor').\n"
            "3. Output 5-8 specific keywords in English. The first 1-2 keywords must be the character name. The other keywords must be the specific distinguishing features (e.g., 'chrome', 'nougat', 'printed legs').\n"
            "4. Provide a brief description of the minifigure in Chinese (within 60 characters) describing who it is and its key visual features.\n"
            "Return the output STRICTLY in JSON format matching this schema:\n"
            "{\n"
            "  \"description\": \"Chinese description here\",\n"
            "  \"keywords\": [\"keyword1\", \"keyword2\", ...]\n"
            "}"
        )
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": image_data
                        }
                    }
                ]
            }],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        
        try:
            req = urllib.request.Request(
                gemini_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=20) as response:
                res_body = json.loads(response.read().decode('utf-8'))
                
            # Parse text response from Gemini
            text_response = res_body["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Clean markdown JSON wrapping if present
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            text_response = text_response.strip()
            
            ai_data = json.loads(text_response)
            ai_desc = ai_data.get("description", "智能分析成功")
            keywords = ai_data.get("keywords", [])
            
        except Exception as e:
            print(f"Gemini API call failed (error: {str(e)}). Falling back to traditional color distance search...")
            params = {"color": [target_color], "query": [""]}
            color_matches = self.api_scan(conn, params)
            self.send_json_response({
                "description": "⚠️ 图像识别大模型暂时不可用，已为您推荐颜色最相近的经典人仔。",
                "results": color_matches
            })
            return

        # 4. Search and score minifigures based on keywords and color distance
        cursor = conn.cursor()
        
        # Clean keywords
        keywords = [k.lower().strip() for k in keywords if k.strip()]
        
        # Fetch all candidate minifigures
        sql = """
            SELECT m.minifig_num, m.name AS minifig_name, m.num_parts, c.rgb
            FROM minifigs m
            JOIN inventories i ON m.minifig_num = i.set_num
            JOIN inventory_parts ip ON i.id = ip.inventory_id
            JOIN colors c ON ip.color_id = c.id
            WHERE m.num_parts BETWEEN 3 AND 12
              AND m.minifig_num LIKE 'fig-%'
              AND LOWER(m.name) NOT LIKE '%keychain%'
              AND LOWER(m.name) NOT LIKE '%magnet%'
              AND LOWER(m.name) NOT LIKE '%watch%'
              AND LOWER(m.name) NOT LIKE '%clock%'
              AND LOWER(m.name) NOT LIKE '%book%'
              AND LOWER(m.name) NOT LIKE '%sticker%'
              AND LOWER(m.name) NOT LIKE '%card%'
              AND LOWER(m.name) NOT LIKE '%pen%'
              AND LOWER(m.name) NOT LIKE '%torch%'
        """
        rows = self.get_scan_candidate_rows(conn)
        
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
            
            # Score keyword matches
            query_score = 0
            for kw in keywords:
                if kw in name_lower or kw in num_lower:
                    query_score += 1000000
                    
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
                    
            total_dist = min_color_dist - query_score
            matches.append((total_dist, fig))
            
        matches.sort(key=lambda x: x[0])
        
        # Take top 3 and translate their names
        top_matches = []
        for m in matches[:3]:
            fig = m[1]
            fig["name"] = translate_to_zh(fig["name"])
            top_matches.append(fig)
        
        return {
            "description": ai_desc,
            "results": top_matches
        }

    def api_minifig_details(self, conn, params):
        minifig_id = params.get("id", [""])[0].strip()
        if not minifig_id:
            self.send_json_response({"error": "Missing 'id' parameter"}, status=400)
            return None

        cursor = conn.cursor()
        
        sql_minifig = """
            SELECT minifig_num, name, num_parts 
            FROM minifigs 
            WHERE minifig_num = ? OR minifig_num = ?
        """
        norm_id = minifig_id.lower()
        norm_id_suffix = f"{norm_id}-1" if "-" not in norm_id else norm_id
        
        cursor.execute(sql_minifig, (norm_id, norm_id_suffix))
        minifig_row = cursor.fetchone()
        
        if not minifig_row:
            self.send_json_response({"error": "Minifigure not found"}, status=404)
            return None
            
        minifig_data = dict(minifig_row)
        minifig_data["name"] = translate_to_zh(minifig_data["name"])
        minifig_num = minifig_data["minifig_num"]

        # Get parts list
        cursor.execute("SELECT id FROM inventories WHERE set_num = ?", (minifig_num,))
        inventory_row = cursor.fetchone()
        
        parts_list = []
        if inventory_row:
            inv_id = inventory_row["id"]
            
            sql_parts = """
                SELECT ip.part_num, ip.color_id, ip.quantity, p.name AS part_name, 
                       c.name AS color_name, c.rgb AS color_rgb, ip.img_url, p.part_cat_id
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
