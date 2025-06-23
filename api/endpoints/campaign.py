from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.schemas.campaign import CampaignCreate, CampaignOut, CampaignUpdate
from api.managers.campaign_manager import CampaignManager
from api.core.database import get_db

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.post("/", response_model=CampaignOut)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    return CampaignManager.create_campaign(db, campaign)

@router.get("/", response_model=List[CampaignOut])
def get_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CampaignManager.get_campaigns(db, skip=skip, limit=limit)

@router.get("/{campaign_id}", response_model=CampaignOut)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = CampaignManager.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.put("/{campaign_id}", response_model=CampaignOut)
def update_campaign(campaign_id: int, campaign_update: CampaignUpdate, db: Session = Depends(get_db)):
    campaign = CampaignManager.update_campaign(db, campaign_id, campaign_update)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.patch("/{campaign_id}", response_model=CampaignOut)
def partial_update_campaign(campaign_id: int, campaign_update: CampaignUpdate, db: Session = Depends(get_db)):
    try:
        campaign = CampaignManager.update_campaign(db, campaign_id, campaign_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.delete("/{campaign_id}", response_model=dict)
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    success = CampaignManager.delete_campaign(db, campaign_id)
    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"ok": True}
