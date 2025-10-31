"""
Class-Schedule - Main Entry Point
Handles university login and schedule extraction workflow
"""

from src.university_login import UniversityLogin
from src.scraper import Scraper
import sys
from src.config import config


def main():
    """Main execution function for the class schedule application"""

    portal = UniversityLogin()
    
    try:
        username, password = config.get_credentials()

        portal.setup_driver()
        print("Attempting login...")
        login_success = portal.login(username, password)

        if login_success:
            print("Login successful! Navigating to courses...")
            
            # Pass the driver to Scraper
            scraper = Scraper(portal.get_driver(), portal.get_wait())
            scraper.go_to_courses()

        # Keep browser open to inspect
        input("Press Enter to close browser...")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Always cleanup resources
        cleanup_resources(portal)


def cleanup_resources(portal):
    """Clean up browser session and temporary files"""
    print("Cleaning up resources...")

    # Close browser
    portal.close()

    # Clean up temporary files
    for file in config.temporary_files:
        try:
            open(file, "w").close()
            print(f"Cleared: {file}")
        except Exception as e:
            print(f"Could not clear {file}: {e}")


if __name__ == "__main__":
    main()