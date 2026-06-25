# server.py - Zero-dependency Python Web Server & SQLite API Gateway (With Chinese Translations & Filters)
import http.server
import socketserver
import urllib.parse
import json
import sqlite3
import os
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", 8000))
DB_PATH = os.path.join(BASE_DIR, "db", "lego.db")
STATIC_DIR = BASE_DIR

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

def translate_to_zh(name_en):
    if not name_en:
        return ""
    name_lower = name_en.lower()
    translated = name_en
    sorted_keys = sorted(EN_TO_ZH_MAP.keys(), key=len, reverse=True)
    replaced = False
    for key in sorted_keys:
        if key in name_lower:
            start_idx = name_lower.find(key)
            original_chunk = name_en[start_idx:start_idx+len(key)]
            translated = translated.replace(original_chunk, EN_TO_ZH_MAP[key])
            replaced = True
            name_lower = name_lower.replace(key, " " * len(key))
    if replaced:
        return f"{translated} [{name_en}]"
    return name_en

class LegoAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def end_headers(self):
        # Add Cache-Control headers for static files to optimize page speed
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        if path.startswith("/api/"):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        elif path.endswith((".js", ".css")):
            self.send_header("Cache-Control", "no-cache") # always revalidate so code updates propagate instantly
        elif path.endswith((".png", ".jpg", ".jpeg", ".svg", ".ico", ".woff", ".woff2")):
            self.send_header("Cache-Control", "public, max-age=86400") # 1 day cache for binary assets
        elif path.endswith((".html", "/")) or not "." in path:
            self.send_header("Cache-Control", "no-cache") # check for updates on HTML/entrypoints
        super().end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if path.startswith("/api/"):
            self.handle_api(path, query_params)
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
                self.api_scan_image(conn, body)
                
            else:
                self.send_json_response({"error": "Endpoint not found"}, status=404)
                
            conn.close()
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def handle_api(self, path, params):
        if not os.path.exists(DB_PATH):
            self.send_json_response({"error": "Database not found. Please run db_builder.py first."}, status=500)
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            
            if path == "/api/search":
                self.api_search(conn, params)
            elif path == "/api/gallery":
                self.api_gallery(conn, params)
            elif path == "/api/scan":
                self.api_scan(conn, params)
            elif path == "/api/minifig":
                self.api_minifig_details(conn, params)
            elif path == "/api/shared-part":
                self.api_shared_part(conn, params)
            else:
                self.send_json_response({"error": "Endpoint not found"}, status=404)
                
            conn.close()
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def api_gallery(self, conn, params):
        try:
            page = int(params.get("page", ["1"])[0])
            limit = int(params.get("limit", ["24"])[0])
            theme = params.get("theme", [""])[0].strip()
            sort = params.get("sort", ["num_parts_desc"])[0].strip()
            
            offset = (page - 1) * limit
            cursor = conn.cursor()
            
            # Base SQL matching standard valid minifigs (similar filters to search)
            sql_select = """
                SELECT DISTINCT m.minifig_num, m.name, m.num_parts 
                FROM minifigs m
                CROSS JOIN inventories i ON m.minifig_num = i.set_num
                CROSS JOIN inventory_parts ip ON i.id = ip.inventory_id
                CROSS JOIN parts p ON ip.part_num = p.part_num
                WHERE p.part_cat_id IN (60, 61, 13)
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
            """
            
            args = []
            if theme:
                translated_theme = translate_query(theme)
                sql_select += " AND (LOWER(m.name) LIKE ? OR LOWER(m.minifig_num) LIKE ?)"
                args.extend([f"%{translated_theme}%", f"%{translated_theme}%"])
                
            if sort == "num_parts_desc":
                sql_select += " ORDER BY m.num_parts DESC"
            elif sort == "num_parts_asc":
                sql_select += " ORDER BY m.num_parts ASC"
            elif sort == "minifig_num_asc":
                sql_select += " ORDER BY m.minifig_num ASC"
            else:
                sql_select += " ORDER BY m.num_parts DESC"
                
            sql_select += " LIMIT ? OFFSET ?"
            args.extend([limit, offset])
            
            cursor.execute(sql_select, args)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                row_dict = dict(row)
                row_dict["name"] = translate_to_zh(row_dict["name"])
                
                # Fetch series/theme
                sql_theme = """
                    SELECT t.name 
                    FROM inventory_minifigs im
                    JOIN inventories i ON im.inventory_id = i.id
                    JOIN sets s ON i.set_num = s.set_num
                    JOIN themes t ON s.theme_id = t.id
                    WHERE LOWER(im.minifig_num) = ?
                    LIMIT 1
                """
                cursor.execute(sql_theme, (row_dict["minifig_num"].lower(),))
                theme_row = cursor.fetchone()
                row_dict["theme_name"] = translate_to_zh(theme_row["name"]) if theme_row else "收藏系列"
                results.append(row_dict)
                
            self.send_json_response(results)
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def api_search(self, conn, params):
        query = params.get("q", [""])[0].strip()
        if not query:
            self.send_json_response([])
            return

        translated_query = translate_query(query)
        cursor = conn.cursor()
        
        # Search query strictly excluding gear, keychains, clocks, magnets, books, stickers, etc.
        # Must have standard torso (60) or legs (61) and have a reasonable part count (3-12 parts)
        sql = """
            SELECT DISTINCT m.minifig_num, m.name, m.num_parts 
            FROM minifigs m
            CROSS JOIN inventories i ON m.minifig_num = i.set_num
            CROSS JOIN inventory_parts ip ON i.id = ip.inventory_id
            CROSS JOIN parts p ON ip.part_num = p.part_num
            WHERE (m.minifig_num LIKE ? OR m.name LIKE ?) 
              AND p.part_cat_id IN (60, 61)
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
            
        self.send_json_response(results)
            
    def api_scan(self, conn, params):
        target_color = params.get("color", ["ffffff"])[0].strip().lower()
        query = params.get("query", [""])[0].strip().lower()
        
        cursor = conn.cursor()
        
        # Fetch parts colors for minifigures
        # Filter popular minifigures to return best results
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
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        # Group by minifigure
        minifigs = {}
        for row in rows:
            num = row["minifig_num"]
            if num not in minifigs:
                minifigs[num] = {
                    "minifig_num": num,
                    "name": translate_to_zh(row["minifig_name"]),
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
        
        # Take top 3
        top_matches = [m[1] for m in matches[:3]]
        self.send_json_response(top_matches)

    def api_scan_image(self, conn, body):
        import urllib.request
        import urllib.error
        
        base64_image = body.get("image", "").strip()
        target_color = body.get("color", "ffffff").strip().lower()
        api_key = body.get("api_key", "").strip()
        
        # 1. Resolve Gemini API Key
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            
        if not api_key:
            self.send_json_response({
                "error": "API_KEY_MISSING",
                "message": "未配置 Gemini API Key。请在设置中配置您的 Key，或联系管理员配置服务器环境变量。"
            }, status=400)
            return
            
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
                
        # 3. Call Gemini API
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        prompt = (
            "Identify the Lego minifigure in this image. Look for distinctive parts like the head/hair/helmet, torso printing, legs, or accessories.\n"
            "Provide a brief description of the minifigure in Chinese (within 60 characters).\n"
            "Provide 3-5 specific English search keywords or character names (e.g. 'vader', 'yoda', 'batman', 'maul', 'clone trooper', 'luke skywalker', 'lloyd', 'harry potter') that can be used to search for this minifigure in our database.\n"
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
            
        except urllib.error.HTTPError as e:
            err_content = e.read().decode('utf-8')
            try:
                err_json = json.loads(err_content)
                err_msg = err_json.get("error", {}).get("message", "Gemini API error")
            except:
                err_msg = f"HTTP Error {e.code}"
            self.send_json_response({
                "error": "GEMINI_ERROR",
                "message": f"Gemini API 调用异常: {err_msg}"
            }, status=500)
            return
        except Exception as e:
            self.send_json_response({
                "error": "SERVER_ERROR",
                "message": f"处理图像或调用 AI 时出错: {str(e)}"
            }, status=500)
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
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        minifigs = {}
        for row in rows:
            num = row["minifig_num"]
            if num not in minifigs:
                minifigs[num] = {
                    "minifig_num": num,
                    "name": translate_to_zh(row["minifig_name"]),
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
        top_matches = [m[1] for m in matches[:3]]
        
        self.send_json_response({
            "description": ai_desc,
            "results": top_matches
        })

    def api_minifig_details(self, conn, params):
        minifig_id = params.get("id", [""])[0].strip()
        if not minifig_id:
            self.send_json_response({"error": "Missing 'id' parameter"}, status=400)
            return

        cursor = conn.cursor()
        
        sql_minifig = """
            SELECT minifig_num, name, num_parts 
            FROM minifigs 
            WHERE LOWER(minifig_num) = ? OR LOWER(minifig_num) = ?
        """
        norm_id = minifig_id.lower()
        norm_id_suffix = f"{norm_id}-1" if "-" not in norm_id else norm_id
        
        cursor.execute(sql_minifig, (norm_id, norm_id_suffix))
        minifig_row = cursor.fetchone()
        
        if not minifig_row:
            self.send_json_response({"error": "Minifigure not found"}, status=404)
            return
            
        minifig_data = dict(minifig_row)
        minifig_data["name"] = translate_to_zh(minifig_data["name"])
        minifig_num = minifig_data["minifig_num"]

        # Get parts list
        cursor.execute("SELECT id FROM inventories WHERE LOWER(set_num) = ?", (minifig_num.lower(),))
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
            WHERE LOWER(im.minifig_num) = ?
        """
        cursor.execute(sql_sets, (minifig_num.lower(),))
        sets_list = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            row_dict["set_name"] = translate_to_zh(row_dict["set_name"])
            row_dict["theme_name"] = translate_to_zh(row_dict["theme_name"])
            sets_list.append(row_dict)

        self.send_json_response({
            "minifig": minifig_data,
            "parts": parts_list,
            "sets": sets_list
        })

    def api_shared_part(self, conn, params):
        part_num = params.get("part_num", [""])[0].strip()
        color_id = params.get("color_id", [""])[0].strip()
        exclude_id = params.get("exclude", [""])[0].strip()

        if not part_num or not color_id:
            self.send_json_response({"error": "Missing 'part_num' or 'color_id'"}, status=400)
            return

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
            
        self.send_json_response(results)

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

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
        conn.commit()
        conn.close()
        print("[Database] Users table initialized successfully.")
    except Exception as e:
        print(f"[Database Error] Failed to initialize users table: {e}")

def main():
    init_users_db()
    handler = LegoAPIHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"[Server] BrickFinder Backend API Gateway running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Server] Shutting down server...")

if __name__ == "__main__":
    main()
