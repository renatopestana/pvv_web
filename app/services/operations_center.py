
# app/services/operations_center.py
import os
import base64
import datetime
import urllib.parse
import requests
from typing import Dict, Any, List, Optional


class OperationsCenterClient:
    def __init__(self):
        # Variáveis do .env
        self.client_id: Optional[str] = os.getenv('OC_CLIENT_ID')
        self.client_secret: Optional[str] = os.getenv('OC_CLIENT_SECRET')
        self.well_known: Optional[str] = os.getenv('OC_WELL_KNOWN')
        self.callback_url: Optional[str] = os.getenv('OC_CALLBACK_URL')  # ex.: http://localhost:9090/callback
        self.scopes: Optional[str] = os.getenv('OC_SCOPES', 'openid profile email org1 org2 eq1 eq2 offline_access')

        self.state: str = os.getenv('OC_STATE', 'state-123')

        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.exp: Optional[datetime.datetime] = None

        self._metadata_cache: Optional[Dict[str, Any]] = None

    def _ensure_env(self):
        missing = []
        if not self.client_id:     missing.append('OC_CLIENT_ID')
        if not self.client_secret: missing.append('OC_CLIENT_SECRET')
        if not self.well_known:    missing.append('OC_WELL_KNOWN')
        if not self.callback_url:  missing.append('OC_CALLBACK_URL')
        if not self.scopes:        missing.append('OC_SCOPES')
        if missing:
            raise RuntimeError(f"Faltam variáveis de ambiente: {', '.join(missing)}. "
                               f"Verifique .env e se load_dotenv() foi chamado.")

    def get_metadata(self) -> Dict[str, Any]:
        self._ensure_env()
        if self._metadata_cache is None:
            r = requests.get(self.well_known, timeout=10)
            r.raise_for_status()
            self._metadata_cache = r.json()
        return self._metadata_cache

    def _basic_auth_header(self) -> str:
        return base64.b64encode(f"{self.client_id}:{self.client_secret}".encode('utf-8')).decode('utf-8')

    def authorization_url(self) -> str:
        meta = self.get_metadata()
        auth_endpoint = meta.get('authorization_endpoint')
        if not auth_endpoint:
            raise RuntimeError("authorization_endpoint ausente no well-known.")
        q = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": self.scopes,
            "redirect_uri": self.callback_url,
            "state": self.state,
        }
        return f"{auth_endpoint}?{urllib.parse.urlencode(q)}"

    def exchange_code(self, code: str):
        meta = self.get_metadata()
        token_endpoint = meta.get('token_endpoint')
        if not token_endpoint:
            raise RuntimeError("token_endpoint ausente no well-known.")
        headers = {
            "authorization": f"Basic {self._basic_auth_header()}",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "grant_type": "authorization_code",
            "redirect_uri": self.callback_url,
            "code": code,
            "scope": self.scopes,
        }
        r = requests.post(token_endpoint, headers=headers, data=payload, timeout=15)
        r.raise_for_status()
        self._update_tokens(r.json())

    def refresh(self):
        if not self.refresh_token:
            raise RuntimeError("refresh_token ausente. Refaça a autorização.")
        meta = self.get_metadata()
        token_endpoint = meta.get('token_endpoint')
        headers = {
            "authorization": f"Basic {self._basic_auth_header()}",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
        r = requests.post(token_endpoint, headers=headers, data=payload, timeout=15)
        r.raise_for_status()
        self._update_tokens(r.json())

    def _update_tokens(self, token_json: Dict[str, Any]):
        self.access_token = token_json.get('access_token')
        self.refresh_token = token_json.get('refresh_token')
        expires_in = token_json.get('expires_in', 0)
        self.exp = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

    def _ensure_token(self):
        if not self.access_token:
            raise RuntimeError("Não autorizado no Operations Center. Acesse /auth/login após login local.")
        if self.exp and datetime.datetime.now() >= self.exp:
            self.refresh()

    # Exemplo de uso para Equipment API
    def _api_get(self, url: str) -> requests.Response:
        self._ensure_token()
        headers = {
            "authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.deere.axiom.v3+json",
            "No_paging": "true",
            "x-deere-no-paging": "true",
        }
        return requests.get(url, headers=headers, timeout=30)

    def get_machines_by_org(self, org_id: str, embed_devices: bool = False) -> List[Dict[str, Any]]:
        url = f"https://equipmentapi.deere.com/isg/equipment?organizationIds={org_id}"
        if embed_devices:
            url += "&embed=devices"
        url += "&pageOffset=0&itemLimit=1000"
        r = self._api_get(url)
        if r.status_code != 200:
            raise RuntimeError(f"OC API error {r.status_code}: {r.content}")
        out: List[Dict[str, Any]] = []
        data = r.json()
        for m in data.get('values', []):
            try:
                if m.get('@type') != "Machine": continue
                if not m.get('isSerialNumberCertified', False): continue
                if m.get('archived') is True or m.get('decommissioned') is True or m.get('stolen') is True: continue
                item = {
                    "serialNumber": m.get('serialNumber'),
                    "name": m.get('name'),
                    "model": (m.get('model') or {}).get('name'),
                    "type": (m.get('type') or {}).get('name'),
                    "year": m.get('modelYear'),
                }
                out.append(item)
            except Exception:
                continue
        return out
