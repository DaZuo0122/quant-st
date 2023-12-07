# User Manual
Please note: this is the very first version of the program, everything may be changed in later release.  


This program is built by pure python code and it aims to help user deal with trade on marketplace of Steam platform.


**DISCLAIMER: We provide no guarantee for you when using our program!**  
**You use this program at your own risk, and accept the responsibility for your action!**


## How to install
0. Make sure you have installed Python3 correctlly.  
We recommend `python 3.11` or higher version. 
1. download and unzip the latest release from our github repo. 
2. use `pip install -r requirements.txt` or run `start.py` to install dependencies. 


---


#### start.py guide
The following is a basic guide for using `start.py` to install dependencies.  
When you double click `start.py`, it should look like this image.  
![start_1](\proof_of_content\start_1.png)  
After entered 3 and press `enter` bottom, the program will install dependencies automatically.


If it shows like following image, it means that it couldn't find `requirements.txt` in corresponding path.  
To solve that, please download `requirements.txt` from our [Github repo](https://github.com/DaZuo0122/quant-st) and put it in right place.


![start_2](\proof_of_content\start_2.png)


---


## How to use
Note: For now, we highly recommend use `Steam_autotrade_cli` only.  
More detailed information can be found in user-interface.


For community developers, we recommend use `trade_strategy.py` directly as a python module instead of using user-interface `advance_trade.py` .  
Though trade logic in `trade_strategy.py` is not perfect, any kind of improvement is welcomed!  
You can upload your improvement by submitting PR at our [Github repo](https://github.com/DaZuo0122/quant-st).


### Steam_autotrade_cli
Double click `Steam_autotrade_cli.py`, or run `start.py` and press 1 to open it.  
`Steam_autotrade_cli.py` will automatically create two config files at its first start.  
Fill these config files and then restart `Steam_autotrade_cli.py`.


### Configuration instructions
`Steam_autotrade_cli` will run automatically without the chance of input.  
So, to customise settings, config files must be filled to 


### Description
`config.json5` : The main configuration file, which can modify most settings of the program.
Only the part of Steam needs to be filled in. Please ignore other parts, they're still in developemnt.


`steam_account_info.json5` : Used to fill in Steam account related information.
All the configuration must be filled in.


##### Examples
`config.json5`  

	// After filling it in as true, the program will stop running directly after an error occurs.
	"no_pause": false,

	//The following is about part of BUFF function                                    
	//BUFF function is still being developed,which can’t be used for now
                
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
      "body": "![good_icon]({good_icon})\nGame: {game}\naccessory: {item_name}\nSelling unit price: {buff_price} RMB\nSteam price: {steam_price} USD\nSteam_price: {steam_price_cny} RMB\n![buyer_avatar]({buyer_avatar})\nBuyer: {buyer_name}\nOrder Time: {order_time}"
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
	
	//The following is about the part of Steam function 
                             
	// Steam auto accept offer configuration
	"steam_auto_accept_offer": {
	//No need to spend any offers for items in your Steam inventory                  
    // Whether to enable automatic acceptance of Steam gift offers
	"enable": false,
	// The interval between each check of the quote list (polling interval), in seconds
	"interval": 300

	//The following is about the part of developer mode                             
	//The function has not been accomplished yet,for reference only
                  
	// Whether to enable developer mode
	"development_mode": false


---


`steam_account_info.json5`  

	//Enter the following parameters to allow the software to automatically log in Steam 
	//To verify identity,Steam token parameter is in need                            
	//SteamDesktopAuthenticator is recommended to use for getting parameter  
     
	// Steam token parameter (for authentication)
	"shared_secret": "",

	// Steam token parameter (for authentication)
	"identity_secret": "",

	// Steam Username
	"steam_username": "",

	// Steam password
	"steam_password": ""


---


### Get SDA info
Note: for current version, these info will be filled automatically.  
This guide is a backup.
To fill the `steam_account_info.json5`, you need to get SDA(SteamDesktopAuthenticator) info.  
Here is the guide!


Firstly, double click to run SteamDesktopAuthenticator.  
Haven't installed? click [here](https://github.com/Jessecar96/SteamDesktopAuthenticator)  
Once opened, it should look like this.  
![sda_1](\proof_of_content\sda_1.png)  
now click the second bottom.  
Once clicked, it should look like this.  
![sda_2](\proof_of_content\sda_2.png)  
enter username and pass words in the corresponding boxes.  


Then enter info required as following images show.


![sda_3](\proof_of_content\sda_3.png)


![sda_4](\proof_of_content\sda_4.png)


If you complete setting SteamDesktopAuthenticator, go to its corresponding path.  
And you can find a `.maFile` file.  
Open it with text editor(we recommend using np++ or vc)  
It should look like this in `vs code`  


![sda_5](\proof_of_content\sda_5.png)  

  
Finally, you can find the corresponding info to fill the `steam_account_info.json5`.


---


## FAQs
**Account security issues**  
All source code is open on GitHub for everyone to independently review code security.  
Unless the user's computer is compromised by malicious software, it is impossible for the account to be leaked.


**Why does the editor show a syntax error after I open the configuration file**  
This program uses a configuration file type called json5, so unsupported editors may show a syntax error, but it doesn't actually affect the program's execution.


---


## Trouble shooting
Please send error info with screenshot at [here](https://github.com/DaZuo0122/quant-st/issues)


---


## Contribute
Feel free to dive in! [Open an issue](https://github.com/DaZuo0122/quant-st/issues) or submit PRs.


---


## License
GPL-3.0 license