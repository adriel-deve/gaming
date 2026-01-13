/**
 * Nintendo Switch eShop Multi-Region Price Scraper
 * Busca preços de jogos em múltiplas regiões para comparação
 */

const { getGamesAmerica, getGamesBrazil } = require('nintendo-switch-eshop');
const fs = require('fs');

// Taxas de conversão para BRL (atualizadas)
const CURRENCY_RATES = {
    USD: 5.80,  // Estados Unidos
    CAD: 4.20,  // Canadá
    MXN: 0.32,  // México
    BRL: 1.00,  // Brasil
    ARS: 0.0062, // Argentina
    CLP: 0.0062, // Chile
    COP: 0.0014, // Colômbia
    PEN: 1.55,  // Peru
    EUR: 6.20,  // Europa
    GBP: 7.20,  // Reino Unido
    JPY: 0.039, // Japão
    AUD: 3.60,  // Austrália
    NZD: 3.40,  // Nova Zelândia
    HKD: 0.74,  // Hong Kong
    KRW: 0.0043, // Coreia do Sul
    ZAR: 0.31,  // África do Sul
    RUB: 0.063, // Rússia
    CHF: 6.50,  // Suíça
    SEK: 0.54,  // Suécia
    NOK: 0.53,  // Noruega
    DKK: 0.83,  // Dinamarca
    PLN: 1.45,  // Polônia
    CZK: 0.25,  // República Tcheca
};

// Mapeamento de regiões disponíveis na biblioteca
const REGIONS = {
    US: { name: 'Estados Unidos', currency: 'USD', fetchFunction: () => getGamesAmerica() },
    BR: { name: 'Brasil', currency: 'BRL', fetchFunction: () => getGamesBrazil() },
};

/**
 * Buscar jogos de uma região específica
 */
async function fetchRegionGames(regionCode) {
    const region = REGIONS[regionCode];
    console.log(`\n========================================`);
    console.log(`Buscando jogos - ${region.name} (${regionCode})`);
    console.log(`========================================\n`);

    try {
        const games = await region.fetchFunction();
        console.log(`  ✓ Encontrados ${games.length} jogos em ${region.name}`);

        const processedGames = [];
        for (const game of games) {
            if (game.msrp && game.msrp > 0) {
                const salePrice = game.salePrice || game.msrp;
                const hasDiscount = game.salePrice && game.salePrice < game.msrp;
                const discount = hasDiscount ? Math.round((1 - game.salePrice / game.msrp) * 100) : 0;

                processedGames.push({
                    nsuid: game.nsuid,
                    title: game.title,
                    slug: game.slug,
                    region: regionCode,
                    currency: region.currency,
                    msrp: game.msrp,
                    sale_price: salePrice,
                    discount_percent: discount,
                    msrp_brl: game.msrp * CURRENCY_RATES[region.currency],
                    price_brl: salePrice * CURRENCY_RATES[region.currency],
                });
            }
        }

        console.log(`  ✓ Processados ${processedGames.length} jogos com preço\n`);
        return processedGames;

    } catch (error) {
        console.error(`  ✗ Erro ao buscar jogos de ${region.name}:`, error.message);
        return [];
    }
}

/**
 * Combinar preços de múltiplas regiões por jogo
 */
function mergePricesByGame(allRegionGames) {
    console.log('\n========================================');
    console.log('Combinando preços por jogo...');
    console.log('========================================\n');

    const gamesByNsuid = new Map();
    const gamesByTitle = new Map();

    // Primeiro passo: agrupar por NSUID
    for (const game of allRegionGames) {
        if (game.nsuid) {
            if (!gamesByNsuid.has(game.nsuid)) {
                gamesByNsuid.set(game.nsuid, {
                    nsuid: game.nsuid,
                    title: game.title,
                    slug: game.slug,
                    prices: []
                });
            }
            gamesByNsuid.get(game.nsuid).prices.push({
                region: game.region,
                currency: game.currency,
                msrp: game.msrp,
                sale_price: game.sale_price,
                discount_percent: game.discount_percent,
                msrp_brl: game.msrp_brl,
                price_brl: game.price_brl
            });
        }
    }

    // Segundo passo: jogos sem NSUID, tentar por título
    for (const game of allRegionGames) {
        if (!game.nsuid && game.title) {
            const normalizedTitle = game.title.toLowerCase().trim();
            if (!gamesByTitle.has(normalizedTitle)) {
                gamesByTitle.set(normalizedTitle, {
                    title: game.title,
                    slug: game.slug,
                    prices: []
                });
            }
            gamesByTitle.get(normalizedTitle).prices.push({
                region: game.region,
                currency: game.currency,
                msrp: game.msrp,
                sale_price: game.sale_price,
                discount_percent: game.discount_percent,
                msrp_brl: game.msrp_brl,
                price_brl: game.price_brl
            });
        }
    }

    // Converter para array
    const gamesWithMultiRegion = [];

    for (const [nsuid, game] of gamesByNsuid) {
        if (game.prices.length > 1) { // Somente jogos com preços em múltiplas regiões
            gamesWithMultiRegion.push(game);
        }
    }

    for (const [, game] of gamesByTitle) {
        if (game.prices.length > 1) {
            gamesWithMultiRegion.push(game);
        }
    }

    console.log(`  ✓ Encontrados ${gamesWithMultiRegion.length} jogos com preços em múltiplas regiões\n`);
    return gamesWithMultiRegion;
}

/**
 * Main
 */
async function main() {
    console.log('============================================================');
    console.log('MULTI-REGION PRICE SCRAPER');
    console.log('============================================================');

    const allRegionGames = [];

    // Buscar de cada região
    for (const regionCode of Object.keys(REGIONS)) {
        const games = await fetchRegionGames(regionCode);
        allRegionGames.push(...games);

        // Aguardar um pouco entre requisições para não sobrecarregar
        await new Promise(resolve => setTimeout(resolve, 2000));
    }

    console.log('\n============================================================');
    console.log(`TOTAL: ${allRegionGames.length} registros de preços coletados`);
    console.log('============================================================\n');

    // Combinar por jogo
    const gamesPriceComparison = mergePricesByGame(allRegionGames);

    // Salvar resultado
    const outputPath = 'multi_region_prices.json';
    fs.writeFileSync(outputPath, JSON.stringify(gamesPriceComparison, null, 2));

    console.log(`\n✓ Dados salvos em: ${outputPath}`);
    console.log(`✓ Total de jogos com comparação: ${gamesPriceComparison.length}`);

    // Estatísticas
    const gamesBy2Regions = gamesPriceComparison.filter(g => g.prices.length === 2).length;
    const gamesBy3Regions = gamesPriceComparison.filter(g => g.prices.length === 3).length;
    console.log(`\n📊 Estatísticas:`);
    console.log(`   - Jogos em 2 regiões: ${gamesBy2Regions}`);
    console.log(`   - Jogos em 3 regiões: ${gamesBy3Regions}`);

    // Mostrar exemplos
    console.log(`\n📋 Exemplos de jogos com múltiplas regiões:\n`);
    gamesPriceComparison.slice(0, 5).forEach((game, i) => {
        console.log(`${i + 1}. ${game.title}`);
        game.prices.forEach(p => {
            const priceText = p.discount_percent > 0
                ? `R$ ${p.price_brl.toFixed(2)} (-${p.discount_percent}%)`
                : `R$ ${p.price_brl.toFixed(2)}`;
            console.log(`   ${p.region}: ${priceText}`);
        });
        console.log('');
    });
}

// Executar
main().catch(error => {
    console.error('Erro fatal:', error);
    process.exit(1);
});
