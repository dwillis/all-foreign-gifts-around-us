from foreign_gifts.officeholders import lookup_tenure, resolve_recipient_name


def test_lookup_tenure_resolves_bush_era_president():
    assert lookup_tenure("president", "2005-03-09") == "George W. Bush"


def test_lookup_tenure_resolves_across_transitions():
    assert lookup_tenure("president", "2009-01-19") == "George W. Bush"
    assert lookup_tenure("president", "2009-01-20") == "Barack Obama"


def test_lookup_tenure_unknown_office_returns_none():
    assert lookup_tenure("secretary of energy", "2010-01-01") is None


def test_resolve_recipient_name_fixes_the_biden_misattribution_bug():
    # The real bug: a 2005 gift with no personal name in the source text
    # ("President" only) was enriched to "Joseph R. Biden Jr." because that's
    # who was president when enrichment ran, not who received the gift.
    name, source = resolve_recipient_name(
        name_and_title="President",
        recipient_name="Joseph R. Biden Jr.",
        received_date="2005-03-09",
        received_precision="day",
    )
    assert name == "George W. Bush"
    assert source == "date-resolved"


def test_resolve_recipient_name_leaves_named_records_alone():
    name, source = resolve_recipient_name(
        name_and_title="The Honorable Jane Doe, Secretary of State",
        recipient_name="Jane Doe",
        received_date="2005-03-09",
        received_precision="day",
    )
    assert name == "Jane Doe"
    assert source is None


def test_resolve_recipient_name_skips_imprecise_dates():
    name, source = resolve_recipient_name(
        name_and_title="President",
        recipient_name="President",
        received_date="2005",
        received_precision="year",
    )
    assert name == "President"
    assert source is None


def test_resolve_recipient_name_skips_unknown_dates():
    name, source = resolve_recipient_name(
        name_and_title="First Lady",
        recipient_name="",
        received_date=None,
        received_precision="unknown",
    )
    assert name == ""
    assert source is None
