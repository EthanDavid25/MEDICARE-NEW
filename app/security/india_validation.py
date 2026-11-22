"""
MEDICARE India-Specific Validation & Localization Module.
Validates Indian 10-digit mobile phone numbers (+91), normalizes formats,
and provides Indian standard date representations (DD/MM/YYYY).
"""
import re
from datetime import datetime
from typing import Tuple, Optional


def validate_indian_mobile(phone_str: Optional[str], allow_empty: bool = False) -> Tuple[bool, str, str]:
    """
    Validates and normalizes an Indian mobile phone number.
    
    Returns:
        (is_valid: bool, normalized_number: str, message: str)
    """
    if not phone_str or not phone_str.strip():
        if allow_empty:
            return True, "", ""
        return False, "", "Enter a valid 10-digit Indian mobile number."

    raw = phone_str.strip()

    # Detect foreign country code prefixes
    if raw.startswith("+"):
        if not raw.startswith("+91"):
            return False, "", "MEDICARE currently supports Indian mobile numbers only (+91)."
        raw_digits = re.sub(r"[^\d]", "", raw[3:])
    else:
        # Strip common punctuation
        clean = re.sub(r"[^\d+]", "", raw)
        if clean.startswith("+"):
            if not clean.startswith("+91"):
                return False, "", "MEDICARE currently supports Indian mobile numbers only (+91)."
            raw_digits = clean[3:]
        elif clean.startswith("91") and len(clean) == 12:
            raw_digits = clean[2:]
        elif clean.startswith("0") and len(clean) == 11:
            raw_digits = clean[1:]
        else:
            raw_digits = clean

    # Strip any remaining non-digit characters
    digits = re.sub(r"\D", "", raw_digits)

    if len(digits) == 0:
        return False, "", "Enter a valid 10-digit Indian mobile number."

    if len(digits) != 10:
        return False, "", "Please enter a valid 10-digit Indian mobile number."

    first_digit = digits[0]
    if first_digit not in ("6", "7", "8", "9"):
        return False, "", "Indian mobile numbers must begin with 6, 7, 8, or 9."

    # Normalised format: +91-XXXXX-XXXXX
    normalized = f"+91-{digits[:5]}-{digits[5:]}"
    return True, normalized, "Valid Indian mobile number."


def validate_indian_date(date_str: Optional[str], allow_empty: bool = True) -> Tuple[bool, str, str]:
    """
    Validates date string and normalizes to DD/MM/YYYY format.
    Accepts DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD.
    
    Returns:
        (is_valid: bool, normalized_date: str, message: str)
    """
    if not date_str or not date_str.strip():
        if allow_empty:
            return True, "", ""
        return False, "", "Date of birth is required (DD/MM/YYYY)."

    s = date_str.strip()
    dt = None

    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"):
        try:
            dt = datetime.strptime(s, fmt)
            break
        except ValueError:
            continue

    if not dt:
        return False, "", "Please enter a valid date in DD/MM/YYYY format."

    # Sanity checks (cannot be in the future, cannot be older than 130 years)
    now = datetime.now()
    if dt > now:
        return False, "", "Date of birth cannot be in the future."
    if (now.year - dt.year) > 130:
        return False, "", "Please enter a realistic date of birth."

    normalized = dt.strftime("%d/%m/%Y")
    return True, normalized, "Valid date."


def format_indian_datetime(dt: Optional[datetime | str]) -> str:
    """Formats datetime object or ISO string to Indian standard DD/MM/YYYY hh:mm A."""
    if not dt:
        return "N/A"
    if isinstance(dt, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                dt_obj = datetime.strptime(dt.split(".")[0], fmt)
                return dt_obj.strftime("%d/%m/%Y %I:%M %p")
            except ValueError:
                continue
        return dt
    elif isinstance(dt, datetime):
        return dt.strftime("%d/%m/%Y %I:%M %p")
    return str(dt)
