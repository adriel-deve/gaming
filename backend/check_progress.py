"""
Verificar progresso do scraper
"""
import json
import os

print("="*60)
print("PROGRESSO DO SCRAPER MULTI-REGIÃO")
print("="*60)

# Verificar arquivo de progresso
progress_file = 'noa_progress_all.json'

if os.path.exists(progress_file):
    try:
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)

        print(f"\n[OK] Arquivo de progresso encontrado!")
        print(f"\nJogos processados: {len(progress)}")

        # Contar regiões
        total_prices = sum(len(g['prices']) for g in progress)
        print(f"Total de preços coletados: {total_prices}")

        # Estatísticas por região
        region_counts = {}
        for game in progress:
            for price in game['prices']:
                region = price['region']
                region_counts[region] = region_counts.get(region, 0) + 1

        print(f"\nPreços por região:")
        for region, count in sorted(region_counts.items()):
            print(f"  {region}: {count} jogos")

        # Últimos 5 jogos processados
        print(f"\nÚltimos 5 jogos processados:")
        for i, game in enumerate(progress[-5:], start=1):
            regions = [p['region'] for p in game['prices']]
            print(f"  {i}. {game['title']} - Regiões: {', '.join(regions)}")

    except Exception as e:
        print(f"[ERRO] Não foi possível ler arquivo: {e}")
else:
    print("[AVISO] Arquivo de progresso ainda não existe")
    print("O scraper está iniciando ou não começou ainda...")

print("\n" + "="*60)
