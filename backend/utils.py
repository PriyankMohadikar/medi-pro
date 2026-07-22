"""
Utility functions for data cleaning and standardization.

Provides deterministic transformations for:
  - City name normalization
  - Test name standardization
  - Provider name normalization
  - Provider type classification
  - Generic value cleaning
  - Logging setup
"""

import logging
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# City Standardization
# ---------------------------------------------------------------------------

CITY_ALIASES: dict[str, str] = {
    "ahmedbad": "Ahmedabad",
    "ahmdabad": "Ahmedabad",
    "ahd": "Ahmedabad",
    "amd": "Ahmedabad",
    "gandhinagar": "Gandhinagar",
    "gnr": "Gandhinagar",
    "rajkot": "Rajkot",
    "surat": "Surat",
    "vadodara": "Vadodara",
    "baroda": "Vadodara",
}


def standardize_city(city: str | None) -> str | None:
    """
    Normalize city names to a canonical form.

    Handles common misspellings and abbreviations.
    Returns None if input is None or empty.
    """
    if not city or not str(city).strip():
        return None

    cleaned = str(city).strip()
    lookup = cleaned.lower()

    if lookup in CITY_ALIASES:
        return CITY_ALIASES[lookup]

    # Title-case if not in alias map (passthrough for already correct values)
    return cleaned.title()


# ---------------------------------------------------------------------------
# Test Name Standardization
# ---------------------------------------------------------------------------

TEST_NAME_ALIASES: dict[str, str] = {
    # CBC variants
    "cbc test": "CBC",
    "cbc": "CBC",
    "complete blood count": "CBC",
    "hemogram": "CBC",
    "complete blood count (cbc)": "CBC",
    # HbA1c variants
    "hba1c test": "HbA1c",
    "hba1c": "HbA1c",
    "glycated hemoglobin": "HbA1c",
    # Vitamin B12 variants
    "vitamin b12 test": "Vitamin B12",
    "vitamin b12": "Vitamin B12",
    "vit b12": "Vitamin B12",
    # Vitamin D variants
    "vitamin d test": "Vitamin D",
    "vitamin d": "Vitamin D",
    "vit d": "Vitamin D",
    "vitamin d (25-oh)": "Vitamin D",
    # FBS variants
    "fbs (fbg)": "FBS",
    "fbs": "FBS",
    "fasting blood sugar": "FBS",
    "fasting blood glucose": "FBS",
    "fbg": "FBS",
    # Lipid Profile variants
    "lipid profile": "Lipid Profile",
    "lipid panel": "Lipid Profile",
    # TSH variants
    "tsh": "TSH",
    "tsh test": "TSH",
    "thyroid stimulating hormone": "TSH",
    # RFT/KFT variants
    "rft (kft)": "RFT / KFT",
    "rft / kft": "RFT / KFT",
    "rft/kft": "RFT / KFT",
    "rft": "RFT / KFT",
    "kft": "RFT / KFT",
    "renal function test": "RFT / KFT",
    "kidney function test": "RFT / KFT",
    # LFT variants
    "lft": "LFT",
    "lft test": "LFT",
    "liver function test": "LFT",
    # Urine Routine variants
    "urine routine": "Urine Routine",
    "urine r/m": "Urine Routine",
    "urine analysis": "Urine Routine",
    # ESR variants
    "esr": "ESR",
    "esr test": "ESR",
    "erythrocyte sedimentation rate": "ESR",
    # Common package tests
    "ppbs / rbs": "PPBS / RBS",
    "ppbs": "PPBS / RBS",
    "rbs": "PPBS / RBS",
    "chest x-ray": "Chest X-Ray",
    "chest xray": "Chest X-Ray",
    "x-ray chest": "Chest X-Ray",
    "ecg": "ECG",
    "electrocardiogram": "ECG",
    "blood group": "Blood Group",
    "bone profile": "Bone Profile",
    "ra factor": "RA Factor",
    "iron studies": "Iron Studies",
    "iron profile": "Iron Studies",
    "calcium": "Calcium",
    "phosphorus": "Phosphorus",
    "uric acid": "Uric Acid",
}


def standardize_test_name(name: str | None) -> str | None:
    """
    Normalize test names to canonical forms.

    Strips whitespace and looks up aliases case-insensitively.
    Returns the cleaned original if no alias match is found.
    """
    if not name or not str(name).strip():
        return None

    cleaned = str(name).strip()
    lookup = cleaned.lower()

    if lookup in TEST_NAME_ALIASES:
        return TEST_NAME_ALIASES[lookup]

    # Return cleaned version if no alias found
    return cleaned


# ---------------------------------------------------------------------------
# Provider Name Standardization
# ---------------------------------------------------------------------------

PROVIDER_NAME_ALIASES: dict[str, str] = {
    # Cross-sheet inconsistencies
    "dr. lalpath labs": "Dr. LalPathLabs",
    "dr. lalpaths": "Dr. LalPathLabs",
    "dr. lalpathlabs": "Dr. LalPathLabs",
    "dr lalpathlab": "Dr. LalPathLabs",
    "pharmeasy": "PharmaEasy",
    "pharmaeasy": "PharmaEasy",
    "greencross": "Green Cross",
    "green cross": "Green Cross",
    "life line laboratory": "Lifeline Laboratory",
    "lifeline laboratory": "Lifeline Laboratory",
    "sterling aqcuris": "Sterling Acquris",
    "sterling acquris": "Sterling Acquris",
    "endocrine and allergy lab": "Endocrine & Allergy Lab",
    "endocrine & allergy lab": "Endocrine & Allergy Lab",
    "red cross society": "Recross",
    "recross": "Recross",
    "nidan pathlab": "Nidan Pathlab",
    "vahcare": "Vahcare",
    "aarthi scan & labs": "Aarthi Scan & Labs",
    "aarthi scan and labs": "Aarthi Scan & Labs",
    "nobelmicropath": "NobelMicropath",
    "usmanpura": "Usmanpura",
    "tata1mg": "Tata1mg",
    "medibuddy": "MediBuddy",
    "krsnaa diagnostics": "Krsnaa Diagnostics",
    "qline diagnostics": "Qline Diagnostics",
    "apollo diagnostics": "Apollo Diagnostics",
    "healthians": "Healthians",
    "maxlab": "MaxLab",
    "redcliffe labs": "Redcliffe Labs",
    "metropolis healthcare": "Metropolis Healthcare",
    "neuberg supratech labs": "Neuberg Supratech Labs",
    "srl/agilus diagnostics": "SRL/Agilus Diagnostics",
    "thyrocare": "Thyrocare",
    "total health solution": "Total Health Solution",
    "unipath": "Unipath",
    "galaxy diagnostics": "Galaxy Diagnostics",
    "shraddha pathology laboratory": "Shraddha Pathology Laboratory",
    "aacharyatulsi diagnostic center": "AacharyaTulsi Diagnostic Center",
}


def standardize_provider_name(name: str | None) -> str | None:
    """
    Normalize provider names to canonical forms.

    Collapses multiple spaces, strips whitespace,
    and applies alias mapping case-insensitively.
    """
    if not name or not str(name).strip():
        return None

    # Collapse multiple spaces and strip
    cleaned = re.sub(r"\s+", " ", str(name).strip())
    lookup = cleaned.lower()

    if lookup in PROVIDER_NAME_ALIASES:
        return PROVIDER_NAME_ALIASES[lookup]

    return cleaned


# ---------------------------------------------------------------------------
# Provider Type Classification
# ---------------------------------------------------------------------------

PROVIDER_TYPE_MAP: dict[str, str] = {
    "healthcare centre": "Healthcare Centre",
    "healthcare  centre": "Healthcare Centre",  # double space variant
    "healthcare center": "Healthcare Centre",
    "diagnostic centre": "Diagnostic Centre",
    "diagnostic center": "Diagnostic Centre",
    "laboratory": "Laboratory",
    "labs": "Laboratory",
    "lab": "Laboratory",
}

# Providers that appear as type values in the Excel data but are actually names
KNOWN_PROVIDER_TYPES: dict[str, str] = {
    "thyrocare": "Diagnostic Centre",
    "srl/agilus diagnostics": "Diagnostic Centre",
    "metropolis healthcare": "Diagnostic Centre",
    "vahcare": "Diagnostic Centre",
    "aacharyatulsi diagnostic center": "Diagnostic Centre",
    "nobelmicropath": "Laboratory",
    "lifeline laboratory": "Laboratory",
}


def classify_provider_type(raw_type: str | None) -> str | None:
    """
    Classify a raw provider type string into a standard category.

    Handles the Excel data quirk where some rows contain provider names
    instead of actual type classifications.
    """
    if not raw_type or not str(raw_type).strip():
        return None

    cleaned = str(raw_type).strip()
    lookup = cleaned.lower()

    # Check standard type map first
    if lookup in PROVIDER_TYPE_MAP:
        return PROVIDER_TYPE_MAP[lookup]

    # Check if it's a known provider name used as a type
    if lookup in KNOWN_PROVIDER_TYPES:
        return KNOWN_PROVIDER_TYPES[lookup]

    return cleaned


# ---------------------------------------------------------------------------
# Generic Value Cleaning
# ---------------------------------------------------------------------------


def clean_value(value) -> str | None:
    """
    Clean a cell value from Excel.

    - Strips whitespace from strings
    - Converts 'Not Available', 'NA', 'N/A', 'None' to None
    - Converts empty/whitespace-only strings to None
    - Passes through numeric values unchanged
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return value

    cleaned = str(value).strip()

    if not cleaned:
        return None

    if cleaned.lower() in ("not available", "na", "n/a", "none", "-", "--"):
        return None

    return cleaned


def clean_price(value) -> float | None:
    """
    Clean a price value from Excel.

    Converts to float, handles 'Not Available' and other non-numeric values.
    Returns None for invalid prices.
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value) if value == value else None  # handles NaN

    cleaned = str(value).strip()

    if not cleaned or cleaned.lower() in ("not available", "na", "n/a", "none", "-", "--"):
        return None

    try:
        # Remove currency symbols and commas
        cleaned = cleaned.replace("₹", "").replace(",", "").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------


def setup_logging(log_dir: Path | None = None) -> logging.Logger:
    """
    Configure logging to both file and console.

    Creates the log directory if it doesn't exist.
    Returns the root logger for the application.
    """
    if log_dir is None:
        log_dir = Path(__file__).resolve().parent / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "etl.log"

    # Create formatters
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # File handler — captures everything
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console handler — INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates on re-runs
    root_logger.handlers.clear()

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger
