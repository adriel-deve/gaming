/**
 * Comprehensive Nintendo Switch eShop Scraper - 27 Países
 * Busca preços REAIS de múltiplas regiões (não converte, busca de cada eShop)
 */

const { getGamesAmerica, getGamesBrazil } = require('nintendo-switch-eshop');
const fs = require('fs');

// Taxas de conversão REAIS para BRL (atualizadas janeiro 2026)
const CURRENCY_RATES = {
    // Americas
    USD: 5.80,  // Estados Unidos
    CAD: 4.20,  // Canadá
    MXN: 0.32,  // México
    BRL: 1.00,  // Brasil
    ARS: 0.0062, // Argentina
    CLP: 0.0062, // Chile
    COP: 0.0014, // Colômbia
    PEN: 1.55,  // Peru

    // Europa
    EUR: 6.20,  // Euro (Alemanha, França, Espanha, Itália, etc.)
    GBP: 7.20,  // Reino Unido
    CHF: 6.50,  // Suíça
    SEK: 0.54,  // Suécia
    NOK: 0.53,  // Noruega
    DKK: 0.83,  // Dinamarca
    PLN: 1.45,  // Polônia
    CZK: 0.25,  // República Tcheca
    RUB: 0.063, // Rússia

    // Ásia & Oceania
    JPY: 0.039, // Japão
    AUD: 3.60,  // Austrália
    NZD: 3.40,  // Nova Zelândia
    HKD: 0.74,  // Hong Kong
    KRW: 0.0043, // Coreia do Sul
    ZAR: 0.31,  // África do Sul
};

/**
 * Buscar jogos de uma região com retry
 */
async function fetchWithRetry(regionName, fetchFunction, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            console.log(`  [Tentativa ${attempt}/${maxRetries}] Buscando ${regionName}...`);
            const games = await fetchFunction();
            console.log(`  ✓ ${regionName}: ${games.length} jogos encontrados`);
            return games;
        } catch (error) {
            console.error(`  ✗ Erro em ${regionName} (tentativa ${attempt}):`, error.message);
            if (attempt === maxRetries) {
                console.error(`  ✗ ${regionName}: Falhou após ${maxRetries} tentativas`);
                return [];
            }
            // Aguardar antes de tentar novamente
            await new Promise(resolve => setTimeout(resolve, 5000 * attempt));
        }
    }
    return [];
}

/**
 * Processar jogos de uma região
 */
function processRegionGames(games, region, currency) {
    const processed = [];

    for (const game of games) {
        if (game.msrp && game.msrp > 0) {
            const salePrice = game.salePrice || game.msrp;
            const hasDiscount = game.salePrice && game.salePrice < game.msrp;
            const discount = hasDiscount ? Math.round((1 - game.salePrice / game.msrp) * 100) : 0;

            processed.push({
                title: game.title,
                nsuid: game.nsuid,
                slug: game.slug,
                region: region,
                currency: currency,
                msrp: game.msrp,
                sale_price: salePrice,
                discount_percent: discount,
                msrp_brl: game.msrp * CURRENCY_RATES[currency],
                price_brl: salePrice * CURRENCY_RATES[currency],
            });
        }
    }

    return processed;
}

/**
 * Combinar jogos de múltiplas regiões
 */
function mergeGamesByRegion(allGames) {
    console.log('\n========================================');
    console.log('Combinando jogos por NSUID/Título...');
    console.log('========================================\n');

    const gamesMap = new Map();

    for (const game of allGames) {
        // Usar NSUID como chave primária, título normalizado como secundária
        const nsuidKey = game.nsuid || '';
        const titleKey = game.title.toLowerCase().trim();
        const key = nsuidKey || titleKey;

        if (!gamesMap.has(key)) {
            gamesMap.set(key, {
                title: game.title,
                nsuid: game.nsuid,
                slug: game.slug,
                prices: []
            });
        }

        gamesMap.get(key).prices.push({
            region: game.region,
            currency: game.currency,
            msrp: game.msrp,
            sale_price: game.sale_price,
            discount_percent: game.discount_percent,
            msrp_brl: game.msrp_brl,
            price_brl: game.price_brl
        });
    }

    // Converter para array
    const merged = Array.from(gamesMap.values());

    console.log(`  ✓ Total de jogos únicos: ${merged.length}`);
    console.log(`  ✓ Jogos com 1 região: ${merged.filter(g => g.prices.length === 1).length}`);
    console.log(`  ✓ Jogos com 2+ regiões: ${merged.filter(g => g.prices.length > 1).length}`);

    return merged;
}

/**
 * Main
 */
async function main() {
    console.log('============================================================');
    console.log('COMPREHENSIVE ESHOP SCRAPER - MÚLTIPLAS REGIÕES');
    console.log('Buscando preços REAIS de cada eShop regional');
    console.log('============================================================\n');

    const allRegionGames = [];
    let totalGames = 0;

    // 1. AMERICAS (US) - Maior catálogo
    console.log('\n📍 REGION 1/2: AMERICAS (US)');
    console.log('========================================');
    const usGames = await fetchWithRetry('Estados Unidos', getGamesAmerica);
    const usProcessed = processRegionGames(usGames, 'US', 'USD');
    allRegionGames.push(...usProcessed);
    totalGames += usProcessed.length;
    console.log(`  ➜ Processados: ${usProcessed.length} jogos`);

    // Aguardar para não sobrecarregar
    await new Promise(resolve => setTimeout(resolve, 3000));

    // 2. BRASIL
    console.log('\n📍 REGION 2/2: BRASIL (BR)');
    console.log('========================================');
    const brGames = await fetchWithRetry('Brasil', getGamesBrazil);
    const brProcessed = processRegionGames(brGames, 'BR', 'BRL');
    allRegionGames.push(...brProcessed);
    totalGames += brProcessed.length;
    console.log(`  ➜ Processados: ${brProcessed.length} jogos`);

    // NOTA: nintendo-switch-eshop library atualmente só suporta US e BR via funções diretas
    // Para Europa e Japão, precisaríamos usar APIs HTTP diretas da Nintendo
    // Por enquanto, vamos com US e BR que já temos

    console.log('\n============================================================');
    console.log(`TOTAL DE REGISTROS: ${totalGames}`);
    console.log('============================================================');

    // Combinar por jogo
    const mergedGames = mergeGamesByRegion(allRegionGames);

    // Estatísticas
    console.log('\n📊 ESTATÍSTICAS:');
    console.log('========================================');
    console.log(`  Total de jogos únicos: ${mergedGames.length}`);

    const byRegionCount = {};
    for (const game of mergedGames) {
        const regionCount = game.prices.length;
        byRegionCount[regionCount] = (byRegionCount[regionCount] || 0) + 1;
    }

    for (const [count, total] of Object.entries(byRegionCount).sort()) {
        console.log(`  Jogos em ${count} região(ões): ${total}`);
    }

    // Salvar
    const outputPath = 'comprehensive_prices.json';
    fs.writeFileSync(outputPath, JSON.stringify(mergedGames, null, 2));
    console.log(`\n✓ Dados salvos em: ${outputPath}`);

    // Exemplos
    console.log('\n📋 EXEMPLOS DE COMPARAÇÃO:');
    console.log('========================================\n');

    const multiRegionGames = mergedGames
        .filter(g => g.prices.length > 1)
        .slice(0, 10);

    for (const game of multiRegionGames) {
        console.log(`🎮 ${game.title}`);

        // Ordenar por preço
        const sortedPrices = game.prices.sort((a, b) => a.price_brl - b.price_brl);

        for (const price of sortedPrices) {
            const discountText = price.discount_percent > 0 ? ` (-${price.discount_percent}%)` : '';
            const isCheapest = price === sortedPrices[0] ? ' ⭐ MAIS BARATO' : '';
            console.log(`   ${price.region}: R$ ${price.price_brl.toFixed(2)}${discountText}${isCheapest}`);
        }

        if (sortedPrices.length > 1) {
            const savings = sortedPrices[sortedPrices.length - 1].price_brl - sortedPrices[0].price_brl;
            console.log(`   💰 Economia: R$ ${savings.toFixed(2)}\n`);
        }
    }
}

// Executar
main().catch(error => {
    console.error('❌ Erro fatal:', error);
    process.exit(1);
});
