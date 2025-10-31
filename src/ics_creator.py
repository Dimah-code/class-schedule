"""
ICS Calendar File Generator
Creates iCalendar (.ics) files for university class schedules
"""

import os
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class IcsCreator:
    """Handles creation of iCalendar files from class schedule data"""
    
    def __init__(self, output_dir: str = "out"):
        self.output_dir = output_dir
        self._ensure_output_directory()
    
    def _ensure_output_directory(self) -> None:
        """Create output directory if it doesn't exist"""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            logger.debug(f"Output directory ensured: {self.output_dir}")
        except Exception as e:
            logger.error(f"Failed to create output directory {self.output_dir}: {e}")
            raise
    
    def create_ics_file(self, results: List[Dict[str, Any]], filename: str = 'class_schedule.ics') -> str:
        """Create .ics file for importing into calendar applications
        
        Args:
            results: List of class information with sessions
            filename: Output filename for the ICS file
            
        Returns:
            Path to the created ICS file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            logger.info(f"Creating ICS file: {filepath}")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write calendar header
                f.write("BEGIN:VCALENDAR\n")
                f.write("VERSION:2.0\n")
                f.write("PRODID:-//University Class Schedule//FA\n")
                f.write("CALSCALE:GREGORIAN\n")
                f.write("METHOD:PUBLISH\n")
                
                # Write events for each class session
                class_counter, session_counter = self._write_events(f, results)
                
                # Write calendar footer
                f.write("END:VCALENDAR\n")
            
            self._log_creation_summary(class_counter, session_counter, filepath)
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to create ICS file {filepath}: {e}")
            raise
    
    def _write_events(self, file_handle, results: List[Dict[str, Any]]) -> tuple[int, int]:
        """Write VEVENT entries for all class sessions
        
        Args:
            file_handle: Open file handle for writing
            results: Class schedule data
            
        Returns:
            Tuple of (class_count, session_count)
        """
        class_counter = 0
        session_counter = 0
        
        for class_info in results:
            class_counter += 1
            class_name = self._sanitize_text(class_info['class_name'])
            
            for session in class_info['sessions']:
                session_counter += 1
                self._write_single_event(file_handle, class_name, session)
        
        return class_counter, session_counter
    
    def _write_single_event(self, file_handle, class_name: str, session: Dict[str, Any]) -> None:
        """Write a single VEVENT entry
        
        Args:
            file_handle: Open file handle for writing
            class_name: Name of the class
            session: Session data with start/end times
        """
        try:
            # Validate session data
            if not self._validate_session_data(session):
                logger.warning(f"Skipping invalid session for {class_name}")
                return
            
            start_dt = session['start_gregorian']['date_object']
            end_dt = session['end_gregorian']['date_object']
            uid = session.get('uid', f"{class_name}_{start_dt.strftime('%Y%m%d%H%M')}")
            
            # Write event
            file_handle.write("BEGIN:VEVENT\n")
            file_handle.write(f"UID:{uid}\n")
            file_handle.write(f"SUMMARY:{class_name}\n")
            file_handle.write(f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}\n")
            file_handle.write(f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}\n")
            file_handle.write(f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}\n")
            file_handle.write("SEQUENCE:0\n")
            file_handle.write("TRANSP:OPAQUE\n")
            file_handle.write("END:VEVENT\n")
            
        except Exception as e:
            logger.error(f"Failed to write event for {class_name}: {e}")
    
    def _validate_session_data(self, session: Dict[str, Any]) -> bool:
        """Validate that session has required data for ICS creation
        
        Args:
            session: Session data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ['start_gregorian', 'end_gregorian']
        
        # Check required keys exist
        if not all(key in session for key in required_keys):
            return False
        
        # Check date objects exist and are valid
        start_data = session['start_gregorian']
        end_data = session['end_gregorian']
        
        if not start_data.get('date_object') or not end_data.get('date_object'):
            return False
        
        # Check end is after start
        if start_data['date_object'] >= end_data['date_object']:
            logger.warning(f"Invalid time range: end before start")
            return False
        
        return True
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text for ICS format
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text safe for ICS format
        """
        if not text:
            return ""
        
        # Remove or replace characters that might break ICS format
        sanitized = text.replace('\n', ' ').replace('\r', ' ')
        sanitized = sanitized.replace(';', ',').replace('\\', '/')
        
        # Limit length for calendar compatibility
        if len(sanitized) > 100:
            sanitized = sanitized[:97] + "..."
            
        return sanitized
    
    def _log_creation_summary(self, class_count: int, session_count: int, filepath: str) -> None:
        """Log summary of ICS file creation
        
        Args:
            class_count: Number of classes processed
            session_count: Number of sessions created
            filepath: Path to the created file
        """
        logger.info(f"ICS file created successfully: {filepath}")
        logger.info(f"Created {class_count} classes with {session_count} sessions")
        
        print(f"\n🎉 Calendar file created successfully!")
        print(f"📁 File: {filepath}")
        print(f"📚 Classes: {class_count}")
        print(f"📅 Sessions: {session_count}")
        print(f"✅ Ready to import into your calendar application!")
    
    def print_debug_info(self, results: List[Dict[str, Any]]) -> None:
        """Print detailed information about extracted classes and sessions
        
        Args:
            results: List of class information with sessions
        """
        if not results:
            print("❌ No data to display")
            return
        
        total_classes = len(results)
        total_sessions = sum(len(class_info['sessions']) for class_info in results)
        
        print("\n" + "=" * 80)
        print("📊 EXTRACTED CLASS SCHEDULE SUMMARY")
        print("=" * 80)
        print(f"🏫 Total Classes: {total_classes}")
        print(f"📅 Total Sessions: {total_sessions}")
        print("=" * 80)
        
        for class_index, class_info in enumerate(results, 1):
            class_name = class_info['class_name']
            session_count = len(class_info['sessions'])
            
            print(f"\n📖 Class {class_index}/{total_classes}: {class_name}")
            print(f"   📋 Sessions: {session_count}")
            print("   " + "─" * 50)
            
            for session_index, session in enumerate(class_info['sessions'], 1):
                start_display = session['start_gregorian']['display']
                end_display = session['end_gregorian']['display']
                
                print(f"   🕒 Session {session_index}:")
                print(f"      🟢 Start: {start_display}")
                print(f"      🔴 End:   {end_display}")
            
            # Add separator between classes (except after last one)
            if class_index < total_classes:
                print("\n   " + "⋅" * 50)
        
        print("\n" + "=" * 80)
        print("✅ Debug information display completed")
        print("=" * 80)