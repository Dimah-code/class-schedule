from bs4 import BeautifulSoup
import re

def persian_to_english_numbers(text):
    """Convert Persian numbers to English numbers"""
    persian_numbers = {
        '۰': '0', '٠': '0',  # Persian and Arabic zero
        '۱': '1', '١': '1',  # Persian and Arabic one
        '۲': '2', '٢': '2',  # Persian and Arabic two
        '۳': '3', '٣': '3',  # Persian and Arabic three
        '۴': '4', '٤': '4',  # Persian and Arabic four
        '۵': '5', '٥': '5',  # Persian and Arabic five
        '۶': '6', '٦': '6',  # Persian and Arabic six
        '۷': '7', '٧': '7',  # Persian and Arabic seven
        '۸': '8', '٨': '8',  # Persian and Arabic eight
        '۹': '9', '٩': '9'   # Persian and Arabic nine
    }
    
    result = ''
    for char in text:
        if char in persian_numbers:
            result += persian_numbers[char]
        else:
            result += char
    return result

def extract_date_components(date_string):
    """استخراج جداگانه سال، ماه، روز و ساعت از تاریخ فارسی"""
    # تبدیل اعداد فارسی به انگلیسی
    cleaned = persian_to_english_numbers(date_string)
    
    # استخراج زمان (باید قبل از استخراج اعداد انجام شود)
    time_match = re.search(r'(\d{1,2}:\d{2})', cleaned)
    time_str = time_match.group(1) if time_match else ""
    
    # حذف زمان از متن برای جلوگیری از اشتباه
    cleaned_without_time = re.sub(r'\d{1,2}:\d{2}', '', cleaned)
    
    # استخراج اعداد (سال، ماه، روز)
    numbers = re.findall(r'\d+', cleaned_without_time)
    
    # تشخیص ترتیب صحیح: در تاریخ فارسی معمولاً: روز ماه سال
    year = ""
    month = ""
    day = ""
    
    # سال همیشه ۴ رقمی است
    for num in numbers:
        if len(num) == 4:
            year = num
            break
    
    # ماه از نام ماه تشخیص داده می‌شود
    month_names = {
        'فروردین': '1', 'اردیبهشت': '2', 'خرداد': '3',
        'تیر': '4', 'مرداد': '5', 'شهریور': '6',
        'مهر': '7', 'آبان': '8', 'آذر': '9',
        'دی': '10', 'بهمن': '11', 'اسفند': '12'
    }
    
    for month_name, month_num in month_names.items():
        if month_name in date_string:
            month = month_num
            break
    
    # روز: اولین عدد ۱ یا ۲ رقمی که سال نیست
    for num in numbers:
        if len(num) <= 2 and num != year and num != month:
            day = num
            break
    
    return {
        'year': year,
        'month': month,
        'day': day,
        'time': time_str,
        'full_date': f"{year}/{month}/{day}" + (f" - {time_str}" if time_str else "")
    }

if __name__ == "__main__":
    date = input("Enter a date in persian: ")
    result = extract_date_components(date)
    print(result['full_date'])