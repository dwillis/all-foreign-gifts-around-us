"""
Visualization utilities for foreign gifts data.
Creates charts, graphs, and visual reports.
"""

from typing import List, Dict, Any, Optional, Tuple
import sqlite3
import sqlite_utils
from pathlib import Path

# Optional imports - gracefully handle if not available
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.gridspec import GridSpec
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False


class GiftsVisualizer:
    """Creates visualizations from gifts data."""

    def __init__(self, db_path: str = "data/gifts.db"):
        """
        Initialize visualizer.

        Args:
            db_path: Path to SQLite database
        """
        if not HAS_MATPLOTLIB:
            raise ImportError("matplotlib is required for visualization. Install with: uv sync --group dev")

        self.db = sqlite_utils.Database(db_path)
        self.db.conn.row_factory = sqlite3.Row
        self.output_dir = Path("data/visualizations")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        if HAS_SEABORN:
            sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10

    def plot_top_donor_countries(
        self,
        limit: int = 15,
        save_path: Optional[str] = None
    ) -> str:
        """
        Create bar chart of top donor countries.

        Args:
            limit: Number of countries to show
            save_path: Optional path to save figure

        Returns:
            Path where figure was saved
        """
        query = f"""
            SELECT donor_country, COUNT(*) as count
            FROM gifts
            WHERE donor_country IS NOT NULL
            GROUP BY donor_country
            ORDER BY count DESC
            LIMIT {limit}
        """

        data = list(self.db.execute(query))
        countries = [row["donor_country"] for row in data]
        counts = [row["count"] for row in data]

        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(countries[::-1], counts[::-1])

        # Color bars by count (gradient)
        colors = plt.cm.Blues([(c - min(counts)) / (max(counts) - min(counts)) for c in counts[::-1]])
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        ax.set_xlabel('Number of Gifts', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {limit} Donor Countries', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        # Add count labels
        for i, (country, count) in enumerate(zip(countries[::-1], counts[::-1])):
            ax.text(count + max(counts) * 0.01, i, str(count), va='center')

        plt.tight_layout()

        if save_path is None:
            save_path = self.output_dir / "top_donor_countries.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        return str(save_path)

    def plot_value_distribution(self, save_path: Optional[str] = None) -> str:
        """
        Create histogram of gift values.

        Args:
            save_path: Optional path to save figure

        Returns:
            Path where figure was saved
        """
        query = """
            SELECT estimated_value
            FROM gifts
            WHERE estimated_value IS NOT NULL
            AND estimated_value < 50000
        """

        values = [row["estimated_value"] for row in self.db.execute(query)]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Histogram
        ax1.hist(values, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
        ax1.set_xlabel('Gift Value (USD)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax1.set_title('Distribution of Gift Values', fontsize=13, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)

        # Box plot
        ax2.boxplot(values, vert=True)
        ax2.set_ylabel('Gift Value (USD)', fontsize=11, fontweight='bold')
        ax2.set_title('Gift Value Statistics', fontsize=13, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)

        # Add statistics text
        stats_text = f"Mean: ${sum(values)/len(values):,.2f}\n"
        stats_text += f"Median: ${sorted(values)[len(values)//2]:,.2f}\n"
        stats_text += f"Max: ${max(values):,.2f}"
        ax2.text(1.15, max(values) * 0.7, stats_text,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save_path is None:
            save_path = self.output_dir / "value_distribution.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        return str(save_path)

    def plot_gifts_over_time(self, save_path: Optional[str] = None) -> str:
        """
        Create line chart of gifts received over time.

        Args:
            save_path: Optional path to save figure

        Returns:
            Path where figure was saved
        """
        query = """
            SELECT
                strftime('%Y', received) as year,
                COUNT(*) as count
            FROM gifts
            WHERE received IS NOT NULL
            AND received != ''
            GROUP BY year
            ORDER BY year
        """

        data = list(self.db.execute(query))
        years = [row["year"] for row in data if row["year"]]
        counts = [row["count"] for row in data if row["year"]]

        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(years, counts, marker='o', linewidth=2, markersize=8, color='#2E86AB')
        ax.fill_between(range(len(years)), counts, alpha=0.3, color='#2E86AB')

        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Gifts', fontsize=12, fontweight='bold')
        ax.set_title('Foreign Gifts Received Over Time', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')

        # Add value labels
        for i, (year, count) in enumerate(zip(years, counts)):
            if i % 2 == 0:  # Label every other point to avoid crowding
                ax.text(i, count + max(counts) * 0.02, str(count),
                       ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        if save_path is None:
            save_path = self.output_dir / "gifts_over_time.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        return str(save_path)

    def plot_regional_distribution(self, save_path: Optional[str] = None) -> str:
        """
        Create pie chart of gifts by region.

        Args:
            save_path: Optional path to save figure

        Returns:
            Path where figure was saved
        """
        # This requires enriched data with regions
        # For now, we'll approximate by grouping known countries

        regions = {
            "Europe": ["France", "Germany", "Italy", "United Kingdom", "Spain", "Poland",
                      "Netherlands", "Belgium", "Sweden", "Norway", "Denmark", "Ireland",
                      "Greece", "Portugal", "Austria", "Switzerland", "Finland"],
            "Middle East": ["Saudi Arabia", "UAE", "Qatar", "Kuwait", "Bahrain", "Oman",
                           "Israel", "Turkey", "Jordan", "Iraq", "Iran", "Lebanon"],
            "Asia": ["China", "Japan", "India", "South Korea", "Singapore", "Thailand",
                    "Vietnam", "Indonesia", "Malaysia", "Philippines", "Taiwan"],
            "Americas": ["Canada", "Mexico", "Brazil", "Argentina", "Chile", "Colombia",
                        "Peru", "Costa Rica", "Panama"],
            "Africa": ["Egypt", "South Africa", "Nigeria", "Kenya", "Ghana", "Morocco",
                      "Ethiopia", "Tanzania"],
            "Oceania": ["Australia", "New Zealand"]
        }

        region_counts = {region: 0 for region in regions.keys()}
        region_counts["Other"] = 0

        for row in self.db.execute("SELECT donor_country FROM gifts WHERE donor_country IS NOT NULL"):
            country = row["donor_country"]
            categorized = False
            for region, countries in regions.items():
                if any(c in country for c in countries):
                    region_counts[region] += 1
                    categorized = True
                    break
            if not categorized:
                region_counts["Other"] += 1

        # Remove regions with 0 gifts
        region_counts = {k: v for k, v in region_counts.items() if v > 0}

        fig, ax = plt.subplots(figsize=(10, 8))

        colors = plt.cm.Set3(range(len(region_counts)))
        wedges, texts, autotexts = ax.pie(
            region_counts.values(),
            labels=region_counts.keys(),
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )

        # Enhance text
        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')

        ax.set_title('Gifts by World Region', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        if save_path is None:
            save_path = self.output_dir / "regional_distribution.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        return str(save_path)

    def plot_recipient_analysis(self, limit: int = 10, save_path: Optional[str] = None) -> str:
        """
        Create visualization of top recipients.

        Args:
            limit: Number of recipients to show
            save_path: Optional path to save figure

        Returns:
            Path where figure was saved
        """
        query = f"""
            SELECT
                recipient_name,
                recipient_title,
                COUNT(*) as count,
                SUM(estimated_value) as total_value
            FROM gifts
            WHERE recipient_name IS NOT NULL
            AND recipient_name != ''
            GROUP BY recipient_name
            ORDER BY count DESC
            LIMIT {limit}
        """

        data = list(self.db.execute(query))
        names = [row["recipient_name"][:30] for row in data]  # Truncate long names
        counts = [row["count"] for row in data]
        values = [row["total_value"] if row["total_value"] else 0 for row in data]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Gift count
        bars1 = ax1.barh(names[::-1], counts[::-1], color='#A23B72')
        ax1.set_xlabel('Number of Gifts', fontsize=11, fontweight='bold')
        ax1.set_title(f'Top {limit} Recipients by Gift Count', fontsize=13, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)

        # Add labels
        for i, count in enumerate(counts[::-1]):
            ax1.text(count + max(counts) * 0.01, i, str(count), va='center')

        # Total value
        bars2 = ax2.barh(names[::-1], values[::-1], color='#F18F01')
        ax2.set_xlabel('Total Gift Value (USD)', fontsize=11, fontweight='bold')
        ax2.set_title(f'Top {limit} Recipients by Total Value', fontsize=13, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)

        # Add labels
        for i, value in enumerate(values[::-1]):
            if value > 0:
                ax2.text(value + max(values) * 0.01, i, f'${value:,.0f}', va='center')

        plt.tight_layout()

        if save_path is None:
            save_path = self.output_dir / "recipient_analysis.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        return str(save_path)

    def create_dashboard(self, save_path: Optional[str] = None) -> str:
        """
        Create comprehensive dashboard with multiple visualizations.

        Args:
            save_path: Optional path to save figure

        Returns:
            Path where figure was saved
        """
        fig = plt.figure(figsize=(20, 12))
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

        # 1. Summary statistics (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        stats = self._get_summary_stats()
        ax1.axis('off')
        stats_text = f"""
        SUMMARY STATISTICS

        Total Gifts: {stats['total']:,}
        Total Value: ${stats['total_value']:,.2f}
        Average Value: ${stats['avg_value']:,.2f}

        Unique Countries: {stats['countries']}
        Unique Recipients: {stats['recipients']}

        Date Range:
        {stats['date_range']}
        """
        ax1.text(0.1, 0.5, stats_text, fontsize=12, family='monospace',
                verticalalignment='center')
        ax1.set_title('Overview', fontsize=14, fontweight='bold', loc='left')

        # 2. Top countries (top middle and right)
        ax2 = fig.add_subplot(gs[0, 1:])
        self._plot_top_countries_inline(ax2, limit=10)

        # 3. Value distribution (middle left)
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_value_hist_inline(ax3)

        # 4. Gifts over time (middle center and right)
        ax4 = fig.add_subplot(gs[1, 1:])
        self._plot_timeline_inline(ax4)

        # 5. Regional distribution (bottom left)
        ax5 = fig.add_subplot(gs[2, 0])
        self._plot_regions_inline(ax5)

        # 6. Top recipients (bottom middle and right)
        ax6 = fig.add_subplot(gs[2, 1:])
        self._plot_recipients_inline(ax6, limit=8)

        fig.suptitle('Foreign Gifts Analysis Dashboard', fontsize=18, fontweight='bold', y=0.995)

        if save_path is None:
            save_path = self.output_dir / "dashboard.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        return str(save_path)

    def _get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for dashboard."""
        total = list(self.db.execute("SELECT COUNT(*) as c FROM gifts"))[0]["c"]

        value_stats = list(self.db.execute("""
            SELECT SUM(estimated_value) as total, AVG(estimated_value) as avg
            FROM gifts WHERE estimated_value IS NOT NULL
        """))[0]

        countries = list(self.db.execute("""
            SELECT COUNT(DISTINCT donor_country) as c
            FROM gifts WHERE donor_country IS NOT NULL
        """))[0]["c"]

        recipients = list(self.db.execute("""
            SELECT COUNT(DISTINCT recipient_name) as c
            FROM gifts WHERE recipient_name IS NOT NULL
        """))[0]["c"]

        date_range = list(self.db.execute("""
            SELECT MIN(received) as min, MAX(received) as max
            FROM gifts WHERE received IS NOT NULL AND received != ''
        """))[0]

        return {
            "total": total,
            "total_value": value_stats["total"] or 0,
            "avg_value": value_stats["avg"] or 0,
            "countries": countries,
            "recipients": recipients,
            "date_range": f"{date_range['min'][:10]} to {date_range['max'][:10]}"
        }

    def _plot_top_countries_inline(self, ax, limit=10):
        """Plot top countries on given axis."""
        query = f"""
            SELECT donor_country, COUNT(*) as count
            FROM gifts WHERE donor_country IS NOT NULL
            GROUP BY donor_country ORDER BY count DESC LIMIT {limit}
        """
        data = list(self.db.execute(query))
        countries = [row["donor_country"] for row in data]
        counts = [row["count"] for row in data]

        ax.barh(countries[::-1], counts[::-1], color='#2E86AB')
        ax.set_xlabel('Gift Count')
        ax.set_title(f'Top {limit} Donor Countries', fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

    def _plot_value_hist_inline(self, ax):
        """Plot value histogram on given axis."""
        values = [row["estimated_value"] for row in self.db.execute(
            "SELECT estimated_value FROM gifts WHERE estimated_value IS NOT NULL AND estimated_value < 20000"
        )]
        ax.hist(values, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        ax.set_xlabel('Value (USD)')
        ax.set_ylabel('Frequency')
        ax.set_title('Value Distribution', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

    def _plot_timeline_inline(self, ax):
        """Plot timeline on given axis."""
        query = """
            SELECT strftime('%Y', received) as year, COUNT(*) as count
            FROM gifts WHERE received IS NOT NULL AND received != ''
            GROUP BY year ORDER BY year
        """
        data = list(self.db.execute(query))
        years = [row["year"] for row in data if row["year"]]
        counts = [row["count"] for row in data if row["year"]]

        ax.plot(years, counts, marker='o', linewidth=2, color='#2E86AB')
        ax.fill_between(range(len(years)), counts, alpha=0.3, color='#2E86AB')
        ax.set_xlabel('Year')
        ax.set_ylabel('Gift Count')
        ax.set_title('Gifts Over Time', fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    def _plot_regions_inline(self, ax):
        """Plot regional distribution on given axis."""
        # Simplified for dashboard
        query = """
            SELECT SUBSTR(donor_country, 1, 1) as region, COUNT(*) as count
            FROM gifts WHERE donor_country IS NOT NULL
            GROUP BY region ORDER BY count DESC LIMIT 8
        """
        data = list(self.db.execute(query))
        labels = [f"Region {row['region']}" for row in data]
        sizes = [row["count"] for row in data]

        ax.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=90)
        ax.set_title('Regional Distribution', fontweight='bold')

    def _plot_recipients_inline(self, ax, limit=8):
        """Plot top recipients on given axis."""
        query = f"""
            SELECT recipient_name, COUNT(*) as count
            FROM gifts WHERE recipient_name IS NOT NULL AND recipient_name != ''
            GROUP BY recipient_name ORDER BY count DESC LIMIT {limit}
        """
        data = list(self.db.execute(query))
        names = [row["recipient_name"][:25] for row in data]
        counts = [row["count"] for row in data]

        ax.barh(names[::-1], counts[::-1], color='#A23B72')
        ax.set_xlabel('Gift Count')
        ax.set_title(f'Top {limit} Recipients', fontweight='bold')
        ax.grid(axis='x', alpha=0.3)


def main():
    """Generate all visualizations."""
    print("Creating visualizations...")

    visualizer = GiftsVisualizer()

    print("1. Top donor countries...")
    visualizer.plot_top_donor_countries()

    print("2. Value distribution...")
    visualizer.plot_value_distribution()

    print("3. Gifts over time...")
    visualizer.plot_gifts_over_time()

    print("4. Regional distribution...")
    visualizer.plot_regional_distribution()

    print("5. Recipient analysis...")
    visualizer.plot_recipient_analysis()

    print("6. Creating dashboard...")
    visualizer.create_dashboard()

    print(f"\n✓ All visualizations saved to {visualizer.output_dir}")


if __name__ == "__main__":
    main()
