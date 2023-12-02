import json
import os
import pickle
import time

from requests.exceptions import ProxyError
from steampy.exceptions import InvalidCredentials, ConfirmationExpected
from utils.static import SESSION_FOLDER


class SteamAutoAcceptOffer:
    def __init__(self, logger, steam_client, steam_client_mutex, config):
        self.logger = logger
        self.steam_client = steam_client
        self.steam_client_mutex = steam_client_mutex
        self.config = config

    def init(self):
        return False

    def exec(self):
        self.logger.info("[SteamAutoAcceptOffer] The Steam auto accepts gift offer plug-in start")
        time.sleep(30)
        while True:
            try:
                with self.steam_client_mutex:
                    if not self.steam_client.is_session_alive():
                        self.logger.info("[SteamAutoAcceptOffer] Steam Session has expired, logging in again...")
                        self.steam_client._session.cookies.clear()
                        self.steam_client.login(
                            self.steam_client.username, self.steam_client._password, json.dumps(self.steam_client.steam_guard)
                        )
                        self.logger.info("[SteamAutoAcceptOffer] Steam Session updated")
                        steam_session_path = os.path.join(SESSION_FOLDER, self.steam_client.username.lower() + ".pkl")
                        with open(steam_session_path, "wb") as f:
                            pickle.dump(self.steam_client.session, f)
                with self.steam_client_mutex:
                    trade_summary = self.steam_client.get_trade_offers_summary()["response"]
                self.logger.info("[SteamAutoAcceptOffer] %d pending received count detected" % trade_summary["pending_received_count"])
                if trade_summary["pending_received_count"] > 0:
                    with self.steam_client_mutex:
                        trade_offers = self.steam_client.get_trade_offers(merge=False)["response"]
                    if len(trade_offers["trade_offers_received"]) > 0:
                        for trade_offer in trade_offers["trade_offers_received"]:
                            self.logger.debug(
                                f'\nquote[{trade_offer["tradeofferid"]}] '
                                f'\nexpenditure: {len(trade_offer.get("items_to_give", {}))} item'
                                f'\nreceive: {len(trade_offer.get("items_to_receive", {}))} item'
                            )
                            if len(trade_offer.get("items_to_give", {})) == 0:
                                self.logger.info(
                                    f'[SteamAutoAcceptOffer] Quote detected[{trade_offer["tradeofferid"]}]' f"Gift offer, accepting..."
                                )
                                try:
                                    with self.steam_client_mutex:
                                        self.steam_client.accept_trade_offer(trade_offer["tradeofferid"])
                                except ProxyError:
                                    self.logger.error("[SteamAutoAcceptOffer] The proxy is abnormal")
                                    self.logger.error("[SteamAutoAcceptOffer] You can try turning off the proxy or VPN and restarting the software.")
                                except (ConnectionError, ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError):
                                    self.logger.error("[SteamAutoAcceptOffer] Network anomaly")
                                    self.logger.error("[SteamAutoAcceptOffer] The error may be caused by a proxy or VPN,the software does not require a proxy or VPN")
                                    self.logger.error("[SteamAutoAcceptOffer] If you are using a proxy or VPN, please try closing and restarting the software")
                                    self.logger.error("[SteamAutoAcceptOffer] If you are not using a proxy or VPN, please check your network connection")
                                except InvalidCredentials as e:
                                    self.logger.error("[SteamAutoAcceptOffer] There is a problem with the mafile, please check if the mafile is correct" "(especially identity_secret)")
                                    self.logger.error(str(e))
                                except ConfirmationExpected:
                                    self.logger.error("[UUAutoAcceptOffer] Steam Session has expired, please delete the session folder and restart")
                                except Exception as e:
                                    self.logger.error(e, exc_info=True)
                                    self.logger.error("[SteamAutoAcceptOffer] Steam exception! Try again later")
                                self.logger.info(f'[SteamAutoAcceptOffer] Quote[{trade_offer["tradeofferid"]}]accept success!')
                            else:
                                self.logger.info(
                                    f'[SteamAutoAcceptOffer] Quote detected in [{trade_offer["tradeofferid"]}]' f"Items need to be spent,auto skipped."
                                )
            except Exception as e:
                self.logger.error(e, exc_info=True)
                self.logger.error("[SteamAutoAcceptOffer] An unknown error occurred! Try again later...")
            time.sleep(self.config["steam_auto_accept_offer"]["interval"])
