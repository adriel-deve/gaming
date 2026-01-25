"""
Generate nintendo.html with ALL 6,438 games
Shows 4-region price comparison for each game
"""
import json
import os

print("="*60)
print("GENERATING NINTENDO PAGE WITH ALL GAMES")
print("="*60)

# Load multi-region data
with open('multi_region_enriched.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

print(f"[OK] Loaded {len(games)} games")

# Process all games
all_games_js = []

for game in games:
    if not game.get('prices'):
        continue

    # Organize prices by region (keep best price per region)
    prices_by_region = {}
    for price in game['prices']:
        region = price['region']
        if region not in prices_by_region or price['price_brl'] < prices_by_region[region]['price_brl']:
            prices_by_region[region] = price

    if not prices_by_region:
        continue

    # Find cheapest overall and best discount
    cheapest_region = min(prices_by_region.keys(), key=lambda r: prices_by_region[r]['price_brl'])
    cheapest = prices_by_region[cheapest_region]
    max_discount = max((p.get('discount_percent', 0) for p in prices_by_region.values()), default=0)

    # Build prices object for JS
    prices_js = {}
    for region in ['BR', 'US', 'CA', 'MX']:
        if region in prices_by_region:
            p = prices_by_region[region]
            prices_js[region] = {
                'currency': p['currency'],
                'msrp': round(p['msrp'], 2),
                'sale': round(p['sale_price'], 2),
                'brl': round(p['price_brl'], 2),
                'discount': p.get('discount_percent', 0)
            }

    # Escape title for JS
    title = game['title'].replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', '').replace("'", "\\'")

    all_games_js.append({
        'title': title,
        'slug': game.get('slug', ''),
        'image': game.get('image', ''),
        'discount': max_discount,
        'cheapest_brl': cheapest['price_brl'],
        'cheapest_region': cheapest_region,
        'num_regions': len(prices_by_region),
        'prices': prices_js
    })

# Sort by discount then price
all_games_js.sort(key=lambda x: (-x['discount'], x['cheapest_brl']))

print(f"[OK] Processed {len(all_games_js)} games")

# Generate JS array string
js_games = []
for g in all_games_js:
    prices_str = json.dumps(g['prices'], separators=(',', ':'))
    img = g.get('image', '').replace('"', '\\"')
    js_games.append(f'{{t:"{g["title"]}",s:"{g["slug"]}",i:"{img}",d:{g["discount"]},p:{g["cheapest_brl"]:.2f},r:"{g["cheapest_region"]}",n:{g["num_regions"]},prices:{prices_str}}}')

js_array = ',\n'.join(js_games)

# Read template and generate new HTML
html_template = '''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Nintendo Switch - Todos os Jogos | Eshop Pulse</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect fill='%23ff3b3b' width='100' height='100' rx='20'/><text x='50' y='68' font-size='50' font-weight='bold' text-anchor='middle' fill='white'>EP</text></svg>">
  <style>
    :root {
      --bg: #0a0a0f;
      --panel: rgba(255, 255, 255, 0.04);
      --panel-strong: rgba(255, 255, 255, 0.08);
      --text: #f7f7f7;
      --muted: #a7acb7;
      --accent: #ff3b3b;
      --border: rgba(255, 255, 255, 0.12);
      --radius-md: 16px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0a0a0f;
      color: var(--text);
      min-height: 100vh;
      line-height: 1.5;
    }
    .container { width: min(1200px, 95vw); margin: 0 auto; }

    /* Header */
    .topbar {
      position: sticky; top: 0; z-index: 10;
      background: #0a0a0f;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .topbar-inner {
      display: flex; align-items: center; justify-content: space-between;
      padding: 18px 0; gap: 16px;
    }
    .brand { display: flex; align-items: center; gap: 12px; text-decoration: none; color: inherit; }
    .brand-mark {
      width: 42px; height: 42px; border-radius: 8px;
      background: var(--accent);
      display: flex; align-items: center; justify-content: center;
      color: #fff; font-weight: 700;
    }
    .brand-name { font-size: 1.2rem; font-weight: 600; }
    .brand-tag { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; color: var(--muted); }
    .nav { display: flex; gap: 18px; font-size: 0.95rem; }
    .nav a { text-decoration: none; color: var(--muted); padding-bottom: 6px; position: relative; }
    .nav a.active { color: var(--text); }
    .nav a.active::after { content: ""; position: absolute; left: 0; bottom: 0; width: 100%; height: 2px; background: var(--accent); }

    /* Page Header */
    .page-header { padding: 40px 0 30px; text-align: center; }
    .page-header h1 { font-size: 2.5rem; font-weight: 700; margin-bottom: 8px; }
    .page-header p { color: var(--muted); font-size: 1rem; }

    /* Filters */
    .filters {
      background: var(--panel); border: 1px solid var(--border);
      border-radius: var(--radius-md); padding: 20px; margin-bottom: 24px;
    }
    .filter-row { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
    .filter-pill {
      display: flex; align-items: center; gap: 8px;
      padding: 10px 16px; border-radius: 999px;
      border: 1px solid var(--border); background: rgba(255, 255, 255, 0.03);
    }
    .filter-pill input, .filter-pill select {
      background: transparent; border: none; color: var(--text); outline: none;
    }
    .filter-pill input { width: 180px; }

    /* Stats */
    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    .stat-card { background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 16px; text-align: center; }
    .stat-label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: var(--muted); margin-bottom: 4px; }
    .stat-value { font-size: 1.5rem; font-weight: 600; color: var(--accent); }

    /* Games Grid */
    .games-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; margin-bottom: 40px; }
    .game-card {
      background: var(--panel); border: 1px solid var(--border);
      border-radius: 12px; padding: 16px; cursor: pointer;
      text-decoration: none; color: inherit; transition: all 0.2s;
    }
    .game-card:hover { border-color: var(--accent); transform: translateY(-2px); }

    .game-cover {
      width: 100%; height: 140px; background: #1a1a2e;
      border-radius: 8px; margin-bottom: 12px;
      overflow: hidden; position: relative;
    }
    .game-cover-img {
      width: 100%; height: 100%; object-fit: cover;
    }
    .game-cover-fallback {
      width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
      font-weight: 600; font-size: 0.85rem; text-align: center; padding: 10px;
    }
    .game-title { font-weight: 600; margin-bottom: 4px; font-size: 0.95rem; }
    .game-meta { font-size: 0.8rem; color: var(--muted); margin-bottom: 10px; }

    /* 4-Region Price Comparison */
    .price-comparison { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-bottom: 10px; }
    .region-price {
      background: rgba(255, 255, 255, 0.03); border-radius: 6px;
      padding: 8px 6px; text-align: center; font-size: 0.75rem;
    }
    .region-price.best { background: rgba(16, 185, 129, 0.2); border: 1px solid rgba(16, 185, 129, 0.4); }
    .region-flag { font-size: 0.7rem; color: var(--muted); margin-bottom: 2px; }
    .region-value { font-weight: 600; font-size: 0.85rem; }
    .region-discount { color: var(--accent); font-size: 0.7rem; }
    .region-na { color: var(--muted); font-size: 0.7rem; }

    .best-price { display: flex; align-items: center; justify-content: space-between; }
    .best-label { font-size: 0.8rem; color: var(--muted); }
    .best-value { font-size: 1.1rem; font-weight: 600; color: #10b981; }
    .badge { background: var(--accent); color: white; padding: 3px 8px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }

    /* Pagination */
    .pagination { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 30px 0 50px; flex-wrap: wrap; }
    .pagination-btn, .page-number {
      background: var(--panel); border: 1px solid var(--border);
      color: var(--text); padding: 10px 16px; border-radius: 8px;
      cursor: pointer; font-size: 0.9rem; transition: all 0.2s;
    }
    .pagination-btn:hover:not(:disabled), .page-number:hover { background: var(--panel-strong); border-color: var(--accent); }
    .pagination-btn:disabled { opacity: 0.3; cursor: not-allowed; }
    .page-number.active { background: var(--accent); border-color: var(--accent); }
    .page-ellipsis { padding: 10px 5px; color: var(--muted); }

    #loading { text-align: center; padding: 60px 20px; font-size: 1.2rem; color: var(--muted); }

    @media (max-width: 768px) {
      .stats-grid { grid-template-columns: repeat(2, 1fr); }
      .games-grid { grid-template-columns: 1fr; }
      .price-comparison { grid-template-columns: repeat(2, 1fr); }
      .nav { display: none; }
    }
  </style>
</head>
<body>
  <div class="topbar">
    <div class="container topbar-inner">
      <a href="index.html" class="brand">
        <div class="brand-mark">EP</div>
        <div>
          <div class="brand-name">Eshop Pulse</div>
          <div class="brand-tag">COMPARADOR GLOBAL DE JOGOS</div>
        </div>
      </a>
      <nav class="nav">
        <a href="index.html">Home</a>
        <a href="nintendo.html" class="active">Nintendo</a>
        <a href="playstation.html">PlayStation</a>
        <a href="xbox.html">Xbox</a>
        <a href="pc.html">PC</a>
        <a href="index.html#midias-fisicas">Midias Fisicas</a>
        <a href="index.html#destaques">Destaques</a>
      </nav>
    </div>
  </div>

  <div class="container">
    <div class="page-header">
      <h1>NINTENDO SWITCH</h1>
      <p>''' + f'{len(all_games_js):,}'.replace(',', '.') + ''' jogos com comparacao de precos em 4 regioes (BR, US, CA, MX)</p>
    </div>

    <div class="filters">
      <div class="filter-row">
        <label class="filter-pill">
          <span>Buscar:</span>
          <input type="text" id="searchInput" placeholder="Nome do jogo..." />
        </label>
        <label class="filter-pill">
          <span>Mostrar:</span>
          <select id="filterType">
            <option value="all">Todos</option>
            <option value="sale">Em promocao</option>
            <option value="4regions">4 regioes</option>
          </select>
        </label>
        <label class="filter-pill">
          <span>Ordenar:</span>
          <select id="sortBy">
            <option value="discount">Maior desconto</option>
            <option value="price-low">Menor preco</option>
            <option value="price-high">Maior preco</option>
            <option value="title">Titulo (A-Z)</option>
          </select>
        </label>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total de Jogos</div>
        <div class="stat-value" id="totalGames">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Em Promocao</div>
        <div class="stat-value" id="totalSales">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Com 4 Regioes</div>
        <div class="stat-value" id="total4Regions">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Maior Desconto</div>
        <div class="stat-value" id="maxDiscount">0%</div>
      </div>
    </div>

    <div id="loading">Carregando ''' + f'{len(all_games_js):,}'.replace(',', '.') + ''' jogos...</div>
    <div class="games-grid" id="gamesGrid" style="display: none;"></div>
    <div class="pagination" id="pagination" style="display: none;"></div>
  </div>

  <script>
    const allGames = [
''' + js_array + '''
    ];

    let filteredGames = [];
    let currentPage = 1;
    const GAMES_PER_PAGE = 24;

    function formatCurrency(value, currency) {
      if (currency === 'BRL') return 'R$ ' + value.toFixed(2);
      if (currency === 'USD') return '$' + value.toFixed(2);
      if (currency === 'CAD') return 'C$' + value.toFixed(2);
      if (currency === 'MXN') return 'MX$' + value.toFixed(2);
      return value.toFixed(2);
    }

    function loadGames() {
      filteredGames = [...allGames];
      updateStats();
      renderPage();
      document.getElementById('loading').style.display = 'none';
      document.getElementById('gamesGrid').style.display = 'grid';
      document.getElementById('pagination').style.display = 'flex';
    }

    function updateStats() {
      document.getElementById('totalGames').textContent = filteredGames.length.toLocaleString('pt-BR');
      document.getElementById('totalSales').textContent = filteredGames.filter(g => g.d > 0).length.toLocaleString('pt-BR');
      document.getElementById('total4Regions').textContent = filteredGames.filter(g => g.n >= 4).length.toLocaleString('pt-BR');
      const maxD = Math.max(...filteredGames.map(g => g.d));
      document.getElementById('maxDiscount').textContent = maxD + '%';
    }

    function renderPage() {
      const start = (currentPage - 1) * GAMES_PER_PAGE;
      const pageGames = filteredGames.slice(start, start + GAMES_PER_PAGE);

      const grid = document.getElementById('gamesGrid');
      grid.innerHTML = pageGames.map(g => {
        const regions = ['BR', 'US', 'CA', 'MX'];
        let pricesHTML = '<div class="price-comparison">';

        regions.forEach(r => {
          if (g.prices[r]) {
            const p = g.prices[r];
            const isBest = r === g.r;
            pricesHTML += '<div class="region-price' + (isBest ? ' best' : '') + '">';
            pricesHTML += '<div class="region-flag">' + r + '</div>';
            pricesHTML += '<div class="region-value">' + formatCurrency(p.sale, p.currency) + '</div>';
            if (p.discount > 0) pricesHTML += '<div class="region-discount">-' + p.discount + '%</div>';
            pricesHTML += '</div>';
          } else {
            pricesHTML += '<div class="region-price"><div class="region-flag">' + r + '</div><div class="region-na">N/A</div></div>';
          }
        });
        pricesHTML += '</div>';

        const coverHTML = g.i ?
          '<img class="game-cover-img" src="' + g.i + '" alt="' + g.t + '" loading="lazy" onerror="this.style.display=\\'none\\';this.nextElementSibling.style.display=\\'flex\\'"><div class="game-cover-fallback" style="display:none">' + g.t + '</div>' :
          '<div class="game-cover-fallback">' + g.t + '</div>';

        return '<a href="jogo-detalhes.html?id=' + g.s + '" class="game-card">' +
          '<div class="game-cover">' + coverHTML + '</div>' +
          '<div class="game-title">' + g.t + '</div>' +
          '<div class="game-meta">' + g.n + ' regioes disponiveis</div>' +
          pricesHTML +
          '<div class="best-price">' +
            '<span class="best-label">Melhor: ' + g.r + '</span>' +
            '<span class="best-value">R$ ' + g.p.toFixed(2) + '</span>' +
            (g.d > 0 ? '<span class="badge">-' + g.d + '%</span>' : '') +
          '</div>' +
        '</a>';
      }).join('');

      renderPagination();
    }

    function renderPagination() {
      const totalPages = Math.ceil(filteredGames.length / GAMES_PER_PAGE);
      const pag = document.getElementById('pagination');

      let html = '<button class="pagination-btn" onclick="goPage(currentPage-1)" ' + (currentPage === 1 ? 'disabled' : '') + '>&larr; Anterior</button>';

      if (totalPages <= 7) {
        for (let i = 1; i <= totalPages; i++) {
          html += '<button class="page-number' + (i === currentPage ? ' active' : '') + '" onclick="goPage(' + i + ')">' + i + '</button>';
        }
      } else {
        if (currentPage <= 4) {
          for (let i = 1; i <= 5; i++) html += '<button class="page-number' + (i === currentPage ? ' active' : '') + '" onclick="goPage(' + i + ')">' + i + '</button>';
          html += '<span class="page-ellipsis">...</span>';
          html += '<button class="page-number" onclick="goPage(' + totalPages + ')">' + totalPages + '</button>';
        } else if (currentPage >= totalPages - 3) {
          html += '<button class="page-number" onclick="goPage(1)">1</button>';
          html += '<span class="page-ellipsis">...</span>';
          for (let i = totalPages - 4; i <= totalPages; i++) html += '<button class="page-number' + (i === currentPage ? ' active' : '') + '" onclick="goPage(' + i + ')">' + i + '</button>';
        } else {
          html += '<button class="page-number" onclick="goPage(1)">1</button>';
          html += '<span class="page-ellipsis">...</span>';
          for (let i = currentPage - 1; i <= currentPage + 1; i++) html += '<button class="page-number' + (i === currentPage ? ' active' : '') + '" onclick="goPage(' + i + ')">' + i + '</button>';
          html += '<span class="page-ellipsis">...</span>';
          html += '<button class="page-number" onclick="goPage(' + totalPages + ')">' + totalPages + '</button>';
        }
      }

      html += '<button class="pagination-btn" onclick="goPage(currentPage+1)" ' + (currentPage === totalPages ? 'disabled' : '') + '>Proxima &rarr;</button>';
      pag.innerHTML = html;
    }

    function goPage(p) {
      const totalPages = Math.ceil(filteredGames.length / GAMES_PER_PAGE);
      if (p < 1 || p > totalPages) return;
      currentPage = p;
      renderPage();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function applyFilters() {
      const search = document.getElementById('searchInput').value.toLowerCase();
      const filterType = document.getElementById('filterType').value;
      const sortBy = document.getElementById('sortBy').value;

      filteredGames = allGames.filter(g => {
        if (search && !g.t.toLowerCase().includes(search)) return false;
        if (filterType === 'sale' && g.d === 0) return false;
        if (filterType === '4regions' && g.n < 4) return false;
        return true;
      });

      filteredGames.sort((a, b) => {
        if (sortBy === 'discount') return b.d - a.d || a.p - b.p;
        if (sortBy === 'price-low') return a.p - b.p;
        if (sortBy === 'price-high') return b.p - a.p;
        if (sortBy === 'title') return a.t.localeCompare(b.t);
        return 0;
      });

      currentPage = 1;
      updateStats();
      renderPage();
    }

    document.getElementById('searchInput').addEventListener('input', applyFilters);
    document.getElementById('filterType').addEventListener('change', applyFilters);
    document.getElementById('sortBy').addEventListener('change', applyFilters);

    loadGames();
  </script>
</body>
</html>'''

# Save HTML file
output_path = os.path.join('..', 'nintendo.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_template)

file_size = os.path.getsize(output_path) / (1024 * 1024)
print(f"\n[OK] Generated: {output_path}")
print(f"[OK] File size: {file_size:.2f} MB")
print(f"[OK] Total games: {len(all_games_js)}")

print("\n" + "="*60)
print("DONE!")
print("="*60)
