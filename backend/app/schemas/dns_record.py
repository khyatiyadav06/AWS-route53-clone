from datetime import datetime
import ipaddress
import re
from pydantic import BaseModel, Field, field_validator, model_validator

RECORD_TYPES = {"A", "AAAA", "CNAME", "TXT", "MX", "NS", "PTR", "SRV", "CAA"}
HOSTNAME_RE = re.compile(r"^(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)*[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.?$")


def validate_hostname(value: str, field: str = "hostname") -> str:
    value = value.strip()
    if len(value) > 253 or not HOSTNAME_RE.fullmatch(value):
        raise ValueError(f"Invalid {field}")
    return value.lower().rstrip(".")


class DNSRecordCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: str
    ttl: int = Field(default=300, ge=1, le=86400)
    value: str = Field(min_length=1, max_length=4000)
    routing_policy: str = Field(default="Simple", max_length=40)

    @field_validator("type")
    @classmethod
    def valid_type(cls, value: str):
        value = value.upper().strip()
        if value not in RECORD_TYPES:
            raise ValueError("Unsupported record type")
        return value

    @field_validator("name")
    @classmethod
    def valid_name(cls, value: str):
        return validate_hostname(value, "record name")

    @field_validator("routing_policy")
    @classmethod
    def valid_policy(cls, value: str):
        value = value.strip()
        if value not in {"Simple", "Weighted", "Latency", "Failover"}:
            raise ValueError("Unsupported routing policy")
        return value

    @model_validator(mode="after")
    def validate_value_for_type(self):
        value = self.value.strip()
        kind = self.type
        try:
            if kind == "A":
                ipaddress.IPv4Address(value)
            elif kind == "AAAA":
                ipaddress.IPv6Address(value)
            elif kind in {"CNAME", "NS", "PTR"}:
                validate_hostname(value, f"{kind} target")
            elif kind == "MX":
                match = re.fullmatch(r"(\d{1,3})\s+(.+)", value)
                if not match or int(match.group(1)) > 65535:
                    raise ValueError("MX value must be '<priority> <hostname>'")
                validate_hostname(match.group(2), "MX hostname")
            elif kind == "SRV":
                match = re.fullmatch(r"(\d{1,5})\s+(\d{1,5})\s+(\d{1,5})\s+(.+)", value)
                if not match or any(int(match.group(i)) > 65535 for i in range(1, 4)):
                    raise ValueError("SRV value must be '<priority> <weight> <port> <hostname>'")
                validate_hostname(match.group(4), "SRV target")
            elif kind == "CAA":
                if not re.fullmatch(r"\d+\s+[A-Za-z0-9-]+\s+.+", value):
                    raise ValueError("CAA value must be '<flags> <tag> <value>'")
            elif kind == "TXT":
                if not value:
                    raise ValueError("TXT value cannot be empty")
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        return self


class DNSRecordUpdate(DNSRecordCreate):
    pass

class DNSRecordOut(DNSRecordCreate):
    id: int
    hosted_zone_id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class PaginatedRecords(BaseModel):
    items: list[DNSRecordOut]
    page: int
    page_size: int
    total: int
    pages: int
