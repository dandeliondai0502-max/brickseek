# server.py - Zero-dependency Python Web Server & SQLite API Gateway (With Chinese Translations & Filters)
import http.server
import socketserver
import urllib.parse
import json
import sqlite3
import os

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

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if path.startswith("/api/"):
            self.handle_api(path, query_params)
        else:
            super().do_GET()

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
                JOIN inventories i ON m.minifig_num = i.set_num
                JOIN inventory_parts ip ON i.id = ip.inventory_id
                JOIN parts p ON ip.part_num = p.part_num
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
            JOIN inventories i ON m.minifig_num = i.set_num
            JOIN inventory_parts ip ON i.id = ip.inventory_id
            JOIN parts p ON ip.part_num = p.part_num
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

def main():
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
