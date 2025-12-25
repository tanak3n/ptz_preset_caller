"""Tiny preset caller for SRG-A40."""

from collections import defaultdict

import requests
import streamlit as st
from requests.auth import HTTPDigestAuth

import srg_a40

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

client = srg_a40.A40Client(CAMERA_ADDR, USER, PASS)


@st.cache_data
def get_preset_list() -> dict[str, str]:
    """Retrieve all presets from connected camera."""
    return client.get_preset_list()


presets: dict[str, str] = get_preset_list()


def clear_preset_cache():
    get_preset_list.clear()


st.button("Reload Preset", on_click=clear_preset_cache)


# def set_wb_indoor() -> None:
#     """Set white balance setting to indoor."""
#     url = "http://" + CAMERA_ADDR + "/command/imaging.cgi?WhiteBalanceMode=indoor"
#     res = requests.get(url, auth=AUTH, timeout=2)
#     res.raise_for_status()


# def set_wb_for_second(b_gain: int, r_gain: int) -> None:
#     """Set while balance setting to custum value."""
#     url = (
#         "http://"
#         + CAMERA_ADDR
#         + "/command/imaging.cgi?"
#         + "WhiteBalanceMode=manual&"
#         + f"WhiteBalanceCbGain={b_gain}&"
#         + f"WhiteBalanceCrGain={r_gain}"
#     )
#     res = requests.get(url, auth=AUTH, timeout=2)
#     res.raise_for_status()

presets_grouped: dict[str, dict[str, str]] = defaultdict(dict)
for k, v in presets.items():
    if v.find("_") != -1:
        group_name, _, child_name = v.partition("_")
        presets_grouped[group_name][k] = child_name
    else:
        presets_grouped["others"][k] = v

for group_name, child_presets in presets_grouped.items():
    st.markdown("## " + group_name)
    cols = st.columns(5, border=False)
    col_now = 0
    for k, v in child_presets.items():
        cols[col_now].button(
            label=str(k) + ": " + str(v),
            on_click=client.call_preset,
            args=(k,),
        )
        col_now += 1
        if col_now == len(cols):
            col_now = 0

# cols = st.columns(5, border=False)
# col_now = 0
# for k, v in presets.items():
# cols[col_now].button(
#     label=str(k) + ": " + str(v),
#     on_click=client.call_preset,
#     args=(k,),
# )
# col_now += 1
# if col_now == len(cols):
#     col_now = 0


# stages = ["1_", "2_", "3_"]
# for stage in stages:
#     st.markdown("## " + stage[0] + "部")
#     cols = st.columns(5, border=False)
#     col_now = 0
#     for k, v in presets.items():
#         if not v.startswith(stage):
#             continue

#         cols[col_now].button(
#             label=str(k) + ": " + str(v),
#             on_click=client.call_preset,
#             args=(k, stage[0]),
#         )
#         col_now += 1
#         if col_now == len(cols):
#             col_now = 0
