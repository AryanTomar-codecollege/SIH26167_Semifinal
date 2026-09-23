import json, re, requests
from app.config import settings

class OmniRouteError(RuntimeError): pass

class OmniRouteClient:
    def __init__(self):
        self.base_url=settings.omniroute_base_url; self.api_key=settings.omniroute_api_key
        self.model=settings.omniroute_model; self.timeout=settings.request_timeout
    def configured(self): return bool(self.base_url and self.api_key)
    def chat(self, messages, temperature=0.0, max_tokens=1200):
        if not self.configured(): raise OmniRouteError('OmniRoute is not configured. Put OMNIROUTE_API_KEY in .env.')
        try:
            r=requests.post(self.base_url+'/chat/completions', headers={'Authorization':f'Bearer {self.api_key}','Content-Type':'application/json'}, json={'model':self.model,'messages':messages,'temperature':temperature,'max_tokens':max_tokens}, timeout=self.timeout)
        except requests.RequestException as e: raise OmniRouteError(f'OmniRoute request failed: {e}') from e
        if r.status_code>=400: raise OmniRouteError(f'OmniRoute HTTP {r.status_code}: {r.text[:1000]}')
        try: content=r.json()['choices'][0]['message']['content']
        except Exception as e: raise OmniRouteError(f'Unexpected OmniRoute response: {r.text[:1200]}') from e
        if isinstance(content,list): content=''.join(x.get('text','') if isinstance(x,dict) else str(x) for x in content)
        return str(content).strip()
    @staticmethod
    def parse_json(text):
        for candidate in [text.strip()]:
            try:
                x=json.loads(candidate); return x if isinstance(x,dict) else None
            except json.JSONDecodeError: pass
        m=re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.S)
        if m:
            try: x=json.loads(m.group(1)); return x if isinstance(x,dict) else None
            except json.JSONDecodeError: pass
        a=text.find('{'); b=text.rfind('}')
        if a>=0 and b>a:
            try: x=json.loads(text[a:b+1]); return x if isinstance(x,dict) else None
            except json.JSONDecodeError: pass
        return None
omniroute=OmniRouteClient()
