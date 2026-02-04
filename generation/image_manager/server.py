#!/usr/bin/env python3
"""Image Manager API Server for HelloBeautyBlog"""

import json
import os
import http.server
import urllib.parse
from pathlib import Path

PORT = 8080
BASE = Path(__file__).parent
DATA_FILE = BASE / "data.json"
PRODUCT_LISTS = BASE.parent / "product_lists"
CONTENT_DIR = Path("/home/ubuntu/hbb/content")

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"products": {}, "published": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_all_products():
    """Load all products from product lists with category info"""
    products = []
    for cat in ["perfumes", "skincare", "makeup", "haircare"]:
        fpath = PRODUCT_LISTS / f"{cat}.json"
        if fpath.exists():
            with open(fpath) as f:
                for p in json.load(f):
                    p["category"] = cat
                    products.append(p)
    return products

def get_official_subcategories():
    """Get subcategories that have actual content pages"""
    subcats = {}
    for cat in ["perfumes", "skincare", "makeup", "haircare"]:
        subcats[cat] = set()
        d = CONTENT_DIR / "en" / cat
        if d.is_dir():
            for item in d.iterdir():
                if item.is_dir() and item.name != "_index.md":
                    subcats[cat].add(item.name)
    return subcats

def get_existing_published():
    """Find products already published (exist in content with all 14 langs)"""
    langs = ["en","fr","de","es","it","pt","nl","pl","tr","ja","ko","zh","ar","hi"]
    published = []
    products = get_all_products()
    slug_to_cat = {p["slug"]: p["category"] for p in products}
    
    for slug, cat in slug_to_cat.items():
        all_langs = True
        for lang in langs:
            fpath = CONTENT_DIR / lang / cat / f"{slug}.md"
            if not fpath.exists():
                all_langs = False
                break
        if all_langs:
            published.append(slug)
    return published

def compute_priority(products, published_slugs, official_subcats, data):
    """Sort products by subcategory coverage priority"""
    # Count how many published/ready products cover each subcat
    subcat_coverage = {}
    for cat, subs in official_subcats.items():
        for s in subs:
            subcat_coverage[f"{cat}:{s}"] = 0
    
    # Count coverage from published products
    for p in products:
        if p["slug"] in published_slugs:
            cat = p["category"]
            for s in p["subcategories"]:
                key = f"{cat}:{s}"
                if key in subcat_coverage:
                    subcat_coverage[key] += 1
    
    # For each non-published product, compute priority score
    # Lower = higher priority (fills more empty subcats)
    scored = []
    for p in products:
        if p["slug"] in published_slugs:
            continue
        cat = p["category"]
        relevant_subcats = [f"{cat}:{s}" for s in p["subcategories"] if f"{cat}:{s}" in subcat_coverage]
        if relevant_subcats:
            min_coverage = min(subcat_coverage.get(k, 999) for k in relevant_subcats)
            avg_coverage = sum(subcat_coverage.get(k, 0) for k in relevant_subcats) / len(relevant_subcats)
            empty_count = sum(1 for k in relevant_subcats if subcat_coverage.get(k, 0) == 0)
        else:
            min_coverage = 999
            avg_coverage = 999
            empty_count = 0
        
        # Sort: most empty subcats first, then lowest min coverage, then lowest avg
        scored.append({
            **p,
            "priority_score": (-empty_count, min_coverage, avg_coverage),
            "empty_subcats": empty_count,
            "min_coverage": min_coverage
        })
    
    scored.sort(key=lambda x: x["priority_score"])
    return scored

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(BASE / "index.html", "rb") as f:
                self.wfile.write(f.read())
                
        elif parsed.path == "/api/products":
            data = load_data()
            products = get_all_products()
            official_subcats = get_official_subcategories()
            existing_pub = get_existing_published()
            
            # Merge saved data
            published_slugs = set(data.get("published", []) + existing_pub)
            saved_images = data.get("products", {})
            
            # Compute priority
            sorted_products = compute_priority(products, published_slugs, official_subcats, data)
            
            # Attach saved images and status
            for p in sorted_products:
                slug = p["slug"]
                if slug in saved_images:
                    p["images"] = saved_images[slug].get("images", [])
                    p["status"] = saved_images[slug].get("status", "pending")
                    p["generated_langs"] = saved_images[slug].get("generated_langs", [])
                else:
                    p["images"] = []
                    p["status"] = "pending"
                    p["generated_langs"] = []
            
            # Published products
            pub_products = []
            for p in products:
                if p["slug"] in published_slugs:
                    slug = p["slug"]
                    p_data = saved_images.get(slug, {})
                    pub_products.append({
                        **p,
                        "images": p_data.get("images", []),
                        "status": "published",
                        "generated_langs": p_data.get("generated_langs", list("en fr de es it pt nl pl tr ja ko zh ar hi".split()))
                    })
            
            # Subcat coverage stats
            subcat_stats = {}
            for cat, subs in official_subcats.items():
                for s in subs:
                    key = f"{cat}:{s}"
                    count = 0
                    for p in products:
                        if p["category"] == cat and s in p["subcategories"] and p["slug"] in published_slugs:
                            count += 1
                    subcat_stats[key] = count
            
            response = {
                "products": sorted_products,
                "published": pub_products,
                "subcat_stats": subcat_stats,
                "total_products": len(products),
                "total_published": len(published_slugs)
            }
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
            
        elif parsed.path.startswith("/api/generation-log"):
            params = urllib.parse.parse_qs(parsed.query)
            log_file = params.get("file", [""])[0]
            if log_file and os.path.exists(log_file):
                with open(log_file) as f:
                    lines = f.readlines()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"lines": lines[-80:], "total": len(lines)}).encode())
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"lines": [], "total": 0}).encode())
                
        elif parsed.path == "/api/export-lot":
            data = load_data()
            saved = data.get("products", {})
            lot = []
            for slug, info in saved.items():
                if info.get("status") == "ready" and len(info.get("images", [])) >= 1:
                    # Find full product info
                    products = get_all_products()
                    for p in products:
                        if p["slug"] == slug:
                            lot.append({**p, "images": info["images"]})
                            break
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Disposition", "attachment; filename=lot.json")
            self.end_headers()
            self.wfile.write(json.dumps(lot, indent=2, ensure_ascii=False).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_len)) if content_len else {}
        
        if parsed.path == "/api/save-images":
            slug = body.get("slug")
            images = body.get("images", [])
            data = load_data()
            if slug not in data["products"]:
                data["products"][slug] = {"images": [], "status": "pending", "generated_langs": []}
            data["products"][slug]["images"] = images
            if len(images) >= 1:
                data["products"][slug]["status"] = "ready"
            else:
                data["products"][slug]["status"] = "pending"
            save_data(data)
            self.send_json({"ok": True})
            
        elif parsed.path == "/api/mark-published":
            slug = body.get("slug")
            data = load_data()
            if slug not in data["published"]:
                data["published"].append(slug)
            if slug in data["products"]:
                data["products"][slug]["status"] = "published"
                data["products"][slug]["generated_langs"] = body.get("langs", [])
            save_data(data)
            self.send_json({"ok": True})
            
        elif parsed.path == "/api/update-status":
            slug = body.get("slug")
            status = body.get("status")
            langs = body.get("generated_langs", [])
            data = load_data()
            if slug in data["products"]:
                data["products"][slug]["status"] = status
                if langs:
                    data["products"][slug]["generated_langs"] = langs
            save_data(data)
            self.send_json({"ok": True})
            
        elif parsed.path == "/api/launch-generation":
            # Save lot.json and launch generation
            lot = body.get("products", [])
            extra_args = body.get("args", "")
            timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
            lot_file = BASE.parent / f"lot_{timestamp}.json"
            with open(lot_file, "w") as f:
                json.dump(lot, f, indent=2, ensure_ascii=False)
            
            log_file = f"/tmp/hbb_generate_{timestamp}.log"
            cmd = f'cd /home/ubuntu/hbb/generation && nohup python3 generate_lot.py "{lot_file}" {extra_args} > "{log_file}" 2>&1 &'
            os.system(cmd)
            
            self.send_json({"ok": True, "log": log_file, "count": len(lot)})
            
        elif parsed.path == "/api/generation-log":
            log_file = body.get("log", "")
            if log_file and os.path.exists(log_file):
                with open(log_file) as f:
                    lines = f.readlines()
                # Return last 50 lines
                self.send_json({"lines": lines[-50:], "total": len(lines)})
            else:
                self.send_json({"lines": [], "total": 0})
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass  # Quiet logging

if __name__ == "__main__":
    os.chdir(str(BASE))
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Image Manager running on http://0.0.0.0:{PORT}")
    server.serve_forever()

# === GENERATION ENDPOINTS (appended) ===
# These are added via the server's POST handler
