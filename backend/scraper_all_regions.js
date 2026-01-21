/**
 * Nintendo eShop Price Scraper - ALL 27 REGIONS
 * Fetches prices from Nintendo's official API for all supported countries
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Nintendo Price API
const PRICE_API = 'https://api.ec.nintendo.com/v1/price';

// All 27 supported countries with their currencies
const ALL_REGIONS = {
    // Americas (8)
    'AR': { currency: 'ARS', name: 'Argentina' },
    'BR': { currency: 'BRL', name: 'Brasil' },
    'CA': { currency: 'CAD', name: 'Canada' },
    'CL': { currency: 'CLP', name: 'Chile' },
    'CO': { currency: 'COP', name: 'Colombia' },
    'MX': { currency: 'MXN', name: 'Mexico' },
    'PE': { currency: 'PEN', name: 'Peru' },
    'US': { currency: 'USD', name: 'United States' },

    // Europe (17)
    'AT': { currency: 'EUR', name: 'Austria' },
    'BE': { currency: 'EUR', name: 'Belgium' },
    'CH': { currency: 'CHF', name: 'Switzerland' },
    'CZ': { currency: 'CZK', name: 'Czech Republic' },
    'DE': { currency: 'EUR', name: 'Germany' },
    'DK': { currency: 'DKK', name: 'Denmark' },
    'ES': { currency: 'EUR', name: 'Spain' },
    'FR': { currency: 'EUR', name: 'France' },
    'GB': { currency: 'GBP', name: 'United Kingdom' },
    'IT': { currency: 'EUR', name: 'Italy' },
    'NL': { currency: 'EUR', name: 'Netherlands' },
    'NO': { currency: 'NOK', name: 'Norway' },
    'PL': { currency: 'PLN', name: 'Poland' },
    'PT': { currency: 'EUR', name: 'Portugal' },
    'RU': { currency: 'RUB', name: 'Russia' },
    'SE': { currency: 'SEK', name: 'Sweden' },
    'ZA': { currency: 'ZAR', name: 'South Africa' },

    // Asia Pacific (2)
    'AU': { currency: 'AUD', name: 'Australia' },
    'JP': { currency: 'JPY', name: 'Japan' },
};

// Exchange rates to BRL (January 2026)
const EXCHANGE_RATES = {
    'ARS': 0.0058,
    'AUD': 3.85,
    'BRL': 1.0,
    'CAD': 4.20,
    'CHF': 6.70,
    'CLP': 0.0062,
    'COP': 0.0015,
    'CZK': 0.26,
    'DKK': 0.85,
    'EUR': 6.35,
    'GBP': 7.45,
    'JPY': 0.039,
    'MXN': 0.32,
    'NOK': 0.55,
    'PEN': 1.55,
    'PLN': 1.48,
    'RUB': 0.065,
    'SEK': 0.56,
    'USD': 5.80,
    'ZAR': 0.32,
};

function fetchPrices(nsuids, country) {
    return new Promise((resolve, reject) => {
        const url = new URL(PRICE_API);
        url.searchParams.set('country', country);
        url.searchParams.set('lang', 'en');
        url.searchParams.set('ids', nsuids.join(','));

        const options = {
            hostname: url.hostname,
            path: url.pathname + url.search,
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        };

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
        req.setTimeout(30000, () => {
            req.destroy();
            reject(new Error('Timeout'));
        });
        req.end();
    });
}

async function fetchRegionPrices(allNsuids, regionCode, regionInfo) {
    const BATCH_SIZE = 50;
    const prices = {};

    for (let i = 0; i < allNsuids.length; i += BATCH_SIZE) {
        const batch = allNsuids.slice(i, i + BATCH_SIZE);

        try {
            const result = await fetchPrices(batch, regionCode);

            if (result && result.prices) {
                for (const priceInfo of result.prices) {
                    const nsuid = String(priceInfo.title_id);

                    let msrp = 0;
                    let salePrice = 0;
                    let onSale = false;

                    if (priceInfo.regular_price && priceInfo.regular_price.raw_value) {
                        msrp = parseFloat(String(priceInfo.regular_price.raw_value).replace(',', '.'));
                    }

                    if (priceInfo.discount_price && priceInfo.discount_price.raw_value) {
                        salePrice = parseFloat(String(priceInfo.discount_price.raw_value).replace(',', '.'));
                        onSale = true;
                    } else {
                        salePrice = msrp;
                    }

                    if (msrp > 0) {
                        prices[nsuid] = {
                            msrp,
                            salePrice,
                            discount: msrp > salePrice ? Math.round((1 - salePrice / msrp) * 100) : 0,
                            onSale,
                            currency: regionInfo.currency
                        };
                    }
                }
            }
        } catch (e) {
            // Silent continue
        }

        // Rate limiting
        await new Promise(r => setTimeout(r, 80));
    }

    return prices;
}

async function main() {
    console.log('='.repeat(70));
    console.log('NINTENDO ESHOP PRICE SCRAPER - ALL 27 REGIONS');
    console.log('='.repeat(70));
    console.log(`Date: ${new Date().toISOString()}`);
    console.log(`Regions: ${Object.keys(ALL_REGIONS).length}`);

    // Load current data
    console.log('\n[1/4] Loading current data...');
    const dataPath = path.join(__dirname, 'multi_region_enriched.json');
    const games = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    console.log(`[OK] ${games.length} games loaded`);

    // Get all NSUIDs
    const allNsuids = games.map(g => g.nsuid).filter(Boolean);
    console.log(`[OK] ${allNsuids.length} NSUIDs to check`);

    // Fetch prices for all regions
    console.log('\n[2/4] Fetching prices from all 27 regions...');
    console.log('This may take several minutes...\n');

    const allRegionPrices = {};
    const regionList = Object.entries(ALL_REGIONS);

    for (let i = 0; i < regionList.length; i++) {
        const [regionCode, regionInfo] = regionList[i];
        const startTime = Date.now();

        process.stdout.write(`  [${i + 1}/${regionList.length}] ${regionCode} (${regionInfo.name})... `);

        allRegionPrices[regionCode] = await fetchRegionPrices(allNsuids, regionCode, regionInfo);

        const count = Object.keys(allRegionPrices[regionCode]).length;
        const sales = Object.values(allRegionPrices[regionCode]).filter(p => p.onSale).length;
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

        console.log(`${count} prices (${sales} sales) [${elapsed}s]`);
    }

    // Summary
    console.log('\n[3/4] Summary of fetched prices:');
    console.log('-'.repeat(50));

    let totalPrices = 0;
    let totalSales = 0;

    for (const [region, prices] of Object.entries(allRegionPrices)) {
        const count = Object.keys(prices).length;
        const sales = Object.values(prices).filter(p => p.onSale).length;
        totalPrices += count;
        totalSales += sales;
        console.log(`  ${region}: ${count.toString().padStart(5)} prices (${sales.toString().padStart(4)} on sale)`);
    }

    console.log('-'.repeat(50));
    console.log(`  TOTAL: ${totalPrices} prices (${totalSales} on sale)`);

    // Update games
    console.log('\n[4/4] Updating games with new prices...');
    let gamesUpdated = 0;
    let pricesAdded = 0;
    let pricesUpdated = 0;

    for (const game of games) {
        const nsuid = game.nsuid;
        if (!nsuid) continue;

        let updated = false;

        // Initialize prices array if needed
        if (!game.prices) game.prices = [];

        // Update each region
        for (const [regionCode, regionPrices] of Object.entries(allRegionPrices)) {
            const priceData = regionPrices[nsuid];
            if (!priceData) continue;

            const regionInfo = ALL_REGIONS[regionCode];
            const exchangeRate = EXCHANGE_RATES[regionInfo.currency] || 1;

            // Calculate BRL equivalent
            const priceBrl = priceData.salePrice * exchangeRate;
            const msrpBrl = priceData.msrp * exchangeRate;

            // Find existing price for this region
            let existingPrice = game.prices.find(p => p.region === regionCode);

            if (existingPrice) {
                // Update existing
                existingPrice.msrp = priceData.msrp;
                existingPrice.sale_price = priceData.salePrice;
                existingPrice.discount_percent = priceData.discount;
                existingPrice.price_brl = priceBrl;
                existingPrice.msrp_brl = msrpBrl;
                existingPrice.on_sale = priceData.onSale;
                existingPrice.currency = priceData.currency;
                existingPrice.api_updated = new Date().toISOString().split('T')[0];
                pricesUpdated++;
            } else {
                // Add new
                game.prices.push({
                    region: regionCode,
                    currency: priceData.currency,
                    msrp: priceData.msrp,
                    sale_price: priceData.salePrice,
                    discount_percent: priceData.discount,
                    price_brl: priceBrl,
                    msrp_brl: msrpBrl,
                    on_sale: priceData.onSale,
                    api_updated: new Date().toISOString().split('T')[0]
                });
                pricesAdded++;
            }

            updated = true;
        }

        if (updated) gamesUpdated++;
    }

    console.log(`[OK] ${gamesUpdated} games updated`);
    console.log(`[OK] ${pricesUpdated} prices updated`);
    console.log(`[OK] ${pricesAdded} new region prices added`);

    // Save
    console.log('\nSaving...');
    fs.writeFileSync(dataPath, JSON.stringify(games, null, 2), 'utf8');
    console.log('[OK] Saved to multi_region_enriched.json');

    // Save progress file
    const progressPath = path.join(__dirname, 'all_regions_progress.json');
    fs.writeFileSync(progressPath, JSON.stringify({
        date: new Date().toISOString(),
        regionsCount: Object.keys(ALL_REGIONS).length,
        regions: Object.fromEntries(
            Object.entries(allRegionPrices).map(([r, p]) => [r, {
                count: Object.keys(p).length,
                sales: Object.values(p).filter(x => x.onSale).length
            }])
        ),
        gamesUpdated,
        pricesAdded,
        pricesUpdated
    }, null, 2), 'utf8');

    // Final statistics
    console.log('\n' + '='.repeat(70));
    console.log('FINAL STATISTICS');
    console.log('='.repeat(70));

    // Count by region
    const regionStats = {};
    for (const region of Object.keys(ALL_REGIONS)) {
        regionStats[region] = { total: 0, sales: 0 };
    }

    for (const game of games) {
        for (const price of (game.prices || [])) {
            if (regionStats[price.region]) {
                regionStats[price.region].total++;
                if (price.on_sale || price.discount_percent > 0) {
                    regionStats[price.region].sales++;
                }
            }
        }
    }

    // Find cheapest region for each game
    const cheapestRegionCount = {};
    for (const game of games) {
        let cheapest = null;
        let cheapestPrice = Infinity;

        for (const price of (game.prices || [])) {
            const brl = price.price_brl || (price.sale_price * (EXCHANGE_RATES[price.currency] || 1));
            if (brl > 0 && brl < cheapestPrice) {
                cheapestPrice = brl;
                cheapest = price.region;
            }
        }

        if (cheapest) {
            cheapestRegionCount[cheapest] = (cheapestRegionCount[cheapest] || 0) + 1;
        }
    }

    console.log('\nCheapest region distribution:');
    const sortedCheapest = Object.entries(cheapestRegionCount).sort((a, b) => b[1] - a[1]);
    for (const [region, count] of sortedCheapest.slice(0, 10)) {
        const name = ALL_REGIONS[region]?.name || region;
        console.log(`  ${region} (${name}): ${count} games`);
    }

    // Games by region count
    const byRegionCount = {};
    for (const game of games) {
        const regions = new Set((game.prices || []).map(p => p.region));
        const count = regions.size;
        byRegionCount[count] = (byRegionCount[count] || 0) + 1;
    }

    console.log('\nGames by number of regions:');
    const sortedByCount = Object.entries(byRegionCount).sort((a, b) => parseInt(b[0]) - parseInt(a[0]));
    for (const [count, games] of sortedByCount) {
        console.log(`  ${count} regions: ${games} games`);
    }

    // Sample Nintendo games
    console.log('\n' + '='.repeat(70));
    console.log('SAMPLE: ZELDA BREATH OF THE WILD - ALL REGIONS');
    console.log('='.repeat(70));

    const zelda = games.find(g => g.title.toLowerCase().includes('breath of the wild') && !g.title.toLowerCase().includes('expansion'));
    if (zelda) {
        console.log(`\n${zelda.title}:`);
        const sortedPrices = (zelda.prices || [])
            .filter(p => p.price_brl > 0)
            .sort((a, b) => a.price_brl - b.price_brl);

        for (const price of sortedPrices) {
            const name = ALL_REGIONS[price.region]?.name || price.region;
            const saleStr = price.on_sale ? ` (SALE -${price.discount_percent}%)` : '';
            console.log(`  ${price.region} (${name}): ${price.currency} ${price.msrp.toFixed(2)} -> ${price.sale_price.toFixed(2)}${saleStr} = R$ ${price.price_brl.toFixed(2)}`);
        }

        console.log(`\n  CHEAPEST: ${sortedPrices[0]?.region} at R$ ${sortedPrices[0]?.price_brl.toFixed(2)}`);
    }

    console.log('\n' + '='.repeat(70));
    console.log('DONE!');
    console.log('='.repeat(70));
}

main().catch(console.error);
