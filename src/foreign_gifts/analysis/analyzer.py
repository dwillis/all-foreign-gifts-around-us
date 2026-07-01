"""
Data analysis module for Foreign Gifts Tracker.
Provides statistical analysis, insights, and trend detection.
"""

import sqlite3
import sqlite_utils
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import json
from pathlib import Path


class GiftsAnalyzer:
    """Analyzes foreign gifts data to extract insights and patterns."""

    def __init__(self, db_path: str = "data/gifts.db"):
        """
        Initialize analyzer with database connection.

        Args:
            db_path: Path to SQLite database
        """
        self.db = sqlite_utils.Database(db_path)
        self.db.conn.row_factory = sqlite3.Row
        self.gifts_table = self.db["gifts"]

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get overall summary statistics.

        Returns:
            Dictionary with key statistics
        """
        total_gifts = self.gifts_table.count

        # Value statistics
        value_query = """
            SELECT
                COUNT(estimated_value) as count_with_value,
                AVG(estimated_value) as avg_value,
                MIN(estimated_value) as min_value,
                MAX(estimated_value) as max_value,
                SUM(estimated_value) as total_value
            FROM gifts
            WHERE estimated_value IS NOT NULL
        """
        value_stats = list(self.db.execute(value_query))[0]

        # Country statistics
        country_count = len(list(self.db.execute(
            "SELECT DISTINCT donor_country FROM gifts WHERE donor_country IS NOT NULL"
        )))

        # Recipient statistics
        recipient_count = len(list(self.db.execute(
            "SELECT DISTINCT recipient_name FROM gifts WHERE recipient_name IS NOT NULL"
        )))

        return {
            "total_gifts": total_gifts,
            "gifts_with_value": value_stats["count_with_value"],
            "gifts_without_value": total_gifts - value_stats["count_with_value"],
            "average_value": round(value_stats["avg_value"], 2) if value_stats["avg_value"] else None,
            "min_value": value_stats["min_value"],
            "max_value": value_stats["max_value"],
            "total_value": round(value_stats["total_value"], 2) if value_stats["total_value"] else None,
            "unique_countries": country_count,
            "unique_recipients": recipient_count
        }

    def get_top_donor_countries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get countries that have given the most gifts.

        Args:
            limit: Number of countries to return

        Returns:
            List of dicts with country, count, and total_value
        """
        query = f"""
            SELECT
                donor_country,
                COUNT(*) as gift_count,
                SUM(estimated_value) as total_value,
                AVG(estimated_value) as avg_value
            FROM gifts
            WHERE donor_country IS NOT NULL
            GROUP BY donor_country
            ORDER BY gift_count DESC
            LIMIT {limit}
        """

        results = []
        for row in self.db.execute(query):
            results.append({
                "country": row["donor_country"],
                "gift_count": row["gift_count"],
                "total_value": round(row["total_value"], 2) if row["total_value"] else None,
                "avg_value": round(row["avg_value"], 2) if row["avg_value"] else None
            })
        return results

    def get_top_recipients(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recipients who have received the most gifts.

        Args:
            limit: Number of recipients to return

        Returns:
            List of dicts with recipient info
        """
        query = f"""
            SELECT
                recipient_name,
                recipient_title,
                COUNT(*) as gift_count,
                SUM(estimated_value) as total_value,
                AVG(estimated_value) as avg_value
            FROM gifts
            WHERE recipient_name IS NOT NULL
            GROUP BY recipient_name, recipient_title
            ORDER BY gift_count DESC
            LIMIT {limit}
        """

        results = []
        for row in self.db.execute(query):
            results.append({
                "name": row["recipient_name"],
                "title": row["recipient_title"],
                "gift_count": row["gift_count"],
                "total_value": round(row["total_value"], 2) if row["total_value"] else None,
                "avg_value": round(row["avg_value"], 2) if row["avg_value"] else None
            })
        return results

    def get_most_valuable_gifts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most valuable gifts by estimated value.

        Args:
            limit: Number of gifts to return

        Returns:
            List of gift details
        """
        query = f"""
            SELECT
                recipient_name,
                recipient_title,
                donor_name,
                donor_country,
                gift_description,
                estimated_value,
                received,
                disposition
            FROM gifts
            WHERE estimated_value IS NOT NULL
            ORDER BY estimated_value DESC
            LIMIT {limit}
        """

        results = []
        for row in self.db.execute(query):
            results.append(dict(row))
        return results

    def get_gifts_by_year(self) -> Dict[str, Dict[str, Any]]:
        """
        Get gift statistics grouped by year.

        Returns:
            Dictionary with year as key and statistics as value
        """
        query = """
            SELECT
                strftime('%Y', received) as year,
                COUNT(*) as gift_count,
                SUM(estimated_value) as total_value,
                AVG(estimated_value) as avg_value
            FROM gifts
            WHERE received IS NOT NULL AND received != ''
            GROUP BY year
            ORDER BY year DESC
        """

        results = {}
        for row in self.db.execute(query):
            if row["year"]:
                results[row["year"]] = {
                    "gift_count": row["gift_count"],
                    "total_value": round(row["total_value"], 2) if row["total_value"] else None,
                    "avg_value": round(row["avg_value"], 2) if row["avg_value"] else None
                }
        return results

    def get_gift_categories(self) -> Dict[str, int]:
        """
        Categorize gifts by type based on description keywords.

        Returns:
            Dictionary with category counts
        """
        categories = {
            "jewelry": ["ring", "necklace", "bracelet", "earring", "brooch", "jewelry", "jewel"],
            "art": ["painting", "sculpture", "artwork", "art", "portrait", "statue", "drawing"],
            "clothing": ["dress", "suit", "robe", "gown", "jacket", "coat", "scarf", "tie"],
            "books": ["book", "album", "manuscript", "publication"],
            "decorative": ["vase", "bowl", "plate", "plaque", "frame", "box", "crystal"],
            "watches": ["watch", "timepiece", "clock"],
            "medals": ["medal", "medallion", "coin", "token"],
            "weapons": ["sword", "dagger", "knife", "blade"],
            "musical": ["instrument", "guitar", "drum", "flute"],
            "sporting": ["ball", "jersey", "sporting", "sport"],
            "food": ["wine", "champagne", "chocolate", "tea", "coffee", "liquor", "spirits"],
            "textiles": ["rug", "carpet", "tapestry", "fabric", "textile", "blanket"],
            "electronics": ["tablet", "phone", "computer", "electronic"],
            "furniture": ["chair", "table", "desk", "furniture"],
            "religious": ["bible", "quran", "religious", "rosary", "prayer"]
        }

        category_counts = defaultdict(int)
        other_count = 0

        for gift in self.gifts_table.rows:
            description = gift["gift_description"].lower() if gift["gift_description"] else ""
            categorized = False

            for category, keywords in categories.items():
                if any(keyword in description for keyword in keywords):
                    category_counts[category] += 1
                    categorized = True
                    break

            if not categorized:
                other_count += 1

        result = dict(category_counts)
        result["other"] = other_count

        # Sort by count
        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    def get_country_relationships(self, min_gifts: int = 5) -> Dict[str, List[str]]:
        """
        Find which countries give gifts to which recipients most often.

        Args:
            min_gifts: Minimum number of gifts to include relationship

        Returns:
            Dictionary mapping countries to their top recipient titles
        """
        query = f"""
            SELECT
                donor_country,
                recipient_title,
                COUNT(*) as gift_count
            FROM gifts
            WHERE donor_country IS NOT NULL
              AND recipient_title IS NOT NULL
            GROUP BY donor_country, recipient_title
            HAVING gift_count >= {min_gifts}
            ORDER BY donor_country, gift_count DESC
        """

        relationships = defaultdict(list)
        for row in self.db.execute(query):
            relationships[row["donor_country"]].append({
                "recipient_title": row["recipient_title"],
                "gift_count": row["gift_count"]
            })

        return dict(relationships)

    def get_disposition_analysis(self) -> Dict[str, Any]:
        """
        Analyze what happened to gifts (disposition).

        Returns:
            Statistics on gift dispositions
        """
        query = """
            SELECT
                disposition,
                COUNT(*) as count,
                AVG(estimated_value) as avg_value
            FROM gifts
            WHERE disposition IS NOT NULL
            GROUP BY disposition
            ORDER BY count DESC
        """

        dispositions = []
        for row in self.db.execute(query):
            dispositions.append({
                "disposition": row["disposition"],
                "count": row["count"],
                "avg_value": round(row["avg_value"], 2) if row["avg_value"] else None
            })

        return {
            "disposition_breakdown": dispositions,
            "total_dispositions": len(dispositions)
        }

    def search_gifts(
        self,
        keyword: Optional[str] = None,
        country: Optional[str] = None,
        recipient: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        year: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for gifts with various filters.

        Args:
            keyword: Search in gift description
            country: Filter by donor country
            recipient: Filter by recipient name
            min_value: Minimum estimated value
            max_value: Maximum estimated value
            year: Filter by year received

        Returns:
            List of matching gifts
        """
        conditions = []
        params = {}

        if keyword:
            conditions.append("gift_description LIKE :keyword")
            params["keyword"] = f"%{keyword}%"

        if country:
            conditions.append("donor_country LIKE :country")
            params["country"] = f"%{country}%"

        if recipient:
            conditions.append("recipient_name LIKE :recipient")
            params["recipient"] = f"%{recipient}%"

        if min_value is not None:
            conditions.append("estimated_value >= :min_value")
            params["min_value"] = min_value

        if max_value is not None:
            conditions.append("estimated_value <= :max_value")
            params["max_value"] = max_value

        if year:
            conditions.append("strftime('%Y', received) = :year")
            params["year"] = year

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM gifts WHERE {where_clause} ORDER BY received DESC"

        return [dict(row) for row in self.db.execute(query, params)]

    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive text report of insights.

        Args:
            output_path: Optional path to save report

        Returns:
            Report text
        """
        stats = self.get_summary_statistics()
        top_countries = self.get_top_donor_countries(10)
        top_recipients = self.get_top_recipients(10)
        valuable_gifts = self.get_most_valuable_gifts(5)
        categories = self.get_gift_categories()
        years = self.get_gifts_by_year()

        report = []
        report.append("=" * 80)
        report.append("FOREIGN GIFTS ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")

        # Summary statistics
        report.append("SUMMARY STATISTICS")
        report.append("-" * 80)
        report.append(f"Total Gifts: {stats['total_gifts']:,}")
        report.append(f"Gifts with Value Data: {stats['gifts_with_value']:,} ({stats['gifts_with_value']/stats['total_gifts']*100:.1f}%)")
        if stats['total_value']:
            report.append(f"Total Value: ${stats['total_value']:,.2f}")
        if stats['average_value']:
            report.append(f"Average Value: ${stats['average_value']:,.2f}")
        if stats['max_value']:
            report.append(f"Most Valuable Gift: ${stats['max_value']:,.2f}")
        report.append(f"Unique Donor Countries: {stats['unique_countries']}")
        report.append(f"Unique Recipients: {stats['unique_recipients']}")
        report.append("")

        # Top donor countries
        report.append("TOP 10 DONOR COUNTRIES")
        report.append("-" * 80)
        for i, country in enumerate(top_countries, 1):
            value_str = f"${country['total_value']:,.2f}" if country['total_value'] else "N/A"
            report.append(f"{i:2d}. {country['country']:30s} - {country['gift_count']:4d} gifts - Total: {value_str}")
        report.append("")

        # Top recipients
        report.append("TOP 10 RECIPIENTS")
        report.append("-" * 80)
        for i, recipient in enumerate(top_recipients, 1):
            value_str = f"${recipient['total_value']:,.2f}" if recipient['total_value'] else "N/A"
            report.append(f"{i:2d}. {recipient['name']:40s} - {recipient['gift_count']:4d} gifts - Total: {value_str}")
        report.append("")

        # Most valuable gifts
        report.append("MOST VALUABLE GIFTS")
        report.append("-" * 80)
        for i, gift in enumerate(valuable_gifts, 1):
            report.append(f"{i}. ${gift['estimated_value']:,.2f} - {gift['gift_description'][:60]}")
            report.append(f"   From: {gift['donor_country']} to {gift['recipient_name']}")
            report.append("")

        # Gift categories
        report.append("GIFT CATEGORIES")
        report.append("-" * 80)
        for category, count in list(categories.items())[:15]:
            report.append(f"{category.capitalize():20s}: {count:4d} gifts")
        report.append("")

        # Yearly trends
        report.append("GIFTS BY YEAR")
        report.append("-" * 80)
        for year, data in sorted(years.items(), reverse=True):
            value_str = f"${data['total_value']:,.2f}" if data['total_value'] else "N/A"
            report.append(f"{year}: {data['gift_count']:4d} gifts - Total: {value_str}")
        report.append("")

        report.append("=" * 80)

        report_text = "\n".join(report)

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(report_text)

        return report_text


def main():
    """Run analysis and generate report."""
    analyzer = GiftsAnalyzer()

    print("Generating analysis report...")
    report = analyzer.generate_report("data/analysis_report.txt")
    print(report)

    print("\n✓ Report saved to data/analysis_report.txt")


if __name__ == "__main__":
    main()
