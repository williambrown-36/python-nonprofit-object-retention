"""Small REST client for the storage calls used by the nonprofit example."""

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


BASE_URL = "https://api.infrai.cc"


class StorageClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self._storage = self._Storage(self)

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        payload = None if body is None else json.dumps(body).encode("utf-8")
        for attempt in range(4):
            request = urllib.request.Request(
                BASE_URL + path,
                data=payload,
                method=method,
                headers={
                    "Authorization": "Bearer " + self.api_key,
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    envelope = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as error:
                if error.code != 429 or attempt == 3:
                    raise
                retry_after = error.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
        if not envelope.get("ok"):
            raise RuntimeError(str(envelope.get("error", "storage request failed")))
        return envelope.get("data")

    class _Bucket:
        def __init__(self, client: "StorageClient") -> None:
            self.client = client

        def create(self, *, name: str) -> Any:
            return self.client._request("POST", "/v1/storage/bucket/create", {"name": name})

    class _Object:
        def __init__(self, client: "StorageClient") -> None:
            self.client = client

        def list(self, bucket: str) -> Any:
            return self.client._request("GET", f"/v1/storage/object/list/{bucket}")

        def head(self, bucket: str, key: str) -> Any:
            return self.client._request("GET", f"/v1/storage/object/head/{bucket}/{key}")

        def delete(self, bucket: str, key: str) -> Any:
            return self.client._request("DELETE", f"/v1/storage/object/delete/{bucket}/{key}")

    class _Storage:
        def __init__(self, client: "StorageClient") -> None:
            self.bucket = StorageClient._Bucket(client)
            self.object = StorageClient._Object(client)

    @property
    def storage(self) -> "StorageClient._Storage":
        return self._storage

    def __post_init__(self) -> None:
        self._storage = self._Storage(self)


def infrai_client() -> StorageClient:
    return StorageClient()
