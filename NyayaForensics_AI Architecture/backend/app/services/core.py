import hashlib,re
from pathlib import Path
def sha256_file(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  while c:=f.read(1024*1024): h.update(c)
 return h.hexdigest()
P={'ip':r'\b(?:\d{1,3}\.){3}\d{1,3}\b','email':r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b','url':r'https?://[^\s<>"\']+'}
def extract_entities(text):
 return [{'type':k,'value':v} for k,p in P.items() for v in sorted(set(re.findall(p,text)))]
def extract_text(path):
 try:return Path(path).read_bytes()[:2000000].decode('utf8','ignore')
 except:return ''
def detect(events):
 types={e.event_type for e in events}; wanted={'usb_connect','file_open','file_copy','archive_create','network_connection','upload'}; score=len(types&wanted)/len(wanted); out=[]
 if score>=.66: out.append({'type':'correlated_activity','severity':'HIGH','description':'Multiple event types form a potentially suspicious access-to-transfer sequence.','confidence':round(score,2)})
 return out
def grounded(question,events,eids):
 if any(x in question.lower() for x in ['upload','transfer','exfiltration','suspicious']):
  r=[e for e in events if e.event_type in {'usb_connect','file_copy','archive_create','network_connection','upload'}]
  if r:return 'The case contains a correlated sequence: '+' → '.join(e.event_type for e in sorted(r,key=lambda x:x.timestamp))+'. This is an investigative lead, not a definitive conclusion.',eids[:8]
 return 'The indexed evidence is insufficient for a deterministic answer. Review the evidence graph and original artifacts.',eids[:8]
