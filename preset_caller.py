"""Tiny preset caller for SRG-A40."""

import requests
import streamlit as st
from requests.auth import HTTPDigestAuth

st.title("Tiny preset caller for SRG-A40")


if "connected" not in st.session_state:
    st.session_state.connected = False

CAMERA_ADDR = st.text_input(
    "Camera IP",
    disabled=st.session_state.connected,
    value="192.0.2.0",
)
USER = st.text_input("user", disabled=st.session_state.connected, value="sample_user")
PASS = st.text_input(
    "pass",
    type="password",
    disabled=st.session_state.connected,
    value="dummy_pass",
)


def connect() -> None:
    """Connect to specified camera."""
    st.session_state.connected = True
    if not CAMERA_ADDR:
        st.error("input camera ip")
        st.session_state.connected = False
    if not USER:
        st.error("input user")
        st.session_state.connected = False
    if not PASS:
        st.error("input pass")
        st.session_state.connected = False


st.button("Connect", on_click=connect, disabled=st.session_state.connected)

if not st.session_state.connected:
    st.stop()


AUTH = HTTPDigestAuth(username=USER, password=PASS)


@st.cache_data
def get_preset_list() -> dict[str, str]:
    """Retrieve all presets from connected camera."""
    url = "http://" + CAMERA_ADDR + "/command/inquiry.cgi?inq=presetposition"
    res = requests.get(url, auth=AUTH, timeout=5)
    res.raise_for_status()
    data = res.text
    kvs = data.split("&")
    kvs = dict((kvs.split("=")) for kvs in kvs)
    presets = kvs["PresetName"]
    presets = presets.split(",")

    return dict(list(zip(presets[::2], presets[1::2], strict=True)))


presets: dict[str, str] = get_preset_list()


def set_wb_indoor() -> None:
    """Set white balance setting to indoor."""
    url = "http://" + CAMERA_ADDR + "/command/imaging.cgi?WhiteBalanceMode=indoor"
    res = requests.get(url, auth=AUTH, timeout=2)
    res.raise_for_status()


def set_wb_for_second(b_gain: int, r_gain: int) -> None:
    """Set while balance setting to custum value."""
    url = (
        "http://"
        + CAMERA_ADDR
        + "/command/imaging.cgi?"
        + "WhiteBalanceMode=manual&"
        + f"WhiteBalanceCbGain={b_gain}&"
        + f"WhiteBalanceCrGain={r_gain}"
    )
    res = requests.get(url, auth=AUTH, timeout=2)
    res.raise_for_status()


def call_preset(num: int, stage: str) -> None:
    """Call specified preset."""
    url = "http://" + CAMERA_ADDR + "/command/presetposition.cgi?PresetCall=" + str(num)
    res = requests.get(url, auth=AUTH, timeout=2)
    res.raise_for_status()
    if stage in ["1", "3"]:
        set_wb_indoor()
    elif stage in ["2"]:
        set_wb_for_second(169, 204)


stages = ["1_", "2_", "3_"]
for stage in stages:
    st.markdown("## " + stage[0] + "部")
    cols = st.columns(5, border=False)
    col_now = 0
    for k, v in presets.items():
        if not v.startswith(stage):
            continue

        cols[col_now].button(
            label=str(k) + ": " + str(v),
            on_click=call_preset,
            args=(k, stage[0]),
        )
        col_now += 1
        if col_now == len(cols):
            col_now = 0
