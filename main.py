from unilog import UniversityLogin


def test_login():
    portal = UniversityLogin()
    
    try:
        portal.setup_driver()
        
        # TEST WITH DUMMY CREDENTIALS FIRST
        success = portal.login("402130284", "2283980429aA")
        
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