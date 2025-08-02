import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
import json
import time
import random
import hashlib
import re
import sys
import locale
import codecs
import webbrowser
import tempfile
import os
from datetime import datetime, timezone
from typing import List, Dict, Set, cast, Optional
import logging
import requests
from playwright.sync_api import sync_playwright, Browser, Page, ViewportSize

# Permanent fix for Unicode console output on Windows
try:
    if sys.platform == "win32":
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
except:
    pass

# Import for Windows notifications - FIXED
try:
    from win10toast_click import ToastNotifier
    WIN10TOAST_AVAILABLE = True
except ImportError:
    ToastNotifier = None  # Fix for "possibly unbound"
    WIN10TOAST_AVAILABLE = False

class VintedMonitor:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.seen_listings: Set[str] = set()
        self.setup_logging()

        # Initialize toast notifier
        self.toaster = None
        if WIN10TOAST_AVAILABLE and ToastNotifier is not None:
            self.toaster = ToastNotifier()
        
        # Enhanced stealth: Multiple user agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # Enhanced stealth: Multiple viewport sizes (properly typed)
        self.viewport_sizes: List[ViewportSize] = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
            {"width": 1440, "height": 900},
            {"width": 1600, "height": 900},
            {"width": 1280, "height": 720}
        ]
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('vinted_monitor.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def safe_log(self, level: str, message: str):
        """Safe logging method that handles Unicode characters"""
        try:
            if level.lower() == 'info':
                self.logger.info(message)
            elif level.lower() == 'warning':
                self.logger.warning(message)
            elif level.lower() == 'error':
                self.logger.error(message)
            elif level.lower() == 'debug':
                self.logger.debug(message)
        except UnicodeEncodeError:
            # Replace problematic characters and log again
            safe_message = message.encode('ascii', errors='replace').decode('ascii')
            if level.lower() == 'info':
                self.logger.info(safe_message)
            elif level.lower() == 'warning':
                self.logger.warning(safe_message)
            elif level.lower() == 'error':
                self.logger.error(safe_message)
            elif level.lower() == 'debug':
                self.logger.debug(safe_message)
    
    def load_config(self) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Config file {self.config_file} not found!")
            return {}
    
    def save_seen_listings(self):
        """Save seen listings to file for persistence"""
        with open('seen_listings.json', 'w') as f:
            json.dump(list(self.seen_listings), f)
    
    def load_seen_listings(self):
        """Load previously seen listings from file"""
        try:
            with open('seen_listings.json', 'r') as f:
                self.seen_listings = set(json.load(f))
        except FileNotFoundError:
            self.seen_listings = set()
    
    def download_image_for_notification(self, image_url: str) -> Optional[str]:
        """Download image temporarily for Windows notification"""
        try:
            if not image_url:
                return None
            
            # Create temp directory if it doesn't exist
            temp_dir = os.path.join(tempfile.gettempdir(), 'vinted_monitor')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate filename from URL hash
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:10]
            temp_path = os.path.join(temp_dir, f"listing_{url_hash}.jpg")
            
            # Download image
            response = requests.get(image_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Save to temp file
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            
            return temp_path
            
        except Exception as e:
            self.logger.debug(f"Failed to download image for notification: {e}")
            return None
    
    def display_startup_info(self):
        """Display startup information"""
        import sys
        
        print("\n" + "="*60, flush=True)
        print("🔍 VINTED MONITOR STARTING UP (STEALTH MODE)", flush=True)
        print("="*60, flush=True)
        
        searches = self.config.get('searches', [])
        if not searches:
            print("❌ No searches configured in config.json!", flush=True)
            return False
        
        print(f"\n📋 CONFIGURED SEARCHES ({len(searches)}):", flush=True)
        print("-" * 40, flush=True)
        
        for i, search in enumerate(searches, 1):
            name = search.get('name', 'Unnamed Search')
            url = search.get('url', 'No URL')
            platform = search.get('platform', 'vinted').upper()
            
            print(f"{i}. {name}", flush=True)
            print(f"   Platform: {platform}", flush=True)
            print(f"   URL: {url}", flush=True)
            print(flush=True)
        
        # Display notification methods status
        notifications = self.config.get('notifications', {})
        print("-" * 40, flush=True)
        print("📢 NOTIFICATION METHODS:", flush=True)
        
        discord_enabled = notifications.get('discord', {}).get('enabled', False)
        telegram_enabled = notifications.get('telegram', {}).get('enabled', False)
        windows_enabled = notifications.get('windows', {}).get('enabled', False)
        
        print(f"   Discord: {'✅ Enabled' if discord_enabled else '❌ Disabled'}", flush=True)
        print(f"   Telegram: {'✅ Enabled' if telegram_enabled else '❌ Disabled'}", flush=True)
        print(f"   Windows Toast: {'✅ Enabled (Clickable + Images)' if windows_enabled else '❌ Disabled'}", flush=True)
        
        if not WIN10TOAST_AVAILABLE and windows_enabled:
            print("   ⚠️  Warning: win10toast-click not installed - Windows notifications won't work", flush=True)
        
        print("-" * 40, flush=True)
        print(f"⏰ Check Interval: {self.config.get('check_interval_minutes', 15)} minutes", flush=True)
        print(f"📢 Max Notifications per Search: {self.config.get('max_notifications_per_search', 10)}", flush=True)
        print(f"🎲 Randomization: ±{self.config.get('randomization_percent', 10)}%", flush=True)
        print(f"🥷 Stealth Features: User-Agent rotation, viewport variation, human-like behavior", flush=True)
        
        # Check if seen listings exist
        try:
            with open('seen_listings.json', 'r') as f:
                seen_count = len(json.load(f))
        except FileNotFoundError:
            seen_count = 0
        
        print(f"💾 Previously Seen Listings: {seen_count}", flush=True)
        
        print("\n🚀 Starting monitoring in 3 seconds...", flush=True)
        sys.stdout.flush()  # Force flush all output
        
        for i in range(3, 0, -1):
            print(f"⏳ {i}...", flush=True)
            time.sleep(1)
        
        print("="*60 + "\n", flush=True)
        
        return True
    
    def simulate_human_behavior(self, page: Page):
        """Enhanced stealth: Simulate human-like browsing behavior"""
        try:
            # Random viewport size (like different users/devices) - Fixed type issue
            viewport = random.choice(self.viewport_sizes)
            page.set_viewport_size(viewport)  # Now properly typed as ViewportSize
            
            # Simulate human-like scrolling behavior
            scroll_actions = [
                "window.scrollTo(0, Math.floor(Math.random() * 300))",  # Random scroll down
                "window.scrollTo(0, Math.floor(Math.random() * 500))",  # Deeper scroll
                "window.scrollTo(0, 0)",  # Back to top
            ]
            
            # Perform 1-3 random scroll actions
            num_actions = random.randint(1, 3)
            for _ in range(num_actions):
                page.evaluate(random.choice(scroll_actions))
                time.sleep(random.uniform(0.5, 2.0))  # Human-like pause between actions
            
            # Sometimes pause longer (like reading)
            if random.random() < 0.3:  # 30% chance
                time.sleep(random.uniform(2, 5))
                
        except Exception as e:
            self.logger.debug(f"Error in human behavior simulation: {e}")
    
    def get_variable_delay(self):
        """Enhanced stealth: More varied delay patterns"""
        delay_patterns = [
            (3, 7),     # Normal delay (60% chance)
            (8, 15),    # Longer delay (25% chance) 
            (1, 3),     # Quick delay (10% chance)
            (15, 25)    # Very long delay (5% chance)
        ]
        
        weights = [0.6, 0.25, 0.1, 0.05]
        chosen_pattern = random.choices(delay_patterns, weights=weights)[0]
        return random.uniform(*chosen_pattern)
    
    def scrape_vinted_listings(self, search_url: str, page: Page) -> List[Dict]:
        """Scrape listings from a Vinted search URL using Playwright and product IDs"""
        try:
            self.safe_log('info', f"Navigating to: {search_url}")
            
            # Enhanced stealth: Set random user agent for this request
            current_user_agent = random.choice(self.user_agents)
            page.set_extra_http_headers({
                'User-Agent': current_user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5,pl;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            })
            
            # Navigate to the search URL
            page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            
            # Enhanced stealth: Simulate human behavior before scraping
            self.simulate_human_behavior(page)
            
            # Wait for listings to load - using the specific selector for product IDs
            page.wait_for_selector('[data-testid*="product-item-id"]', timeout=15000)
            
            # Enhanced stealth: Additional human-like pause
            time.sleep(random.uniform(1, 3))
            
            # Extract listing data using the product ID selector
            listings = []
            
            # Use more specific selector to avoid false positives
            listing_elements = page.query_selector_all('a[data-testid*="product-item-id"][href*="/items/"]')
            
            if not listing_elements:
                self.logger.warning("No listing elements found")
                return []
            
            self.safe_log('info', f"Found {len(listing_elements)} listings")
            
            for element in listing_elements:
                try:
                    # Extract the product ID from data-testid attribute
                    testid = element.get_attribute('data-testid')
                    if not testid or 'product-item-id' not in testid:
                        continue
                    
                    # Extract the actual ID number (e.g., "6787407871" from "product-item-id-6787407871--overlay-link")
                    product_id = testid.split('product-item-id-')[1].split('--')[0]
                    
                    # Get the href for the full listing URL
                    listing_url = element.get_attribute('href')
                    if not listing_url:
                        continue
                        
                    if listing_url.startswith('/'):
                        listing_url = 'https://www.vinted.pl' + listing_url
                    
                    # Get title from the title attribute - this contains all the info
                    title = element.get_attribute('title')
                    if not title:
                        self.logger.debug(f"No title found for product ID: {product_id}")
                        continue
                    
                    # Extract image URL from the same container
                    image_url = None
                    try:
                        # Try multiple image selectors
                        image_selectors = [
                            'img',  # Direct img tag
                            '.item-image img',  # Image with specific class
                            '[data-testid*="image"] img',  # Image with testid
                            '.item-box__image img',  # Common Vinted class pattern
                        ]
                        
                        for selector in image_selectors:
                            try:
                                img_element = element.query_selector(selector)
                                if not img_element:
                                    # Also try in parent container
                                    parent = element.query_selector('xpath=..')
                                    if parent:
                                        img_element = parent.query_selector(selector)
                                
                                if img_element:
                                    image_url = img_element.get_attribute('src')
                                    if image_url:
                                        break
                            except:
                                continue
                        
                        # Handle relative URLs
                        if image_url:
                            if image_url.startswith('//'):
                                image_url = 'https:' + image_url
                            elif image_url.startswith('/'):
                                image_url = 'https://www.vinted.pl' + image_url
                            
                            self.logger.debug(f"Found image URL for {product_id}: {image_url}")
                    
                    except Exception as e:
                        self.logger.debug(f"Error extracting image for {product_id}: {e}")
                    
                    listing = {
                        'id': product_id,
                        'title': title,  # Keep the full title with all information
                        'url': listing_url,
                        'image_url': image_url,  # Add image URL
                        'platform': 'Vinted'
                    }
                    
                    listings.append(listing)
                    
                except Exception as e:
                    self.logger.debug(f"Error parsing individual listing: {e}")
                    continue
            
            self.safe_log('info', f"Successfully extracted {len(listings)} valid listings")
            return listings
            
        except Exception as e:
            self.logger.error(f"Error scraping Vinted listings: {e}")
            return []
    
    def send_discord_notification(self, listing: Dict, search_name: str):
        """Send Discord notification with retry logic"""
        notifications = self.config.get('notifications', {})
        discord_config = notifications.get('discord', {})
        
        if not discord_config.get('enabled', False):
            return  # Discord disabled - this is fine
        
        webhook_url = discord_config.get('webhook_url')
        if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
            self.logger.warning("Discord enabled but webhook URL not configured - skipping Discord notification")
            return  # Don't raise error, just skip
        
        # Create a cleaner description with title and link
        item_description = f"{listing['title']}\n\n[🔗 View Listing]({listing['url']})"
        
        embed = {
            "title": f"🔍 New {listing['platform']} Listing Found!",
            "description": f"**Search:** {search_name}",
            "color": 0x00ff00,
            "fields": [
                {
                    "name": "Item Details",
                    "value": item_description[:1024],  # Discord field limit
                    "inline": False
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "footer": {
                "text": f"{listing['platform']} Monitor • ID: {listing['id']}"
            }
        }
        
        # Add image if available
        if listing.get('image_url'):
            embed["image"] = {
                "url": listing['image_url']
            }
        
        payload = {
            "embeds": [embed]
        }
        
        # Enhanced retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    webhook_url, 
                    json=payload, 
                    timeout=15,
                    headers={
                        'User-Agent': 'Vinted-Monitor/1.0',
                        'Content-Type': 'application/json'
                    }
                )
                response.raise_for_status()
                self.logger.info("Discord notification sent successfully")
                return
                
            except requests.exceptions.SSLError as e:
                self.logger.warning(f"Discord SSL error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Discord request error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        
        self.logger.warning(f"Failed to send Discord notification after {max_retries} attempts")
    
    def send_telegram_notification(self, listing: Dict, search_name: str):
        """Send Telegram notification"""
        notifications = self.config.get('notifications', {})
        telegram_config = notifications.get('telegram', {})
        
        if not telegram_config.get('enabled', False):
            return
        
        bot_token = telegram_config.get('bot_token')
        chat_id = telegram_config.get('chat_id')
        
        if not bot_token or not chat_id:
            self.logger.warning("Telegram enabled but bot_token or chat_id not configured - skipping Telegram notification")
            return
        
        # Prepare message text
        message_text = f"🔍 *New Vinted Listing Found!*\n\n*Search:* {search_name}\n\n{listing['title']}\n\n[View Listing]({listing['url']})"
        
        try:
            # Send photo with caption if image available
            if listing.get('image_url'):
                url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
                data = {
                    'chat_id': chat_id,
                    'photo': listing['image_url'],
                    'caption': message_text,
                    'parse_mode': 'Markdown'
                }
            else:
                # Send text message only
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = {
                    'chat_id': chat_id,
                    'text': message_text,
                    'parse_mode': 'Markdown'
                }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            self.logger.info("Telegram notification sent successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to send Telegram notification: {e}")
    
    def send_windows_notification(self, listing: Dict, search_name: str):
        """Send Windows toast notification with image and clickable URL"""
        notifications = self.config.get('notifications', {})
        windows_config = notifications.get('windows', {})
        
        if not windows_config.get('enabled', False):
            return
        
        if not WIN10TOAST_AVAILABLE or self.toaster is None:  # ← Added self.toaster check
            self.logger.warning("win10toast-click library not installed or toaster not initialized - cannot send Windows notifications")
            return
        
        try:
            # Download image for notification if available
            image_path = None
            if listing.get('image_url'):
                image_path = self.download_image_for_notification(listing['image_url'])
            
            # Function to open URL when notification is clicked
            def open_listing_url():
                try:
                    webbrowser.open(listing['url'])
                    self.safe_log('info', f"Opened Vinted listing URL: {listing['url']}")
                    
                    # Show confirmation notification with URL preview - FIXED
                    if self.toaster is not None:  # ← Added None check
                        self.toaster.show_toast(
                            title="✅ Opening Vinted Listing",
                            msg=f"Opening: {listing['url'][:60]}...\n\nItem: {listing['title'][:40]}...",
                            duration=4,
                            threaded=True
                        )
                except Exception as e:
                    self.safe_log('error', f"Failed to open listing URL: {e}")
            
            # Truncate title for toast notification
            title_text = listing['title'][:80] + "..." if len(listing['title']) > 80 else listing['title']
            
            # Create clickable notification with image - FIXED
            if self.toaster is not None:  # ← Added None check
                self.toaster.show_toast(
                    title="🔍 New Vinted Listing",
                    msg=f"{search_name}:\n{title_text}\n\nClick to open listing!",
                    icon_path=image_path,  # Image thumbnail
                    duration=12,  # Notification stays for 12 seconds
                    threaded=True,  # Don't block the main script
                    callback_on_click=open_listing_url  # Function to run when clicked
                )
                
                self.logger.info("Windows toast notification sent successfully (clickable with image)")
                
                # Clean up temp image file after a delay
                if image_path:
                    def cleanup_temp_file():
                        time.sleep(15)  # Wait 15 seconds then clean up
                        try:
                            if os.path.exists(image_path):
                                os.remove(image_path)
                        except:
                            pass
                    
                    import threading
                    threading.Thread(target=cleanup_temp_file, daemon=True).start()
            
        except Exception as e:
            self.logger.warning(f"Failed to send Windows notification: {e}")
    
    def send_all_notifications(self, listing: Dict, search_name: str):
        """Send notifications via all enabled methods"""
        notification_methods = [
            ('Discord', self.send_discord_notification),
            ('Telegram', self.send_telegram_notification),
            ('Windows', self.send_windows_notification)
        ]
        
        success_count = 0
        for method_name, method_func in notification_methods:
            try:
                method_func(listing, search_name)
                success_count += 1
            except Exception as e:
                self.logger.warning(f"{method_name} notification failed: {e}")
        
        # Extract first few words from title for logging
        title_preview = listing['title'].split(',')[0][:50] if listing['title'] else listing['id']
        
        # Safe logging with Unicode handling
        self.safe_log('info', f"Notifications sent for: {title_preview}... (Success: {success_count})")
    
    def check_search(self, search_config: Dict, browser: Browser):
        """Check a single search URL for new listings"""
        search_name = search_config['name']
        search_url = search_config['url']
        platform = search_config.get('platform', 'vinted').lower()
        
        self.safe_log('info', f"Checking search: {search_name}")
        
        if platform != 'vinted':
            self.logger.warning(f"Platform {platform} not yet supported")
            return
        
        # Create new page for this search
        page = browser.new_page()
        
        try:
            listings = self.scrape_vinted_listings(search_url, page)
            
            # Limit to first N listings (newest ones) and check for new items
            max_notifications = self.config.get('max_notifications_per_search', 10)
            listings_to_check = listings[:max_notifications]  # Only check first N
            
            new_listings = []
            for listing in listings_to_check:
                if listing['id'] not in self.seen_listings:
                    new_listings.append(listing)
                    self.seen_listings.add(listing['id'])
            
            # Still add ALL listings to seen_listings to avoid future spam, but only notify about the top ones
            for listing in listings:
                self.seen_listings.add(listing['id'])
            
            if new_listings:
                self.safe_log('info', f"Found {len(new_listings)} new listings for {search_name} (checked top {max_notifications})")
                for i, listing in enumerate(new_listings):
                    self.send_all_notifications(listing, search_name)
                    # Add small delay between notifications if there are multiple
                    if i < len(new_listings) - 1:
                        time.sleep(random.uniform(1, 3))
            else:
                self.safe_log('info', f"No new listings found for {search_name} (checked top {max_notifications})")
                
        finally:
            page.close()
    
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle for all searches"""
        searches = self.config.get('searches', [])
        if not searches:
            self.logger.error("No searches configured!")
            return
        
        with sync_playwright() as p:
            # Enhanced stealth: Launch browser with additional anti-detection flags
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--no-first-run',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',
                    '--disable-javascript-harmony-shipping',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ]
            )
            
            try:
                for search in searches:
                    try:
                        self.check_search(search, browser)
                        
                        # Enhanced stealth: More varied delays between searches
                        delay = self.get_variable_delay()
                        self.logger.debug(f"Waiting {delay:.1f}s before next search...")
                        time.sleep(delay)
                        
                    except Exception as e:
                        self.logger.error(f"Error checking search {search.get('name', 'Unknown')}: {e}")
                        
            finally:
                browser.close()
    
    def run(self):
        """Main monitoring loop"""
        import sys
        
        # Force console output to appear immediately
        sys.stdout.flush()
        
        # Display startup info
        if not self.display_startup_info():
            return
        
        # Force flush again after startup info
        sys.stdout.flush()
        
        # Always load existing seen listings
        self.load_seen_listings()
        
        base_interval = self.config.get('check_interval_minutes', 15) * 60
        
        self.safe_log('info', "Starting Vinted Monitor with Enhanced Stealth Mode...")
        self.safe_log('info', f"Base check interval: {base_interval/60} minutes")
        
        try:
            while True:
                cycle_start = time.time()
                
                self.run_monitoring_cycle()
                self.save_seen_listings()
                
                cycle_duration = time.time() - cycle_start
                
                # Enhanced stealth: More varied intervals
                randomization_percent = self.config.get('randomization_percent', 10)
                
                # Sometimes use larger randomization (20% chance)
                if random.random() < 0.2:
                    randomization_percent *= 2  # Double the randomization occasionally
                
                random_offset = random.uniform(-randomization_percent/100, randomization_percent/100)
                sleep_time = base_interval * (1 + random_offset)
                
                # Adjust sleep time to account for cycle duration
                adjusted_sleep = max(60, sleep_time - cycle_duration)  # Minimum 1 minute between cycles
                
                next_check_time = datetime.now()
                self.safe_log('info', f"Cycle completed in {cycle_duration:.1f}s. Next check in {adjusted_sleep/60:.1f} minutes")
                time.sleep(adjusted_sleep)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
            self.save_seen_listings()

if __name__ == "__main__":
    monitor = VintedMonitor()
    monitor.run()
