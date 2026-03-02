"""
LinkedIn Automation Agent
Automates messaging 1st degree connections from a specific company
COMPLETELY REWRITTEN with COUNTER-BASED PAGINATION
Messages directly from search results page without navigating to profiles
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import random

class LinkedInBot:
    def __init__(self, email, password):
        """Initialize the LinkedIn bot with credentials"""
        self.email = email
        self.password = password
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add user agent to avoid detection
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        
    def human_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to mimic human behavior"""
        time.sleep(random.uniform(min_seconds, max_seconds))
        
    def login(self):
        """Login to LinkedIn"""
        try:
            print("Opening LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            self.human_delay(1.5, 2)
            
            print("Entering credentials...")
            # Enter email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.clear()
            email_field.send_keys(self.email)
            
            self.human_delay(0.3, 0.5)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            
            self.human_delay(0.3, 0.5)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            print("Logging in...")
            self.human_delay(3, 4)
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                print("✓ Successfully logged in!")
                return True
            else:
                print("⚠ Login may have failed. Please check for CAPTCHA or verification.")
                return False
                
        except Exception as e:
            print(f"❌ Error during login: {str(e)}")
            return False
    
    def load_search_page(self, company_name, page_number):
        """Load a specific page of search results"""
        try:
            # Build URL with page number
            if page_number == 1:
                url = f"https://www.linkedin.com/search/results/people/?network=%5B%22F%22%5D&keywords={company_name.replace(' ', '%20')}"
            else:
                url = f"https://www.linkedin.com/search/results/people/?network=%5B%22F%22%5D&keywords={company_name.replace(' ', '%20')}&page={page_number}"
            
            print(f"\n{'='*60}")
            print(f"📄 Loading Page {page_number}")
            print(f"{'='*60}")
            print(f"URL: {url}")
            
            self.driver.get(url)
            self.human_delay(3, 4)
            
            # Scroll to load all results
            print("Loading results...")
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.human_delay(1, 1.5)
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.human_delay(0.5, 1)
            
            print(f"✓ Page {page_number} loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error loading page {page_number}: {str(e)}")
            return False
    
    def get_results_from_current_page(self):
        """Get all search result items from the current page"""
        try:
            result_items = []
            
            selectors = [
                "//li[contains(@class, 'reusable-search__result-container')]",
                "//div[contains(@class, 'search-results-container')]//li",
                "//ul[contains(@class, 'reusable-search__entity-result-list')]//li",
            ]
            
            for selector in selectors:
                try:
                    items = self.driver.find_elements(By.XPATH, selector)
                    if items and len(items) > 0:
                        result_items = items
                        break
                except:
                    continue
            
            # If still no results, try a more general approach
            if not result_items:
                all_li = self.driver.find_elements(By.TAG_NAME, "li")
                for li in all_li:
                    try:
                        if li.find_element(By.XPATH, ".//a[contains(@href, '/in/')]"):
                            result_items.append(li)
                    except:
                        continue
            
            print(f"Found {len(result_items)} results on current page")
            return result_items
            
        except Exception as e:
            print(f"❌ Error getting results: {str(e)}")
            return []
    
    def get_person_name_from_result(self, result_item):
        """Extract person's name from search result item"""
        try:
            name_selectors = [
                ".//span[@dir='ltr']//span[@aria-hidden='true']",
                ".//span[contains(@class, 'entity-result__title-text')]//span[@aria-hidden='true']",
                ".//a[contains(@class, 'app-aware-link')]//span[@aria-hidden='true']",
            ]
            
            for selector in name_selectors:
                try:
                    name_element = result_item.find_element(By.XPATH, selector)
                    name = name_element.text.strip()
                    if name and len(name) > 2:
                        return name
                except:
                    continue
            
            return "Unknown"
        except:
            return "Unknown"
    
    def click_message_button_in_result(self, result_item, person_name):
        """Click the Message button directly from search result"""
        try:
            # Scroll the result item into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", result_item)
            self.human_delay(0.5, 1)
            
            message_button = None
            
            button_selectors = [
                ".//button[contains(@aria-label, 'Message')]",
                ".//button[contains(@aria-label, 'message')]",
                ".//button[.//span[text()='Message']]",
            ]
            
            for selector in button_selectors:
                try:
                    buttons = result_item.find_elements(By.XPATH, selector)
                    for btn in buttons:
                        try:
                            if btn.is_displayed() and btn.is_enabled():
                                aria_label = btn.get_attribute('aria-label')
                                if aria_label and 'message' in aria_label.lower():
                                    message_button = btn
                                    break
                        except:
                            continue
                    if message_button:
                        break
                except:
                    continue
            
            if not message_button:
                all_buttons = result_item.find_elements(By.TAG_NAME, "button")
                for btn in all_buttons:
                    try:
                        if btn.is_displayed():
                            aria = btn.get_attribute('aria-label')
                            if aria and 'message' in aria.lower():
                                message_button = btn
                                break
                    except:
                        continue
            
            if not message_button:
                print(f"  ⚠ Message button not found for {person_name}")
                return False
            
            try:
                message_button.click()
            except:
                self.driver.execute_script("arguments[0].click();", message_button)
            
            self.human_delay(1.5, 2)
            return True
            
        except Exception as e:
            print(f"  ❌ Error clicking message button: {str(e)}")
            return False
    
    def send_message_in_modal(self, message_text, person_name):
        """Send message in the messaging modal/popup"""
        try:
            self.human_delay(1, 1.5)
            
            message_box = None
            selectors = [
                "//div[contains(@class, 'msg-form__contenteditable')][@role='textbox']",
                "//div[@role='textbox' and @contenteditable='true']",
            ]
            
            for selector in selectors:
                try:
                    message_box = self.driver.find_element(By.XPATH, selector)
                    if message_box.is_displayed():
                        break
                except:
                    continue
            
            if not message_box:
                print(f"  ⚠ Message box not found")
                return False
            
            message_box.click()
            self.human_delay(0.2, 0.4)
            message_box.clear()
            message_box.send_keys(message_text)
            self.human_delay(0.5, 1)
            
            send_button = None
            send_selectors = [
                "//button[contains(@class, 'msg-form__send-button')]",
                "//button[@type='submit' and contains(., 'Send')]",
            ]
            
            for selector in send_selectors:
                try:
                    send_button = self.driver.find_element(By.XPATH, selector)
                    if send_button.is_displayed() and send_button.is_enabled():
                        break
                except:
                    continue
            
            if not send_button:
                print(f"  ⚠ Send button not found")
                return False
            
            try:
                send_button.click()
            except:
                self.driver.execute_script("arguments[0].click();", send_button)
            
            print(f"  ✓ Message sent to {person_name}")
            self.human_delay(1, 3)
            
            # Close modal
            try:
                webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                self.human_delay(3, 4)
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error sending message: {str(e)}")
            return False
    
    def run_automation(self, company_name, message_text, max_messages, start_from=1):
        """
        Main automation workflow with COUNTER-BASED PAGINATION
        
        Logic:
        - Counter starts at START_FROM value
        - For each person, counter increments by 1
        - When counter % 10 == 1 (e.g., 1, 11, 21, 31), calculate and load new page
        - Page number = (counter - 1) // 10 + 1
        """
        try:
            print("="*60)
            print("LINKEDIN AUTOMATION AGENT - COUNTER-BASED PAGINATION")
            print("="*60)
            
            if start_from < 1:
                start_from = 1
            
            # Setup and login
            self.setup_driver()
            if not self.login():
                print("\n❌ Login failed. Exiting...")
                return
            
            print(f"\n{'='*60}")
            print(f"Configuration:")
            print(f"  Company: {company_name}")
            print(f"  Start from: Connection #{start_from}")
            print(f"  Max messages: {max_messages}")
            print(f"{'='*60}")
            
            # Counters
            counter = start_from  # Current connection number
            successful = 0
            failed = 0
            current_page = 0
            page_results = []
            
            while successful < max_messages:
                # Calculate which page we need based on counter
                # counter=1 -> page 1, counter=11 -> page 2, counter=21 -> page 3
                needed_page = ((counter - 1) // 10) + 1
                
                # Calculate position within that page (0-indexed)
                # counter=1 -> position 0, counter=11 -> position 0, counter=5 -> position 4
                position_in_page = (counter - 1) % 10
                
                print(f"\n{'─'*60}")
                print(f"Counter: {counter} | Needed Page: {needed_page} | Position: {position_in_page}")
                print(f"{'─'*60}")
                
                # Load new page if needed
                if needed_page != current_page:
                    print(f"🔄 Page change required: {current_page} → {needed_page}")
                    
                    if not self.load_search_page(company_name, needed_page):
                        print(f"❌ Failed to load page {needed_page}")
                        break
                    
                    current_page = needed_page
                    
                    # Get fresh results from this page
                    page_results = self.get_results_from_current_page()
                    
                    if not page_results:
                        print(f"⚠ No results on page {needed_page}")
                        break
                
                # Check if we have enough results for this position
                if position_in_page >= len(page_results):
                    print(f"⚠ Not enough results on page {current_page} (need index {position_in_page}, have {len(page_results)} results)")
                    break
                
                # Get the result item at this position
                result_item = page_results[position_in_page]
                person_name = self.get_person_name_from_result(result_item)
                
                print(f"\n[Connection #{counter}] {person_name}")
                print(f"  Page: {current_page} | Position: {position_in_page + 1}/{len(page_results)}")
                
                # Try to message this person
                if self.click_message_button_in_result(result_item, person_name):
                    if self.send_message_in_modal(message_text, person_name):
                        successful += 1
                        print(f"  ✅ Success! ({successful}/{max_messages})")
                    else:
                        failed += 1
                        print(f"  ❌ Failed to send message")
                else:
                    failed += 1
                    print(f"  ❌ Failed to click message button")
                
                # Increment counter for next iteration
                counter += 1
                
                # Delay before next message
                if successful < max_messages:
                    delay = random.uniform(5, 8)
                    print(f"  ⏳ Waiting {delay:.1f} seconds...")
                    time.sleep(delay)
            
            print(f"\n{'='*60}")
            print("AUTOMATION COMPLETE")
            print(f"{'='*60}")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
            print(f"📊 Total attempts: {successful + failed}")
            print(f"{'='*60}")
            print(f"\n💡 To continue, set START_FROM = {counter}")
            
        except Exception as e:
            print(f"\n❌ Error in automation: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n⏳ Keeping browser open for 5 seconds...")
            time.sleep(5)
            if self.driver:
                self.driver.quit()
                print("Browser closed.")


def main():
    """Main function"""
    
    # ========== CONFIGURATION ==========
    LINKEDIN_EMAIL = ""   # Your LinkedIn email
    LINKEDIN_PASSWORD = ""
    
    COMPANY_NAME = "Jp Morgan Chase"
    MESSAGE_TEXT = """

[Refferal] Hi , I came across the Data Engineer opening at Jp Morgan Chase
Job link - https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/210706279/
and would like to apply. I’m currently a Software Engineer Analyst at Accenture with 2.4+ years of experience in databricks , pyspark , data pipelines, SQL optimization, and cloud technologies.
Would you be open to referring me or sharing my profile with the hiring team? Let me know if you need any details. Thanks !
Resume - https://drive.google.com/file/d/1ir4d3yKLf9_vjlzyXzA2-nzxXWGiPI1P/view?usp=sharing

"""
    
    MAX_MESSAGES = 20  # How many messages to send
    START_FROM = 1      # Which connection to start from
                        # Examples:
                        #   START_FROM = 1  -> Starts at page 1, position 1
                        #   START_FROM = 11 -> Starts at page 2, position 1
                        #   START_FROM = 15 -> Starts at page 2, position 5
                        #   START_FROM = 21 -> Starts at page 3, position 1
    # ===================================
    
    print("\n" + "="*60)
    print("CONFIGURATION")
    print("="*60)
    print(f"Company: {COMPANY_NAME}")
    print(f"Max Messages: {MAX_MESSAGES}")
    print(f"Start From: #{START_FROM}")
    print("="*60)
    
    print("\n⚠️  DISCLAIMER:")
    print("Educational purposes only. May violate LinkedIn ToS.")
    print("Use at your own risk.")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    bot = LinkedInBot(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)
    bot.run_automation(COMPANY_NAME, MESSAGE_TEXT, MAX_MESSAGES, START_FROM)


if __name__ == "__main__":
    main()