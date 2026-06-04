from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.common.db.connection import get_session
from src.common.db.models import DimSupplier
from src.ingestion_api.models.contracts import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter()

@router.get("/", response_model=list[SupplierResponse])
def get_suppliers(db: Session = Depends(get_session)):
    suppliers = db.query(DimSupplier).all()
    return suppliers

@router.post("/", response_model=SupplierResponse)
def create_supplier(supplier: SupplierCreate, db: Session = Depends(get_session)):
    db_supplier = DimSupplier(
        supplier_code=supplier.supplier_code,
        name=supplier.name,
        location=supplier.location,
        tier=supplier.tier,
        contact_info=supplier.contact_info
    )
    db.add(db_supplier)
    try:
        db.commit()
        db.refresh(db_supplier)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_supplier

@router.put("/{supplier_code}", response_model=SupplierResponse)
def update_supplier(supplier_code: str, update: SupplierUpdate, db: Session = Depends(get_session)):
    db_supplier = db.query(DimSupplier).filter(DimSupplier.supplier_code == supplier_code).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
        
    if update.name is not None:
        db_supplier.name = update.name
    if update.location is not None:
        db_supplier.location = update.location
    if update.tier is not None:
        db_supplier.tier = update.tier
    if update.contact_info is not None:
        db_supplier.contact_info = update.contact_info
        
    try:
        db.commit()
        db.refresh(db_supplier)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_supplier
