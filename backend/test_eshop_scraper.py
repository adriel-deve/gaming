#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para o Nintendo eShop scraper
Usage: python test_eshop_scraper.py [--regions US BR JP] [--limit 10]
"""
import argparse
import json
import sys
from pathlib import Path
from providers.nintendo_eshop_provider import NintendoEshopScraper, ESHOP_REGIONS

# Configura encoding para UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description="Test Nintendo eShop scraper")
    parser.add_argument(
        "--regions",
        nargs="+",
        default=["US", "BR"],
        help="List of region codes (e.g., US BR JP)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of games per region"
    )
    parser.add_argument(
        "--query",
        type=str,
        default="",
        help="Search query (optional)"
    )
    parser.add_argument(
        "--show-regions",
        action="store_true",
        help="Show all available regions and exit"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Save results to JSON file"
    )

    args = parser.parse_args()

    if args.show_regions:
        print("\nAvailable regions:")
        print("-" * 50)
        for code, info in sorted(ESHOP_REGIONS.items()):
            print(f"  {code:3s} - {info['name']:25s} ({info['currency']})")
        print(f"\nTotal: {len(ESHOP_REGIONS)} regions")
        return

    # Valida regiões
    invalid_regions = [r for r in args.regions if r not in ESHOP_REGIONS]
    if invalid_regions:
        print(f"Error: Invalid regions: {', '.join(invalid_regions)}")
        print(f"Use --show-regions to see available regions")
        return

    print(f"\nTesting Nintendo eShop Scraper")
    print(f"Regions: {', '.join(args.regions)}")
    print(f"Limit per region: {args.limit}")
    if args.query:
        print(f"Search query: '{args.query}'")
    print("-" * 60)

    # Cria scraper e executa
    scraper = NintendoEshopScraper(regions=args.regions, rate_limit_delay=0.5)
    items = scraper.scrape_all_regions(query=args.query, limit_per_region=args.limit)

    # Mostra resultados
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    # Agrupa por região
    by_region = {}
    for item in items:
        region = item["region"]
        if region not in by_region:
            by_region[region] = []
        by_region[region].append(item)

    for region in args.regions:
        region_items = by_region.get(region, [])
        print(f"\n{ESHOP_REGIONS[region]['name']} ({region}) - {len(region_items)} items")
        print("-" * 60)

        # Mostra primeiros 5 itens
        for item in region_items[:5]:
            title = item["title"][:40]
            price = item.get("msrp") or item.get("sale_price")
            currency = item["currency"]
            discount = item.get("discount_percent", 0)

            price_str = f"{currency} {price:.2f}" if price else "N/A"
            discount_str = f"(-{discount}%)" if discount > 0 else ""

            print(f"  • {title:42s} {price_str:12s} {discount_str}")

        if len(region_items) > 5:
            print(f"  ... and {len(region_items) - 5} more")

    # Estatísticas
    print("\n" + "=" * 60)
    print("STATISTICS")
    print("=" * 60)
    total = len(items)
    with_prices = len([i for i in items if i.get("msrp") or i.get("sale_price")])
    on_sale = len([i for i in items if i.get("discount_percent", 0) > 0])

    print(f"Total items: {total}")
    if total > 0:
        print(f"Items with prices: {with_prices} ({with_prices/total*100:.1f}%)")
        print(f"Items on sale: {on_sale} ({on_sale/total*100:.1f}%)")
    else:
        print("No items found.")

    if on_sale > 0:
        discounts = [i["discount_percent"] for i in items if i.get("discount_percent", 0) > 0]
        avg_discount = sum(discounts) / len(discounts)
        max_discount = max(discounts)
        print(f"Average discount: {avg_discount:.1f}%")
        print(f"Maximum discount: {max_discount:.0f}%")

    # Salva em arquivo se solicitado
    if args.output:
        output_path = Path(args.output)
        output_data = {
            "scraped_at": items[0]["last_updated"] if items else None,
            "total_items": len(items),
            "regions": args.regions,
            "items": items
        }
        output_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nResults saved to: {output_path}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
