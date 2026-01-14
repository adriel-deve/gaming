/**
 * Nintendo Switch eShop Scraper - 27 PAÍSES
 * Usando biblioteca + API Nintendo Search
 */

const { getGamesAmerica, getGamesBrazil } = require('nintendo-switch-eshop');
const https = require('https');
const fs = require('fs');

// Taxas de conversão para BRL
const RATES = {
    USD: 5.80, CAD: 4.20, MXN: 0.32, BRL: 1.00, ARS: 0.0062,
    CLP: 0.0062, COP: 0.0014, PEN: 1.55, EUR: 6.20, GBP: 7.20,
    CHF: 6.50, SEK: 0.54, NOK: 0.53, DKK: 0.83, PLN: 1.45,
    CZK: 0.25, RUB: 0.063, JPY: 0.039, AUD: 3.60, NZD: 3.40,
    HKD: 0.74, KRW: 0.0043, ZAR: 0.31,
};

/**
 * Buscar preços via API Nintendo Search (US Algolia)
 */
async function searchGamePricesByTitle(titles, region = 'US') {
    console.log(`\nBuscando preços via Nintendo Search API (${region})...`);

    const allPrices = [];

    for (let i = 0; i < Math.min(titles.length, 100); i++) {
        const title = titles[i];

        try {
            // URL da API de busca da Nintendo (US)
            const query = encodeURIComponent(title);
            const url = `https://u3b6gr4ua3-dsn.algolia.net/1/indexes/ncom_game_en_us/query`;

            const postData = JSON.stringify({
                params: `query=${query}&hitsPerPage=1`
            });

            const options = {
                hostname: 'u3b6gr4ua3-dsn.algolia.net',
                path: '/1/indexes/ncom_game_en_us/query',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Algolia-API-Key': '9a20c93440cf63cf1a7008d75f7438bf',
                    'X-Algolia-Application-Id': 'U3B6GR4UA3'
                }
            };

            const result = await new Promise((resolve, reject) => {
                const req = https.request(options, (res) => {
                    let data = '';
                    res.on('data', chunk => data += chunk);
                    res.on('end', () => {
                        try {
                            resolve(JSON.parse(data));
                        } catch (e) {
                            reject(e);
                        }
                    });
                });
                req.on('error', reject);
                req.write(postData);
                req.end();
            });

            if (result.hits && result.hits.length > 0) {
                const game = result.hits[0];
                const msrp = parseFloat(game.msrp || 0);
                const salePrice = parseFloat(game.salePrice || msrp);

                if (msrp > 0) {
                    const discount = salePrice < msrp ? Math.round((1 - salePrice / msrp) * 100) : 0;

                    allPrices.push({
                        title: game.title,
                        nsuid: game.nsuid,
                        slug: game.url,
                        region: region,
                        currency: 'USD',
                        msrp: msrp,
                        sale_price: salePrice,
                        discount_percent: discount,
                        msrp_brl: msrp * RATES.USD,
                        price_brl: salePrice * RATES.USD
                    });

                    if ((i + 1) % 10 === 0) {
                        console.log(`  Processados ${i + 1}/${titles.length} jogos`);
                    }
                }
            }

            // Rate limiting
            await new Promise(resolve => setTimeout(resolve, 300));

        } catch (error) {
            // Ignorar erros silenciosamente
        }
    }

    console.log(`  [OK] ${allPrices.length} preços encontrados`);
    return allPrices;
}

/**
 * Combinar dados
 */
function mergeData(usGames, brGames) {
    console.log('\n========================================');
    console.log('COMBINANDO DADOS...');
    console.log('========================================');

    const gamesMap = new Map();

    // Adicionar jogos US
    for (const game of usGames) {
        const key = game.nsuid || game.title;
        if (!gamesMap.has(key)) {
            gamesMap.set(key, {
                title: game.title,
                nsuid: game.nsuid,
                slug: game.slug || game.game_id,
                prices: []
            });
        }

        gamesMap.get(key).prices.push({
            region: 'US',
            currency: 'USD',
            msrp: game.msrp,
            sale_price: game.sale_price,
            discount_percent: game.discount_percent,
            msrp_brl: game.msrp_brl,
            price_brl: game.price_brl
        });
    }

    // Adicionar jogos BR
    for (const game of brGames) {
        const key = game.nsuid || game.title;
        if (!gamesMap.has(key)) {
            gamesMap.set(key, {
                title: game.title,
                nsuid: game.nsuid,
                slug: game.slug || game.game_id,
                prices: []
            });
        }

        gamesMap.get(key).prices.push({
            region: 'BR',
            currency: 'BRL',
            msrp: game.msrp,
            sale_price: game.sale_price,
            discount_percent: game.discount_percent,
            msrp_brl: game.msrp,
            price_brl: game.sale_price
        });
    }

    const merged = Array.from(gamesMap.values());
    console.log(`  [OK] ${merged.length} jogos únicos`);
    console.log(`  [OK] ${merged.filter(g => g.prices.length > 1).length} jogos multi-região`);

    return merged;
}

/**
 * Main
 */
async function main() {
    console.log('============================================================');
    console.log('SCRAPER NINTENDO SWITCH - US + BR (REAL PRICES)');
    console.log('============================================================\n');

    // Fase 1: Buscar US
    console.log('[FASE 1] Buscando jogos dos EUA...');
    const usGames = await getGamesAmerica();
    const usProcessed = [];

    for (const game of usGames) {
        if (game.msrp && game.msrp > 0) {
            const salePrice = game.salePrice || game.msrp;
            const discount = game.salePrice && game.salePrice < game.msrp
                ? Math.round((1 - game.salePrice / game.msrp) * 100)
                : 0;

            usProcessed.push({
                title: game.title,
                nsuid: game.nsuid,
                slug: game.slug,
                game_id: game.slug,
                region: 'US',
                currency: 'USD',
                msrp: game.msrp,
                sale_price: salePrice,
                discount_percent: discount,
                msrp_brl: game.msrp * RATES.USD,
                price_brl: salePrice * RATES.USD
            });
        }
    }
    console.log(`  [OK] ${usProcessed.length} jogos processados\n`);

    // Fase 2: Buscar BR
    console.log('[FASE 2] Buscando jogos do Brasil...');
    const brGames = await getGamesBrazil();
    const brProcessed = [];

    for (const game of brGames) {
        if (game.msrp && game.msrp > 0) {
            const salePrice = game.salePrice || game.msrp;
            const discount = game.salePrice && game.salePrice < game.msrp
                ? Math.round((1 - game.salePrice / game.msrp) * 100)
                : 0;

            brProcessed.push({
                title: game.title,
                nsuid: game.nsuid,
                slug: game.slug,
                game_id: game.slug,
                region: 'BR',
                currency: 'BRL',
                msrp: game.msrp,
                sale_price: salePrice,
                discount_percent: discount,
                msrp_brl: game.msrp,
                price_brl: salePrice
            });
        }
    }
    console.log(`  [OK] ${brProcessed.length} jogos processados\n`);

    // Combinar
    const merged = mergeData(usProcessed, brProcessed);

    // Salvar
    const output = 'all_27_countries_prices.json';
    fs.writeFileSync(output, JSON.stringify(merged, null, 2));

    console.log('\n============================================================');
    console.log(`CONCLUIDO!`);
    console.log(`  Total: ${merged.length} jogos`);
    console.log(`  Multi-região: ${merged.filter(g => g.prices.length > 1).length} jogos`);
    console.log(`  Arquivo: ${output}`);
    console.log('============================================================\n');

    // Mostrar exemplos
    console.log('EXEMPLOS DE COMPARAÇÃO:\n');
    const examples = merged.filter(g => g.prices.length > 1).slice(0, 10);

    for (const game of examples) {
        console.log(`${game.title}`);
        const sorted = game.prices.sort((a, b) => a.price_brl - b.price_brl);
        for (const p of sorted) {
            const disc = p.discount_percent > 0 ? ` (-${p.discount_percent}%)` : '';
            const best = p === sorted[0] ? ' <- MAIS BARATO' : '';
            console.log(`  ${p.region}: R$ ${p.price_brl.toFixed(2)}${disc}${best}`);
        }
        if (sorted.length > 1) {
            const savings = sorted[sorted.length - 1].price_brl - sorted[0].price_brl;
            console.log(`  Economia: R$ ${savings.toFixed(2)}\n`);
        }
    }
}

main().catch(error => {
    console.error('ERRO:', error);
    process.exit(1);
});
