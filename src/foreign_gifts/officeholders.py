"""Date-aware officeholder resolution.

Some Federal Register entries give only a bare title ("President", "Vice
President", "First Lady") with no personal name at all — the source text
never says who. When that happens, the LLM enrichment step has nothing to
extract from and has been observed to either guess whoever was in the news at
enrichment time (attributing 2005 Bush-era gifts to "Joseph R. Biden Jr.") or
leave the title itself as the name. Both are wrong, and wrong in a way that
misattributes real historical gifts to the wrong person.

This module fixes that deterministically: given the office and the date the
gift was received, look up who actually held that office on that date.
"""

# (start_date, end_date, name) — end dates are exclusive (the incoming
# officeholder is credited on inauguration/swearing-in day itself). Only
# offices and eras that actually appear as bare-title records in this dataset
# are listed; extend as the dataset grows or new bare-title offices show up.
_TENURES = {
    "president": [
        ("2001-01-20", "2009-01-20", "George W. Bush"),
        ("2009-01-20", "2017-01-20", "Barack Obama"),
        ("2017-01-20", "2021-01-20", "Donald J. Trump"),
        ("2021-01-20", "2025-01-20", "Joseph R. Biden Jr."),
        ("2025-01-20", "2029-01-20", "Donald J. Trump"),
    ],
    "vice president": [
        ("2001-01-20", "2009-01-20", "Dick Cheney"),
        ("2009-01-20", "2017-01-20", "Joseph R. Biden Jr."),
        ("2017-01-20", "2021-01-20", "Michael R. Pence"),
        ("2021-01-20", "2025-01-20", "Kamala D. Harris"),
        ("2025-01-20", "2029-01-20", "JD Vance"),
    ],
    "first lady": [
        ("2001-01-20", "2009-01-20", "Laura Bush"),
        ("2009-01-20", "2017-01-20", "Michelle Obama"),
        ("2017-01-20", "2021-01-20", "Melania Trump"),
        ("2021-01-20", "2025-01-20", "Dr. Jill Biden"),
        ("2025-01-20", "2029-01-20", "Melania Trump"),
    ],
    "secretary of state": [
        ("2005-01-26", "2009-01-20", "Condoleezza Rice"),
        ("2009-01-21", "2013-02-01", "Hillary Clinton"),
        ("2013-02-01", "2017-01-20", "John Kerry"),
        ("2017-02-01", "2018-03-31", "Rex Tillerson"),
        ("2018-04-26", "2021-01-20", "Mike Pompeo"),
        ("2021-01-20", "2025-01-20", "Antony Blinken"),
        ("2025-01-20", "2029-01-20", "Marco Rubio"),
    ],
    "secretary of defense": [
        ("2005-01-01", "2006-12-18", "Donald H. Rumsfeld"),
        ("2006-12-18", "2011-07-01", "Robert M. Gates"),
        ("2011-07-01", "2013-02-27", "Leon E. Panetta"),
        ("2013-02-27", "2015-02-17", "Chuck Hagel"),
        ("2015-02-17", "2017-01-20", "Ash Carter"),
        ("2017-01-20", "2019-01-01", "James Mattis"),
        ("2019-07-23", "2020-11-09", "Mark Esper"),
        ("2020-11-09", "2021-01-20", "Christopher Miller"),
        ("2021-01-20", "2025-01-20", "Lloyd Austin"),
        ("2025-01-20", "2029-01-20", "Pete Hegseth"),
    ],
}


def _match_generic_office(name_and_title: str) -> str | None:
    """Return the office key if name_and_title is a bare office title with no
    personal name attached, else None."""
    text = (name_and_title or "").strip().lower()
    if text.startswith("the "):
        text = text[4:].strip()
    return text if text in _TENURES else None


def lookup_tenure(office: str, date: str) -> str | None:
    """Return who held `office` on `date` (yyyy-mm-dd), or None if unknown.

    End dates are exclusive so an inauguration day itself resolves to the
    incoming officeholder, not the outgoing one.
    """
    for start, end, name in _TENURES.get(office, []):
        if start <= date < end:
            return name
    return None


def resolve_recipient_name(
    name_and_title: str,
    recipient_name: str,
    received_date: str | None,
    received_precision: str,
) -> tuple[str, str | None]:
    """Return (recipient_name, source) for a gift record.

    If `name_and_title` is nothing but a bare, recognized office title (no
    personal name in the source text), the recipient name is replaced with
    whoever actually held that office on `received_date`, and source is
    "date-resolved". Otherwise the original `recipient_name` is returned
    unchanged with source None.

    Resolution only happens for day-precision dates: month/year-only or
    unknown dates are too close to plausible inauguration-day transitions to
    resolve safely.
    """
    office = _match_generic_office(name_and_title)
    if office is None or received_precision != "day" or not received_date:
        return recipient_name, None

    resolved = lookup_tenure(office, received_date)
    if resolved is None:
        return recipient_name, None

    return resolved, "date-resolved"
