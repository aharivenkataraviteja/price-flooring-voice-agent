from pydantic import BaseModel
from typing import Optional


class LookupCustomerRequest(BaseModel):
    phone_number: str


class SaveCustomerRequest(BaseModel):
    phone_number: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CreateLeadRequest(BaseModel):
    phone_number: str
    customer_name: str
    email: Optional[str] = None
    property_address: Optional[str] = None
    project_type: Optional[str] = None
    flooring_interest: Optional[str] = None


class AddLeadDetailsRequest(BaseModel):
    lead_id: int
    rooms_involved: Optional[str] = None
    approximate_sqft: Optional[int] = None
    residential_or_commercial: Optional[str] = None
    material_only_or_install: Optional[str] = None
    timeline: Optional[str] = None
    budget_range: Optional[str] = None
    preferred_callback: Optional[str] = None
    notes: Optional[str] = None


class GetAvailableSlotsRequest(BaseModel):
    preferred_date: Optional[str] = None
    appointment_type: Optional[str] = "estimate"


class ConfirmAppointmentRequest(BaseModel):
    lead_id: int
    slot_id: Optional[int] = None
    customer_name: str
    phone_number: str
    appointment_type: Optional[str] = "estimate"
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    notes: Optional[str] = None


class CheckStoreStatusRequest(BaseModel):
    pass
