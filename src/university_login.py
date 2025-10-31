"""
University Portal Login Handler
Handles authentication and browser session management for the university portal
"""

import time
import logging
from typing import Optional
from src.config import config

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logger = logging.getLogger(__name__)

class UniversityLogin:
    """Handles university portal authentication and browser management"""
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.login_url = config.login_url
    
    def setup_driver(self):
        """Setup and configure Chrome driver with appropriate options"""
        try:
            logger.info("Setting up Chrome driver...")
            
            chrome_options = Options()
            # Add essential options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            # Initialize driver with WebDriverManager
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Set up wait for element interactions
            self.wait = WebDriverWait(self.driver, 10)
            
            logger.info("Chrome driver setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    

    def login(self, username: str, password: str) -> bool:
        """Login to university portal with provided credentials
        
        Args:
            username: University portal username
            password: University portal password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info("Attempting to login to university portal...")
            
            # Navigate to login page
            self.driver.get(self.login_url)
            logger.debug("Navigated to login page")
            
            # Wait for and populate username field
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "UserName"))
            )
            username_field.send_keys(username)
            logger.debug("Username entered")
            
            # Find and populate password field
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            logger.debug("Password entered")
            
            # Click login button
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            logger.debug("Login button clicked")
            
            # Wait for login process to complete
            time.sleep(3)
            
            # Check if login was successful by looking for dashboard or error
            if self._is_login_successful():
                logger.info("Login successful!")
                return True
            else:
                logger.warning("Login may have failed - unable to verify success")
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False


    def _is_login_successful(self) -> bool:
        """Check if login was successful by looking for indicators on the page"""
        try:
            # Check for common elements that appear after successful login
            # Adjust these selectors based on your university portal
            success_indicators = [
                "//a[contains(text(), 'Logout')]",
                "//a[contains(text(), 'Dashboard')]",
                "//span[contains(text(), 'Welcome')]"
            ]
            
            for indicator in success_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        return True
                except:
                    continue
            
            # Also check if we're still on login page (indicating failure)
            if "Login" in self.driver.title or "login" in self.driver.current_url:
                return False
                
            return True
            
        except Exception as e:
            logger.debug(f"Could not determine login status: {e}")
            return False
    
    def close(self) -> None:
        """Close the browser and cleanup resources"""
        if self.driver:
            logger.info("Closing browser...")
            self.driver.quit()
            self.driver = None
            self.wait = None


    def get_driver(self):
        """Get the current driver instance for sharing with other components"""
        return self.driver

    def get_wait(self):
        """Get the WebDriverWait instance"""
        return self.wait