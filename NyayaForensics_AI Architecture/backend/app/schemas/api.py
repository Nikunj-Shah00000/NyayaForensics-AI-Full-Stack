from datetime import datetime
from pydantic import BaseModel,Field
class CaseCreate(BaseModel): case_number:str; title:str; description:str=''
class CaseOut(CaseCreate):
 id:int; status:str; created_at:datetime
 class Config: from_attributes=True
class EvidenceOut(BaseModel):
 id:int; evidence_id:str; filename:str; mime_type:str; size:int; sha256:str; integrity_status:str; source:str; acquired_at:datetime
 class Config: from_attributes=True
class CopilotQuery(BaseModel): question:str=Field(min_length=2,max_length=1000)
class CopilotResponse(BaseModel): answer:str; supporting_evidence:list[str]; status:str='AI-assisted; investigator review required'
