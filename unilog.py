from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import time
import jdatetime
from datetime import datetime, timedelta
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

    def persian_to_gregorian_secure(self, persian_date_str):
        """
        تبدیل تاریخ شمسی به میلادی - نسخه کاملاً مطمئن
        """
        try:
            print(f"🔧 در حال تبدیل: {persian_date_str}")  # دیباگ
            
            # استخراج اجزای تاریخ با روش مطمئن
            day_str, month_name, year_str, time_str = self.extract_date_parts_secure(persian_date_str)
            
            # تبدیل به عدد
            day = int(day_str)
            year = int(year_str)
            
            # تبدیل نام ماه به عدد
            month_dict = {
                'فروردین': 1, 'اردیبهشت': 2, 'خرداد': 3,
                'تیر': 4, 'مرداد': 5, 'شهریور': 6,
                'مهر': 7, 'آبان': 8, 'آذر': 9,
                'دی': 10, 'بهمن': 11, 'اسفند': 12
            }
            
            month = month_dict.get(month_name)
            if month is None:
                raise ValueError(f"نام ماه نامعتبر: {month_name}")
            
            # تبدیل تاریخ شمسی به میلادی
            jalali_date = jdatetime.date(year, month, day)
            gregorian_date = jalali_date.togregorian()
            
            # ترکیب با زمان
            time_parts = time_str.split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            final_datetime = datetime(
                gregorian_date.year, gregorian_date.month, gregorian_date.day,
                hour, minute
            )
            
            print(f"✅ تبدیل موفق: {day} {month_name} {year} - {time_str} -> {final_datetime}")
            return final_datetime
        
        except Exception as e:
            print(f"❌ خطا در تبدیل تاریخ: {persian_date_str} - {e}")
            
    def extract_class_sessions(self):
        file = open("dates.html", "r")
        html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        class_headers = soup.find_all('h4', class_='text-info')
        
        results = []
        
        for class_header in class_headers:
            class_name = class_header.get_text(strip=True)
            # تبدیل اعداد در نام کلاس هم
            class_name = self.convert_persian_numbers(class_name)
            
            sessions = []
            current_element = class_header.next_sibling
            
            while current_element and (current_element.name != 'h4' or 'text-info' not in current_element.get('class', [])):
                if current_element.name == 'td':
                    td_text = current_element.get_text(strip=True)
                    # تبدیل اعداد در متن جلسه
                    td_text = self.convert_persian_numbers(td_text)
                    
                    if td_text == 'جلسه':
                        session_data = {}
                        
                        next_td = current_element.find_next_sibling('td')
                        if next_td:
                            start_text = next_td.get_text(strip=True)
                            session_data['start_persian'] = start_text
                            session_data['start_gregorian'] = self.persian_to_gregorian_secure(start_text)
                        
                        next_td = next_td.find_next_sibling('td') if next_td else None
                        if next_td:
                            end_text = next_td.get_text(strip=True)
                            session_data['end_persian'] = end_text
                            session_data['end_gregorian'] = self.persian_to_gregorian_secure(end_text)
                        
                        if session_data:
                            # ایجاد شناسه منحصر به فرد برای هر جلسه
                            session_data['uid'] = f"{class_name}_{len(sessions)+1}_{session_data['start_gregorian'].strftime('%Y%m%d%H%M')}"
                            sessions.append(session_data)
                
                current_element = current_element.next_sibling if current_element else None
            
            results.append({
                'class_name': class_name,
                'sessions': sessions
            })
        
        return results

    def create_ics_file(self, results, filename='class_schedule.ics'):
        """
        ساخت فایل ICS از نتایج
        """
        with open(filename, 'w', encoding='utf-8') as f:
            # هدر فایل ICS
            f.write("BEGIN:VCALENDAR\n")
            f.write("VERSION:2.0\n")
            f.write("PRODID:-//Class Schedule//FA\n")
            f.write("CALSCALE:GREGORIAN\n")
            f.write("METHOD:PUBLISH\n")
            
            # برای هر کلاس و هر جلسه
            for class_info in results:
                for i, session in enumerate(class_info['sessions']):
                    f.write("BEGIN:VEVENT\n")
                    
                    # UID منحصر به فرد
                    f.write(f"UID:{session['uid']}\n")
                    
                    # خلاصه رویداد (عنوان)
                    summary = f"{class_info['class_name']} - جلسه {i+1}"
                    f.write(f"SUMMARY:{summary}\n")
                    
                    # زمان شروع
                    dtstart = session['start_gregorian'].strftime('%Y%m%dT%H%M%S')
                    f.write(f"DTSTART:{dtstart}\n")
                    
                    # زمان پایان
                    dtend = session['end_gregorian'].strftime('%Y%m%dT%H%M%S')
                    f.write(f"DTEND:{dtend}\n")
                    
                    # توضیحات
                    description = f"کلاس: {class_info['class_name']}\\n"
                    description += f"جلسه: {i+1}\\n"
                    description += f"زمان شمسی: {session['start_persian']} تا {session['end_persian']}"
                    f.write(f"DESCRIPTION:{description}\n")
                    
                    # زمان ایجاد رویداد
                    created = datetime.now().strftime('%Y%m%dT%H%M%SZ')
                    f.write(f"DTSTAMP:{created}\n")
                    
                    f.write("END:VEVENT\n")
            
            # پایان فایل ICS
            f.write("END:VCALENDAR\n")
        
        print(f"✅ فایل ICS با موفقیت ایجاد شد: {filename}")
        print(f"📅 تعداد کل رویدادها: {sum(len(class_info['sessions']) for class_info in results)}")

    def print_debug_info(self, results):
        """
        نمایش اطلاعات دیباگ برای اطمینان از صحت تبدیل تاریخ
        """
        print("\n" + "=" * 100)
        print("🔍 اطلاعات دیباگ (نمونه‌ای از جلسات تبدیل شده):")
        print("=" * 100)
        
        for class_info in results[:2]:  # فقط دو کلاس اول برای نمونه
            print(f"\n📚 کلاس: {class_info['class_name']}")
            print(f"📊 تعداد جلسات: {len(class_info['sessions'])}")
            
            for i, session in enumerate(class_info['sessions'][:3]):  # فقط سه جلسه اول
                print(f"  جلسه {i+1}:")
                print(f"    📅 شمسی: {session['start_persian']} -> {session['end_persian']}")
                print(f"    🌍 میلادی: {session['start_gregorian']} -> {session['end_gregorian']}")
                print()


    def convert_persian_numbers(self, text):
        """تبدیل اعداد فارسی به انگلیسی"""
        persian_numbers = {
            '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
            '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
        }
        
        result = ""
        for char in text:
            if char in persian_numbers:
                result += persian_numbers[char]
            else:
                result += char
        return result

    def normalize_weekday_name(self, text):
        """نرمال‌سازی نام روزهای هفته"""
        # حذف فاصله‌های اضافی و نرمال‌سازی
        text = ' '.join(text.split())
        
        # جایگزینی نام روزها (برای اطمینان از فرمت یکسان)
        weekday_replacements = {
            'یکشنبه': 'یکشنبه',
            'دوشنبه': 'دوشنبه', 
            'سه شنبه': 'سه‌شنبه',
            'چهارشنبه': 'چهارشنبه',
            'پنجشنبه': 'پنجشنبه',
            'پنج شنبه': 'پنجشنبه',
            'جمعه': 'جمعه',
            'شنبه': 'شنبه'
        }
        
        words = text.split()
        if words and words[0] in weekday_replacements:
            words[0] = weekday_replacements[words[0]]
            return ' '.join(words)
        
        return text
    def extract_date_parts(self, date_text):
        """استخراج مطمئن اجزای تاریخ - فقط اعداد و نام ماه"""
        # تبدیل اعداد فارسی به انگلیسی
        date_text = self.convert_persian_numbers(date_text)
        
        # حذف تمام روزهای هفته به هر شکلی
        weekdays = ['شنبه', 'یک شنبه', 'یکشنبه','یک‌شنبه', 'دوشنبه', 'دو شنبه', 'دو‌شنبه',
                    'سهشنبه', 'سه شنبه', 'سه‌شنبه', 'چهارشنبه', 'چهار شنبه', 'چهار‌شنبه',
                    'پنج‌شنبه', 'پنجشنبه', 'پنج شنبه', 'جمعه']
        
        for weekday in weekdays:
            date_text = date_text.replace(weekday, '')
        
        # حذف فاصله‌های اضافی
        date_text = ' '.join(date_text.split())
        
        print(f"🔧 متن بعد از حذف روزها: {date_text}")  # دیباگ
        
        # جدا کردن تاریخ و زمان
        if ' - ' not in date_text:
            raise ValueError(f"فرمت تاریخ نامعتبر است: {date_text}")
        
        date_part, time_part = date_text.split(' - ', 1)
        date_part = date_part.strip()
        time_part = time_part.strip()
        
        # استخراج اجزای تاریخ
        date_parts = date_part.split()
        
        # پیدا کردن موقعیت ماه در لیست
        month_names = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 
                    'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
        
        month_index = -1
        month_name = None
        
        for i, part in enumerate(date_parts):
            if part in month_names:
                month_index = i
                month_name = part
                break
        
        if month_index == -1:
            raise ValueError(f"نام ماه پیدا نشد: {date_part}")
        
        # روز باید قبل از ماه باشد
        if month_index == 0:
            raise ValueError(f"روز پیدا نشد: {date_part}")
        
        day_str = date_parts[month_index - 1]
        
        # سال باید بعد از ماه باشد
        if month_index + 1 >= len(date_parts):
            raise ValueError(f"سال پیدا نشد: {date_part}")
        
        year_str = date_parts[month_index + 1]
        
        return day_str, month_name, year_str, time_part


    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
