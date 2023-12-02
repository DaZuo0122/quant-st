import os

global no_pause
no_pause = False

VERSION_FILE = "version.json"
APPRISE_ASSET_FOLDER = "Apprise"
LOGS_FOLDER = "logs"
CONFIG_FOLDER = "config"
CONFIG_FILE_PATH = os.path.join(CONFIG_FOLDER, "config.json5")
BUFF_COOKIES_FILE_PATH = os.path.join(CONFIG_FOLDER, "buff_cookies.txt")
UU_TOKEN_FILE_PATH = os.path.join(CONFIG_FOLDER, "uu_token.txt")
STEAM_ACCOUNT_INFO_FILE_PATH = os.path.join(CONFIG_FOLDER, "steam_account_info.json5")
SESSION_FOLDER = "session"
DEV_FILE_FOLDER = "dev"
BUFF_ACCOUNT_DEV_FILE_PATH = os.path.join(DEV_FILE_FOLDER, "buff_account.json")
MESSAGE_NOTIFICATION_DEV_FILE_PATH = os.path.join(DEV_FILE_FOLDER, "message_notification.json")
STEAM_TRADE_DEV_FILE_PATH = os.path.join(DEV_FILE_FOLDER, "steam_trade.json")
SELL_ORDER_HISTORY_DEV_FILE_PATH = os.path.join(DEV_FILE_FOLDER, "sell_order_history.json")
SHOP_LISTING_DEV_FILE_PATH = os.path.join(DEV_FILE_FOLDER, "shop_listing.json")
TO_DELIVER_DEV_FILE_PATH = os.path.join(DEV_FILE_FOLDER, "to_deliver_{game}.json")
SUPPORT_GAME_TYPES = [{"game": "csgo", "app_id": 730}, {"game": "dota2", "app_id": 570}]
UU_ARG_FILE_PATH = "uu.txt"

DEFAULT_STEAM_ACCOUNT_JSON = """
{

  // Steam token parameter (for authentication)
  "shared_secret": "",

  // Steam token parameter (for authentication)
  "identity_secret": "",

  // Steam Username
  "steam_username": "",

  // Steam password
  "steam_password": ""
}
"""

DEFAULT_CONFIG_JSON = r"""
{ 
  // After filling it in as true, the program will stop running directly after an error occurs.
  "no_pause": false,

  // BUFF automatic shipping plug-in configuration
  "buff_auto_accept_offer": {
    // Whether to enable the BUFF automatic shipping quotation function
    "enable": true,
    // The new quote checking interval (polling interval), in seconds
    "interval": 300,
    // Whether to enable sale protection
    "sell_protection": false,
    // Sale protection price, if the lowest price of other sellers is lower than it, there will be no sale protection
    "protection_price": 30,
    // Sale Price Protection Ratio
    "protection_price_percentage": 0.9,
    // Sale notification configuration
    "sell_notification": {
      // Sale notification configuration
      "title": "Sold{game}successfully: {item_name} * {sold_count}",
      // Sale notice content
      "body": "![good_icon]({good_icon})\nGame: {game}\naccessory: {item_name}\nSelling unit price: {buff_price} RMB\nSteam price: {steam_price} USD\nSteam price: {steam_price_cny} RMB\n![buyer_avatar]({buyer_avatar})\nBuyer: {buyer_name}\nOrder Time: {order_time}"
    },
    // Protection Notification
    "protection_notification": {
      // Sale Protection Notice Title
      "title": "{game}accessory: {item_name} The quotation was not automatically accepted, and the price was too different from the lowest price in the market.",
      // Sale protection notice content
      "body": "Please go to BUFF to confirm the quotation yourself!"
    },
    // Item Mismatch Notification Configuration
    "item_mismatch_notification": {
      // Item Mismatch Notification Title
      "title": "BUFF sold accessory does not match Steam offer accessory",
      // Item Mismatch Notification Announcement
      "body": "Please go to BUFF to confirm the quotation yourself!(Offer: {offer_id})"
    },
  // BUFF auto on sale plug-in configuration
  "buff_auto_on_sale": {
    // Whether to enable BUFF to auto list all inventory at the lowest price
    "enable": false,
    // Each time the inventory is checked, the BUFF inventory is forced to be refreshed. 
    "force_refresh": true,
    // Blacklist time, in hour, int format, empty means the blacklist is not enabled
    "blacklist_time": [],
    // The whitelist time is hour, in int format. 
    "whitelist_time": [],
    // Random listing probability, an integer, 1~100, 100 means 100% listing, 1 means 1% listing, 0 means no listing
    "random_chance": 100,
    // Product listing description
    "description": "",
    // Check inventory interval
    "interval": 1800
  },
  
  // Steam auto accept offer configuration
  "steam_auto_accept_offer": {
    // Whether to enable automatic acceptance of Steam gift offers
    "enable": false,
    // The interval between each check of the quote list (polling interval), in seconds
    "interval": 300
  },
  // Whether to enable developer mode
  "development_mode": false
}
"""


def set_no_pause(no_pause_):
    global no_pause
    no_pause = no_pause_


def get_no_pause():
    global no_pause
    return no_pause
