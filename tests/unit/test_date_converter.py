import sys
import os
from datetime import datetime


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.date_converter import DateConverter

def test_persian_to_english_numbers():
    assert DateConverter.persian_to_english_numbers("پنجشنبه ۲۱/۳/۱۳۸۳") == "پنجشنبه 21/3/1383"
    assert DateConverter.persian_to_english_numbers("۱۳۸۳/۳/۲۱ پنجشنبه") == "1383/3/21 پنجشنبه"
    assert DateConverter.persian_to_english_numbers("یک شنبه ۱۳۸۳-۲-۲۱") == "یک شنبه 1383-2-21"

def test_extract_date_components():
    assert DateConverter.extract_date_components("پنج شنبه ۲۴ مهر ۱۴۰۴ - ۱۸:۰۰") == {
        'year': '1404', 'month': '7', 'day': '24', 'time': '18:00', 'full_date': '1404/7/24 - 18:00', 'original_string': 'پنج شنبه ۲۴ مهر ۱۴۰۴ - ۱۸:۰۰'
    }
    assert DateConverter.extract_date_components("یکشنبه ۱۳ مهر ۱۴۰۴ - ۱۴:۰۰") == {
        'year': '1404', 'month': '7', 'day': '13', 'time': '14:00', 'full_date': '1404/7/13 - 14:00', 'original_string': 'یکشنبه ۱۳ مهر ۱۴۰۴ - ۱۴:۰۰'
    }
    assert DateConverter.extract_date_components("دوشنبه ۱۴ اسفند ۱۴۰۴ - ۰۸:۰۰") == {
        'year': '1404', 'month': '12', 'day': '14', 'time': '08:00', 'full_date': '1404/12/14 - 08:00', 'original_string': 'دوشنبه ۱۴ اسفند ۱۴۰۴ - ۰۸:۰۰'
    }

def test_extract_month_from_persian():
    assert DateConverter._extract_month_from_persian("پنج شنبه ۲۴ مهر ۱۴۰۴ - ۱۸:۰۰") == '7'
    assert DateConverter._extract_month_from_persian("یکشنبه ۱۳ اردیبهشت ۱۴۰۴ - ۱۴:۰۰") == '2'
    assert DateConverter._extract_month_from_persian("یکشنبه ۱۳ فروردین ۱۴۰۴ - ۱۴:۰۰") == '1'
    assert DateConverter._extract_month_from_persian("دوشنبه ۱۴ اسفند ۱۴۰۴ - ۰۸:۰۰") == '12'

def test_persian_to_georgian():
    assert DateConverter.persian_to_georgian({
        'year': '1404', 'month': '7', 'day': '24', 'time': '18:00', 'full_date': '1404/7/24 - 18:00', 'original_string': 'پنج شنبه ۲۴ مهر ۱۴۰۴ - ۱۸:۰۰'
    }) == {
            'year': "2025",
            'month': "10",
            'day': "16",
            'time': "18:00",
            'date_object': datetime(2025, 10, 16, 18, 0),
            'full_date': "2025-10-16 18:00",
            'display': f"2025/10/16 - 18:00"
    }
    assert DateConverter.persian_to_georgian({
        'year': '1404', 'month': '7', 'day': '13', 'time': '14:00', 'full_date': '1404/7/13 - 14:00', 'original_string': 'یکشنبه ۱۳ مهر ۱۴۰۴ - ۱۴:۰۰'
    }) == {
        'year': "2025",
        'month': "10",
        'day': "05",
        'time': "14:00",
        'date_object': datetime(2025, 10, 5, 14, 0),
        'full_date': "2025-10-05 14:00",
        'display': f"2025/10/05 - 14:00"
    }
    assert DateConverter.persian_to_georgian({
        'year': '1404', 'month': '12', 'day': '14', 'time': '08:00', 'full_date': '1404/12/14 - 08:00', 'original_string': 'دوشنبه ۱۴ اسفند ۱۴۰۴ - ۰۸:۰۰'
    }) == {
        'year': "2026",
        'month': "03",
        'day': "05",
        'time': "08:00",
        'date_object': datetime(2026, 3, 5, 8, 0),
        'full_date': "2026-03-05 08:00",
        'display': f"2026/03/05 - 08:00"
    }

def test_convert_persian_date_string():
    assert DateConverter.convert_persian_date_string("پنج شنبه ۲۴ مهر ۱۴۰۴ - ۱۸:۰۰") == {
        'year': "2025",
        'month': "10",
        'day': "16",
        'time': "18:00",
        'date_object': datetime(2025, 10, 16, 18, 0),
        'full_date': "2025-10-16 18:00",
        'display': f"2025/10/16 - 18:00"
    }