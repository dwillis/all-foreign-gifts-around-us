"""Pydantic schemas for gift records, shared across the extraction pipeline."""

from pydantic import BaseModel


class GiftRecord(BaseModel):
    name_and_title: str
    gift_description: str
    received: str
    estimated_value: str
    disposition: str
    foreign_donor: str
    circumstances: str


class GiftRecordList(BaseModel):
    gifts: list[GiftRecord]


class DonorDetails(BaseModel):
    donor_name: str
    donor_title: str
    donor_country: str


class RecipientDetails(BaseModel):
    recipient_name: str
    recipient_title: str
