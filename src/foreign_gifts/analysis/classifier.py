"""
Gift categorization and classification system.
Uses keyword matching and pattern recognition to categorize gifts.
"""

from typing import Dict, List, Set, Optional
import re
from dataclasses import dataclass


@dataclass
class GiftCategory:
    """Represents a gift category with keywords and patterns."""
    name: str
    keywords: List[str]
    patterns: List[str] = None
    subcategories: Dict[str, List[str]] = None

    def __post_init__(self):
        if self.patterns is None:
            self.patterns = []
        if self.subcategories is None:
            self.subcategories = {}


class GiftClassifier:
    """Classifies gifts into categories and subcategories."""

    def __init__(self):
        """Initialize classifier with category definitions."""
        self.categories = self._define_categories()

    def _define_categories(self) -> Dict[str, GiftCategory]:
        """
        Define comprehensive gift categories.

        Returns:
            Dictionary of category definitions
        """
        return {
            "jewelry": GiftCategory(
                name="Jewelry & Accessories",
                keywords=["ring", "necklace", "bracelet", "earring", "brooch", "jewelry",
                         "jewel", "pendant", "chain", "cufflink", "tiara", "crown"],
                subcategories={
                    "rings": ["ring"],
                    "necklaces": ["necklace", "pendant", "chain"],
                    "bracelets": ["bracelet", "bangle"],
                    "earrings": ["earring"],
                    "brooches": ["brooch", "pin"],
                    "cufflinks": ["cufflink"]
                }
            ),
            "art": GiftCategory(
                name="Art & Sculpture",
                keywords=["painting", "sculpture", "artwork", "art", "portrait", "statue",
                         "drawing", "lithograph", "print", "canvas", "watercolor", "oil painting"],
                subcategories={
                    "paintings": ["painting", "portrait", "canvas", "watercolor", "oil painting"],
                    "sculptures": ["sculpture", "statue", "bust", "figurine"],
                    "prints": ["lithograph", "print", "etching"]
                }
            ),
            "clothing": GiftCategory(
                name="Clothing & Textiles",
                keywords=["dress", "suit", "robe", "gown", "jacket", "coat", "scarf", "tie",
                         "shirt", "blouse", "vest", "shawl", "kimono", "sari"],
                subcategories={
                    "formal_wear": ["suit", "gown", "tuxedo", "dress"],
                    "traditional": ["kimono", "sari", "robe", "kaftan"],
                    "accessories": ["scarf", "tie", "shawl", "belt"]
                }
            ),
            "books": GiftCategory(
                name="Books & Publications",
                keywords=["book", "album", "manuscript", "publication", "volume", "encyclopedia",
                         "diary", "journal", "text"],
                subcategories={
                    "photo_albums": ["album", "photograph"],
                    "manuscripts": ["manuscript", "scroll"],
                    "reference": ["encyclopedia", "dictionary"]
                }
            ),
            "decorative": GiftCategory(
                name="Decorative Items",
                keywords=["vase", "bowl", "plate", "plaque", "frame", "box", "crystal",
                         "urn", "jar", "dish", "tray", "mirror", "candlestick"],
                subcategories={
                    "ceramic": ["vase", "bowl", "plate", "dish", "pottery", "porcelain"],
                    "glass": ["crystal", "glass"],
                    "frames": ["frame", "plaque"],
                    "boxes": ["box", "case", "chest"]
                }
            ),
            "watches": GiftCategory(
                name="Watches & Timepieces",
                keywords=["watch", "timepiece", "clock", "wristwatch"],
                subcategories={
                    "wristwatches": ["watch", "wristwatch"],
                    "clocks": ["clock", "timepiece"]
                }
            ),
            "medals": GiftCategory(
                name="Medals & Coins",
                keywords=["medal", "medallion", "coin", "token", "badge", "insignia",
                         "decoration", "order"],
                subcategories={
                    "medals": ["medal", "medallion"],
                    "coins": ["coin", "token"],
                    "badges": ["badge", "insignia"]
                }
            ),
            "weapons": GiftCategory(
                name="Weapons & Military",
                keywords=["sword", "dagger", "knife", "blade", "saber", "scabbard",
                         "rifle", "pistol", "gun"],
                subcategories={
                    "swords": ["sword", "saber", "blade"],
                    "daggers": ["dagger", "knife"],
                    "firearms": ["rifle", "pistol", "gun"]
                }
            ),
            "musical": GiftCategory(
                name="Musical Instruments",
                keywords=["instrument", "guitar", "drum", "flute", "violin", "piano",
                         "trumpet", "harp", "lute"],
                subcategories={
                    "string": ["guitar", "violin", "harp", "lute"],
                    "percussion": ["drum"],
                    "wind": ["flute", "trumpet"]
                }
            ),
            "sporting": GiftCategory(
                name="Sporting Goods",
                keywords=["ball", "jersey", "sporting", "sport", "athletic", "trophy",
                         "racket", "bat", "club"],
                subcategories={
                    "equipment": ["ball", "racket", "bat", "club"],
                    "apparel": ["jersey", "uniform"],
                    "trophies": ["trophy", "cup"]
                }
            ),
            "food": GiftCategory(
                name="Food & Beverages",
                keywords=["wine", "champagne", "chocolate", "tea", "coffee", "liquor",
                         "spirits", "cognac", "whiskey", "vodka", "honey", "caviar"],
                subcategories={
                    "wine": ["wine", "champagne"],
                    "spirits": ["liquor", "cognac", "whiskey", "vodka", "spirits"],
                    "non_alcoholic": ["tea", "coffee", "chocolate"],
                    "delicacies": ["caviar", "honey", "truffle"]
                }
            ),
            "textiles": GiftCategory(
                name="Rugs & Textiles",
                keywords=["rug", "carpet", "tapestry", "fabric", "textile", "blanket",
                         "quilt", "wall hanging"],
                subcategories={
                    "rugs": ["rug", "carpet"],
                    "wall_hangings": ["tapestry", "wall hanging"],
                    "bedding": ["blanket", "quilt"]
                }
            ),
            "electronics": GiftCategory(
                name="Electronics",
                keywords=["tablet", "phone", "computer", "electronic", "camera",
                         "device", "ipad", "iphone"],
                subcategories={
                    "mobile": ["phone", "iphone", "tablet", "ipad"],
                    "cameras": ["camera", "video"],
                    "computers": ["computer", "laptop"]
                }
            ),
            "furniture": GiftCategory(
                name="Furniture",
                keywords=["chair", "table", "desk", "furniture", "cabinet", "bench",
                         "stool", "throne"],
                subcategories={
                    "seating": ["chair", "bench", "stool", "throne"],
                    "tables": ["table", "desk"],
                    "storage": ["cabinet", "chest"]
                }
            ),
            "religious": GiftCategory(
                name="Religious Items",
                keywords=["bible", "quran", "religious", "rosary", "prayer", "cross",
                         "icon", "torah", "sacred"],
                subcategories={
                    "texts": ["bible", "quran", "torah"],
                    "items": ["rosary", "cross", "icon"]
                }
            ),
            "diplomatic": GiftCategory(
                name="Diplomatic & Ceremonial",
                keywords=["flag", "seal", "crest", "emblem", "banner", "standard"],
                subcategories={
                    "flags": ["flag", "banner", "standard"],
                    "emblems": ["seal", "crest", "emblem"]
                }
            )
        }

    def classify(self, description: str) -> Dict[str, any]:
        """
        Classify a gift based on its description.

        Args:
            description: Gift description text

        Returns:
            Dictionary with category, subcategory, and confidence
        """
        if not description:
            return {
                "category": "unknown",
                "subcategory": None,
                "confidence": 0.0,
                "matches": []
            }

        desc_lower = description.lower()
        matches = []

        # Check each category
        for cat_id, category in self.categories.items():
            keyword_matches = []

            # Check main keywords
            for keyword in category.keywords:
                if keyword in desc_lower:
                    keyword_matches.append(keyword)

            if keyword_matches:
                # Determine subcategory
                subcategory = None
                for subcat_name, subcat_keywords in category.subcategories.items():
                    if any(kw in desc_lower for kw in subcat_keywords):
                        subcategory = subcat_name
                        break

                confidence = min(len(keyword_matches) / 3.0, 1.0)  # More matches = higher confidence

                matches.append({
                    "category": cat_id,
                    "category_name": category.name,
                    "subcategory": subcategory,
                    "confidence": confidence,
                    "matched_keywords": keyword_matches
                })

        if not matches:
            return {
                "category": "other",
                "category_name": "Other/Uncategorized",
                "subcategory": None,
                "confidence": 0.0,
                "matches": []
            }

        # Return highest confidence match
        best_match = max(matches, key=lambda x: x["confidence"])
        best_match["matches"] = matches

        return best_match

    def get_value_category(self, value: Optional[float]) -> str:
        """
        Categorize gift by value range.

        Args:
            value: Estimated value in USD

        Returns:
            Value category name
        """
        if value is None:
            return "unknown"
        elif value < 100:
            return "token (<$100)"
        elif value < 500:
            return "modest ($100-$500)"
        elif value < 1000:
            return "moderate ($500-$1000)"
        elif value < 5000:
            return "valuable ($1,000-$5,000)"
        elif value < 10000:
            return "highly_valuable ($5,000-$10,000)"
        else:
            return "extremely_valuable (>$10,000)"

    def extract_materials(self, description: str) -> List[str]:
        """
        Extract materials mentioned in description.

        Args:
            description: Gift description

        Returns:
            List of materials found
        """
        materials = {
            "gold", "silver", "platinum", "bronze", "brass", "copper",
            "diamond", "ruby", "emerald", "sapphire", "pearl", "jade",
            "wood", "mahogany", "oak", "teak", "ebony",
            "leather", "silk", "cotton", "wool", "cashmere",
            "crystal", "glass", "porcelain", "ceramic", "clay",
            "marble", "granite", "stone",
            "ivory", "bone"
        }

        found = []
        desc_lower = description.lower()

        for material in materials:
            if material in desc_lower:
                found.append(material)

        return found

    def is_ceremonial(self, description: str) -> bool:
        """
        Determine if gift is ceremonial in nature.

        Args:
            description: Gift description

        Returns:
            True if ceremonial
        """
        ceremonial_keywords = [
            "ceremonial", "traditional", "cultural", "national",
            "official", "state", "formal", "diplomatic"
        ]

        desc_lower = description.lower()
        return any(kw in desc_lower for kw in ceremonial_keywords)


def main():
    """Test the classifier."""
    classifier = GiftClassifier()

    test_cases = [
        "Gold necklace with diamond pendant",
        "Oil painting depicting mountain landscape",
        "Ceremonial sword with silver scabbard",
        "Persian rug with intricate patterns",
        "Leather-bound book set",
        "Crystal vase",
        "Rolex watch with gold band"
    ]

    print("Gift Classification Examples")
    print("=" * 80)

    for desc in test_cases:
        result = classifier.classify(desc)
        materials = classifier.extract_materials(desc)
        ceremonial = classifier.is_ceremonial(desc)

        print(f"\nDescription: {desc}")
        print(f"Category: {result['category_name']}")
        if result['subcategory']:
            print(f"Subcategory: {result['subcategory']}")
        print(f"Confidence: {result['confidence']:.1%}")
        if materials:
            print(f"Materials: {', '.join(materials)}")
        if ceremonial:
            print("Type: Ceremonial")
        print("-" * 80)


if __name__ == "__main__":
    main()
