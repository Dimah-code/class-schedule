from unilog import UniversityLogin


def login():
    portal = UniversityLogin()
    
    try:
        portal.setup_driver()
        
        # Enter your username and password
        username = "ENTER YOUR USERNAME"
        password = "ENTER YOUR PASSWORD"
        portal.login(username, password)
        
        
        # Keep browser open to inspect
        input("Press Enter to close browser...")
        
    finally:
        portal.close()
        open("dates.html", "w").close()
        open("urls.txt", "w").close()
        open("abs_urls.txt", "w").close()

if __name__ == "__main__":
    login()