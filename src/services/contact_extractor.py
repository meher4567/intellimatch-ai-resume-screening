"""
Contact Information Extractor

Extracts contact information from resume text:
- Email addresses
- Phone numbers (multiple formats)
- LinkedIn profiles
- GitHub profiles
- Location (city, state, country)
- Personal websites
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContactInfo:
    """Contact information extracted from resume"""
    emails: List[str]
    phones: List[str]
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'emails': self.emails,
            'phones': self.phones,
            'linkedin': self.linkedin,
            'github': self.github,
            'website': self.website,
            'location': self.location
        }


class ContactExtractor:
    """Extract contact information from resume text"""
    
    def __init__(self):
        """Initialize contact extractor with regex patterns"""
        
        # Email pattern (comprehensive)
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        )
        
        # Phone patterns (multiple formats)
        self.phone_patterns = [
            # US formats: (123) 456-7890, 123-456-7890, 123.456.7890, 1234567890
            re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            # International: +1 123 456 7890, +91 98765 43210
            re.compile(r'\+\d{1,3}[-.\s]?\d{3,5}[-.\s]?\d{3,5}[-.\s]?\d{3,5}\b'),
            # With country code: +1-123-456-7890
            re.compile(r'\+\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
        ]
        
        # LinkedIn patterns
        self.linkedin_patterns = [
            re.compile(r'linkedin\.com/in/[\w-]+', re.IGNORECASE),
            re.compile(r'linkedin\.com/pub/[\w-]+', re.IGNORECASE),
            re.compile(r'www\.linkedin\.com/in/[\w-]+', re.IGNORECASE),
        ]
        
        # GitHub patterns
        self.github_patterns = [
            re.compile(r'github\.com/[\w-]+', re.IGNORECASE),
            re.compile(r'www\.github\.com/[\w-]+', re.IGNORECASE),
        ]
        
        # Website patterns (personal domains, portfolios)
        self.website_pattern = re.compile(
            r'https?://(?:www\.)?[\w.-]+\.[a-z]{2,}(?:/[\w.-]*)*',
            re.IGNORECASE
        )
        
        # Location patterns
        self.location_patterns = [
            # City, State format
            re.compile(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z]{2})\b'),
            # City, State, ZIP
            re.compile(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z]{2})\s+\d{5}\b'),
            # City, Country
            re.compile(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b'),
        ]
    
    def extract_emails(self, text: str) -> List[str]:
        """
        Extract email addresses from text
        
        Args:
            text: Resume text
            
        Returns:
            List of email addresses found
        """
        emails = self.email_pattern.findall(text)
        # Remove duplicates while preserving order
        seen = set()
        unique_emails = []
        for email in emails:
            email_lower = email.lower()
            if email_lower not in seen:
                seen.add(email_lower)
                unique_emails.append(email)
        
        logger.debug(f"Found {len(unique_emails)} email(s): {unique_emails}")
        return unique_emails
    
    def extract_phones(self, text: str) -> List[str]:
        """
        Extract phone numbers from text
        
        Args:
            text: Resume text
            
        Returns:
            List of phone numbers found
        """
        phones = []
        for pattern in self.phone_patterns:
            matches = pattern.findall(text)
            phones.extend(matches)
        
        # Clean up phone numbers (remove duplicates, normalize)
        cleaned_phones = []
        seen = set()
        for phone in phones:
            # Remove all non-digit characters for comparison
            digits_only = re.sub(r'\D', '', phone)
            if digits_only not in seen and len(digits_only) >= 10:
                seen.add(digits_only)
                cleaned_phones.append(phone.strip())
        
        logger.debug(f"Found {len(cleaned_phones)} phone number(s): {cleaned_phones}")
        return cleaned_phones
    
    def extract_linkedin(self, text: str) -> Optional[str]:
        """
        Extract LinkedIn profile URL
        
        Args:
            text: Resume text
            
        Returns:
            LinkedIn URL if found, None otherwise
        """
        for pattern in self.linkedin_patterns:
            match = pattern.search(text)
            if match:
                url = match.group(0)
                # Ensure it starts with https://
                if not url.startswith('http'):
                    url = 'https://' + url
                logger.debug(f"Found LinkedIn: {url}")
                return url
        
        return None
    
    def extract_github(self, text: str) -> Optional[str]:
        """
        Extract GitHub profile URL
        
        Args:
            text: Resume text
            
        Returns:
            GitHub URL if found, None otherwise
        """
        for pattern in self.github_patterns:
            match = pattern.search(text)
            if match:
                url = match.group(0)
                # Ensure it starts with https://
                if not url.startswith('http'):
                    url = 'https://' + url
                # Avoid common false positives (like github.com/repos, github.com/organizations)
                if any(word in url.lower() for word in ['/repos', '/organizations', '/projects']):
                    continue
                logger.debug(f"Found GitHub: {url}")
                return url
        
        return None
    
    def extract_website(self, text: str) -> Optional[str]:
        """
        Extract personal website URL (excluding LinkedIn, GitHub)
        
        Args:
            text: Resume text
            
        Returns:
            Website URL if found, None otherwise
        """
        matches = self.website_pattern.findall(text)
        for url in matches:
            url_lower = url.lower()
            # Skip LinkedIn, GitHub, common job sites, email providers
            skip_domains = [
                'linkedin.com', 'github.com', 'indeed.com', 'monster.com',
                'glassdoor.com', 'gmail.com', 'yahoo.com', 'outlook.com',
                'hotmail.com', 'example.com', 'test.com'
            ]
            if not any(domain in url_lower for domain in skip_domains):
                logger.debug(f"Found website: {url}")
                return url
        
        return None
    
    def extract_location(self, text: str) -> Optional[str]:
        """
        Extract location (city, state/country) from text
        
        Args:
            text: Resume text
            
        Returns:
            Location string if found, None otherwise
        """
        # Try to find location in first 500 characters (usually in header)
        header_text = text[:500]
        
        for pattern in self.location_patterns:
            match = pattern.search(header_text)
            if match:
                location = match.group(0)
                logger.debug(f"Found location: {location}")
                return location
        
        # If not found in header, try common location keywords
        location_keywords = [
            r'Location:\s*(.+?)(?:\n|$)',
            r'Address:\s*(.+?)(?:\n|$)',
            r'Based in:\s*(.+?)(?:\n|$)',
        ]
        
        for keyword_pattern in location_keywords:
            match = re.search(keyword_pattern, header_text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                logger.debug(f"Found location via keyword: {location}")
                return location
        
        return None
    
    def extract_contact_info(self, text: str) -> ContactInfo:
        """
        Extract all contact information from resume text
        
        Args:
            text: Resume text
            
        Returns:
            ContactInfo object with all extracted information
        """
        logger.info("Extracting contact information from resume")
        
        emails = self.extract_emails(text)
        phones = self.extract_phones(text)
        linkedin = self.extract_linkedin(text)
        github = self.extract_github(text)
        website = self.extract_website(text)
        location = self.extract_location(text)
        
        contact_info = ContactInfo(
            emails=emails,
            phones=phones,
            linkedin=linkedin,
            github=github,
            website=website,
            location=location
        )
        
        logger.info(f"Extracted contact info: {len(emails)} email(s), {len(phones)} phone(s)")
        
        return contact_info


# Convenience function for quick extraction
def extract_contact_info(text: str) -> ContactInfo:
    """
    Quick function to extract contact information from text
    
    Args:
        text: Resume text
        
    Returns:
        ContactInfo object
    """
    extractor = ContactExtractor()
    return extractor.extract_contact_info(text)
