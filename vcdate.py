import re

def persian_to_english_numbers(text):
    """Convert Persian numbers to English numbers"""
    persian_numbers = {
        '۰': '0', '٠': '0',
        '۱': '1', '١': '1',
        '۲': '2', '٢': '2',
        '۳': '3', '٣': '3',
        '۴': '4', '٤': '4',
        '۵': '5', '٥': '5',
        '۶': '6', '٦': '6',
        '۷': '7', '٧': '7',
        '۸': '8', '٨': '8',
        '۹': '9', '٩': '9'
    }
    
    result = ''
    for char in text:
        if char in persian_numbers:
            result += persian_numbers[char]
        else:
            result += char
    return result

def extract_date_components(date_string):
    """ Extract year month day and time """
    # Convert persian numbers to english numbers
    cleaned = persian_to_english_numbers(date_string)
    
    # Extract time before date
    time_match = re.search(r'(\d{1,2}:\d{2})', cleaned)
    time_str = time_match.group(1) if time_match else ""
    
    # remove time to imporve cleanness
    cleaned_without_time = re.sub(r'\d{1,2}:\d{2}', '', cleaned)
    
    # Extract date(Year, Month, Day)
    numbers = re.findall(r'\d+', cleaned_without_time)
    
    # Make it in Persian date format
    year = ""
    month = ""
    day = ""
    
    # Year must be 4 digits
    for num in numbers:
        if len(num) == 4:
            year = num
            break
    
    # find month with month names
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
    
    # find day
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