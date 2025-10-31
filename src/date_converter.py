"""
Date Conversion Utilities
Handles Persian-to-Gregorian date conversion and Persian number normalization
"""

import re
import logging
from datetime import datetime
from typing import Dict, Optional, Any

import jdatetime

logger = logging.getLogger(__name__)


class DateConverter:
    """Handles conversion between Persian and Gregorian calendar systems"""
    
    # Persian and Arabic to English number mapping
    PERSIAN_TO_ENGLISH_NUMBERS = {
        '۰': '0', '٠': '0',  # Persian zero, Arabic zero
        '۱': '1', '١': '1',  # Persian one, Arabic one
        '۲': '2', '٢': '2',  # Persian two, Arabic two
        '۳': '3', '٣': '3',  # Persian three, Arabic three
        '۴': '4', '٤': '4',  # Persian four, Arabic four
        '۵': '5', '٥': '5',  # Persian five, Arabic five
        '۶': '6', '٦': '6',  # Persian six, Arabic six
        '۷': '7', '٧': '7',  # Persian seven, Arabic seven
        '۸': '8', '٨': '8',  # Persian eight, Arabic eight
        '۹': '9', '٩': '9'   # Persian nine, Arabic nine
    }
    
    # Persian month names to numbers
    PERSIAN_MONTHS = {
        'فروردین': '1', 'اردیبهشت': '2', 'خرداد': '3',
        'تیر': '4', 'مرداد': '5', 'شهریور': '6',
        'مهر': '7', 'آبان': '8', 'آذر': '9',
        'دی': '10', 'بهمن': '11', 'اسفند': '12'
    }

    @staticmethod
    def persian_to_english_numbers(text: str) -> str:
        """Convert Persian and Arabic numbers to English numbers
        
        Args:
            text: String containing Persian/Arabic numbers
            
        Returns:
            String with English numbers
        """
        if not text:
            return text
            
        result = ''
        for char in text:
            result += DateConverter.PERSIAN_TO_ENGLISH_NUMBERS.get(char, char)
        return result

    @staticmethod
    def extract_date_components(date_string: str) -> Dict[str, str]:
        """Extract year, month, day, and time from Persian date string
        
        Args:
            date_string: Persian date string with possible time
            
        Returns:
            Dictionary with extracted date components
        """
        if not date_string or not date_string.strip():
            logger.warning("Empty date string provided")
            return {
                'year': '', 'month': '', 'day': '', 'time': '', 
                'full_date': '', 'original_string': date_string
            }
        
        try:
            # Convert Persian numbers to English for easier processing
            cleaned = DateConverter.persian_to_english_numbers(date_string)
            logger.debug(f"Cleaned date string: {cleaned}")
            
            # Extract time component (HH:MM format)
            time_match = re.search(r'(\d{1,2}:\d{2})', cleaned)
            time_str = time_match.group(1) if time_match else ""
            
            # Remove time to focus on date extraction
            cleaned_without_time = re.sub(r'\d{1,2}:\d{2}', '', cleaned)
            
            # Extract all numbers from the date string
            numbers = re.findall(r'\d+', cleaned_without_time)
            
            # Initialize components
            year, month, day = "", "", ""
            
            # Year is typically 4 digits in Persian dates
            for num in numbers:
                if len(num) == 4:
                    year = num
                    break
            
            # Find month using Persian month names
            month = DateConverter._extract_month_from_persian(date_string)
            
            # Day is typically 1-2 digits and not the year or month
            for num in numbers:
                if len(num) <= 2 and num != year and num != month:
                    day = num
                    # Use first valid day found
                    break
            
            # Validate that we have all required components
            if not all([year, month, day]):
                logger.warning(f"Incomplete date components extracted: {year}/{month}/{day}")
            
            full_date = f"{year}/{month}/{day}"
            if time_str:
                full_date += f" - {time_str}"
                
            return {
                'year': year,
                'month': month,
                'day': day,
                'time': time_str,
                'full_date': full_date,
                'original_string': date_string
            }
            
        except Exception as e:
            logger.error(f"Error extracting date components from '{date_string}': {e}")
            return {
                'year': '', 'month': '', 'day': '', 'time': '', 
                'full_date': '', 'original_string': date_string
            }

    @staticmethod
    def _extract_month_from_persian(date_string: str) -> str:
        """Extract month number from Persian month names
        
        Args:
            date_string: Original Persian date string
            
        Returns:
            Month number as string, empty string if not found
        """
        for month_name, month_num in DateConverter.PERSIAN_MONTHS.items():
            if month_name in date_string:
                return month_num
        return ""

    @staticmethod
    def persian_to_georgian(date_dict: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Convert Persian date components to Gregorian date
        
        Args:
            date_dict: Dictionary with Persian date components
                       (must contain 'year', 'month', 'day')
                       
        Returns:
            Dictionary with Gregorian date components or None if conversion fails
        """
        try:
            # Validate input
            if not all(key in date_dict for key in ['year', 'month', 'day']):
                logger.error("Missing required date components")
                return None
            
            year_str = date_dict['year']
            month_str = date_dict['month']
            day_str = date_dict['day']
            time_str = date_dict.get('time', '')
            
            # Validate components are not empty
            if not all([year_str, month_str, day_str]):
                logger.error("Empty date components provided")
                return None
            
            # Convert to integers
            year = int(year_str)
            month = int(month_str)
            day = int(day_str)
            
            logger.debug(f"Converting Persian date: {year}/{month}/{day} {time_str}")
            
            # Convert Persian date to Gregorian
            persian_date = jdatetime.date(year, month, day)
            georgian_date = persian_date.togregorian()
            
            # Handle time component if present
            if time_str:
                try:
                    hour, minute = map(int, time_str.split(':'))
                    georgian_datetime = datetime(
                        georgian_date.year, georgian_date.month, georgian_date.day,
                        hour, minute
                    )
                    full_date = georgian_datetime.strftime('%Y-%m-%d %H:%M')
                except ValueError as e:
                    logger.warning(f"Invalid time format '{time_str}': {e}")
                    georgian_datetime = None
                    full_date = georgian_date.strftime('%Y-%m-%d')
            else:
                georgian_datetime = None
                full_date = georgian_date.strftime('%Y-%m-%d')
            
            result = {
                'year': str(georgian_date.year),
                'month': str(georgian_date.month).zfill(2),
                'day': str(georgian_date.day).zfill(2),
                'time': time_str,
                'date_object': georgian_datetime,
                'full_date': full_date,
                'display': f"{georgian_date.year}/{georgian_date.month:02d}/{georgian_date.day:02d}"
            }
            
            if time_str:
                result['display'] += f" - {time_str}"
            
            logger.debug(f"Conversion result: {result['display']}")
            return result
            
        except ValueError as e:
            logger.error(f"Invalid date values in {date_dict}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error converting date {date_dict}: {e}")
            return None

    @staticmethod
    def convert_persian_date_string(persian_date: str) -> Optional[Dict[str, Any]]:
        """Convenience method to convert Persian date string directly to Gregorian
        
        Args:
            persian_date: Persian date string
            
        Returns:
            Gregorian date dictionary or None if conversion fails
        """
        try:
            # Extract components from Persian string
            persian_components = DateConverter.extract_date_components(persian_date)
            
            # Convert to Gregorian
            return DateConverter.persian_to_georgian(persian_components)
            
        except Exception as e:
            logger.error(f"Failed to convert Persian date '{persian_date}': {e}")
            return None


def main():
    """Test function for date conversion"""
    try:
        test_date = input("Enter a Persian date to test: ").strip()
        if not test_date:
            print("No date provided.")
            return
            
        print(f"\nTesting conversion for: '{test_date}'")
        
        # Test component extraction
        components = DateConverter.extract_date_components(test_date)
        print(f"Extracted components: {components}")
        
        # Test full conversion
        gregorian = DateConverter.convert_persian_date_string(test_date)
        if gregorian:
            print(f"Gregorian date: {gregorian['display']}")
        else:
            print("Conversion failed!")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Error during test: {e}")


if __name__ == "__main__":
    main()