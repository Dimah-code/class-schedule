from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from pprint import pprint
import time
import jdatetime
from datetime import datetime, timedelta
from vcdate import extract_date_components
import re


class UniversityLogin:
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 10)

    def login(self, username, password):
        """Login to university portal"""
        try:
            # Navigate to login page
            self.driver.get("https://vc.farspnu.ac.ir/Identity/Account/Login?returnUrl=%2F")
            
            # Find login elements using the identifiers you found
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "UserName"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.NAME, "login")
            
            # Enter credentials and login
            username_field.send_keys(username)
            password_field.send_keys(password)
            login_button.click()
            
            # Wait for login to complete - we'll need to see what page loads after login
            time.sleep(3)

            self.go_to_courses()

        except Exception as e:
            print(f"Login error: {e}")
            return False

    def go_to_courses(self):
        self.driver.get("https://vc.farspnu.ac.ir/Student/Course")
            
        table = self.wait.until(EC.presence_of_element_located((By.ID, 'table')))
        rows = table.find_elements(By.TAG_NAME, 'tr')

        urls = []
        for row in rows:
            style = row.get_attribute('style')
            if "background-color: rgb(255, 238, 186);" in style:
                continue
            
            html = row.get_attribute('outerHTML')
            urls.append(str(html))
        
        with open("urls.txt", "w") as file:
            file.writelines(urls)
        print(f"Found {(len(urls) - 1)} courses to process")
        self.bs_logics()

    def bs_logics(self):

        with open("urls.txt", "r+") as file:
            text = file.read()
            soup = BeautifulSoup(text, 'html.parser')
            links = soup.find_all('a', href=True)

        with open("abs_urls.txt", "w") as wfile:
            for link in links:
                wfile.write(link['href'] + '\n')
        self.each_course()

    def each_course(self):

        with open("abs_urls.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                if len(line) > 7:
                    main = "https://vc.farspnu.ac.ir"
                    full_url = main + line
                    self.get_table(full_url)
            result = self.extract_class_sessions()
            self.print_debug_info(result)
            self.create_ics_file(result)
            

    def get_table(self, url):

        self.driver.get(url)
        print(f"We go to {url}")

        title = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h4')))
        table = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'table')))
        rows = table.find_elements(By.TAG_NAME, 'td')
        with open("dates.html", "a") as file:            
            
            file.write(title.get_attribute('outerHTML'))
            for row in rows:
                file.write(row.get_attribute('outerHTML'))

 
    def extract_class_sessions(self):
        file = open("dates.html", "r")
        html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        class_headers = soup.find_all('h4', class_='text-info')

        results = []
        for class_header in class_headers:
            class_name = class_header.get_text(strip=True)
            
            sessions = []
            current_element = class_header.next_sibling
            
            while current_element and (current_element.name != 'h4' or 'text-info' not in current_element.get('class', [])):
                if current_element.name == 'td':
                    td_text = current_element.get_text(strip=True)
                    
                    if td_text == 'جلسه':
                        session_data = {}
                        
                        next_td = current_element.find_next_sibling('td')
                        if next_td:
                            start_text = next_td.get_text(strip=True)
                            start_date = extract_date_components(start_text)
                            session_data['start_persian'] = start_date
                            session_data['start_gregorian'] = self.persian_to_georgian(start_date)
                        
                        next_td = next_td.find_next_sibling('td') if next_td else None
                        if next_td:
                            end_text = next_td.get_text(strip=True)
                            end_date = extract_date_components(end_text)
                            session_data['end_persian'] = end_date
                            session_data['end_gregorian'] = self.persian_to_georgian(end_date)
                        
                        if session_data:
                            # ایجاد شناسه منحصر به فرد برای هر جلسه
                            session_data['uid'] = f"{class_name}_{len(sessions)+1}_{session_data['start_gregorian']}"
                            sessions.append(session_data)
                
                current_element = current_element.next_sibling if current_element else None
            
            results.append({
                'class_name': class_name,
                'sessions': sessions
            })
        
        return results


    def persian_to_georgian(self, date_dict):
        try:
            year = int(date_dict['year'])
            month = int(date_dict['month'])
            day = int(date_dict['day'])
            time_str = date_dict.get('time', '')
            
            # Convert Persian date to Georgian
            persian_date = jdatetime.date(year, month, day)
            georgian_date = persian_date.togregorian()
            
            # Handle time
            if time_str:
                hour, minute = map(int, time_str.split(':'))
                georgian_datetime = datetime(
                    georgian_date.year, georgian_date.month, georgian_date.day,
                    hour, minute
                )
                full_date = georgian_datetime.strftime('%Y-%m-%d %H:%M')
            else:
                georgian_datetime = None
                full_date = georgian_date.strftime('%Y-%m-%d')
            
            return {
                'year': str(georgian_date.year),
                'month': str(georgian_date.month).zfill(2),
                'day': str(georgian_date.day).zfill(2),
                'time': time_str,
                'date_object': georgian_datetime,
                'full_date': full_date
            }
            
        except Exception as e:
            print(f"Error converting date: {e}")
            return None

    def create_ics_file(self, results, filename='class_schedule.ics'):
        """
        ساده‌ترین نسخه
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//University//FA\n")
            class_counter = 0
            session_counter = 0
            for class_info in results:
                class_counter += 1
                for i, session in enumerate(class_info['sessions']):
                    session_counter += 1
                    start = session['start_gregorian']['date_object']
                    end = session['end_gregorian']['date_object']
                    
                    f.write(f"BEGIN:VEVENT\n")
                    f.write(f"SUMMARY:{class_info['class_name']}\n")
                    f.write(f"DTSTART:{start.strftime('%Y%m%dT%H%M%S')}\n")
                    f.write(f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}\n")
                    f.write(f"END:VEVENT\n")
            
            f.write("END:VCALENDAR\n")
        
        print("✅ فایل ICS ایجاد شد")
        print(f"{class_counter} class created, {session_counter} created")



    def print_debug_info(self, results):
        """
        نمایش اطلاعات دیباگ برای اطمینان از صحت تبدیل تاریخ
        """
        print("\n" + "=" * 80)
        print("🔍 اطلاعات دیباگ (تمامی جلسات تبدیل شده)")
        print("=" * 80)
        
        total_classes = len(results)
        total_sessions = sum(len(class_info['sessions']) for class_info in results)
        
        print(f"📊 آمار کلی: {total_classes} کلاس | {total_sessions} جلسه")
        print("-" * 80)
        
        for class_index, class_info in enumerate(results, 1):
            print(f"\n🏫 کلاس {class_index}/{total_classes}: {class_info['class_name']}")
            print(f"📅 تعداد جلسات: {len(class_info['sessions'])}")
            print("-" * 60)
            
            for session_index, session in enumerate(class_info['sessions'], 1):
                print(f"  🔸 جلسه {session_index}:")
                print(f"     📅 تاریخ شمسی: {session['start_persian']} → {session['end_persian']}")
                print(f"     🌍 تاریخ میلادی: {session['start_gregorian']} → {session['end_gregorian']}")
            
            # خط جداکننده بین کلاس‌ها
            if class_index < total_classes:
                print("\n" + "─" * 60)
        
        print("\n" + "=" * 80)
        print("✅ نمایش اطلاعات دیباگ به پایان رسید")
        print("=" * 80)



    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
