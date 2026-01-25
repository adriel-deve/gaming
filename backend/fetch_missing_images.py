"""
Fetch missing game images from Nintendo API
"""
import json
import urllib.request
import urllib.parse
import time
import ssl

# Create SSL context
try:
    ssl_context = ssl.create_default_context()
except:
    ssl_context = None

def fetch_image_from_nintendo_api(title, nsuid=None):
    """Try to fetch image from Nintendo API"""

    # Try US Nintendo API search
    search_url = f"https://www.nintendo.com/json/content/get/filter/game?system=switch&limit=1&title={urllib.parse.quote(title)}"

    try:
        req = urllib.request.Request(search_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('games', {}).get('game'):
                game = data['games']['game'][0] if isinstance(data['games']['game'], list) else data['games']['game']
                if game.get('front_box_art'):
                    return game['front_box_art']
                if game.get('image_url'):
                    return game['image_url']
    except Exception as e:
        pass

    # Try EU Nintendo API with NSUID
    if nsuid:
        try:
            eu_url = f"https://ec.nintendo.com/api/JP/ja/search/title/{nsuid}?limit=1"
            req = urllib.request.Request(eu_url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json'
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data and len(data) > 0:
                    if data[0].get('screenshots') and len(data[0]['screenshots']) > 0:
                        return data[0]['screenshots'][0]['images'][0]['url']
        except:
            pass

    return None

def generate_placeholder_url(title, slug):
    """Generate a placeholder image URL using a service"""
    # Use DiceBear for placeholder avatars based on game name
    encoded_seed = urllib.parse.quote(slug or title)
    return f"https://api.dicebear.com/7.x/shapes/svg?seed={encoded_seed}&backgroundColor=1a1a2e&shape1Color=ff3b3b"

print("="*60)
print("FETCHING MISSING GAME IMAGES")
print("="*60)

# Load enriched data
with open('multi_region_enriched.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

print(f"[OK] Loaded {len(games)} games")

# Find games without images
no_image_games = [g for g in games if not g.get('image')]
print(f"[!] Found {len(no_image_games)} games without images")

# Try to fetch images
fetched = 0
failed = 0

for i, game in enumerate(no_image_games):
    title = game.get('title', '')
    nsuid = game.get('nsuid', '')
    slug = game.get('slug', '')

    safe_title = title[:50].encode('ascii', 'replace').decode('ascii')
    print(f"[{i+1}/{len(no_image_games)}] {safe_title}...", end=' ')

    # Try Nintendo API first
    image_url = fetch_image_from_nintendo_api(title, nsuid)

    if image_url:
        game['image'] = image_url
        fetched += 1
        print("FOUND!")
    else:
        # Use placeholder
        game['image'] = generate_placeholder_url(title, slug)
        failed += 1
        print("using placeholder")

    # Rate limiting
    time.sleep(0.3)

    # Progress update every 50 games
    if (i + 1) % 50 == 0:
        print(f"\n--- Progress: {i+1}/{len(no_image_games)} | Found: {fetched} | Placeholders: {failed} ---\n")

print(f"\n[OK] Fetched {fetched} images from Nintendo")
print(f"[OK] Using {failed} placeholder images")

# Save updated data
with open('multi_region_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(games, f, ensure_ascii=False)

print(f"[OK] Saved updated data to multi_region_enriched.json")

print("\n" + "="*60)
print("DONE!")
print("="*60)
