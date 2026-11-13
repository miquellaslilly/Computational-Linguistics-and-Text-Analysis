import re
from datetime import date


# ============================================================
# 0. CONFIGURATION
# ============================================================

MAX_YEAR = 2050
MIN_YEAR = 1


def year_in_range(year):
    """Check year"""
    return MIN_YEAR <= int(year) <= MAX_YEAR


# ============================================================
# 1. REGULAR EXPRESSION COMPONENTS
# ============================================================

MONTHS = (
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
)

WEEKDAYS = (
    r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|"
    r"Mon|Tue|Tues|Wed|Thu|Thur|Thurs|Fri|Sat|Sun)"
)

MONTH_MAP = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12
}

DAY = r"(?:0?[1-9]|[12][0-9]|3[01])(?:st|nd|rd|th)?"
YEAR = r"[0-9]{4}"

# Used for detecting potentially invalid dates.
# Unlike DAY, this pattern also accepts numbers above 31.
ANY_DAY = r"[0-9]{1,2}(?:st|nd|rd|th)?"

NUMBER = (
    r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
    r"seventeen|eighteen|nineteen|twenty|thirty|forty|"
    r"fifty|sixty|seventy|eighty|ninety|one hundred)"
)


# ============================================================
# 2. DATE PREFIXES
# ============================================================

PREFIX = (
    r"(?:(?:as\s+of|starting\s+from|beginning\s+on|"
    r"from|until|through|since|during|before|after|"
    r"around|about|between|by|on|in|at|to)\s+)?"
)


# ============================================================
# 3. RELATIVE DATES
# ============================================================

RELATIVE_DATE = (
    r"(?:"
    r"the\s+day\s+before\s+yesterday|"
    r"the\s+day\s+after\s+tomorrow|"
    r"day\s+before\s+yesterday|"
    r"day\s+after\s+tomorrow|"
    r"yesterday|tomorrow|today|tonight|"
    r"this\s+(?:morning|afternoon|evening|night)|"
    r"last\s+night|next\s+morning|"
    r"last\s+(?:" + WEEKDAYS + r")|"
    r"next\s+(?:" + WEEKDAYS + r")|"
    r"this\s+(?:" + WEEKDAYS + r")|"
    r"in\s+" + NUMBER + r"\s+(?:days?|weeks?|months?)|"
    + NUMBER + r"\s+(?:days?|weeks?|months?|years?)\s+ago"
    r")"
)


# ============================================================
# 4. CALENDAR DATE FORMATS
# ============================================================

CALENDAR_DATE = (
    r"(?:"
    + MONTHS + r"\s+" + DAY + r"(?:\s*,\s*" + YEAR + r")?"
    + r"|"

    + DAY + r"\s+" + MONTHS + r"(?:\s+" + YEAR + r")?"
    + r"|"

    + MONTHS + r"\s+" + YEAR
    + r"|"

    + YEAR + r"\s+" + MONTHS
    + r"|"

    + MONTHS
    + r")"
)


# Weekday with an optional calendar date
WEEKDAY_DATE = (
    r"(?:" + WEEKDAYS + r")"
    r"(?:\s*,?\s*(?:" + CALENDAR_DATE + r"))?"
)


# ============================================================
# 5. NUMERIC DATE FORMATS
# ============================================================

NUMERIC_DATE = (
    r"(?:"
    # DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
    r"(?:0?[1-9]|[12][0-9]|3[01])[./-]"
    r"(?:0?[1-9]|1[0-2])[./-]"
    + YEAR
    + r"|"

    # YYYY/MM/DD, YYYY-MM-DD, YYYY.MM.DD
    + YEAR + r"[./-](?:0?[1-9]|1[0-2])"
    + r"[./-](?:0?[1-9]|[12][0-9]|3[01])"
    + r")"
)


# ============================================================
# 6. DATE RANGES
# ============================================================

DATE_RANGE = (
    r"(?:"
    # from 2013 to 2020
    + r"(?:from\s+)?" + YEAR + r"\s+(?:to|through|until)\s+" + YEAR
    + r"|"

    # from August 2019 to December 2021
    + r"(?:from\s+)?" + MONTHS + r"\s+" + YEAR
    + r"\s+(?:to|through|until)\s+" + MONTHS + r"\s+" + YEAR
    + r"|"

    # between 2013 and 2020
    + r"between\s+" + YEAR + r"\s+and\s+" + YEAR
    + r")"
)


# ============================================================
# 7. DETECT INVALID FULL DATE EXPRESSIONS
# ============================================================

DATE_LIKE_PATTERNS = [
    re.compile(
        r"(?<!\w)" + MONTHS + r"\s+" + ANY_DAY
        + r"(?:\s*,?\s*" + YEAR + r")?(?!\w)",
        re.IGNORECASE
    ),

    re.compile(
        r"(?<!\w)" + ANY_DAY + r"\s+" + MONTHS
        + r"(?:\s+" + YEAR + r")?(?!\w)",
        re.IGNORECASE
    ),

    re.compile(
        r"(?<![\w-])"
        r"(?:\d{1,4}[./-]\d{1,2}[./-]\d{1,4})"
        r"(?![\w-])"
    )
]


# ============================================================
# 8. CALENDAR VALIDATION
# ============================================================

def is_calendar_valid(value):
    """
    Checks whether a date is calendar-valid AND its year
    is within [MIN_YEAR, MAX_YEAR].
    """

    s = value.strip()

    # Remove date prepositions
    s = re.sub(
        r"^(?:as\s+of|starting\s+from|beginning\s+on|"
        r"from|until|through|since|during|before|after|"
        r"around|about|between|by|on|in|at|to)\s+",
        "",
        s,
        flags=re.IGNORECASE
    ).strip()

    if not s:
        return True

    # --------------------------------------------------------
    # Date ranges
    # --------------------------------------------------------
    if re.search(r"\b(?:to|through|until|and)\b", s, re.I):
        years = re.findall(r"\b\d{4}\b", s)
        return bool(years) and all(year_in_range(y) for y in years)

    # Remove weekday prefix
    s = re.sub(
        r"^(?:" + WEEKDAYS + r")\s*,?\s*",
        "",
        s,
        flags=re.IGNORECASE
    ).strip()

    if not s:
        return True

    # --------------------------------------------------------
    # Numeric dates: DD/MM/YYYY, YYYY/MM/DD, etc.
    # --------------------------------------------------------
    if re.fullmatch(r"\d{1,4}[./-]\d{1,2}[./-]\d{1,4}", s):
        parts = re.split(r"[./-]", s)

        if len(parts[0]) == 4:
            year, month, day = map(int, parts)
        else:
            day, month, year = map(int, parts)

        # Year range check (fixes 02.09.3000)
        if not year_in_range(year):
            return False

        try:
            date(year, month, day)
            return True
        except ValueError:
            return False

    # --------------------------------------------------------
    # Month Day, Year: February 29, 2024
    # --------------------------------------------------------
    match = re.fullmatch(
        r"([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?"
        r"(?:,\s*(\d{4}))?",
        s,
        re.IGNORECASE
    )

    if match:
        month_name, day, year = match.groups()
        month = MONTH_MAP.get(month_name.lower())

        if month is None:
            return False

        if year is not None and not year_in_range(year):
            return False

        try:
            date(int(year or 2000), month, int(day))
            return True
        except ValueError:
            return False

    # --------------------------------------------------------
    # Day Month Year: 29 February 2024
    # --------------------------------------------------------
    match = re.fullmatch(
        r"(\d{1,2})(?:st|nd|rd|th)?\s+"
        r"([A-Za-z]+)(?:\s+(\d{4}))?",
        s,
        re.IGNORECASE
    )

    if match:
        day, month_name, year = match.groups()
        month = MONTH_MAP.get(month_name.lower())

        if month is None:
            return False

        if year is not None and not year_in_range(year):
            return False

        try:
            date(int(year or 2000), month, int(day))
            return True
        except ValueError:
            return False

    # --------------------------------------------------------
    # Month Year: August 2023
    # --------------------------------------------------------
    match = re.fullmatch(r"([A-Za-z]+)\s+(\d{4})", s)

    if match:
        month_name, year = match.groups()
        return month_name.lower() in MONTH_MAP and year_in_range(year)

    # --------------------------------------------------------
    # Year Month: 2023 August
    # --------------------------------------------------------
    match = re.fullmatch(r"(\d{4})\s+([A-Za-z]+)", s)

    if match:
        year, month_name = match.groups()
        return year_in_range(year) and month_name.lower() in MONTH_MAP

    # --------------------------------------------------------
    # Month only
    # --------------------------------------------------------
    if s.lower() in MONTH_MAP:
        return True

    # --------------------------------------------------------
    # Year only
    # --------------------------------------------------------
    if re.fullmatch(r"\d{4}", s):
        return year_in_range(s)

    return True


# ============================================================
# 9. FIND INVALID DATE RANGES IN THE TEXT
# ============================================================

def find_invalid_spans(text):
    """
    Finds complete date-like expressions that are not
    calendar-valid. Their parts must not be extracted
    as separate dates.
    """

    invalid_spans = []

    for pattern in DATE_LIKE_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group()

            if not is_calendar_valid(value):
                invalid_spans.append(
                    (match.start(), match.end())
                )

    return invalid_spans


def overlaps_invalid_span(start, end, invalid_spans):
    """Checks whether a candidate overlaps an invalid date."""

    for invalid_start, invalid_end in invalid_spans:
        if start < invalid_end and end > invalid_start:
            return True

    return False


# ============================================================
# 10. MAIN DATE SEARCH FUNCTION
# ============================================================

DATE_PATTERNS = [
    # Date ranges
    re.compile(
        r"(?<!\w)" + DATE_RANGE + r"(?!\w)",
        re.IGNORECASE
    ),

    # Relative dates
    re.compile(
        r"(?<!\w)" + PREFIX + RELATIVE_DATE + r"(?!\w)",
        re.IGNORECASE
    ),

    # Weekday and calendar date
    re.compile(
        r"(?<!\w)" + PREFIX + WEEKDAY_DATE + r"(?!\w)",
        re.IGNORECASE
    ),

    # Numeric dates
    re.compile(
        r"(?<![\w-])" + PREFIX + NUMERIC_DATE + r"(?![\w-])",
        re.IGNORECASE
    ),

    # Calendar dates
    re.compile(
        r"(?<!\w)" + PREFIX + CALENDAR_DATE + r"(?!\w)",
        re.IGNORECASE
    ),

    # Year only
    re.compile(
        r"(?<![\w-])" + PREFIX + YEAR + r"(?![\w-])",
        re.IGNORECASE
    )
]


def find_dates(text):
    """
    Finds unique, non-overlapping, calendar-valid
    date mentions in English text.
    """

    matches = []

    # First, identify invalid complete dates
    invalid_spans = find_invalid_spans(text)

    # Search using all regular expressions
    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group().strip()

            # Do not extract parts of invalid dates
            if overlaps_invalid_span(
                match.start(),
                match.end(),
                invalid_spans
            ):
                continue

            # Check calendar correctness + year range
            if not is_calendar_valid(value):
                continue

            matches.append({
                "start": match.start(),
                "end": match.end(),
                "value": value
            })

    # Sort by position, preferring longer matches
    matches.sort(
        key=lambda item: (
            item["start"],
            -(item["end"] - item["start"])
        )
    )

    result = []
    last_end = -1

    # Remove overlapping matches
    for match in matches:
        if match["start"] < last_end:
            continue

        result.append(match["value"])
        last_end = match["end"]

    return result


# ============================================================
# 11. MAIN PROGRAM
# ============================================================

def main():
    print("DATE MENTION DETECTOR")
    print("=" * 60)

    text = """
    The Nobel Prize was awarded in 2017.
    The conference took place on Thursday, June 14, 2021.
    From August 2019 to December 2021, the project was active.
    The results were published on 7 August.
    Five weeks ago, a new record was established.
    Yesterday, we discussed the project.
    Tomorrow, the team will start working.
    The meeting is scheduled for March 2024.
    The event happened on Monday.
    The previous season was successful.
    The system was developed in 12 years.
    The Great Marathon Monster was the ruler from 2013 to 2020.
    CHM-2077 was mentioned in the report.

    Valid dates:
    February 28, 2024.
    February 29, 2024.
    January 31, 2023.
    March 15, 2025.
    2024-02-29.
    14 June 2021.
    August 2023.

    Invalid dates:
    February 29, 2023.
    February 31, 2024.
    47 March 2024.
    32 January 2024.
    2024-13-01.
    2023-02-29.
    0000.
    -2024.

    I went for a walk 02.09.3000
    Tomorrow, 05.11.2026 we'll go for the lessons.
    """

    print("\nINPUT TEXT:")
    print(text)

    dates = find_dates(text)

    print("\nFOUND DATE MENTIONS:")
    print("-" * 60)

    if dates:
        for number, found_date in enumerate(dates, start=1):
            print(f"{number}. {found_date}")
    else:
        print("No dates found.")

    print("-" * 60)
    print(f"Total date mentions found: {len(dates)}")


if __name__ == "__main__":
    main()