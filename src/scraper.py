"""
Web Scraper for University Course Data
Handles extraction of course information and session schedules
"""

import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from src.date_converter import DateConverter
from src.config import config

logger = logging.getLogger(__name__)


class Scraper:
    """Handles web scraping operations for university course data"""
    
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.base_url = config.base_url
    
    def go_to_courses(self) -> None:
        """Navigate to courses page and extract course URLs"""
        try:
            logger.info("Navigating to courses page...")
            self.driver.get(config.courses_url)

            # Wait for courses table to load
            table = self.wait.until(
                EC.presence_of_element_located((By.ID, 'table'))
            )
            rows = table.find_elements(By.TAG_NAME, 'tr')

            urls = []
            for row in rows:
                # Skip rows with specific background color
                style = row.get_attribute('style')
                if "background-color: rgb(255, 238, 186);" in style:
                    continue
                
                html = row.get_attribute('outerHTML')
                urls.append(str(html))
            
            # Save course URLs
            with open("src/temp/urls.txt", "w", encoding='utf-8') as file:
                file.writelines(urls)
            
            logger.info(f"Found {len(urls) - 1} courses to process")
            self._process_course_urls()
            
        except Exception as e:
            logger.error(f"Failed to extract courses: {e}")
            raise   
    
    def _process_course_urls(self) -> None:
        """Process course URLs and extract absolute links"""
        try:
            with open("src/temp/urls.txt", "r", encoding='utf-8') as file:
                text = file.read()
            
            soup = BeautifulSoup(text, 'html.parser')
            links = soup.find_all('a', href=True)

            # Save absolute URLs
            with open("src/temp/absolute_urls.txt", "w", encoding='utf-8') as wfile:
                for link in links:
                    absolute_url = self.base_url + link['href']
                    wfile.write(absolute_url + '\n')
            
            self._process_each_course()
            
        except Exception as e:
            logger.error(f"Failed to process course URLs: {e}")
            raise
    
    def _process_each_course(self) -> None:
        """Process each course to extract session data"""
        try:
            with open("src/temp/absolute_urls.txt", "r", encoding='utf-8') as file:
                lines = file.readlines()
            
            for line in lines:
                line = line.strip()
                if len(line) > 5:
                    self._extract_course_sessions(line)

            # Process extracted data and create calendar
            result = self._extract_class_sessions()
            self._create_ics_file(result)
            
        except Exception as e:
            logger.error(f"Failed to process courses: {e}")
            raise
    
    def _extract_course_sessions(self, url: str) -> None:
        """Extract session data from a course page"""
        try:
            logger.debug(f"Extracting sessions from: {url}")
            self.driver.get(url)

            # Wait for page elements
            title = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, 'h4'))
            )
            table = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'table'))
            )
            rows = table.find_elements(By.TAG_NAME, 'td')
            
            # Save session data
            with open("src/temp/dates.html", "a", encoding='utf-8') as file:            
                file.write(title.get_attribute('outerHTML'))
                for row in rows:
                    file.write(row.get_attribute('outerHTML'))
                    
        except Exception as e:
            logger.error(f"Failed to extract sessions from {url}: {e}")
    
    def _extract_class_sessions(self) -> List[Dict[str, Any]]:
        """Extract and parse class sessions from saved HTML"""
        try:
            with open("src/temp/dates.html", "r", encoding='utf-8') as file:
                html_content = file.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            class_headers = soup.find_all('h4', class_='text-info')

            results = []
            for class_header in class_headers:
                class_name = class_header.get_text(strip=True)
                sessions = self._extract_sessions_for_class(class_header)
                
                results.append({
                    'class_name': class_name,
                    'sessions': sessions
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to extract class sessions: {e}")
            raise
    
    def _extract_sessions_for_class(self, class_header) -> List[Dict[str, Any]]:
        """Extract session data for a specific class"""
        sessions = []
        current_element = class_header.next_sibling
        
        while current_element and not self._is_next_class_header(current_element):
            if current_element.name == 'td':
                td_text = current_element.get_text(strip=True)
                
                if td_text == 'جلسه':  # Session
                    session_data = self._parse_session_data(current_element)
                    if session_data:
                        session_data['uid'] = self._generate_session_uid(
                            class_header.get_text(strip=True), 
                            len(sessions) + 1, 
                            session_data['start_gregorian']
                        )
                        sessions.append(session_data)
            
            current_element = current_element.next_sibling if current_element else None
        
        return sessions
    
    def _parse_session_data(self, session_element) -> Dict[str, Any]:
        """Parse individual session data from table elements"""
        session_data = {}
        
        # Extract start date
        start_td = session_element.find_next_sibling('td')
        if start_td:
            start_text = start_td.get_text(strip=True)
            start_date = DateConverter.extract_date_components(start_text)
            session_data['start_persian'] = start_date
            session_data['start_gregorian'] = DateConverter.persian_to_georgian(start_date)
        
        # Extract end date
        end_td = start_td.find_next_sibling('td') if start_td else None
        if end_td:
            end_text = end_td.get_text(strip=True)
            end_date = DateConverter.extract_date_components(end_text)
            session_data['end_persian'] = end_date
            session_data['end_gregorian'] = DateConverter.persian_to_georgian(end_date)
        
        return session_data if session_data else None
    
    def _is_next_class_header(self, element) -> bool:
        """Check if element is a class header indicating next class"""
        return (element.name == 'h4' and 
                'text-info' in element.get('class', []))
    
    def _generate_session_uid(self, class_name: str, session_num: int, gregorian_date: str) -> str:
        """Generate unique ID for calendar event"""
        return f"{class_name}_{session_num}_{gregorian_date}"
    
    def _create_ics_file(self, results: List[Dict[str, Any]]) -> None:
        """Create ICS calendar file from extracted sessions"""
        try:
            from src.ics_creator import IcsCreator
            
            # Create ICS file
            ics_creator = IcsCreator()
            ics_creator.print_debug_info(results)
            ics_creator.create_ics_file(results)
            
        except Exception as e:
            logger.error(f"Failed to create ICS file: {e}")
            raise

# For backward compatibility during transition
def go_to_courses():
    """Legacy function - use Scraper class instead"""
    logger.warning("Using legacy go_to_courses function - migrate to Scraper class")