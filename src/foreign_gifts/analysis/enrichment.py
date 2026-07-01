"""
Data enrichment utilities for foreign gifts data.
Adds country metadata, normalizes values, and extracts additional insights.
"""

from typing import Dict, Optional, List, Any
import re
from datetime import datetime


# Country metadata - regions, codes, and additional context
COUNTRY_METADATA = {
    "Afghanistan": {"region": "South Asia", "code": "AF", "continent": "Asia"},
    "Albania": {"region": "Southern Europe", "code": "AL", "continent": "Europe"},
    "Algeria": {"region": "North Africa", "code": "DZ", "continent": "Africa"},
    "Argentina": {"region": "South America", "code": "AR", "continent": "Americas"},
    "Australia": {"region": "Oceania", "code": "AU", "continent": "Oceania"},
    "Austria": {"region": "Central Europe", "code": "AT", "continent": "Europe"},
    "Bahrain": {"region": "Middle East", "code": "BH", "continent": "Asia"},
    "Bangladesh": {"region": "South Asia", "code": "BD", "continent": "Asia"},
    "Belgium": {"region": "Western Europe", "code": "BE", "continent": "Europe"},
    "Brazil": {"region": "South America", "code": "BR", "continent": "Americas"},
    "Bulgaria": {"region": "Eastern Europe", "code": "BG", "continent": "Europe"},
    "Canada": {"region": "North America", "code": "CA", "continent": "Americas"},
    "Chile": {"region": "South America", "code": "CL", "continent": "Americas"},
    "China": {"region": "East Asia", "code": "CN", "continent": "Asia"},
    "Colombia": {"region": "South America", "code": "CO", "continent": "Americas"},
    "Costa Rica": {"region": "Central America", "code": "CR", "continent": "Americas"},
    "Croatia": {"region": "Southern Europe", "code": "HR", "continent": "Europe"},
    "Cuba": {"region": "Caribbean", "code": "CU", "continent": "Americas"},
    "Cyprus": {"region": "Middle East", "code": "CY", "continent": "Asia"},
    "Czech Republic": {"region": "Central Europe", "code": "CZ", "continent": "Europe"},
    "Denmark": {"region": "Northern Europe", "code": "DK", "continent": "Europe"},
    "Ecuador": {"region": "South America", "code": "EC", "continent": "Americas"},
    "Egypt": {"region": "North Africa", "code": "EG", "continent": "Africa"},
    "Estonia": {"region": "Northern Europe", "code": "EE", "continent": "Europe"},
    "Ethiopia": {"region": "East Africa", "code": "ET", "continent": "Africa"},
    "Finland": {"region": "Northern Europe", "code": "FI", "continent": "Europe"},
    "France": {"region": "Western Europe", "code": "FR", "continent": "Europe"},
    "Georgia": {"region": "Caucasus", "code": "GE", "continent": "Asia"},
    "Germany": {"region": "Central Europe", "code": "DE", "continent": "Europe"},
    "Ghana": {"region": "West Africa", "code": "GH", "continent": "Africa"},
    "Greece": {"region": "Southern Europe", "code": "GR", "continent": "Europe"},
    "Guatemala": {"region": "Central America", "code": "GT", "continent": "Americas"},
    "Guyana": {"region": "South America", "code": "GY", "continent": "Americas"},
    "Honduras": {"region": "Central America", "code": "HN", "continent": "Americas"},
    "Hungary": {"region": "Central Europe", "code": "HU", "continent": "Europe"},
    "Iceland": {"region": "Northern Europe", "code": "IS", "continent": "Europe"},
    "India": {"region": "South Asia", "code": "IN", "continent": "Asia"},
    "Indonesia": {"region": "Southeast Asia", "code": "ID", "continent": "Asia"},
    "Iran": {"region": "Middle East", "code": "IR", "continent": "Asia"},
    "Iraq": {"region": "Middle East", "code": "IQ", "continent": "Asia"},
    "Ireland": {"region": "Northern Europe", "code": "IE", "continent": "Europe"},
    "Israel": {"region": "Middle East", "code": "IL", "continent": "Asia"},
    "Italy": {"region": "Southern Europe", "code": "IT", "continent": "Europe"},
    "Jamaica": {"region": "Caribbean", "code": "JM", "continent": "Americas"},
    "Japan": {"region": "East Asia", "code": "JP", "continent": "Asia"},
    "Jordan": {"region": "Middle East", "code": "JO", "continent": "Asia"},
    "Kazakhstan": {"region": "Central Asia", "code": "KZ", "continent": "Asia"},
    "Kenya": {"region": "East Africa", "code": "KE", "continent": "Africa"},
    "Korea": {"region": "East Asia", "code": "KR", "continent": "Asia"},
    "South Korea": {"region": "East Asia", "code": "KR", "continent": "Asia"},
    "Kuwait": {"region": "Middle East", "code": "KW", "continent": "Asia"},
    "Latvia": {"region": "Northern Europe", "code": "LV", "continent": "Europe"},
    "Lebanon": {"region": "Middle East", "code": "LB", "continent": "Asia"},
    "Libya": {"region": "North Africa", "code": "LY", "continent": "Africa"},
    "Lithuania": {"region": "Northern Europe", "code": "LT", "continent": "Europe"},
    "Luxembourg": {"region": "Western Europe", "code": "LU", "continent": "Europe"},
    "Malaysia": {"region": "Southeast Asia", "code": "MY", "continent": "Asia"},
    "Mexico": {"region": "North America", "code": "MX", "continent": "Americas"},
    "Mongolia": {"region": "East Asia", "code": "MN", "continent": "Asia"},
    "Morocco": {"region": "North Africa", "code": "MA", "continent": "Africa"},
    "Nepal": {"region": "South Asia", "code": "NP", "continent": "Asia"},
    "Netherlands": {"region": "Western Europe", "code": "NL", "continent": "Europe"},
    "New Zealand": {"region": "Oceania", "code": "NZ", "continent": "Oceania"},
    "Nigeria": {"region": "West Africa", "code": "NG", "continent": "Africa"},
    "Norway": {"region": "Northern Europe", "code": "NO", "continent": "Europe"},
    "Oman": {"region": "Middle East", "code": "OM", "continent": "Asia"},
    "Pakistan": {"region": "South Asia", "code": "PK", "continent": "Asia"},
    "Panama": {"region": "Central America", "code": "PA", "continent": "Americas"},
    "Peru": {"region": "South America", "code": "PE", "continent": "Americas"},
    "Philippines": {"region": "Southeast Asia", "code": "PH", "continent": "Asia"},
    "Poland": {"region": "Central Europe", "code": "PL", "continent": "Europe"},
    "Portugal": {"region": "Southern Europe", "code": "PT", "continent": "Europe"},
    "Qatar": {"region": "Middle East", "code": "QA", "continent": "Asia"},
    "Romania": {"region": "Eastern Europe", "code": "RO", "continent": "Europe"},
    "Russia": {"region": "Eastern Europe", "code": "RU", "continent": "Europe"},
    "Rwanda": {"region": "East Africa", "code": "RW", "continent": "Africa"},
    "Saudi Arabia": {"region": "Middle East", "code": "SA", "continent": "Asia"},
    "Senegal": {"region": "West Africa", "code": "SN", "continent": "Africa"},
    "Serbia": {"region": "Southern Europe", "code": "RS", "continent": "Europe"},
    "Singapore": {"region": "Southeast Asia", "code": "SG", "continent": "Asia"},
    "Slovakia": {"region": "Central Europe", "code": "SK", "continent": "Europe"},
    "Slovenia": {"region": "Southern Europe", "code": "SI", "continent": "Europe"},
    "South Africa": {"region": "Southern Africa", "code": "ZA", "continent": "Africa"},
    "Spain": {"region": "Southern Europe", "code": "ES", "continent": "Europe"},
    "Sri Lanka": {"region": "South Asia", "code": "LK", "continent": "Asia"},
    "Sudan": {"region": "North Africa", "code": "SD", "continent": "Africa"},
    "Sweden": {"region": "Northern Europe", "code": "SE", "continent": "Europe"},
    "Switzerland": {"region": "Central Europe", "code": "CH", "continent": "Europe"},
    "Syria": {"region": "Middle East", "code": "SY", "continent": "Asia"},
    "Taiwan": {"region": "East Asia", "code": "TW", "continent": "Asia"},
    "Tanzania": {"region": "East Africa", "code": "TZ", "continent": "Africa"},
    "Thailand": {"region": "Southeast Asia", "code": "TH", "continent": "Asia"},
    "Tunisia": {"region": "North Africa", "code": "TN", "continent": "Africa"},
    "Turkey": {"region": "Middle East", "code": "TR", "continent": "Asia"},
    "Uganda": {"region": "East Africa", "code": "UG", "continent": "Africa"},
    "Ukraine": {"region": "Eastern Europe", "code": "UA", "continent": "Europe"},
    "United Arab Emirates": {"region": "Middle East", "code": "AE", "continent": "Asia"},
    "UAE": {"region": "Middle East", "code": "AE", "continent": "Asia"},
    "United Kingdom": {"region": "Northern Europe", "code": "GB", "continent": "Europe"},
    "Uruguay": {"region": "South America", "code": "UY", "continent": "Americas"},
    "Uzbekistan": {"region": "Central Asia", "code": "UZ", "continent": "Asia"},
    "Venezuela": {"region": "South America", "code": "VE", "continent": "Americas"},
    "Vietnam": {"region": "Southeast Asia", "code": "VN", "continent": "Asia"},
    "Yemen": {"region": "Middle East", "code": "YE", "continent": "Asia"},
    "Zambia": {"region": "Southern Africa", "code": "ZM", "continent": "Africa"},
    "Zimbabwe": {"region": "Southern Africa", "code": "ZW", "continent": "Africa"},
}


class DataEnricher:
    """Enriches gift data with additional metadata and insights."""

    def __init__(self):
        """Initialize enricher."""
        self.country_metadata = COUNTRY_METADATA

    def enrich_gift(self, gift: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a single gift record with additional metadata.

        Args:
            gift: Gift data dictionary

        Returns:
            Enriched gift dictionary
        """
        enriched = gift.copy()

        # Add country metadata
        if gift.get("donor_country"):
            country_info = self.get_country_info(gift["donor_country"])
            enriched["donor_region"] = country_info.get("region")
            enriched["donor_continent"] = country_info.get("continent")
            enriched["donor_country_code"] = country_info.get("code")

        # Normalize and categorize value
        if gift.get("estimated_value"):
            enriched["value_category"] = self.categorize_value(gift["estimated_value"])
            enriched["value_tier"] = self.get_value_tier(gift["estimated_value"])

        # Extract temporal information
        if gift.get("received"):
            date_info = self.extract_date_info(gift["received"])
            enriched.update(date_info)

        # Analyze description
        if gift.get("gift_description"):
            desc_info = self.analyze_description(gift["gift_description"])
            enriched.update(desc_info)

        # Determine if high-profile
        enriched["is_high_profile"] = self.is_high_profile_gift(enriched)

        return enriched

    def get_country_info(self, country_name: str) -> Dict[str, str]:
        """
        Get metadata for a country.

        Args:
            country_name: Name of the country

        Returns:
            Dictionary with region, code, and continent
        """
        # Try exact match first
        if country_name in self.country_metadata:
            return self.country_metadata[country_name]

        # Try fuzzy matching
        country_lower = country_name.lower()
        for key, value in self.country_metadata.items():
            if key.lower() in country_lower or country_lower in key.lower():
                return value

        # Default
        return {"region": "Unknown", "code": "XX", "continent": "Unknown"}

    def categorize_value(self, value: float) -> str:
        """
        Categorize gift by value range.

        Args:
            value: Estimated value in USD

        Returns:
            Value category
        """
        if value < 100:
            return "token"
        elif value < 500:
            return "modest"
        elif value < 1000:
            return "moderate"
        elif value < 5000:
            return "valuable"
        elif value < 10000:
            return "highly_valuable"
        else:
            return "extremely_valuable"

    def get_value_tier(self, value: float) -> int:
        """
        Get value tier (1-5).

        Args:
            value: Estimated value

        Returns:
            Tier number
        """
        if value < 500:
            return 1
        elif value < 1000:
            return 2
        elif value < 5000:
            return 3
        elif value < 10000:
            return 4
        else:
            return 5

    def extract_date_info(self, date_str: str) -> Dict[str, Any]:
        """
        Extract temporal information from date.

        Args:
            date_str: Date string

        Returns:
            Dictionary with year, month, quarter, etc.
        """
        try:
            # Try parsing ISO format
            if isinstance(date_str, str):
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return {}

            quarter = (date.month - 1) // 3 + 1

            return {
                "received_year": date.year,
                "received_month": date.month,
                "received_quarter": quarter,
                "received_month_name": date.strftime("%B"),
                "received_day_of_week": date.strftime("%A")
            }
        except (ValueError, AttributeError):
            return {}

    def analyze_description(self, description: str) -> Dict[str, Any]:
        """
        Analyze gift description for additional insights.

        Args:
            description: Gift description

        Returns:
            Dictionary with analysis results
        """
        desc_lower = description.lower()

        # Detect set/collection
        is_set = any(word in desc_lower for word in ["set", "collection", "pair", "suite"])

        # Detect personalization
        is_personalized = any(word in desc_lower for word in ["engraved", "monogrammed", "inscribed", "personalized"])

        # Detect handmade/artisan
        is_handmade = any(word in desc_lower for word in ["handmade", "hand-crafted", "artisan", "hand-painted"])

        # Detect historical/antique
        is_historical = any(word in desc_lower for word in ["antique", "historical", "vintage", "ancient", "century"])

        # Extract quantities
        quantity = self.extract_quantity(description)

        # Estimate description complexity (as proxy for gift complexity)
        word_count = len(description.split())

        return {
            "is_set": is_set,
            "is_personalized": is_personalized,
            "is_handmade": is_handmade,
            "is_historical": is_historical,
            "description_word_count": word_count,
            "description_complexity": "detailed" if word_count > 15 else "simple",
            "quantity_mentioned": quantity
        }

    def extract_quantity(self, description: str) -> Optional[int]:
        """
        Extract quantity from description.

        Args:
            description: Gift description

        Returns:
            Quantity if found
        """
        # Look for patterns like "set of 12", "6 bottles", etc.
        patterns = [
            r'set of (\d+)',
            r'(\d+)[-\s]piece',
            r'(\d+) bottles',
            r'(\d+) volumes',
            r'pair'  # special case
        ]

        desc_lower = description.lower()

        for pattern in patterns:
            match = re.search(pattern, desc_lower)
            if match:
                if pattern == 'pair':
                    return 2
                try:
                    return int(match.group(1))
                except (IndexError, ValueError):
                    pass

        return None

    def is_high_profile_gift(self, gift: Dict[str, Any]) -> bool:
        """
        Determine if gift is high-profile based on multiple factors.

        Args:
            gift: Enriched gift dictionary

        Returns:
            True if high-profile
        """
        criteria = []

        # High value
        if gift.get("estimated_value") and gift["estimated_value"] > 5000:
            criteria.append(True)

        # President or Vice President
        recipient_title = (gift.get("recipient_title") or "").lower()
        if "president" in recipient_title or "vice president" in recipient_title:
            criteria.append(True)

        # Personalized or historical
        if gift.get("is_personalized") or gift.get("is_historical"):
            criteria.append(True)

        # Major donor country (subjective, but let's use G20 as proxy)
        major_countries = ["China", "Japan", "Germany", "United Kingdom", "France",
                          "India", "Italy", "Brazil", "Canada", "Russia",
                          "South Korea", "Australia", "Spain", "Mexico",
                          "Indonesia", "Saudi Arabia", "Turkey"]
        if gift.get("donor_country") in major_countries:
            criteria.append(True)

        # At least 2 criteria must be met
        return len(criteria) >= 2

    def get_regional_statistics(self, gifts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate statistics by region.

        Args:
            gifts: List of enriched gift dictionaries

        Returns:
            Regional statistics
        """
        from collections import defaultdict

        region_stats = defaultdict(lambda: {
            "count": 0,
            "total_value": 0,
            "gifts": []
        })

        for gift in gifts:
            region = gift.get("donor_region", "Unknown")
            region_stats[region]["count"] += 1

            if gift.get("estimated_value"):
                region_stats[region]["total_value"] += gift["estimated_value"]

            region_stats[region]["gifts"].append(gift)

        # Calculate averages
        for region, stats in region_stats.items():
            if stats["count"] > 0:
                stats["avg_value"] = stats["total_value"] / stats["count"]
            else:
                stats["avg_value"] = 0

        return dict(region_stats)


def main():
    """Test enrichment functionality."""
    enricher = DataEnricher()

    # Test gift
    test_gift = {
        "donor_country": "Japan",
        "estimated_value": 7500.00,
        "received": "2022-03-15",
        "gift_description": "Handmade set of 6 ceramic bowls with traditional patterns",
        "recipient_title": "President of the United States"
    }

    enriched = enricher.enrich_gift(test_gift)

    print("Enriched Gift Data:")
    print("=" * 80)
    for key, value in enriched.items():
        print(f"{key:30s}: {value}")


if __name__ == "__main__":
    main()
