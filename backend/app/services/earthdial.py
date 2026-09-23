import requests
from app.config import settings
class EarthDialError(RuntimeError): pass
class EarthDialClient:
    def __init__(self): self.base_url=settings.kaggle_ngrok_url; self.timeout=settings.request_timeout
    def configured(self): return bool(self.base_url)
    def health(self):
        if not self.configured(): raise EarthDialError('KAGGLE_NGROK_URL is not configured.')
        try:
            r=requests.get(self.base_url+'/health',headers={'ngrok-skip-browser-warning':'true'},timeout=15); r.raise_for_status(); return r.json()
        except Exception as e: raise EarthDialError(f'EarthDial health failed: {e}') from e
    def infer(self, file, query, tag='[caption]'):
        if not self.configured(): raise EarthDialError('KAGGLE_NGROK_URL is not configured.')
        name,content,ctype=file
        try:
            r=requests.post(self.base_url+'/infer', files={'file':(name,content,ctype or 'application/octet-stream')}, data={'query':query,'tag':tag}, headers={'ngrok-skip-browser-warning':'true'}, timeout=self.timeout)
        except requests.RequestException as e: raise EarthDialError(f'EarthDial request failed: {e}') from e
        if r.status_code>=400: raise EarthDialError(f'EarthDial HTTP {r.status_code}: {r.text[:1200]}')
        return r.json()
    def infer_multi(self, files, query, tag='[changedet]'):
        if not self.configured(): raise EarthDialError('KAGGLE_NGROK_URL is not configured.')
        multipart=[('files',(n,c,t or 'application/octet-stream')) for n,c,t in files]
        r=requests.post(self.base_url+'/infer_multi',files=multipart,data={'query':query,'tag':tag},headers={'ngrok-skip-browser-warning':'true'},timeout=self.timeout)
        if r.status_code==404: raise EarthDialError('MULTI_ENDPOINT_NOT_AVAILABLE')
        if r.status_code>=400: raise EarthDialError(f'EarthDial multi HTTP {r.status_code}: {r.text[:1200]}')
        return r.json()
earthdial=EarthDialClient()
