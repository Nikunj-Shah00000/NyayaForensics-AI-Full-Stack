from pathlib import Path
from fastapi import FastAPI,Depends,UploadFile,File,Form,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from .core.config import settings
from .models.entities import Base,Case,Evidence,Artifact,Event,Anomaly
from .schemas.api import *
from .services.core import sha256_file,extract_text,extract_entities,detect,grounded
import uuid
engine=create_engine(settings.database_url,connect_args={'check_same_thread':False} if settings.database_url.startswith('sqlite') else {})
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False); Base.metadata.create_all(engine); Path(settings.upload_dir).mkdir(parents=True,exist_ok=True)
def db():
 d=SessionLocal()
 try:yield d
 finally:d.close()
app=FastAPI(title=settings.app_name); app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
@app.get('/')
def root():return {'name':settings.app_name,'status':'online'}
@app.get('/health')
def health():return {'status':'healthy'}
@app.post('/api/cases',response_model=CaseOut)
def create_case(x:CaseCreate,d:Session=Depends(db)):
 if d.query(Case).filter(Case.case_number==x.case_number).first():raise HTTPException(409,'Case exists')
 o=Case(**x.model_dump());d.add(o);d.commit();d.refresh(o);return o
@app.get('/api/cases',response_model=list[CaseOut])
def cases(d:Session=Depends(db)):return d.query(Case).order_by(Case.created_at.desc()).all()
@app.post('/api/evidence/upload',response_model=EvidenceOut)
async def upload(case_id:int=Form(...),source:str=Form('uploaded'),file:UploadFile=File(...),d:Session=Depends(db)):
 eid='E-'+uuid.uuid4().hex[:10].upper(); dest=Path(settings.upload_dir)/(eid+'_'+Path(file.filename).name); size=0
 with dest.open('wb') as o:
  while c:=await file.read(1024*1024):o.write(c);size+=len(c)
 e=Evidence(case_id=case_id,evidence_id=eid,filename=file.filename,mime_type=file.content_type or 'application/octet-stream',size=size,sha256=sha256_file(dest),source=source,storage_path=str(dest),integrity_status='VERIFIED');d.add(e);d.commit();d.refresh(e)
 for x in extract_entities(extract_text(dest)):d.add(Artifact(case_id=case_id,evidence_id=eid,artifact_type=x['type'],value=x['value'],source='text-extraction'))
 d.commit();return e
@app.get('/api/evidence/{case_id}',response_model=list[EvidenceOut])
def evidence(case_id:int,d:Session=Depends(db)):return d.query(Evidence).filter(Evidence.case_id==case_id).all()
@app.post('/api/demo/seed')
def seed(d:Session=Depends(db)):
 c=d.query(Case).filter(Case.case_number=='CASE-2026-001').first()
 if not c:c=Case(case_number='CASE-2026-001',title='Synthetic Insider Data Transfer',description='Synthetic demo investigation.');d.add(c);d.commit();d.refresh(c)
 if d.query(Event).filter(Event.case_id==c.id).count()==0:
  from datetime import datetime
  rows=[('E001','login','2026-09-15T09:41:12+00:00','system_log','USER-A'),('E002','usb_connect','2026-09-15T09:43:08+00:00','system_log','USB-02'),('E003','file_open','2026-09-15T09:47:31+00:00','filesystem','F117'),('E004','file_copy','2026-09-15T09:51:02+00:00','filesystem','F117'),('E005','archive_create','2026-09-15T09:54:11+00:00','filesystem','F201'),('E006','network_connection','2026-09-15T10:01:47+00:00','network_log','103.0.0.17'),('E007','upload','2026-09-15T10:04:22+00:00','network_log','F201')]
  for eid,t,ts,s,ent in rows:d.add(Event(case_id=c.id,event_id=eid,event_type=t,timestamp=datetime.fromisoformat(ts),source=s,entity_id=ent))
  for i,n in enumerate(['browser_history.db','system_events.log','confidential.pdf'],1):d.add(Evidence(case_id=c.id,evidence_id=f'EVID-{i:03d}',filename=n,mime_type='application/octet-stream',size=1024*i,sha256=str(i)*64,source='synthetic-demo',storage_path='synthetic/'+n,integrity_status='VERIFIED'))
  d.commit()
 return {'case_id':c.id,'message':'Synthetic case ready'}
@app.get('/api/investigation/{cid}/timeline')
def timeline(cid:int,d:Session=Depends(db)):
 return [{'event_id':e.event_id,'event_type':e.event_type,'timestamp':e.timestamp.isoformat(),'source':e.source,'entity_id':e.entity_id,'confidence':e.confidence,'observed_or_inferred':e.observed_or_inferred} for e in d.query(Event).filter(Event.case_id==cid).order_by(Event.timestamp).all()]
@app.post('/api/investigation/{cid}/analyze')
def analyze(cid:int,d:Session=Depends(db)):
 es=d.query(Event).filter(Event.case_id==cid).order_by(Event.timestamp).all();fs=detect(es)
 for f in fs:d.add(Anomaly(case_id=cid,**f))
 d.commit();return {'findings':fs}
@app.get('/api/investigation/{cid}/anomalies')
def anomalies(cid:int,d:Session=Depends(db)):
 return [{'id':a.id,'type':a.type,'severity':a.severity,'description':a.description,'confidence':a.confidence} for a in d.query(Anomaly).filter(Anomaly.case_id==cid).all()]
@app.get('/api/investigation/{cid}/graph')
def graph(cid:int,d:Session=Depends(db)):
 es=d.query(Event).filter(Event.case_id==cid).all();nodes={};edges=[]
 for e in es:
  nodes.setdefault(e.entity_id,{'id':e.entity_id,'type':'entity'}); en='event:'+e.event_id;nodes[en]={'id':en,'type':'event','label':e.event_type};edges.append({'source':e.entity_id,'target':en,'label':e.event_type})
 return {'nodes':list(nodes.values()),'edges':edges}
@app.post('/api/investigation/{cid}/copilot',response_model=CopilotResponse)
def copilot(cid:int,x:CopilotQuery,d:Session=Depends(db)):
 es=d.query(Event).filter(Event.case_id==cid).order_by(Event.timestamp).all();ids=[e.evidence_id for e in d.query(Evidence).filter(Evidence.case_id==cid).all()];a,i=grounded(x.question,es,ids);return CopilotResponse(answer=a,supporting_evidence=i)
