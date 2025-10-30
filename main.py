from unilog import UniversityLogin


def test_login():
    portal = UniversityLogin()
    
    try:
        portal.setup_driver()
        
        # TEST WITH DUMMY CREDENTIALS FIRST
        username = "ENTER YOUR USERNAME"
        password = "ENTER YOUR PASSWORD"
        success = portal.login(username, password)
        
        if success:
            print("Ready to use real credentials!")
        else:
            print("Need to adjust the script")
            
        # Keep browser open to inspect
        input("Press Enter to close browser...")
        
    finally:
        portal.close()
        open("dates.html", "w").close()
        open("urls.txt", "w").close()
        open("abs_urls.txt", "w").close()

if __name__ == "__main__":
    test_login()