"""Historial por navegador con una credencial aleatoria y políticas RLS de Supabase."""
import base64
import json
import hashlib
import re
from uuid import UUID
from urllib.parse import urlparse

import requests


class HistoryError(Exception):
    pass


class HistoryConflict(HistoryError):
    pass


class SupabaseHistory:
    def __init__(self, url, key, browser_token):
        self.url = url.strip().rstrip("/")
        self.key = key.strip()
        parsed = urlparse(self.url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise HistoryError("SUPABASE_URL debe ser la URL HTTPS de tu proyecto.")
        if self.key.startswith("sb_secret_"):
            raise HistoryError("Usa la clave publishable o anon; no una clave secret/service_role.")
        if self.key.count(".") == 2:
            try:
                part = self.key.split(".")[1]
                claims = json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))
            except (ValueError, UnicodeError):
                claims = {}
            if claims.get("role") == "service_role":
                raise HistoryError("Usa la clave publishable o anon; no service_role.")
        if not isinstance(browser_token, str) or not re.fullmatch(r"[0-9a-f]{64}", browser_token):
            raise HistoryError("No se pudo identificar este navegador. Recarga la página.")
        self.browser_token = browser_token
        self.owner_hash = hashlib.sha256(browser_token.encode()).hexdigest()

    def _request(self, method, path, *, params=None, body=None, prefer=None):
        headers = {"apikey": self.key, "Content-Type": "application/json"}
        headers["x-xeco-browser-token"] = self.browser_token
        if prefer:
            headers["Prefer"] = prefer
        try:
            response = requests.request(
                method, self.url + path, headers=headers, params=params,
                json=body, timeout=(10, 30), allow_redirects=False,
            )
        except requests.RequestException:
            raise HistoryError("No se pudo conectar con el historial. Intenta nuevamente.") from None
        if response.status_code == 429:
            raise HistoryError("Se alcanzó un límite de Supabase. Espera unos minutos e intenta nuevamente.")
        if not 200 <= response.status_code < 300:
            raise HistoryError("No se pudo leer o guardar el historial. Revisa la conexión y la instalación de las tablas y políticas de Supabase.")
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            raise HistoryError("Supabase devolvió una respuesta inesperada.") from None

    def list_conversations(self):
        rows = []
        offset = 0
        while True:
            page = self._request("GET", "/rest/v1/xeco_browser_conversations", params={
                "select": "id,title,updated_at", "owner_hash": f"eq.{self.owner_hash}",
                "order": "updated_at.desc,id.asc", "limit": 100, "offset": offset,
            })
            rows.extend(page)
            if len(page) < 100:
                return rows
            offset += 100

    def load(self, conversation_id):
        conversation_id = str(UUID(conversation_id))
        rows = self._request("GET", "/rest/v1/xeco_browser_conversations", params={
            "select": "id,title,messages,version", "id": f"eq.{conversation_id}",
            "owner_hash": f"eq.{self.owner_hash}",
        })
        if not rows:
            raise HistoryError("Esta conversación no está disponible en este navegador.")
        return rows[0]

    def save(self, conversation_id, version, messages):
        conversation_id = str(UUID(conversation_id))
        title = next((m["content"] for m in messages if m["role"] == "user"), "Nueva conversación")[:80]
        payload = {"messages": messages, "title": title, "version": version + 1}
        if version == 0:
            payload.update({"id": conversation_id, "owner_hash": self.owner_hash})
            rows = self._request("POST", "/rest/v1/xeco_browser_conversations",
                                 params={"on_conflict": "id"}, body=payload,
                                 prefer="resolution=ignore-duplicates,return=representation")
        else:
            rows = self._request("PATCH", "/rest/v1/xeco_browser_conversations",
                                 params={"id": f"eq.{conversation_id}", "owner_hash": f"eq.{self.owner_hash}",
                                         "version": f"eq.{version}"},
                                 body=payload, prefer="return=representation")
        if rows:
            return rows[0]["version"]
        current = self.load(conversation_id)
        # Permite reintentar una escritura confirmada por el servidor cuya respuesta se perdió.
        if current["messages"] == messages:
            return current["version"]
        raise HistoryConflict("La conversación cambió en otra pestaña. Recupera la versión guardada antes de continuar.")
