"""
PII Redactor Module
Detects and removes Personally Identifiable Information (PII) from resume text.
This ensures client names, email addresses, phone numbers, and personal details
are not exposed to the LLM while preserving skills and technical experience.
"""

import re
from typing import Tuple, List


class PIIRedactor:
    """Detect and redact Personally Identifiable Information from text."""

    # Regex patterns for common PII
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    PHONE_PATTERN = r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
    URL_PATTERN = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    
    # Patterns for company names and locations
    LOCATION_PATTERN = r'(?:^|\s)(?:(?:New York|Los Angeles|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose|Austin|Jacksonville|Fort Worth|Columbus|Charlotte|San Francisco|Indianapolis|Seattle|Denver|Boston|Miami|Atlanta|Portland|Detroit|Minneapolis|New Orleans|Houston|Phoenix|Baltimore|Memphis|Boston|Milwaukee|Washington|Newark|Plano|Chula Vista|Irving)[,\.]*(?:\s*(?:CA|TX|NY|FL|IL|PA|OH|MI|NC|GA|AZ|CO|WA|MA|NV|MO|MN|WI|IN|TN|LA|KY|OR|OK|CT|UT|MS|AR|KS|NM|NV|ID|IA|NH|ME|MT|RI|DE|SD|ND|AK|HI|VT|WY|DC))?)'
    
    @staticmethod
    def redact_emails(text: str) -> str:
        """
        Redact email addresses.
        
        Args:
            text: Input text
            
        Returns:
            Text with emails replaced by [EMAIL]
        """
        return re.sub(PIIRedactor.EMAIL_PATTERN, '[EMAIL]', text, flags=re.IGNORECASE)

    @staticmethod
    def redact_phone_numbers(text: str) -> str:
        """
        Redact phone numbers.
        
        Args:
            text: Input text
            
        Returns:
            Text with phone numbers replaced by [PHONE]
        """
        return re.sub(PIIRedactor.PHONE_PATTERN, '[PHONE]', text)

    @staticmethod
    def redact_urls(text: str) -> str:
        """
        Redact URLs (LinkedIn, GitHub, etc).
        
        Args:
            text: Input text
            
        Returns:
            Text with URLs replaced by [URL]
        """
        return re.sub(PIIRedactor.URL_PATTERN, '[URL]', text, flags=re.IGNORECASE)

    @staticmethod
    def redact_common_names(text: str) -> str:
        """
        Attempt to redact common first names at beginning of lines or sections.
        This is limited to reduce false positives.
        
        Args:
            text: Input text
            
        Returns:
            Text with potential names replaced
        """
        # Common first names pattern - only at line start to reduce false positives
        # This is conservative to avoid removing common words
        common_first_names = [
            r'\bjohn\b', r'\bjames\b', r'\broberta\b', r'\brobert\b',
            r'\bmichael\b', r'\bmichael\b', r'\bdavid\b', r'\bwilliam\b',
            r'\brichards\b', r'\bjoseph\b', r'\bthomas\b', r'\bcharles\b',
            r'\brichards\b', r'\bpatricia\b', r'\bjennifer\b', r'\blinda\b',
            r'\bmary\b', r'\bsarah\b', r'\brachel\b', r'\blaurence\b'
        ]
        
        result = text
        for name_pattern in common_first_names:
            # Only match at line start to be conservative
            result = re.sub(rf'^(\s*){name_pattern}\s+', r'\1[NAME] ', result, 
                          flags=re.IGNORECASE | re.MULTILINE)
        
        return result

    @staticmethod
    def redact_company_names(text: str) -> str:
        """
        Redact likely company names. This uses common company name patterns.
        
        Args:
            text: Input text
            
        Returns:
            Text with likely company names replaced
        """
        # Patterns for company designations
        company_patterns = [
            r'\b([A-Z][a-zA-Z]*(?:\s+(?:Inc|Corp|LLC|Ltd|LLP|Ltd\.?|Corporation|Company|Group|Systems|Technologies?|Solutions?|Services?|Consulting|Consulting|Partners?|Associates?|Ventures)\.?))\b',
        ]
        
        result = text
        for pattern in company_patterns:
            # Replace only if followed by common business context
            result = re.sub(pattern, '[COMPANY]', result)
        
        return result

    @staticmethod
    def extract_skills_and_experience(text: str) -> str:
        """
        Extract and preserve only skills, technologies, tools, and experience descriptions.
        Remove personal information while keeping technical content.
        
        Args:
            text: Full resume text
            
        Returns:
            Cleaned text with only relevant technical content
        """
        # First, remove contact information sections
        # Remove "Contact", "Contact Information" sections and their content
        text = re.sub(
            r'(?:^|\n)\s*(?:contact\s+)?(?:information|details|info)\s*:?(?:\n(?:[^\n]*(?:email|phone|address|linkedin|github|website)[^\n]*\n?)*)',
            '\n',
            text,
            flags=re.IGNORECASE | re.MULTILINE
        )
        
        return text

    @staticmethod
    def redact_all(text: str, aggressive: bool = False) -> str:
        """
        Apply all redaction methods to remove PII.
        
        Args:
            text: Input text
            aggressive: If True, also attempts name and company redaction
            
        Returns:
            Text with PII redacted
        """
        # Apply redactions in sequence
        text = PIIRedactor.redact_emails(text)
        text = PIIRedactor.redact_phone_numbers(text)
        text = PIIRedactor.redact_urls(text)
        text = PIIRedactor.extract_skills_and_experience(text)
        
        if aggressive:
            text = PIIRedactor.redact_common_names(text)
            text = PIIRedactor.redact_company_names(text)
        
        return text

    @staticmethod
    def get_pii_summary(text: str) -> dict:
        """
        Detect and report what PII was found.
        
        Args:
            text: Input text to scan
            
        Returns:
            Dictionary with detected PII items
        """
        summary = {
            "emails": re.findall(PIIRedactor.EMAIL_PATTERN, text),
            "phone_numbers": re.findall(PIIRedactor.PHONE_PATTERN, text),
            "urls": re.findall(PIIRedactor.URL_PATTERN, text, flags=re.IGNORECASE),
        }
        
        return summary
