# Vinted Listing Tracker 🔍

**Automated Vinted marketplace monitor with multi-platform notifications**

A sophisticated Python script that monitors Vinted searches for new listings and sends instant notifications via Discord, Telegram, and Windows Toast notifications. Features advanced stealth capabilities to avoid detection and includes thumbnail images in all notification types.

Windows Notification


Telegram Notification


<img width="333" height="363" alt="Telegram Notification" src="https://github.com/user-attachments/assets/dfb538a3-9062-42d8-8ad1-56874ec1b648" />


## ✨ Features

### 🔔 Multi-Platform Notifications
- **Discord**: Rich embeds with item images and clickable links
- **Telegram**: Photo messages with item details and direct links  
- **Windows Toast**: Native notifications with thumbnails that open listings when clicked

### 🥷 Advanced Stealth Capabilities
- **User-Agent Rotation**: 5 different realistic browser signatures
- **Human Behavior Simulation**: Random scrolling, viewport changes, variable timing
- **Request Randomization**: Intelligent delay patterns to mimic human browsing
- **Anti-Detection Headers**: Complete browser fingerprint simulation

### 🎯 Smart Monitoring
- **Product ID Tracking**: Reliable duplicate detection using Vinted's internal IDs
- **Configurable Limits**: Prevent notification spam (max 10 per search by default)
- **Persistent Memory**: Remembers seen listings across restarts
- **Multiple Search Support**: Monitor up to 20+ different searches simultaneously

### ⚙️ Flexible Configuration
- **JSON Configuration**: Easy search management and notification toggle
- **Customizable Intervals**: Adjust monitoring frequency (default: 15 minutes)
- **Individual Notification Control**: Enable/disable each notification method independently
- **International Support**: Works with all Vinted domains (vinted.pl, vinted.com, vinted.de, etc.)
- **Unicode Handling**: Full support for international characters and languages

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Windows 10+ (for Windows Toast notifications)

### Installation

1. **Clone the repository**
https://github.com/miciek335/vinted-listing-tracker.git
cd vinted-listing-tracker
2. **Install dependencies**
pip install -r requirements.txt
python -m playwright install chromium
3. **Configure your settings**
   - Create `config.json` based on the example below
   - Add your notification credentials
   - Configure your Vinted searches

4. **Run the monitor**
python vinted_monitor.py

## 📋 Configuration

### config.json Example
{
"check_interval_minutes": 15,
"randomization_percent": 10,
"max_notifications_per_search": 10,
"notifications": {
"discord": {
"enabled": true,
"webhook_url": "YOUR_DISCORD_WEBHOOK_URL"
},
"telegram": {
"enabled": true,
"bot_token": "YOUR_BOT_TOKEN",
"chat_id": "YOUR_CHAT_ID"
},
"windows": {
"enabled": true
}
},
"searches": [
{
"name": "Nintendo Games under 100 PLN",
"url": "https://www.vinted.pl/catalog?search_text=nintendo&price_to=100&order=newest_first",
"platform": "vinted"
},
{
"name": "Vintage Clothing",
"url": "https://www.vinted.com/catalog?search_text=vintage&order=newest_first",
"platform": "vinted"
}
]
}


### Setting Up Notifications

#### Discord Webhooks
1. Go to your Discord server settings
2. Navigate to Integrations → Webhooks
3. Create a new webhook
4. Copy the webhook URL to your config

#### Telegram Bot Setup
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save your bot token
4. Get your chat ID:
   - Message [@userinfobot](https://t.me/userinfobot)
   - Or send a message to your bot and visit: `https://api.telegram.org/bot[BOT_TOKEN]/getUpdates`

#### Windows Toast (Automatic)
- No setup required on Windows 10+
- Notifications are clickable and open listings directly in your browser
- Includes thumbnail images downloaded automatically

## 🎯 Creating Vinted Search URLs

1. Visit any Vinted domain (vinted.pl, vinted.com, vinted.de, etc.)
2. Use the search and filter options to find items you want to monitor
3. Apply filters like price range, category, condition, etc.
4. Copy the URL from your browser's address bar
5. Add to your `config.json` searches array

**Example URLs:**
Basic search:
https://www.vinted.pl/catalog?search_text=nintendo&order=newest_first

With price limit:
https://www.vinted.com/catalog?search_text=vintage&price_to=50&order=newest_first

Specific category:
https://www.vinted.de/catalog?search_text=sneakers&catalog[]=1&order=newest_first

Multiple filters:
https://www.vinted.pl/catalog?search_text=pokemon&price_to=200&catalog[]=2994&order=newest_first

## 🛠️ Requirements


requests>=2.28.0
playwright>=1.44.0
win10toast-click>=0.1.2


## 🔧 Advanced Configuration

### Stealth Settings
- `check_interval_minutes`: Time between monitoring cycles (default: 15)
- `randomization_percent`: Timing variation to appear more human (default: 10%)
- `max_notifications_per_search`: Prevent spam by limiting notifications per search

### Notification Customization
Each notification method can be independently:
- Enabled/disabled with simple true/false flags
- Configured with different credentials
- Customized for different notification styles

### Performance Tuning
- **Memory efficient**: Only stores product IDs, not full listing data
- **Network optimized**: Reuses browser sessions and implements smart delays
- **Resource conscious**: Automatic cleanup of temporary image files

## 📊 Monitoring Output

When running, the script provides detailed startup information:


🔍 VINTED MONITOR STARTING UP (STEALTH MODE)
📋 CONFIGURED SEARCHES (3):

    Nintendo Games under 100 PLN
    Platform: VINTED
    URL: https://www.vinted.pl/catalog?search_text=nintendo...

    Vintage Clothing
    Platform: VINTED
    URL: https://www.vinted.com/catalog?search_text=vintage...

📢 NOTIFICATION METHODS:
Discord: ✅ Enabled
Telegram: ✅ Enabled
Windows Toast: ✅ Enabled (Clickable + Images)

⏰ Check Interval: 15 minutes
📢 Max Notifications per Search: 10
🎲 Randomization: ±10%
🥷 Stealth Features: User-Agent rotation, viewport variation, human-like behavior
💾 Previously Seen Listings: 1,247
🚀 Starting monitoring in 3 seconds...
⏳ 3...
⏳ 2...
⏳ 1...


## 🌍 International Support

This tracker works with all Vinted domains worldwide:
- 🇵🇱 **Poland**: vinted.pl
- 🇺🇸 **United States**: vinted.com  
- 🇩🇪 **Germany**: vinted.de
- 🇫🇷 **France**: vinted.fr
- 🇬🇧 **United Kingdom**: vinted.co.uk
- 🇮🇹 **Italy**: vinted.it
- 🇪🇸 **Spain**: vinted.es
- And more...

Simply use the appropriate domain in your search URLs!

## 📸 Screenshots

### Windows Toast Notifications
![Windows Notification Example](screenshots/windows-notification-example.png)
*Replace with your Windows notification screenshot*

### Telegram Notifications  
![Telegram Notification Example](screenshots/telegram-notification-example.png)
*Replace with your Telegram notification screenshot*

### Console Output
![Console Output](screenshots/console-output.png)
*Replace with your console output screenshot*

## 🚨 Important Notes

### Responsible Usage
- **Respect Vinted's Terms of Service**: Use reasonable monitoring intervals (15+ minutes recommended)
- **Don't Overload**: The built-in delays and randomization help prevent server strain
- **Personal Use**: This tool is intended for personal use to track items you're interested in buying

### Rate Limiting & Stealth
- Default 15-minute intervals between full monitoring cycles
- Randomized timing (±10%) to appear more human-like
- 3-7 second delays between individual searches within a cycle
- Maximum 10 notifications per search to prevent spam
- Realistic browser simulation with rotating user agents

### Legal Compliance
Users are responsible for:
- Complying with Vinted's Terms of Service
- Following applicable local laws and regulations  
- Using the tool ethically and responsibly

## 🔍 Troubleshooting

### Common Issues

**Installation Problems**
If playwright installation fails:

python -m playwright install chromium --force
If requirements installation fails:

pip install --upgrade pip
pip install -r requirements.txt


**Discord Webhook Errors**
- Verify your webhook URL starts with `https://discord.com/api/webhooks/`
- Check that your Discord server permissions allow webhooks
- Test the webhook URL in your browser (should show "Method Not Allowed")

**Telegram Bot Issues**
- Ensure your bot token is correct and active
- Verify your chat ID is a number, not a username
- Send a message to your bot first to initiate the chat

**Windows Notification Problems**

Reinstall the notification library:

pip uninstall win10toast-click
pip install win10toast-click


**No New Listings Found**
- The script only notifies about listings it hasn't seen before
- On first run, it marks all current listings as "seen"
- Wait for actual new listings to be posted on Vinted

### Debug Mode
Enable detailed logging by changing the log level in `vinted_monitor.py`:
logging.basicConfig(level=logging.DEBUG, ...)


## 📁 Project Structure

vinted-listing-tracker/
├── vinted_monitor.py # Main monitoring script
├── config.json # Your configuration file
├── requirements.txt # Python dependencies
├── README.md # This documentation
├── LICENSE # MIT License file
├── screenshots/ # Directory for documentation images
│ ├── windows-notification.png
│ ├── telegram-notification.png
│ └── console-output.png
├── seen_listings.json # Auto-generated (stores seen item IDs)
└── vinted_monitor.log # Auto-generated (application logs)


## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Ways to Contribute
- 🐛 **Bug Reports**: Open an issue with details about the problem
- 💡 **Feature Requests**: Suggest new functionality or improvements  
- 🔧 **Code Contributions**: Submit pull requests with bug fixes or new features
- 📖 **Documentation**: Help improve the README or add code comments
- 🌍 **Internationalization**: Test with different Vinted domains and languages

### Development Setup
1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a feature branch: `git checkout -b feature-name`
4. Make your changes and test thoroughly
5. Commit with clear messages: `git commit -m "Add feature description"`
6. Push to your fork: `git push origin feature-name`
7. Submit a pull request with a detailed description

### Code Style
- Follow existing code formatting and structure
- Add comments for complex logic
- Update documentation for new features
- Test with multiple Vinted domains if applicable

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What this means:
- ✅ **Free to use** for personal and commercial purposes
- ✅ **Modify and distribute** as you wish
- ✅ **Private use** allowed
- ⚠️ **Attribution required** - please credit Maciej Jeka (MicieK) in your projects
- ❌ **No warranty** - use at your own risk

## 👨‍💻 Author

**Maciej Jeka (MicieK)**

If this project helped you find great deals on Vinted, consider:
- ⭐ **Starring the repository**
- 🐛 **Reporting bugs** you encounter
- 💡 **Suggesting improvements**
- 🤝 **Contributing code** or documentation

## 🙏 Acknowledgments

Special thanks to:
- **[Playwright](https://playwright.dev/)** - Reliable browser automation framework
- **[Vinted](https://www.vinted.com/)** - The marketplace platform that makes this tool possible
- **[Discord](https://discord.com/)** - Webhook API for rich notifications
- **[Telegram](https://core.telegram.org/bots/api)** - Bot API for mobile notifications
- **The open-source community** - For the libraries and tools that make this project possible

## ⚠️ Disclaimer

This tool is created for educational purposes and personal use only. It is not affiliated with, endorsed by, or connected to Vinted in any way. Users are solely responsible for:

- Complying with Vinted's Terms of Service
- Following applicable laws and regulations in their jurisdiction  
- Using the tool ethically and responsibly
- Any consequences resulting from the use of this software

The authors and contributors provide this software "as is" without warranty of any kind and are not liable for any damages or legal issues arising from its use.

---

**⭐ Found this useful? Please star the repository to show your support!**

**📢 Have questions? Open an issue on GitHub and I'll help you get started!**

