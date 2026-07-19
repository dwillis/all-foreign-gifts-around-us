"""Standardization helpers: country/disposition/date canonicalization.

These turn the free-text values an LLM extracted from Federal Register notices
into a small set of consistent values, while always preserving the original
text alongside so nothing is silently lost.
"""

import re

# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------

_MISSING_DATE_VALUES = {"", "n/a", "na", "unknown", "unkn"}
_FULL_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MONTH_DATE_RE = re.compile(r"^\d{4}-\d{2}$")
_YEAR_DATE_RE = re.compile(r"^\d{4}$")


def normalize_date(raw: str | None) -> tuple[str | None, str]:
    """Normalize a `received` value to (date, precision).

    precision is one of "day", "month", "year", "range", or "unknown". A date
    range (e.g. "2014-05-19-2014-05-24" or "2022-05-27–2022-06-05")
    resolves to its start date with precision "range" so the imprecision is
    visible rather than silently dropped.
    """
    text = (raw or "").strip()
    lower = text.lower()
    if lower in _MISSING_DATE_VALUES:
        return None, "unknown"

    candidate = text.replace("–", "-").replace("—", "-")
    is_range = False
    if " to " in candidate.lower():
        candidate = re.split(r"\s+to\s+", candidate, maxsplit=1, flags=re.IGNORECASE)[0]
        is_range = True

    parts = candidate.split("-")
    if len(parts) > 3:
        candidate = "-".join(parts[:3])
        is_range = True

    if _FULL_DATE_RE.match(candidate):
        return candidate, "range" if is_range else "day"
    if _MONTH_DATE_RE.match(candidate):
        return candidate, "range" if is_range else "month"
    if _YEAR_DATE_RE.match(candidate):
        return candidate, "range" if is_range else "year"
    return None, "unknown"


# ---------------------------------------------------------------------------
# Disposition
# ---------------------------------------------------------------------------

_UNKNOWN_DISPOSITIONS = {"", "n/a", "na", "unknown", "rec'd", "disposition", "disposition-"}

# Checked in order; the first matching rule wins. Ordered from most specific
# (a distinct handling protocol) to most general (generic retention language).
_DISPOSITION_RULES = [
    (lambda t: "purchased" in t, "Purchased by Recipient"),
    (lambda t: "secret service" in t, "Handled per Secret Service Policy"),
    (lambda t: "secretary of the senate" in t, "Deposited with the Secretary of the Senate"),
    (lambda t: "destroy" in t or "perishable" in t or "consum" in t, "Destroyed or Consumed"),
    (lambda t: "pending disposal" in t, "Pending Disposal"),
    (lambda t: "pending" in t and ("nara" in t or "archives" in t), "Pending Transfer to NARA"),
    (lambda t: "nara" in t or "archives" in t, "Transferred to NARA"),
    (
        lambda t: "pending" in t and ("gsa" in t or "general services administration" in t),
        "Pending Transfer to GSA",
    ),
    (lambda t: "gsa" in t or "general services administration" in t, "Transferred to GSA"),
    (
        lambda t: any(
            kw in t
            for kw in ("retain", "official use", "official display", "on display", "vault", "gift office")
        ),
        "Retained for Official Use",
    ),
    (lambda t: "forwarded" in t or "property" in t, "Forwarded to Agency Property Office"),
]


def canonicalize_disposition(raw: str | None) -> str:
    """Map free-text disposition values to a small controlled vocabulary."""
    text = (raw or "").strip()
    lower = text.lower()
    if lower in _UNKNOWN_DISPOSITIONS:
        return "Unknown"
    for predicate, label in _DISPOSITION_RULES:
        if predicate(lower):
            return label
    return "Other"


# ---------------------------------------------------------------------------
# Countries
# ---------------------------------------------------------------------------

_JUNK_COUNTRY_VALUES = {"", "government", "national", "protocol", "country unknown", "<unknown>", "unknown"}

# International organizations that appear as "donor countries" in the source data.
_ORG_ALIASES = {
    "united nations": "United Nations",
    "united nations environment program": "United Nations",
    "united nations educational, scientific, and cultural organization": "United Nations",
    "world health organization": "World Health Organization",
    "european union": "European Union",
    "european communities": "European Union",
    "european commission": "European Union",
    "organization of the islamic conference": "Organization of Islamic Cooperation",
    "turksoy": "TURKSOY",
}

# Cities/regions that appear instead of a country; mapped to their sovereign parent.
_SUBNATIONAL_ALIASES = {
    "abu dhabi": "United Arab Emirates",
    "dubai": "United Arab Emirates",
    "zanzibar": "Tanzania",
    "bavaria": "Germany",
    "rhineland-palatinate": "Germany",
    "mecklenburg-west pomerania": "Germany",
    "london": "United Kingdom",
    "hague": "Netherlands",
    "qassim": "Saudi Arabia",
    "wales": "United Kingdom",
    "northern ireland": "United Kingdom",
    "iraqi kurdistan region": "Iraq",
    "kurdistan regional government": "Iraq",
    "kurdistan": "Iraq",
    "erbil province": "Iraq",
    "french polynesia": "France",
}

# Variant spellings/typos/former names -> canonical country name. Checked
# case-insensitively after stripping a leading "the ". Only covers variants
# actually observed in this dataset, not every country on earth.
_COUNTRY_ALIASES = {
    "people's republic of china": "China",
    "china": "China",
    "republic of china (taiwan)": "Taiwan",
    "chinese taipei (taiwan)": "Taiwan",
    "chinese taipei": "Taiwan",
    "taiwan": "Taiwan",
    "hong kong special administrative region": "Hong Kong",
    "hong kong": "Hong Kong",
    "republic of korea": "South Korea",
    "republic of south korea": "South Korea",
    "south korea": "South Korea",
    "korea": "South Korea",
    "democratic people's republic of korea": "North Korea",
    "saudi arabia": "Saudi Arabia",
    "kingdom of saudi arabia": "Saudi Arabia",
    "hashemite kingdom of jordan": "Jordan",
    "jordan": "Jordan",
    "republic of iraq": "Iraq",
    "iraq": "Iraq",
    "socialist republic of vietnam": "Vietnam",
    "vietnam": "Vietnam",
    "united kingdom of great britain and northern ireland": "United Kingdom",
    "great britain and northern ireland": "United Kingdom",
    "united kingdom": "United Kingdom",
    "arab republic of egypt": "Egypt",
    "egypt": "Egypt",
    "united mexican states": "Mexico",
    "mexico": "Mexico",
    "islamic republic of afghanistan": "Afghanistan",
    "republic of afghanistan": "Afghanistan",
    "afghanistan": "Afghanistan",
    "hellenic republic": "Greece",
    "greece": "Greece",
    "state of qatar": "Qatar",
    "qatar": "Qatar",
    "republic of indonesia": "Indonesia",
    "indonesia": "Indonesia",
    "republic of india": "India",
    "india": "India",
    "kingdom of bahrain": "Bahrain",
    "bahrain": "Bahrain",
    "state of kuwait": "Kuwait",
    "kuwait": "Kuwait",
    "sultanate of oman": "Oman",
    "oman": "Oman",
    "kingdom of thailand": "Thailand",
    "thailand": "Thailand",
    "republic of the philippines": "Philippines",
    "philippines": "Philippines",
    "republic of singapore": "Singapore",
    "singapore": "Singapore",
    "republic of turkey": "Turkey",
    "turkey": "Turkey",
    "russian federation": "Russia",
    "russia": "Russia",
    "federal republic of germany": "Germany",
    "germany": "Germany",
    "french republic": "France",
    "france": "France",
    "italian republic": "Italy",
    "italian": "Italy",
    "italy": "Italy",
    "swiss confederation": "Switzerland",
    "switzerland": "Switzerland",
    "kingdom of the netherlands": "Netherlands",
    "netherlands": "Netherlands",
    "republic of poland": "Poland",
    "poland": "Poland",
    "federative republic of brazil": "Brazil",
    "federal republic of brazil": "Brazil",
    "brazil": "Brazil",
    "argentine republic": "Argentina",
    "argentina": "Argentina",
    "republic of colombia": "Colombia",
    "colombia": "Colombia",
    "republic of chile": "Chile",
    "chile": "Chile",
    "republic of tajikistan": "Tajikistan",
    "tajikistan": "Tajikistan",
    "republic of yemen": "Yemen",
    "yemen": "Yemen",
    "republic of moldova": "Moldova",
    "moldova": "Moldova",
    "republic of mauritius": "Mauritius",
    "mauritius": "Mauritius",
    "republic of macedonia": "North Macedonia",
    "macedonia": "North Macedonia",
    "north macedonia": "North Macedonia",
    "republic of trinidad and tobago": "Trinidad and Tobago",
    "trinidad and tobago": "Trinidad and Tobago",
    "republic of union of myanmar": "Myanmar",
    "burma": "Myanmar",
    "myanmar": "Myanmar",
    "united republic of tanzania": "Tanzania",
    "tanzania": "Tanzania",
    "republic of south africa": "South Africa",
    "south africa": "South Africa",
    "republic of kazakhstan": "Kazakhstan",
    "kazakhstan": "Kazakhstan",
    "republic of uzbekistan": "Uzbekistan",
    "uzbekistan": "Uzbekistan",
    "kyrgyz republic": "Kyrgyzstan",
    "kyrgyzstan": "Kyrgyzstan",
    "democratic republic of the congo": "Democratic Republic of the Congo",
    "democratic rep. of the congo": "Democratic Republic of the Congo",
    "republic of congo": "Republic of the Congo",
    "gabonese republic": "Gabon",
    "gabon": "Gabon",
    "democratic socialist republic of sri lanka": "Sri Lanka",
    "sri lanka": "Sri Lanka",
    "lao people's democratic republic": "Laos",
    "bahamas": "Bahamas",
    "cote d'ivoire": "Côte d'Ivoire",
    "côte d'ivoire": "Côte d'Ivoire",
    "bosnia & herzegovina": "Bosnia and Herzegovina",
    "bosnia and herzegovina": "Bosnia and Herzegovina",
    "slovak republic": "Slovakia",
    "slovakia": "Slovakia",
    "kingdom of morocco": "Morocco",
    "morocco": "Morocco",
    "kingdom of spain": "Spain",
    "spain": "Spain",
    "kingdom of norway": "Norway",
    "norway": "Norway",
    "kingdom of belgium": "Belgium",
    "belgium": "Belgium",
    "republic of azerbaijan": "Azerbaijan",
    "azerbaijan": "Azerbaijan",
    "republic of armenia": "Armenia",
    "armenia": "Armenia",
    "republic of rwanda": "Rwanda",
    "rwanda": "Rwanda",
    "republic of palau": "Palau",
    "palau": "Palau",
    "republic of the marshall islands": "Marshall Islands",
    "marshall islands": "Marshall Islands",
    "republic of lebanon": "Lebanon",
    "lebanese republic": "Lebanon",
    "lebanon": "Lebanon",
    "syrian arab republic": "Syria",
    "syria": "Syria",
    "islamic republic of iran": "Iran",
    "iran": "Iran",
    "islamic republic of pakistan": "Pakistan",
    "pakistan": "Pakistan",
    "people's democratic republic of algeria": "Algeria",
    "algeria": "Algeria",
    "republic of austria": "Austria",
    "austria": "Austria",
    "swaziland": "Eswatini",
    "eswatini": "Eswatini",
    "commonwealth of australia": "Australia",
    "australia": "Australia",
    "guatamala": "Guatemala",
    "guatemala": "Guatemala",
    "brunei darussalum": "Brunei",
    "brunei darussalem": "Brunei",
    "brunei darussalam": "Brunei",
    "brunei": "Brunei",
    "palestinian national authority": "Palestinian Authority",
    "palestinian authority": "Palestinian Authority",
    "palestinian": "Palestinian Authority",
    "democratic republic of timor-leste": "Timor-Leste",
    "timor-leste": "Timor-Leste",
    "union of the comoros": "Comoros",
    "comoros": "Comoros",
    "principality of monaco": "Monaco",
    "monaco": "Monaco",
    "holy see": "Vatican City",
    "vatican city": "Vatican City",
    "republic of tatarstan": "Russia",
    "portuguese republic": "Portugal",
    "portugal": "Portugal",
    "st. kitts, west indies": "Saint Kitts and Nevis",
    "saint kitts and nevis": "Saint Kitts and Nevis",
}

_LEADING_THE_RE = re.compile(r"^the\s+", re.IGNORECASE)


def _normalize_key(text: str) -> str:
    key = re.sub(r"\s+", " ", text.strip().lower())
    key = _LEADING_THE_RE.sub("", key)
    return key


def canonicalize_country(raw: str | None) -> dict:
    """Canonicalize a donor_country value.

    Returns a dict with:
      - country: canonical name for country-level rollups (None if unknown)
      - country_iso3: ISO 3166-1 alpha-3 code (None if not a sovereign state
        we have a code for, e.g. an organization or unresolved name)
      - entity_type: "country", "organization", "subnational", or "unknown"
    """
    text = (raw or "").strip()
    if not text:
        return {"country": None, "country_iso3": None, "entity_type": "unknown"}

    key = _normalize_key(text)

    if key in _JUNK_COUNTRY_VALUES:
        return {"country": None, "country_iso3": None, "entity_type": "unknown"}

    if key in _ORG_ALIASES:
        name = _ORG_ALIASES[key]
        return {"country": name, "country_iso3": None, "entity_type": "organization"}

    if key in _SUBNATIONAL_ALIASES:
        parent = _SUBNATIONAL_ALIASES[key]
        return {"country": parent, "country_iso3": ISO3.get(parent), "entity_type": "subnational"}

    if key in _COUNTRY_ALIASES:
        name = _COUNTRY_ALIASES[key]
        return {"country": name, "country_iso3": ISO3.get(name), "entity_type": "country"}

    # Fallback: the value isn't a known variant. Use it as its own canonical
    # name (preserving original casing, but with a leading "the" dropped for
    # consistency and lookup) so nothing is dropped, and still look up an
    # ISO3 code in case it's already a standard name we just haven't seen a
    # variant of.
    display = _LEADING_THE_RE.sub("", text)
    return {"country": display, "country_iso3": ISO3.get(display), "entity_type": "country"}


# ISO 3166-1 alpha-3 codes for canonical country names used above, plus a
# handful of non-ISO entries (Taiwan, Vatican City, Kosovo, Palestinian
# Authority, Hong Kong) that are meaningful "donor countries" in this dataset
# even though they aren't UN member states.
ISO3 = {
    "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA", "Andorra": "AND", "Angola": "AGO",
    "Antigua and Barbuda": "ATG", "Argentina": "ARG", "Armenia": "ARM", "Australia": "AUS",
    "Austria": "AUT", "Azerbaijan": "AZE", "Bahamas": "BHS", "Bahrain": "BHR", "Bangladesh": "BGD",
    "Barbados": "BRB", "Belarus": "BLR", "Belgium": "BEL", "Belize": "BLZ", "Benin": "BEN",
    "Bhutan": "BTN", "Bolivia": "BOL", "Bosnia and Herzegovina": "BIH", "Botswana": "BWA",
    "Brazil": "BRA", "Brunei": "BRN", "Bulgaria": "BGR", "Burkina Faso": "BFA", "Burundi": "BDI",
    "Cambodia": "KHM", "Cameroon": "CMR", "Canada": "CAN", "Cabo Verde": "CPV", "Cook Islands": "COK",
    "Central African Republic": "CAF", "Chad": "TCD", "Chile": "CHL", "China": "CHN",
    "Colombia": "COL", "Comoros": "COM", "Costa Rica": "CRI", "Croatia": "HRV", "Cuba": "CUB",
    "Cyprus": "CYP", "Czech Republic": "CZE", "Democratic Republic of the Congo": "COD",
    "Denmark": "DNK", "Djibouti": "DJI", "Dominican Republic": "DOM", "Ecuador": "ECU",
    "Egypt": "EGY", "El Salvador": "SLV", "Equatorial Guinea": "GNQ", "Eritrea": "ERI",
    "Estonia": "EST", "Eswatini": "SWZ", "Ethiopia": "ETH", "Fiji": "FJI", "Finland": "FIN",
    "France": "FRA", "Gabon": "GAB", "Gambia": "GMB", "Georgia": "GEO", "Germany": "DEU",
    "Ghana": "GHA", "Greece": "GRC", "Guatemala": "GTM", "Guinea": "GIN", "Guyana": "GUY",
    "Haiti": "HTI", "Honduras": "HND", "Hong Kong": "HKG", "Hungary": "HUN", "Iceland": "ISL",
    "India": "IND", "Indonesia": "IDN", "Iran": "IRN", "Iraq": "IRQ", "Ireland": "IRL",
    "Israel": "ISR", "Italy": "ITA", "Jamaica": "JAM", "Japan": "JPN", "Jordan": "JOR",
    "Kazakhstan": "KAZ", "Kenya": "KEN", "Kosovo": "XKX", "Kuwait": "KWT", "Kyrgyzstan": "KGZ",
    "Laos": "LAO", "Latvia": "LVA", "Lebanon": "LBN", "Liberia": "LBR", "Libya": "LBY",
    "Liechtenstein": "LIE", "Lithuania": "LTU", "Luxembourg": "LUX", "Madagascar": "MDG",
    "Malawi": "MWI", "Malaysia": "MYS", "Maldives": "MDV", "Mali": "MLI", "Malta": "MLT",
    "Marshall Islands": "MHL", "Mauritania": "MRT", "Mauritius": "MUS", "Mexico": "MEX",
    "Moldova": "MDA", "Monaco": "MCO", "Mongolia": "MNG", "Montenegro": "MNE", "Morocco": "MAR",
    "Mozambique": "MOZ", "Myanmar": "MMR", "Namibia": "NAM", "Nepal": "NPL", "Netherlands": "NLD",
    "New Zealand": "NZL", "Nicaragua": "NIC", "Niger": "NER", "Nigeria": "NGA",
    "North Korea": "PRK", "North Macedonia": "MKD", "Norway": "NOR", "Oman": "OMN",
    "Pakistan": "PAK", "Palau": "PLW", "Palestinian Authority": "PSE", "Panama": "PAN",
    "Papua New Guinea": "PNG", "Paraguay": "PRY", "Peru": "PER", "Philippines": "PHL",
    "Poland": "POL", "Portugal": "PRT", "Qatar": "QAT", "Republic of the Congo": "COG",
    "Romania": "ROU", "Russia": "RUS", "Rwanda": "RWA", "Saudi Arabia": "SAU",
    "Saint Kitts and Nevis": "KNA",
    "Senegal": "SEN", "Serbia": "SRB", "Singapore": "SGP", "Slovakia": "SVK",
    "Slovenia": "SVN", "South Africa": "ZAF", "South Korea": "KOR", "South Sudan": "SSD",
    "Spain": "ESP", "Sri Lanka": "LKA", "Sudan": "SDN", "Suriname": "SUR", "Sweden": "SWE",
    "Switzerland": "CHE", "Syria": "SYR", "Taiwan": "TWN", "Tajikistan": "TJK",
    "Tanzania": "TZA", "Thailand": "THA", "Timor-Leste": "TLS", "Togo": "TGO",
    "Trinidad and Tobago": "TTO", "Tunisia": "TUN", "Turkey": "TUR", "Turkmenistan": "TKM",
    "Uganda": "UGA", "Ukraine": "UKR", "United Arab Emirates": "ARE", "United Kingdom": "GBR",
    "United States": "USA",
    "Uruguay": "URY", "Uzbekistan": "UZB", "Vanuatu": "VUT", "Vatican City": "VAT",
    "Venezuela": "VEN", "Vietnam": "VNM", "Yemen": "YEM", "Zambia": "ZMB", "Zimbabwe": "ZWE",
    "Côte d'Ivoire": "CIV",
}
