import requests
from config import BASE_URL, get_tenant


class RattleClient:
    def __init__(self, tenant):
        self.tenant = tenant
        self.api_key = get_tenant(tenant)
        self.base_url = BASE_URL.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        })

    def _url(self, path):
        return f"{self.base_url}/{path.lstrip('/')}"

    def _handle(self, resp):
        if not resp.ok:
            raise RuntimeError(
                f"API error {resp.status_code} on {resp.request.method} {resp.url}: "
                f"{resp.text}"
            )
        return resp.json()

    def get(self, path, **params):
        return self._handle(self.session.get(self._url(path), params=params))

    def post(self, path, json=None):
        return self._handle(self.session.post(self._url(path), json=json))

    def patch(self, path, json=None):
        return self._handle(self.session.patch(self._url(path), json=json))

    def delete(self, path):
        return self._handle(self.session.delete(self._url(path)))

    def list_all(self, path, **params):
        items = []
        while True:
            data = self.get(path, **params)
            if isinstance(data, list):
                return data
            items.extend(data.get("data", []))
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
            params["cursor"] = cursor
        return items
