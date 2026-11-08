import json, os
from pathlib import Path
class DocumentStore:
    """Educational single-process JSON document store; not MongoDB."""
    def __init__(self,path):
        self.path=Path(path)
        self.docs=json.loads(self.path.read_text()) if self.path.exists() else {}
    def save(self):
        tmp=self.path.with_suffix('.tmp')
        tmp.write_text(json.dumps(self.docs,indent=2))
        os.replace(tmp,self.path)
    def insert(self,doc):
        if doc['_id'] in self.docs: raise ValueError('duplicate id')
        self.docs[doc['_id']]=doc
        self.save()
    def find(self,category):
        return [d for d in self.docs.values() if d['category']==category]
    def update(self,key,attributes):
        self.docs[key]['attributes'].update(attributes)
        self.save()
    def delete(self,key):
        del self.docs[key]
        self.save()
