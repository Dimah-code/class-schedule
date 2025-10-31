# src/config.py
"""
Configuration settings for class schedule
"""

import os
from getpass import getpass


class Config:
    """Handles application configuration and credentials"""
    OUTPUT_DIR: str = "out"
    TEMP_DIR: str = "src/temp"
    
    def __init__(self):
        
        self.base_url = "https://vc.farspnu.ac.ir"
        self.login_url = "https://vc.farspnu.ac.ir/Identity/Account/Login?returnUrl=%2F"
        self.courses_url = "https://vc.farspnu.ac.ir/Student/Course"
        self.temporary_files = ["src/temp/dates.html", "src/temp/urls.txt", "src/temp/absolute_urls.txt"]
        
    def get_credentials(self):
        """Safely get username and password from user input"""
        print("University Portal Login")
        print("-" * 30)
        
        username = input("Enter your username: ").strip()
        password = getpass("Enter your password: ").strip()
        
        if not username or not password:
            raise ValueError("Username and password cannot be empty")
            
        return username, password


# Create global config instance
config = Config()