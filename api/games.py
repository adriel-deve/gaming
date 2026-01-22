"""
Vercel Serverless API for Eshop Pulse
Endpoints:
  GET /api/games/image/[slug] - Get game image from database
  GET /api/games/history/[slug] - Get price history for a game
  GET /api/games/history/[slug]?region=BR - Get history for specific region
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse, parse_qs

DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_game_image(slug):
    """Get game cover image URL"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT slug, image_url
        FROM game_images
        WHERE slug = %s
    """, (slug,))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result

def get_price_history(slug, region=None):
    """Get price history for a game (for charts)"""
    conn = get_connection()
    cursor = conn.cursor()

    if region:
        cursor.execute("""
            SELECT
                recorded_at,
                region_code,
                currency,
                msrp,
                sale_price,
                price_brl,
                discount_percent,
                on_sale
            FROM price_history
            WHERE slug = %s AND region_code = %s
            ORDER BY recorded_at ASC
        """, (slug, region))
    else:
        cursor.execute("""
            SELECT
                recorded_at,
                region_code,
                currency,
                msrp,
                sale_price,
                price_brl,
                discount_percent,
                on_sale
            FROM price_history
            WHERE slug = %s
            ORDER BY recorded_at ASC, price_brl ASC
        """, (slug,))

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results

def get_price_stats(slug):
    """Get price statistics for a game"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            region_code,
            MIN(price_brl) as min_price,
            MAX(price_brl) as max_price,
            AVG(price_brl)::DECIMAL(10,2) as avg_price,
            MIN(recorded_at) as first_date,
            MAX(recorded_at) as last_date,
            COUNT(*) as records
        FROM price_history
        WHERE slug = %s
        GROUP BY region_code
        ORDER BY min_price ASC
    """, (slug,))

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Cache-Control', 'public, max-age=300')
        self.end_headers()

        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            path_parts = parsed.path.strip('/').split('/')

            # Route: /api/games/image/[slug]
            if len(path_parts) >= 4 and path_parts[2] == 'image':
                slug = path_parts[3]
                result = get_game_image(slug)
                if result:
                    self.wfile.write(json.dumps(result, default=str).encode())
                else:
                    self.wfile.write(json.dumps({'error': 'Image not found'}).encode())

            # Route: /api/games/history/[slug]
            elif len(path_parts) >= 4 and path_parts[2] == 'history':
                slug = path_parts[3]
                region = params.get('region', [None])[0]
                result = get_price_history(slug, region)
                self.wfile.write(json.dumps(result, default=str).encode())

            # Route: /api/games/stats/[slug]
            elif len(path_parts) >= 4 and path_parts[2] == 'stats':
                slug = path_parts[3]
                result = get_price_stats(slug)
                self.wfile.write(json.dumps(result, default=str).encode())

            else:
                self.wfile.write(json.dumps({
                    'endpoints': [
                        '/api/games/image/[slug]',
                        '/api/games/history/[slug]',
                        '/api/games/history/[slug]?region=BR',
                        '/api/games/stats/[slug]'
                    ]
                }).encode())

        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
