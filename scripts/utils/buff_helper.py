import os
import time
from typing import Dict

import qrcode_terminal
import qrcode
import requests
from bs4 import BeautifulSoup

from steampy.client import SteamClient
from utils.static import BUFF_COOKIES_FILE_PATH
from utils.tools import get_encoding, logger


def parse_openid_params(response: str) -> Dict[str, str]:
    bs = BeautifulSoup(response, "html.parser")
    params_to_find = ["action", "openid.mode", "openidparams", "nonce"]
    input_form = bs.find("form", {"id": "openidForm"})
    params = {}
    for param in params_to_find:
        params[param] = input_form.find("input", {"name": param}).attrs["value"]
    return params


def get_openid_params(steam_client: SteamClient) -> Dict[str, str]:
    response = requests.get("https://buff.163.com/account/login/steam?back_url=/", allow_redirects=False)
    response = steam_client._session.get(response.headers["Location"])
    return parse_openid_params(response.text)


# Return the cookies of buff
def login_to_buff_by_steam(steam_client: SteamClient) -> str:
    params = get_openid_params(steam_client)
    response = steam_client._session.post("https://steamcommunity.com/openid/login", data=params, allow_redirects=False)
    while response.status_code == 302:
        response = steam_client._session.get(response.headers["Location"], allow_redirects=False)
    return steam_client._session.cookies.get_dict(domain="buff.163.com")


def login_to_buff_by_qrcode() -> str:
    session = requests.session()
    response_json = session.get(
        "https://buff.163.com/account/api/qr_code_login_open", params={"_": str(int(time.time() * 1000))}
    ).json()
    if response_json["code"] != "OK":
        return ""
    qr_code_create_url = "https://buff.163.com/account/api/qr_code_create"
    response_json = session.post(qr_code_create_url, json={"code_type": 1, "extra_param": "{}"}).json()
    if response_json["code"] != "OK":
        logger.error("Failed to obtain QR code")
        return ""
    code_id = response_json["data"]["code_id"]
    qr_code_url = response_json["data"]["url"]
    qrcode_terminal.draw(qr_code_url)
    img = qrcode.make(qr_code_url)
    img.save("qrcode.png")
    logger.info("Please use your phone to scan the QR code above to log in")
    status = 0
    scanned = False
    while status != 3:
        time.sleep(1)
        response_json = session.get(
            "https://buff.163.com/account/api/qr_code_poll", params={"_": str(int(time.time() * 1000)), "item_id": code_id}
        ).json()
        status = response_json["data"]["state"]
        if status == 4 or response_json["code"] != "OK":
            logger.error("The QR code has expired")
            return ""
        if status == 2 and not scanned:
            scanned = True
            logger.info("Scan successful")
    response = session.post(
        "https://buff.163.com/account/api/qr_code_login",
        json={"item_id": code_id},
    )
    logger.debug(response.json())
    cookies = response.cookies.get_dict(domain="buff.163.com")
    return cookies["session"]


def is_session_has_enough_permission(session: str) -> bool:
    if "session=" not in session:
        session = "session=" + session
    response_json = requests.get("https://buff.163.com/api/market/steam_trade", headers={"Cookie": session}).json()
    if "data" not in response_json:
        return False
    return True


def get_valid_session_for_buff(steam_client: SteamClient, logger) -> str:
    logger.info('[BuffLoginSolver] obtaining and checking BUFF session...')
    global session
    session = ""
    if not os.path.exists(BUFF_COOKIES_FILE_PATH):
        with open(BUFF_COOKIES_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("session=")
    else:
        with open(BUFF_COOKIES_FILE_PATH, "r", encoding=get_encoding(BUFF_COOKIES_FILE_PATH)) as f:
            session = f.read().replace("\n", "")
        if session and session != "session=":
            logger.info("[BuffLoginSolver] use cached sessions")
            logger.info("[BuffLoginSolver] checking whether the session is valid...")
            if not is_session_has_enough_permission(session):
                logger.error("[BuffLoginSolver] cached session is invalid")
                session = ""
            else:
                logger.info("[BuffLoginSolver] cached session is valid")
        else:
            session = ""
    if not session:  # Try it via Steam
        logger.info("[BuffLoginSolver] Try logging into BUFF via Steam")
        got_cookies = login_to_buff_by_steam(steam_client)
        if "session" not in got_cookies or not is_session_has_enough_permission(got_cookies["session"]):
            logger.error("[BuffLoginSolver] Login to BUFF using Steam failed")
            logger.error("[BuffLoginSolver] Login to BUFF using Steam failed")
        else:
            logger.info('[BuffLoginSolver] Login to BUFF using Steam success')
            session = got_cookies["session"]
    if not session:  # Try it via QR code
        logger.info("[BuffLoginSolver] Try to log in to BUFF via QR code")
        session = login_to_buff_by_qrcode()
        if (not session) or (not is_session_has_enough_permission(session)):
            logger.error("[BuffLoginSolver] Login to BUFF using Steam failed")
        else:
            logger.info('[BuffLoginSolver] Login to BUFF using Steam success')
    if not session:  # 无法登录至BUFF
        logger.error("[BuffLoginSolver] Unable to log in to BUFF, please update BUFF cookies manually! ")
    else:
        with open(BUFF_COOKIES_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("session=" + session.replace("session=", ""))
    return session


def get_buff_username(session) -> str:
    if "session=" not in session:
        session = "session=" + session
    response_json = requests.get("https://buff.163.com/account/api/user/info", headers={"Cookie": session}).json()
    if response_json["code"] == "OK":
        if "data" in response_json:
            if "nickname" in response_json["data"]:
                return response_json["data"]["nickname"]
    return ""
