from fastapi import APIRouter
from app.services.omniroute import omniroute
from app.services.earthdial import earthdial
router=APIRouter()
@router.get('/health')
def health(): return {'status':'ok','omniroute_configured':omniroute.configured(),'earthdial_configured':earthdial.configured()}
@router.get('/api/model/health')
def model_health():
    out={'omniroute':{'configured':omniroute.configured(),'base_url':omniroute.base_url,'model':omniroute.model},'earthdial':None}
    if earthdial.configured():
        try: out['earthdial']=earthdial.health()
        except Exception as e: out['earthdial']={'configured':True,'reachable':False,'error':str(e)}
    else: out['earthdial']={'configured':False}
    return out
