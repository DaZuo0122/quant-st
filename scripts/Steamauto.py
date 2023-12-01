import os
import pickle
import re
import shutil
import signal
import sys
import threading
import time
from ssl import SSLCertVerificationError

import pyjson5 as json
import requests
from bs4 import BeautifulSoup
from requests.exceptions import SSLError

from utils.static import (
    CONFIG_FILE_PATH,
    CONFIG_FOLDER,
    DEFAULT_STEAM_ACCOUNT_JSON,
    DEV_FILE_FOLDER,
    SESSION_FOLDER,
    STEAM_ACCOUNT_INFO_FILE_PATH,
    UU_TOKEN_FILE_PATH,
    UU_ARG_FILE_PATH,
    DEFAULT_CONFIG_JSON,
    set_no_pause,
)
from plugins.BuffAutoAcceptOffer import BuffAutoAcceptOffer
from plugins.BuffAutoOnSale import BuffAutoOnSale
from plugins.SteamAutoAcceptOffer import SteamAutoAcceptOffer
from plugins.UUAutoAcceptOffer import UUAutoAcceptOffer
from steampy.client import SteamClient
from steampy.exceptions import ApiException, CaptchaRequired, InvalidCredentials
from steampy.utils import ping_proxy
from utils.logger import handle_caught_exception
from utils.tools import accelerator, compare_version, get_encoding, logger, pause, exit_code

def handle_global_exception(exc_type, exc_value, exc_traceback):
    logger.exception(
        "A fatal error occurred in the program. Please take a screenshot of this interface and submit the latest log file to https://github.com/jiajiaxd/Steamauto/issues",
        exc_info=(exc_type, exc_value, exc_traceback),
    )
    logger.error("The program is about to exit due to a fatal error...")
    pause()


def set_exit_code(code):
    global exit_code
    exit_code = code


def get_api_key(steam_client):
    resp = steam_client._session.get("https://steamcommunity.com/dev/apikey")
    soup = BeautifulSoup(resp.text, "html.parser")
    if soup.find(id="bodyContents_ex") is not None:
        api_key = soup.find(id="bodyContents_ex").find("p").text.split(" ")[-1]
        regex = re.compile(r"[a-zA-Z0-9]{32}")
        if regex.match(api_key):
            return api_key
    resp = steam_client._session.post(
        "https://steamcommunity.com/dev/registerkey",
        data={
            "domain": "localhost",
            "agreeToTerms": "agreed",
            "sessionid": steam_client._session.cookies.get_dict()["sessionid"],
            "Submit": "register",
        },
    )
    soup = BeautifulSoup(resp.text, "html.parser")
    if soup.find(id="bodyContents_ex") is None:
        return ""
    api_key = soup.find(id="bodyContents_ex").find("p").text.split(" ")[-1]
    return api_key


def get_steam_64_id_from_steam_community(steam_client):
    resp = steam_client._session.get("https://steamcommunity.com/")
    soup = BeautifulSoup(resp.text, "html.parser")
    steam_user_json = soup.find(id="webui_config").get("data-userinfo")
    steam_user = json.loads(steam_user_json)
    return str(steam_user["steamid"])


def login_to_steam():
    global config
    steam_client = None
    with open(STEAM_ACCOUNT_INFO_FILE_PATH, "r", encoding=get_encoding(STEAM_ACCOUNT_INFO_FILE_PATH)) as f:
        try:
            acc = json.load(f)
        except (json.Json5DecoderException, json.Json5IllegalCharacter) as e:
            handle_caught_exception(e)
            logger.error("detected" + STEAM_ACCOUNT_INFO_FILE_PATH + "Format error, please check the configuration file format is correct! ")
            pause()
            return None
    steam_session_path = os.path.join(SESSION_FOLDER, acc.get("steam_username").lower() + ".pkl")
    if steam_client is None:
        try:
            logger.info("Logging in Steam...")
            if "use_proxies" not in config:
                config["use_proxies"] = False
            if config["use_proxies"]:
                logger.info("The Steam agent has been enabled")
                if "proxies" not in config:
                    config["proxies"] = {}

                if not isinstance(config["proxies"], dict):
                    logger.error("proxies are in wrong format. Please check the configuration file")
                    pause()
                    return None
                logger.info("Checking proxy server availability...")
                proxy_status = ping_proxy(config["proxies"])
                if proxy_status is False:
                    logger.error("The proxy server is unavailable. Check the configuration file")
                    pause()
                    return None
                else:
                    # logger.info("Proxy server available")
                    logger.warning("Warning: You have enabled proxy, this configuration will be cached, the next time you start Steamauto make sure proxy is available, or delete the cached file in the session folder and start again")

                client = SteamClient(api_key="", proxies=config["proxies"])

            else:
                client = SteamClient(api_key="")
            if config["steam_login_ignore_ssl_error"]:
                logger.warning("Warning: SSL authentication has been turned off, please ensure your network security")
                client._session.verify = False
                requests.packages.urllib3.disable_warnings()
            if config["steam_local_accelerate"]:
                logger.info("Steamauto built-in acceleration has been enabled")
                client._session.auth = accelerator()
            logger.info("Logging in...")
            SteamClient.login(client, acc.get("steam_username"), acc.get("steam_password"), STEAM_ACCOUNT_INFO_FILE_PATH)
            with open(steam_session_path, "wb") as f:
                pickle.dump(client, f)
            logger.info("Login complete! The session was automatically cached.")
            steam_client = client
        except FileNotFoundError as e:
            handle_caught_exception(e)
            logger.error("not detected" + STEAM_ACCOUNT_INFO_FILE_PATH + "Please add to " + STEAM_ACCOUNT_INFO_FILE_PATH + "After the operation! ")
            pause()
            return None
        except (SSLCertVerificationError, SSLError) as e:
            handle_caught_exception(e)
            if config["steam_local_accelerate"]:
                logger.error("Login failed. You have local acceleration enabled, but not SSL certificate authentication turned off. Set steam_login_ignore_ssl_error to true in the configuration file")
            else:
                logger.error("Login failed. SSL certificate validation error! "If you are sure your network environment is secure, try setting steam_login_ignore_ssl_error to true\n in your configuration file")
            pause()
            return None
        except InvalidCredentials as e:
            handle_caught_exception(e)
            logger.error("Login failed (incorrect account or password). Please check" + STEAM_ACCOUNT_INFO_FILE_PATH + "Check whether the account password is correct\n")
    steam_client._api_key = get_api_key(steam_client)
    steam_client.steam_guard["steamid"] = str(get_steam_64_id_from_steam_community(steam_client))
    return steam_client

def get_plugins_enabled(steam_client, steam_client_mutex):
    global config
    plugins_enabled = []
    if (
        "buff_auto_accept_offer" in config
        and "enable" in config["buff_auto_accept_offer"]
        and config["buff_auto_accept_offer"]["enable"]
    ):
        buff_auto_accept_offer = BuffAutoAcceptOffer(logger, steam_client, steam_client_mutex, config)
        plugins_enabled.append(buff_auto_accept_offer)
    if "buff_auto_on_sale" in config and "enable" in config["buff_auto_on_sale"] and config["buff_auto_on_sale"]["enable"]:
        buff_auto_on_sale = BuffAutoOnSale(logger, steam_client, steam_client_mutex, config)
        plugins_enabled.append(buff_auto_on_sale)
    if (
        "uu_auto_accept_offer" in config
        and "enable" in config["uu_auto_accept_offer"]
        and config["uu_auto_accept_offer"]["enable"]
    ):
        uu_auto_accept_offer = UUAutoAcceptOffer(logger, steam_client, steam_client_mutex, config)
        plugins_enabled.append(uu_auto_accept_offer)
    if (
        "steam_auto_accept_offer" in config
        and "enable" in config["steam_auto_accept_offer"]
        and config["steam_auto_accept_offer"]["enable"]
    ):
        steam_auto_accept_offer = SteamAutoAcceptOffer(logger, steam_client, steam_client_mutex, config)
        plugins_enabled.append(steam_auto_accept_offer)

    return plugins_enabled


def plugins_check(plugins_enabled):
    if len(plugins_enabled) == 0:
        logger.error("No plug-ins are enabled, please check" + CONFIG_FILE_PATH + "right or not! ")
        return 2
    for plugin in plugins_enabled:
        if plugin.init():
            return 0
    return 1


def get_steam_client_mutexs(num):
    steam_client_mutexs = []
    for i in range(num):
        steam_client_mutexs.append(threading.Lock())
    return steam_client_mutexs


def init_plugins_and_start(steam_client, steam_client_mutex):
    plugins_enabled = get_plugins_enabled(steam_client, steam_client_mutex)
    logger.info("Initialization complete, start running the plugin!")
    print("\n")
    time.sleep(0.1)
    if len(plugins_enabled) == 1:
        exit_code.set(plugins_enabled[0].exec())
    else:
        threads = []
        for plugin in plugins_enabled:
            threads.append(threading.Thread(target=plugin.exec))
        for thread in threads:
            thread.daemon = True
            thread.start()
        for thread in threads:
            thread.join()
    if exit_code.get() != 0:
        logger.warning("All plugins have quit! This is not a normal situation, please check the configuration file.")


def main():
    global config
    init_status = init_files_and_params()
    if init_status == 0:
        pause()
        return 1
    elif init_status == 1:
        pause()
        return 0

    steam_client = None
    steam_client = login_to_steam()
    if steam_client is None:
        return 1
    steam_client_mutex = threading.Lock()
    plugins_enabled = get_plugins_enabled(steam_client, steam_client_mutex)
    plugins_check_status = plugins_check(plugins_enabled)
    if plugins_check_status == 0:
        logger.info("There is a plugin running for the first time, please follow the README prompts to fill in the configuration file! ")
        pause()
        return 1

    if steam_client is not None:
        init_plugins_and_start(steam_client, steam_client_mutex)

    logger.info("The program is about to exit because all plug-ins are closed...")
    pause()
    sys.exit(exit_code.get())


def exit_app(signal_, frame):
    logger.info("aborting...")
    sys.exit()


if __name__ == "__main__":
    sys.excepthook = handle_global_exception
    signal.signal(signal.SIGINT, exit_app)
    if not os.path.exists(DEV_FILE_FOLDER):
        os.mkdir(DEV_FILE_FOLDER)
    if not os.path.exists(SESSION_FOLDER):
        os.mkdir(SESSION_FOLDER)
    exit_code.set(main())
    if exit_code is not None:
        sys.exit(exit_code.get())
    else:
        sys.exit()
