"""
Command-line interface for Foreign Gifts Tracker.
Provides easy access to analysis, search, and export functionality.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.analyzer import GiftsAnalyzer
from src.utils.classifier import GiftClassifier
from src.utils.enrichment import DataEnricher
try:
    from src.utils.visualizer import GiftsVisualizer, HAS_MATPLOTLIB
except ImportError:
    HAS_MATPLOTLIB = False

import sqlite_utils
import json


def cmd_analyze(args):
    """Run analysis and generate report."""
    analyzer = GiftsAnalyzer(args.database)

    if args.output:
        report = analyzer.generate_report(args.output)
        print(f"✓ Report saved to {args.output}")
    else:
        report = analyzer.generate_report()
        print(report)


def cmd_search(args):
    """Search for gifts."""
    analyzer = GiftsAnalyzer(args.database)

    results = analyzer.search_gifts(
        keyword=args.keyword,
        country=args.country,
        recipient=args.recipient,
        min_value=args.min_value,
        max_value=args.max_value,
        year=args.year
    )

    print(f"Found {len(results)} matching gifts:\n")

    for i, gift in enumerate(results[:args.limit], 1):
        print(f"{i}. {gift['gift_description'][:80]}")
        print(f"   From: {gift['donor_name']} ({gift['donor_country']})")
        print(f"   To: {gift['recipient_name']}")
        if gift['estimated_value']:
            print(f"   Value: ${gift['estimated_value']:,.2f}")
        print(f"   Date: {gift['received']}")
        print()


def cmd_stats(args):
    """Show summary statistics."""
    analyzer = GiftsAnalyzer(args.database)

    stats = analyzer.get_summary_statistics()

    print("\n" + "=" * 60)
    print("FOREIGN GIFTS SUMMARY STATISTICS")
    print("=" * 60)
    print(f"\nTotal Gifts: {stats['total_gifts']:,}")
    print(f"Gifts with Value Data: {stats['gifts_with_value']:,} ({stats['gifts_with_value']/stats['total_gifts']*100:.1f}%)")

    if stats['total_value']:
        print(f"\nTotal Value: ${stats['total_value']:,.2f}")
        print(f"Average Value: ${stats['average_value']:,.2f}")
        print(f"Min Value: ${stats['min_value']:,.2f}")
        print(f"Max Value: ${stats['max_value']:,.2f}")

    print(f"\nUnique Donor Countries: {stats['unique_countries']}")
    print(f"Unique Recipients: {stats['unique_recipients']}")
    print()


def cmd_top_countries(args):
    """Show top donor countries."""
    analyzer = GiftsAnalyzer(args.database)

    countries = analyzer.get_top_donor_countries(args.limit)

    print(f"\nTop {args.limit} Donor Countries:")
    print("=" * 70)
    print(f"{'Rank':<6} {'Country':<30} {'Gifts':<10} {'Total Value':<15}")
    print("-" * 70)

    for i, country in enumerate(countries, 1):
        value_str = f"${country['total_value']:,.2f}" if country['total_value'] else "N/A"
        print(f"{i:<6} {country['country']:<30} {country['gift_count']:<10} {value_str:<15}")
    print()


def cmd_top_recipients(args):
    """Show top recipients."""
    analyzer = GiftsAnalyzer(args.database)

    recipients = analyzer.get_top_recipients(args.limit)

    print(f"\nTop {args.limit} Gift Recipients:")
    print("=" * 80)
    print(f"{'Rank':<6} {'Name':<35} {'Gifts':<10} {'Total Value':<15}")
    print("-" * 80)

    for i, recipient in enumerate(recipients, 1):
        value_str = f"${recipient['total_value']:,.2f}" if recipient['total_value'] else "N/A"
        print(f"{i:<6} {recipient['name']:<35} {recipient['gift_count']:<10} {value_str:<15}")
    print()


def cmd_valuable(args):
    """Show most valuable gifts."""
    analyzer = GiftsAnalyzer(args.database)

    gifts = analyzer.get_most_valuable_gifts(args.limit)

    print(f"\n{args.limit} Most Valuable Gifts:")
    print("=" * 80)

    for i, gift in enumerate(gifts, 1):
        print(f"\n{i}. ${gift['estimated_value']:,.2f}")
        print(f"   Description: {gift['gift_description']}")
        print(f"   From: {gift['donor_name']} ({gift['donor_country']})")
        print(f"   To: {gift['recipient_name']}")
        print(f"   Date: {gift['received']}")
    print()


def cmd_categories(args):
    """Show gift categories."""
    analyzer = GiftsAnalyzer(args.database)

    categories = analyzer.get_gift_categories()

    print("\nGift Categories:")
    print("=" * 50)
    print(f"{'Category':<25} {'Count':<10}")
    print("-" * 50)

    for category, count in categories.items():
        print(f"{category.capitalize():<25} {count:<10}")
    print()


def cmd_classify(args):
    """Classify a gift description."""
    classifier = GiftClassifier()

    result = classifier.classify(args.description)
    materials = classifier.extract_materials(args.description)
    ceremonial = classifier.is_ceremonial(args.description)

    print(f"\nClassification for: {args.description}")
    print("=" * 80)
    print(f"Category: {result['category_name']}")
    if result['subcategory']:
        print(f"Subcategory: {result['subcategory']}")
    print(f"Confidence: {result['confidence']:.1%}")

    if materials:
        print(f"Materials Detected: {', '.join(materials)}")

    if ceremonial:
        print("Type: Ceremonial/Formal")
    print()


def cmd_export(args):
    """Export data to various formats."""
    db = sqlite_utils.Database(args.database)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == 'csv':
        # Export to CSV
        with open(output_path, 'w') as f:
            db["gifts"].rows_where(order_by="id").write_csv(f)
        print(f"✓ Exported to CSV: {output_path}")

    elif args.format == 'json':
        # Export to JSON
        data = list(db["gifts"].rows)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Exported to JSON: {output_path}")

    elif args.format == 'jsonl':
        # Export to JSON Lines
        with open(output_path, 'w') as f:
            for row in db["gifts"].rows:
                f.write(json.dumps(row) + '\n')
        print(f"✓ Exported to JSON Lines: {output_path}")


def cmd_visualize(args):
    """Create visualizations."""
    if not HAS_MATPLOTLIB:
        print("Error: matplotlib is required for visualization.")
        print("Install with: pip install matplotlib seaborn")
        return

    visualizer = GiftsVisualizer(args.database)

    if args.type == 'all' or args.type == 'dashboard':
        print("Creating dashboard...")
        path = visualizer.create_dashboard()
        print(f"✓ Dashboard saved to {path}")

    if args.type == 'all' or args.type == 'countries':
        print("Creating top countries chart...")
        path = visualizer.plot_top_donor_countries()
        print(f"✓ Countries chart saved to {path}")

    if args.type == 'all' or args.type == 'values':
        print("Creating value distribution chart...")
        path = visualizer.plot_value_distribution()
        print(f"✓ Value chart saved to {path}")

    if args.type == 'all' or args.type == 'timeline':
        print("Creating timeline chart...")
        path = visualizer.plot_gifts_over_time()
        print(f"✓ Timeline chart saved to {path}")

    if args.type == 'all' or args.type == 'recipients':
        print("Creating recipients chart...")
        path = visualizer.plot_recipient_analysis()
        print(f"✓ Recipients chart saved to {path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Foreign Gifts Tracker - Analyze foreign gifts to U.S. officials',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--database',
        default='data/output/gifts.db',
        help='Path to SQLite database (default: data/output/gifts.db)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Generate comprehensive analysis report')
    analyze_parser.add_argument('--output', help='Output file path')
    analyze_parser.set_defaults(func=cmd_analyze)

    # search command
    search_parser = subparsers.add_parser('search', help='Search for gifts')
    search_parser.add_argument('--keyword', help='Search in gift description')
    search_parser.add_argument('--country', help='Filter by donor country')
    search_parser.add_argument('--recipient', help='Filter by recipient name')
    search_parser.add_argument('--min-value', type=float, help='Minimum value')
    search_parser.add_argument('--max-value', type=float, help='Maximum value')
    search_parser.add_argument('--year', help='Filter by year')
    search_parser.add_argument('--limit', type=int, default=10, help='Max results (default: 10)')
    search_parser.set_defaults(func=cmd_search)

    # stats command
    stats_parser = subparsers.add_parser('stats', help='Show summary statistics')
    stats_parser.set_defaults(func=cmd_stats)

    # top-countries command
    countries_parser = subparsers.add_parser('top-countries', help='Show top donor countries')
    countries_parser.add_argument('--limit', type=int, default=10, help='Number to show (default: 10)')
    countries_parser.set_defaults(func=cmd_top_countries)

    # top-recipients command
    recipients_parser = subparsers.add_parser('top-recipients', help='Show top recipients')
    recipients_parser.add_argument('--limit', type=int, default=10, help='Number to show (default: 10)')
    recipients_parser.set_defaults(func=cmd_top_recipients)

    # valuable command
    valuable_parser = subparsers.add_parser('valuable', help='Show most valuable gifts')
    valuable_parser.add_argument('--limit', type=int, default=10, help='Number to show (default: 10)')
    valuable_parser.set_defaults(func=cmd_valuable)

    # categories command
    categories_parser = subparsers.add_parser('categories', help='Show gift categories')
    categories_parser.set_defaults(func=cmd_categories)

    # classify command
    classify_parser = subparsers.add_parser('classify', help='Classify a gift description')
    classify_parser.add_argument('description', help='Gift description to classify')
    classify_parser.set_defaults(func=cmd_classify)

    # export command
    export_parser = subparsers.add_parser('export', help='Export data to file')
    export_parser.add_argument('--format', choices=['csv', 'json', 'jsonl'], default='csv', help='Output format')
    export_parser.add_argument('--output', required=True, help='Output file path')
    export_parser.set_defaults(func=cmd_export)

    # visualize command
    viz_parser = subparsers.add_parser('visualize', help='Create visualizations')
    viz_parser.add_argument('--type', choices=['all', 'dashboard', 'countries', 'values', 'timeline', 'recipients'],
                           default='dashboard', help='Type of visualization')
    viz_parser.set_defaults(func=cmd_visualize)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Run the appropriate command
    args.func(args)


if __name__ == '__main__':
    main()
