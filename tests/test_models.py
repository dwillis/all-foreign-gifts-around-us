import json
from pathlib import Path

from foreign_gifts.models import DonorDetails, GiftRecord, GiftRecordList, RecipientDetails

FIXTURES = Path(__file__).parent / "fixtures"


def test_gift_record_validates_sample_records():
    records = json.loads((FIXTURES / "sample_records.json").read_text())
    for record in records:
        GiftRecord(**record)


def test_gift_record_list_wraps_records():
    records = json.loads((FIXTURES / "sample_records.json").read_text())
    parsed = GiftRecordList(gifts=records)
    assert len(parsed.gifts) == len(records)


def test_donor_details_schema():
    details = DonorDetails(donor_name="Michael Martin", donor_title="Prime Minister", donor_country="Ireland")
    assert details.donor_country == "Ireland"


def test_recipient_details_schema():
    details = RecipientDetails(recipient_name="Joseph R. Biden Jr.", recipient_title="President of the United States")
    assert details.recipient_name == "Joseph R. Biden Jr."
