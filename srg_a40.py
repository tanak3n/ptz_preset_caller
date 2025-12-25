import ipaddress

import requests
from requests.auth import HTTPDigestAuth

SCHEME_HTTP = "http://"


class A40Client:
    def __init__(
        self,
        camera_addr: str,
        camera_user: str,
        camera_password: str,
    ) -> None:
        self.camera_addr: ipaddress.IPv4Address = ipaddress.IPv4Address(camera_addr)
        self.camera_auth: HTTPDigestAuth = HTTPDigestAuth(
            username=camera_user,
            password=camera_password,
        )

    def get_preset_list(self) -> dict[str, str]:
        path = "/command/inquiry.cgi"
        payload = {"inq": "presetposition"}
        res = self._get(path, payload=payload)

        data = res.text
        kvs = data.split("&")
        kvs = dict((kvs.split("=")) for kvs in kvs)
        presets = kvs["PresetName"]
        presets = presets.split(",")

        return dict(list(zip(presets[::2], presets[1::2], strict=True)))

    def add_preset(self, num: int, name: str = "", thumb: bool = True):
        path = "/command/presetposition.cgi"
        thumb_str = "on" if thumb else "off"
        if name == "":
            name = f"Preset{num}"
        payload = {"PresetSet": ",".join((str(num), name, thumb_str))}
        self._get(path=path, payload=payload)

    def delete_preset(self, num: int) -> None:
        path = "/command/presetposition.cgi"
        payload = {"PresetClear": str(num)}
        self._get(path=path, payload=payload)

    def call_preset(self, num: int) -> None:
        path = "/command/presetposition.cgi"
        payload = {"PresetCall": str(num)}
        self._get(path=path, payload=payload)

    def set_wb(self, b_gain: int, r_gain: int) -> None:
        path = "/command/imaging.cgi"
        payload = {
            "WhiteBalanceMode": "manual",
            "WhiteBalanceCbGain": str(b_gain),
            "WhiteBalanceCrGain": str(r_gain),
        }
        self._get(path=path, payload=payload)

    def _get(self, path: str, payload: dict[str, str]) -> requests.Response:
        url = SCHEME_HTTP + str(self.camera_addr) + path
        res = requests.get(url, auth=self.camera_auth, timeout=5, params=payload)
        res.raise_for_status()

        return res
