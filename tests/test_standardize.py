from foreign_gifts.standardize import canonicalize_country, canonicalize_disposition, normalize_date


def test_normalize_date_full_date():
    assert normalize_date("2005-03-09") == ("2005-03-09", "day")


def test_normalize_date_missing_markers_are_unified():
    for raw in ("", "Unknown", "unknown", "UNKN", None):
        assert normalize_date(raw) == (None, "unknown")


def test_normalize_date_partial_precision():
    assert normalize_date("2010-07") == ("2010-07", "month")
    assert normalize_date("2012") == ("2012", "year")


def test_normalize_date_range_keeps_start_and_flags_precision():
    assert normalize_date("2014-05-19-2014-05-24") == ("2014-05-19", "range")
    assert normalize_date("2022-05-27–2022-06-05") == ("2022-05-27", "range")


def test_canonicalize_disposition_collapses_gsa_variants():
    variants = [
        "Pending Transfer to General Services Administration",
        "Pending transfer to General Services Administration",
        "Pending Transfer to GSA",
        "Pending transfer to GSA",
        "Foreign Gift Locker 5D333. Pending transfer to General Services Administration",
    ]
    for v in variants:
        assert canonicalize_disposition(v) == "Pending Transfer to GSA"


def test_canonicalize_disposition_collapses_nara_variants():
    variants = ["National Archives and Records Administration", "Transferred to NARA", "Archives Foreign"]
    for v in variants:
        assert canonicalize_disposition(v) == "Transferred to NARA"


def test_canonicalize_disposition_purchased_takes_priority_over_gsa():
    assert canonicalize_disposition("Purchased by recipient from General Services Administration") == (
        "Purchased by Recipient"
    )


def test_canonicalize_disposition_marker_leak_maps_to_unknown():
    for v in ("Rec'd", "", "N/A", None, "Disposition", "Disposition-"):
        assert canonicalize_disposition(v) == "Unknown"


def test_canonicalize_disposition_unrecognized_falls_to_other():
    assert canonicalize_disposition("Currently stored in NAC05-01-111-F suite") == "Other"


def test_canonicalize_country_collapses_china_variants():
    for v in ("People's Republic of China", "the People's Republic of China", "China"):
        result = canonicalize_country(v)
        assert result["country"] == "China"
        assert result["country_iso3"] == "CHN"
        assert result["entity_type"] == "country"


def test_canonicalize_country_collapses_korea_variants():
    for v in ("Republic of Korea", "South Korea", "Korea", "The Republic of Korea"):
        assert canonicalize_country(v)["country"] == "South Korea"
    assert canonicalize_country("Democratic People's Republic of Korea")["country"] == "North Korea"


def test_canonicalize_country_saudi_variants():
    for v in ("Saudi Arabia", "Kingdom of Saudi Arabia", "the Kingdom of Saudi Arabia"):
        assert canonicalize_country(v)["country"] == "Saudi Arabia"


def test_canonicalize_country_junk_values_are_unknown():
    for v in ("", None, "<UNKNOWN>", "Country Unknown", "Government", "National"):
        result = canonicalize_country(v)
        assert result["country"] is None
        assert result["entity_type"] == "unknown"


def test_canonicalize_country_organizations_flagged():
    result = canonicalize_country("European Union")
    assert result["country"] == "European Union"
    assert result["country_iso3"] is None
    assert result["entity_type"] == "organization"


def test_canonicalize_country_subnational_rolls_up_to_parent():
    result = canonicalize_country("Dubai")
    assert result["country"] == "United Arab Emirates"
    assert result["country_iso3"] == "ARE"
    assert result["entity_type"] == "subnational"


def test_canonicalize_country_unmatched_passes_through():
    result = canonicalize_country("Bolivia")
    assert result["country"] == "Bolivia"
    assert result["country_iso3"] == "BOL"
    assert result["entity_type"] == "country"
