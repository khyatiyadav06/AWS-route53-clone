import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DNSRecord, HostedZone
from app.dependencies import get_current_user
from app.schemas.dns_record import DNSRecordCreate, DNSRecordOut, DNSRecordUpdate, PaginatedRecords

router = APIRouter(tags=["DNS Records"])

def ensure_zone(db, zone_id):
    zone = db.get(HostedZone, zone_id)
    if not zone: raise HTTPException(404, "Hosted zone not found")
    return zone

@router.get("/api/hosted-zones/{zone_id}/records", response_model=PaginatedRecords)
def list_records(zone_id: int, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), search: str = "", db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_zone(db, zone_id); q = db.query(DNSRecord).filter(DNSRecord.hosted_zone_id == zone_id)
    if search.strip():
        term=f"%{search.strip()}%"; q=q.filter(or_(DNSRecord.name.ilike(term), DNSRecord.type.ilike(term), DNSRecord.value.ilike(term)))
    total=q.count(); records=q.order_by(DNSRecord.name.asc()).offset((page-1)*page_size).limit(page_size).all()
    return PaginatedRecords(items=records, page=page, page_size=page_size, total=total, pages=max(1, math.ceil(total/page_size)))

@router.get("/api/records/{record_id}", response_model=DNSRecordOut)
def get_record(record_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    r=db.get(DNSRecord, record_id)
    if not r: raise HTTPException(404,"Record not found")
    return r

@router.post("/api/hosted-zones/{zone_id}/records", response_model=DNSRecordOut, status_code=201)
def create_record(zone_id: int, payload: DNSRecordCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ensure_zone(db, zone_id)
    r=DNSRecord(hosted_zone_id=zone_id, name=payload.name.strip().lower(), type=payload.type, ttl=payload.ttl, value=payload.value.strip(), routing_policy=payload.routing_policy)
    db.add(r); db.commit(); db.refresh(r); return r

@router.put("/api/records/{record_id}", response_model=DNSRecordOut)
def update_record(record_id: int, payload: DNSRecordUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    r=db.get(DNSRecord, record_id)
    if not r: raise HTTPException(404,"Record not found")
    r.name=payload.name.strip().lower(); r.type=payload.type; r.ttl=payload.ttl; r.value=payload.value.strip(); r.routing_policy=payload.routing_policy
    db.commit(); db.refresh(r); return r

@router.delete("/api/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    r=db.get(DNSRecord, record_id)
    if not r: raise HTTPException(404,"Record not found")
    db.delete(r); db.commit(); return {"message":"Record deleted successfully"}
