import requests
from app.config import settings
class EarthDialError(RuntimeError): pass
class EarthDialClient:
    def __init__(self):
        self.base_url = (settings.kaggle_ngrok_url or "").strip()
        self.timeout = settings.request_timeout

    def configured(self) -> bool:
        url = (self.base_url or "").strip()
        if not url:
            return False
        if not (url.startswith("http://") or url.startswith("https://")):
            return False
        placeholders = ["PUT_", "YOUR_", "EXAMPLE", "CHANGEME", "HERE"]
        url_upper = url.upper()
        if any(p in url_upper for p in placeholders):
            return False
        return True

    def health(self):
        if not self.configured():
            raise EarthDialError('KAGGLE_NGROK_URL is not configured or contains placeholder.')
        try:
            r = requests.get(
                self.base_url + '/health',
                headers={'ngrok-skip-browser-warning': 'true'},
                timeout=15
            )
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict) and data.get("success") is False:
                raise EarthDialError(f"EarthDial health error: {data.get('error', 'Unknown error')}")
            return data
        except Exception as e:
            raise EarthDialError(f'EarthDial health failed: {e}') from e

    def infer(self, file, query, tag='[caption]'):
        if not self.configured():
            raise EarthDialError('KAGGLE_NGROK_URL is not configured.')
        name, content, ctype = file
        try:
            r = requests.post(
                self.base_url + '/infer',
                files={'file': (name, content, ctype or 'application/octet-stream')},
                data={'query': query, 'tag': tag},
                headers={'ngrok-skip-browser-warning': 'true'},
                timeout=self.timeout
            )
        except requests.RequestException as e:
            raise EarthDialError(f'EarthDial request failed: {e}') from e

        if r.status_code >= 400:
            raise EarthDialError(f'EarthDial HTTP {r.status_code}: {r.text[:1200]}')

        data = r.json()
        if isinstance(data, dict) and data.get("success") is False:
            raise EarthDialError(f"EarthDial inference error: {data.get('error', 'Unknown model error')}")
        return data

    def infer_multi(self, files, query, tag='[changedet]'):
        if not self.configured():
            raise EarthDialError('KAGGLE_NGROK_URL is not configured.')
        multipart = [('files', (n, c, t or 'application/octet-stream')) for n, c, t in files]
        try:
            r = requests.post(
                self.base_url + '/infer_multi',
                files=multipart,
                data={'query': query, 'tag': tag},
                headers={'ngrok-skip-browser-warning': 'true'},
                timeout=self.timeout
            )
        except requests.RequestException as e:
            raise EarthDialError(f'EarthDial multi request failed: {e}') from e

        if r.status_code == 404:
            raise EarthDialError('MULTI_ENDPOINT_NOT_AVAILABLE')
        if r.status_code >= 400:
            raise EarthDialError(f'EarthDial multi HTTP {r.status_code}: {r.text[:1200]}')

        data = r.json()
        if isinstance(data, dict) and data.get("success") is False:
            raise EarthDialError(f"EarthDial multi inference error: {data.get('error', 'Unknown model error')}")
        return data

earthdial = EarthDialClient()

