import math
import re
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import HostedZone
from app.schemas.hosted_zone import HostedZoneCreate, HostedZoneOut, HostedZoneUpdate, PaginatedZones

router = APIRouter(prefix="/api/hosted-zones", tags=["Hosted Zones"])
DOMAIN_RE = re.compile(r"^(?=.{3,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$", re.I)


def normalize_domain(value: str) -> str:
    name = value.strip().lower().rstrip(".")
    if not DOMAIN_RE.fullmatch(name):
        raise HTTPException(status_code=422, detail="Enter a valid domain name such as example.com")
    return name


def serialize(z: HostedZone):
    return HostedZoneOut(
        id=z.id, name=z.name, zone_id=z.zone_id, description=z.description or "",
        zone_type=z.zone_type, created_at=z.created_at, record_count=len(z.records)
    )

@router.get("", response_model=PaginatedZones)
def list_zones(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), search: str = "", db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(HostedZone)
    if search.strip():
        term = f"%{search.strip()}%"
        q = q.filter(or_(HostedZone.name.ilike(term), HostedZone.zone_id.ilike(term), HostedZone.description.ilike(term)))
    total = q.count()
    zones = q.order_by(HostedZone.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedZones(items=[serialize(z) for z in zones], page=page, page_size=page_size, total=total, pages=max(1, math.ceil(total / page_size)))

@router.get("/{zone_id}", response_model=HostedZoneOut)
def get_zone(zone_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    z = db.get(HostedZone, zone_id)
    if not z:
        raise HTTPException(404, "Hosted zone not found")
    return serialize(z)

@router.post("", response_model=HostedZoneOut, status_code=201)
def create_zone(payload: HostedZoneCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    name = normalize_domain(payload.name)
    if payload.zone_type not in {"Public", "Private"}:
        raise HTTPException(422, "Zone type must be Public or Private")
    if db.query(HostedZone).filter(HostedZone.name == name).first():
        raise HTTPException(409, "Hosted zone already exists")
    z = HostedZone(name=name, zone_id="Z" + uuid4().hex[:10].upper(), description=payload.description.strip(), zone_type=payload.zone_type)
    db.add(z)
    db.commit()
    db.refresh(z)
    return serialize(z)

@router.put("/{zone_id}", response_model=HostedZoneOut)
def update_zone(zone_id: int, payload: HostedZoneUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    z = db.get(HostedZone, zone_id)
    if not z:
        raise HTTPException(404, "Hosted zone not found")
    name = normalize_domain(payload.name)
    if payload.zone_type not in {"Public", "Private"}:
        raise HTTPException(422, "Zone type must be Public or Private")
    duplicate = db.query(HostedZone).filter(HostedZone.name == name, HostedZone.id != zone_id).first()
    if duplicate:
        raise HTTPException(409, "Another hosted zone already uses that name")
    z.name, z.description, z.zone_type = name, payload.description.strip(), payload.zone_type
    db.commit()
    db.refresh(z)
    return serialize(z)

@router.delete("/{zone_id}")
def delete_zone(zone_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    z = db.get(HostedZone, zone_id)
    if not z:
        raise HTTPException(404, "Hosted zone not found")
    db.delete(z)
    db.commit()
    return {"message": "Hosted zone deleted successfully"}
