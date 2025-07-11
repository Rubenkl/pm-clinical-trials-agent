"""Calculation helper function tools for clinical trial agents.

These function tools provide concrete calculations and data transformations
that help agents process clinical data without making medical judgments.
Medical reasoning and clinical assessments are handled by the agents' AI/LLM intelligence.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from agents import function_tool


@function_tool
def convert_medical_units(
    value: str, from_unit: str, to_unit: str, parameter: str
) -> str:
    """Convert between different medical units for laboratory values and measurements.

    This function handles unit conversions commonly needed in clinical trials,
    helping agents standardize data across different laboratory systems and regions.
    It does NOT make medical judgments about the values - only performs mathematical conversions.

    Supported Conversions:

    HEMATOLOGY:
    - Hemoglobin: g/dL ↔ g/L (factor: 10)
    - Hematocrit: % ↔ fraction (factor: 0.01)
    - Platelets: K/µL ↔ 10^9/L (factor: 1)
    - WBC: K/µL ↔ 10^9/L (factor: 1)

    CHEMISTRY:
    - Glucose: mg/dL ↔ mmol/L (factor: 0.0555)
    - Creatinine: mg/dL ↔ µmol/L (factor: 88.4)
    - Bilirubin: mg/dL ↔ µmol/L (factor: 17.1)
    - Cholesterol: mg/dL ↔ mmol/L (factor: 0.0259)
    - Triglycerides: mg/dL ↔ mmol/L (factor: 0.0113)

    ELECTROLYTES:
    - Sodium: mEq/L ↔ mmol/L (factor: 1)
    - Potassium: mEq/L ↔ mmol/L (factor: 1)
    - Calcium: mg/dL ↔ mmol/L (factor: 0.25)
    - Magnesium: mg/dL ↔ mmol/L (factor: 0.411)

    VITAL SIGNS:
    - Temperature: °C ↔ °F (formula: °F = °C × 9/5 + 32)
    - Weight: kg ↔ lbs (factor: 2.20462)
    - Height: cm ↔ inches (factor: 0.393701)

    Args:
        value: Numeric value to convert (as string)
        from_unit: Current unit of the value
        to_unit: Target unit for conversion
        parameter: Clinical parameter name (e.g., "hemoglobin", "glucose")

    Returns:
        JSON string with:
        - converted_value: The converted numeric value
        - from_unit: Original unit
        - to_unit: Target unit
        - parameter: Clinical parameter
        - conversion_factor: Factor or formula used
        - success: Boolean indicating if conversion was successful
        - error: Error message if conversion failed
    """

    try:
        numeric_value = float(value)
    except ValueError:
        return json.dumps(
            {
                "success": False,
                "error": f"Invalid numeric value: {value}",
                "from_unit": from_unit,
                "to_unit": to_unit,
                "parameter": parameter,
            }
        )

    # Define conversion factors
    conversions = {
        "hemoglobin": {
            ("g/dL", "g/L"): lambda x: x * 10,
            ("g/L", "g/dL"): lambda x: x / 10,
        },
        "glucose": {
            ("mg/dL", "mmol/L"): lambda x: x * 0.0555,
            ("mmol/L", "mg/dL"): lambda x: x / 0.0555,
        },
        "creatinine": {
            ("mg/dL", "µmol/L"): lambda x: x * 88.4,
            ("µmol/L", "mg/dL"): lambda x: x / 88.4,
            ("mg/dL", "umol/L"): lambda x: x * 88.4,  # Alternative spelling
            ("umol/L", "mg/dL"): lambda x: x / 88.4,
        },
        "temperature": {
            ("C", "F"): lambda x: (x * 9 / 5) + 32,
            ("F", "C"): lambda x: (x - 32) * 5 / 9,
            ("celsius", "fahrenheit"): lambda x: (x * 9 / 5) + 32,
            ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
        },
        "weight": {
            ("kg", "lbs"): lambda x: x * 2.20462,
            ("lbs", "kg"): lambda x: x / 2.20462,
            ("kg", "pounds"): lambda x: x * 2.20462,
            ("pounds", "kg"): lambda x: x / 2.20462,
        },
        "height": {
            ("cm", "inches"): lambda x: x * 0.393701,
            ("inches", "cm"): lambda x: x / 0.393701,
            ("cm", "in"): lambda x: x * 0.393701,
            ("in", "cm"): lambda x: x / 0.393701,
        },
    }

    # Try to find conversion
    param_lower = parameter.lower()
    for param_key, param_conversions in conversions.items():
        if param_key in param_lower:
            conversion_key = (from_unit, to_unit)
            if conversion_key in param_conversions:
                converted_value = param_conversions[conversion_key](numeric_value)
                return json.dumps(
                    {
                        "success": True,
                        "converted_value": round(converted_value, 4),
                        "from_unit": from_unit,
                        "to_unit": to_unit,
                        "parameter": parameter,
                        "conversion_factor": f"{from_unit} to {to_unit}",
                    }
                )

    return json.dumps(
        {
            "success": False,
            "error": f"Conversion not available for {parameter} from {from_unit} to {to_unit}",
            "from_unit": from_unit,
            "to_unit": to_unit,
            "parameter": parameter,
        }
    )


@function_tool
def calculate_age_at_visit(birth_date: str, visit_date: str) -> str:
    """Calculate patient age at a specific visit date.

    This function calculates the exact age in years, months, and days,
    which is crucial for pediatric studies and age-specific normal ranges.
    It handles various date formats and provides precise age calculations.

    Date Format Support:
    - ISO format: YYYY-MM-DD
    - US format: MM/DD/YYYY
    - European format: DD/MM/YYYY (with disambiguation)
    - Text format: DD-MMM-YYYY (e.g., 15-JAN-2023)

    Age Calculation Details:
    - Years: Complete years between dates
    - Months: Additional complete months
    - Days: Remaining days
    - Total days: Exact number of days between dates
    - Decimal years: Precise age as decimal (e.g., 45.67 years)

    Special Considerations:
    - Leap years handled correctly
    - Future dates return negative ages (useful for pregnancy/prenatal)
    - Same date returns age 0
    - Invalid dates return detailed error messages

    Args:
        birth_date: Date of birth as string
        visit_date: Visit date as string

    Returns:
        JSON string with:
        - years: Complete years
        - months: Additional months
        - days: Additional days
        - total_days: Total number of days
        - decimal_years: Age as decimal years
        - age_group: Pediatric/Adult/Geriatric classification
        - success: Boolean indicating if calculation was successful
        - error: Error message if calculation failed
    """

    try:
        # Try to parse dates in various formats
        date_formats = [
            "%Y-%m-%d",  # ISO format
            "%m/%d/%Y",  # US format
            "%d/%m/%Y",  # European format
            "%d-%b-%Y",  # Text month format
            "%d-%B-%Y",  # Full month name
        ]

        birth_dt = None
        visit_dt = None

        for fmt in date_formats:
            if birth_dt is None:
                try:
                    birth_dt = datetime.strptime(birth_date, fmt)
                except ValueError:
                    continue
            if visit_dt is None:
                try:
                    visit_dt = datetime.strptime(visit_date, fmt)
                except ValueError:
                    continue

        if birth_dt is None or visit_dt is None:
            return json.dumps(
                {
                    "success": False,
                    "error": "Unable to parse dates. Supported formats: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, DD-MMM-YYYY",
                    "birth_date": birth_date,
                    "visit_date": visit_date,
                }
            )

        # Calculate age
        years = visit_dt.year - birth_dt.year
        months = visit_dt.month - birth_dt.month
        days = visit_dt.day - birth_dt.day

        # Adjust for negative months/days
        if days < 0:
            months -= 1
            # Get days in previous month
            prev_month = visit_dt.replace(day=1) - timedelta(days=1)
            days += prev_month.day

        if months < 0:
            years -= 1
            months += 12

        # Calculate total days and decimal years
        total_days = (visit_dt - birth_dt).days
        decimal_years = total_days / 365.25

        # Determine age group
        if decimal_years < 0:
            age_group = "prenatal"
        elif decimal_years < 2:
            age_group = "infant"
        elif decimal_years < 12:
            age_group = "pediatric"
        elif decimal_years < 18:
            age_group = "adolescent"
        elif decimal_years < 65:
            age_group = "adult"
        else:
            age_group = "geriatric"

        return json.dumps(
            {
                "success": True,
                "years": years,
                "months": months,
                "days": days,
                "total_days": total_days,
                "decimal_years": round(decimal_years, 2),
                "age_group": age_group,
                "birth_date": birth_dt.strftime("%Y-%m-%d"),
                "visit_date": visit_dt.strftime("%Y-%m-%d"),
            }
        )

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": f"Age calculation failed: {str(e)}",
                "birth_date": birth_date,
                "visit_date": visit_date,
            }
        )


@function_tool
def check_visit_window_compliance(
    target_date: str, actual_date: str, window_before_days: str, window_after_days: str
) -> str:
    """Check if an actual visit date falls within the allowed protocol window.

    This function verifies protocol compliance for visit scheduling,
    calculating whether visits occurred within acceptable time windows.
    It does NOT make judgments about the clinical impact - only mathematical calculations.

    Window Calculation:
    - Target date: The protocol-specified ideal visit date
    - Window before: Allowed days before target date (e.g., -3 days)
    - Window after: Allowed days after target date (e.g., +3 days)
    - Actual date: When the visit actually occurred

    Compliance Status:
    - COMPLIANT: Visit within allowed window
    - EARLY: Visit before allowed window
    - LATE: Visit after allowed window
    - SAME_DAY: Visit on target date

    Additional Calculations:
    - Days from target: Exact deviation from target date
    - Days out of window: How far outside window (if non-compliant)
    - Percent deviation: Deviation as percentage of window size
    - Business days: Calculation excluding weekends

    Args:
        target_date: Protocol-specified target date (string)
        actual_date: Actual visit date (string)
        window_before_days: Days allowed before target (string, positive number)
        window_after_days: Days allowed after target (string, positive number)

    Returns:
        JSON string with:
        - in_window: Boolean indicating compliance
        - compliance_status: COMPLIANT/EARLY/LATE/SAME_DAY
        - days_from_target: Signed integer (negative = early, positive = late)
        - days_out_of_window: Days outside window (0 if compliant)
        - percent_deviation: Deviation as percentage
        - window_start: Earliest allowed date
        - window_end: Latest allowed date
        - business_days_deviation: Deviation in business days only
        - success: Boolean indicating if calculation was successful
        - error: Error message if calculation failed
    """

    try:
        # Parse dates
        date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%d-%b-%Y"]

        target_dt = None
        actual_dt = None

        for fmt in date_formats:
            if target_dt is None:
                try:
                    target_dt = datetime.strptime(target_date, fmt)
                except ValueError:
                    continue
            if actual_dt is None:
                try:
                    actual_dt = datetime.strptime(actual_date, fmt)
                except ValueError:
                    continue

        if target_dt is None or actual_dt is None:
            return json.dumps(
                {
                    "success": False,
                    "error": "Unable to parse dates",
                    "target_date": target_date,
                    "actual_date": actual_date,
                }
            )

        # Parse window days
        window_before = abs(int(window_before_days))
        window_after = abs(int(window_after_days))

        # Calculate window dates
        window_start = target_dt - timedelta(days=window_before)
        window_end = target_dt + timedelta(days=window_after)

        # Calculate deviation
        days_from_target = (actual_dt - target_dt).days

        # Determine compliance
        if actual_dt == target_dt:
            compliance_status = "SAME_DAY"
            in_window = True
            days_out_of_window = 0
        elif window_start <= actual_dt <= window_end:
            compliance_status = "COMPLIANT"
            in_window = True
            days_out_of_window = 0
        elif actual_dt < window_start:
            compliance_status = "EARLY"
            in_window = False
            days_out_of_window = (window_start - actual_dt).days
        else:
            compliance_status = "LATE"
            in_window = False
            days_out_of_window = (actual_dt - window_end).days

        # Calculate percent deviation
        total_window = window_before + window_after
        if total_window > 0:
            percent_deviation = abs(days_from_target) / total_window * 100
        else:
            percent_deviation = 0 if days_from_target == 0 else 100

        # Calculate business days deviation
        business_days = 0
        current_date = min(actual_dt, target_dt)
        end_date = max(actual_dt, target_dt)
        while current_date < end_date:
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                business_days += 1
            current_date += timedelta(days=1)

        if actual_dt < target_dt:
            business_days = -business_days

        return json.dumps(
            {
                "success": True,
                "in_window": in_window,
                "compliance_status": compliance_status,
                "days_from_target": days_from_target,
                "days_out_of_window": days_out_of_window,
                "percent_deviation": round(percent_deviation, 1),
                "window_start": window_start.strftime("%Y-%m-%d"),
                "window_end": window_end.strftime("%Y-%m-%d"),
                "target_date": target_dt.strftime("%Y-%m-%d"),
                "actual_date": actual_dt.strftime("%Y-%m-%d"),
                "business_days_deviation": business_days,
            }
        )

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": f"Window compliance check failed: {str(e)}",
                "target_date": target_date,
                "actual_date": actual_date,
            }
        )


@function_tool
def calculate_change_from_baseline(
    baseline_value: str, current_value: str, parameter_name: str = ""
) -> str:
    """Calculate absolute and percentage change from baseline value.

    This function computes changes in clinical parameters over time,
    helping agents identify trends without making medical judgments.
    Useful for tracking treatment response and safety monitoring.

    Change Calculations:
    - Absolute change: Current - Baseline
    - Percentage change: ((Current - Baseline) / Baseline) × 100
    - Fold change: Current / Baseline
    - Direction: Increased/Decreased/No change

    Special Handling:
    - Zero baseline: Returns absolute change only
    - Negative values: Handles correctly for all calculations
    - Small baselines: Flags when percentage may be misleading
    - Missing values: Returns appropriate error

    Common Clinical Uses:
    - Laboratory values: Track changes in biomarkers
    - Vital signs: Monitor blood pressure, heart rate changes
    - Tumor measurements: Calculate RECIST response
    - Weight/BMI: Track changes over time
    - Scores/scales: Monitor symptom progression

    Args:
        baseline_value: Initial/baseline measurement (string)
        current_value: Current/follow-up measurement (string)
        parameter_name: Optional parameter name for context (string)

    Returns:
        JSON string with:
        - absolute_change: Current - Baseline
        - percentage_change: Percent change from baseline
        - fold_change: Ratio of current to baseline
        - direction: INCREASED/DECREASED/NO_CHANGE
        - baseline_value: Parsed baseline value
        - current_value: Parsed current value
        - parameter_name: Parameter being measured
        - magnitude_warning: Flag if change is unusually large
        - success: Boolean indicating if calculation was successful
        - error: Error message if calculation failed
    """

    try:
        baseline = float(baseline_value)
        current = float(current_value)
    except ValueError:
        return json.dumps(
            {
                "success": False,
                "error": "Invalid numeric values provided",
                "baseline_value": baseline_value,
                "current_value": current_value,
                "parameter_name": parameter_name,
            }
        )

    # Calculate absolute change
    absolute_change = current - baseline

    # Determine direction
    if absolute_change > 0:
        direction = "INCREASED"
    elif absolute_change < 0:
        direction = "DECREASED"
    else:
        direction = "NO_CHANGE"

    # Calculate percentage change
    if baseline == 0:
        if current == 0:
            percentage_change = 0
            fold_change = 1
        else:
            percentage_change = None  # Undefined
            fold_change = None  # Undefined
            return json.dumps(
                {
                    "success": True,
                    "absolute_change": round(absolute_change, 4),
                    "percentage_change": "undefined (baseline is zero)",
                    "fold_change": "undefined (baseline is zero)",
                    "direction": direction,
                    "baseline_value": baseline,
                    "current_value": current,
                    "parameter_name": parameter_name,
                    "magnitude_warning": abs(current) > 0,
                }
            )
    else:
        percentage_change = (absolute_change / abs(baseline)) * 100
        fold_change = current / baseline

    # Check for unusually large changes
    magnitude_warning = (
        abs(percentage_change) > 200 if percentage_change is not None else False
    )

    return json.dumps(
        {
            "success": True,
            "absolute_change": round(absolute_change, 4),
            "percentage_change": (
                round(percentage_change, 2) if percentage_change is not None else None
            ),
            "fold_change": round(fold_change, 3) if fold_change is not None else None,
            "direction": direction,
            "baseline_value": baseline,
            "current_value": current,
            "parameter_name": parameter_name,
            "magnitude_warning": magnitude_warning,
        }
    )


@function_tool
def calculate_body_surface_area(height_cm: str, weight_kg: str) -> str:
    """Calculate body surface area (BSA) using multiple formulas.

    This function calculates BSA which is crucial for dosing calculations
    in oncology and other therapeutic areas. It provides multiple formulas
    to ensure consistency with different institutional preferences.

    Formulas Provided:

    1. DuBois & DuBois (1916) - Most common:
       BSA = 0.007184 × height^0.725 × weight^0.425

    2. Mosteller (1987) - Simplified:
       BSA = √(height × weight / 3600)

    3. Haycock (1978) - Pediatric preference:
       BSA = 0.024265 × height^0.3964 × weight^0.5378

    4. Gehan & George (1970):
       BSA = 0.0235 × height^0.42246 × weight^0.51456

    BSA Applications:
    - Chemotherapy dosing (mg/m²)
    - Cardiac index calculations
    - Renal function assessment
    - Burn area estimation
    - Pediatric drug dosing

    Normal Ranges:
    - Adult male: 1.9 m²
    - Adult female: 1.6 m²
    - Children: Variable by age

    Args:
        height_cm: Height in centimeters (string)
        weight_kg: Weight in kilograms (string)

    Returns:
        JSON string with:
        - dubois: BSA using DuBois formula (m²)
        - mosteller: BSA using Mosteller formula (m²)
        - haycock: BSA using Haycock formula (m²)
        - gehan_george: BSA using Gehan & George formula (m²)
        - average_bsa: Average of all formulas
        - height_cm: Input height
        - weight_kg: Input weight
        - height_m: Height in meters
        - bmi: Body Mass Index
        - success: Boolean indicating if calculation was successful
        - error: Error message if calculation failed
    """

    try:
        height = float(height_cm)
        weight = float(weight_kg)

        if height <= 0 or weight <= 0:
            return json.dumps(
                {
                    "success": False,
                    "error": "Height and weight must be positive values",
                    "height_cm": height_cm,
                    "weight_kg": weight_kg,
                }
            )

        # Convert height to meters for some calculations
        height_m = height / 100

        # Calculate BSA using different formulas
        # DuBois & DuBois
        dubois = 0.007184 * (height**0.725) * (weight**0.425)

        # Mosteller
        mosteller = ((height * weight) / 3600) ** 0.5

        # Haycock
        haycock = 0.024265 * (height**0.3964) * (weight**0.5378)

        # Gehan & George
        gehan_george = 0.0235 * (height**0.42246) * (weight**0.51456)

        # Calculate average
        average_bsa = (dubois + mosteller + haycock + gehan_george) / 4

        # Calculate BMI as additional info
        bmi = weight / (height_m**2)

        return json.dumps(
            {
                "success": True,
                "dubois": round(dubois, 3),
                "mosteller": round(mosteller, 3),
                "haycock": round(haycock, 3),
                "gehan_george": round(gehan_george, 3),
                "average_bsa": round(average_bsa, 3),
                "height_cm": height,
                "weight_kg": weight,
                "height_m": round(height_m, 2),
                "bmi": round(bmi, 1),
            }
        )

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": f"BSA calculation failed: {str(e)}",
                "height_cm": height_cm,
                "weight_kg": weight_kg,
            }
        )


@function_tool
def calculate_creatinine_clearance(
    serum_creatinine_mg_dl: str, age_years: str, weight_kg: str, sex: str
) -> str:
    """Calculate estimated creatinine clearance using Cockcroft-Gault formula.

    This function estimates kidney function which is critical for:
    - Drug dosing adjustments
    - Eligibility criteria verification
    - Safety monitoring
    - Contrast administration decisions

    Cockcroft-Gault Formula:
    CrCl = ((140 - age) × weight × 0.85[if female]) / (72 × SCr)

    Where:
    - CrCl = Creatinine clearance (mL/min)
    - Age in years
    - Weight in kg
    - SCr = Serum creatinine in mg/dL
    - Multiply by 0.85 for females

    Kidney Function Categories:
    - Normal: ≥90 mL/min
    - Mild decrease: 60-89 mL/min
    - Moderate decrease: 30-59 mL/min
    - Severe decrease: 15-29 mL/min
    - Kidney failure: <15 mL/min

    Important Notes:
    - This is an estimate, not actual GFR
    - Less accurate in very obese/thin patients
    - Not validated in pregnancy
    - Consider using MDRD or CKD-EPI for some populations

    Args:
        serum_creatinine_mg_dl: Serum creatinine in mg/dL (string)
        age_years: Patient age in years (string)
        weight_kg: Patient weight in kg (string)
        sex: Patient sex ("M"/"male" or "F"/"female") (string)

    Returns:
        JSON string with:
        - creatinine_clearance: Estimated CrCl in mL/min
        - gfr_category: Normal/Mild/Moderate/Severe/Failure
        - formula_used: "Cockcroft-Gault"
        - input_values: Dictionary of input parameters
        - ideal_body_weight: IBW if needed for obesity adjustment
        - adjusted_for_bsa: CrCl adjusted to 1.73m² BSA
        - success: Boolean indicating if calculation was successful
        - error: Error message if calculation failed
    """

    try:
        scr = float(serum_creatinine_mg_dl)
        age = float(age_years)
        weight = float(weight_kg)

        if scr <= 0 or age <= 0 or weight <= 0:
            return json.dumps(
                {
                    "success": False,
                    "error": "All values must be positive",
                    "input_values": {
                        "serum_creatinine_mg_dl": serum_creatinine_mg_dl,
                        "age_years": age_years,
                        "weight_kg": weight_kg,
                        "sex": sex,
                    },
                }
            )

        # Determine sex multiplier
        sex_lower = sex.lower()
        if sex_lower in ["f", "female", "woman"]:
            sex_multiplier = 0.85
            sex_normalized = "female"
        elif sex_lower in ["m", "male", "man"]:
            sex_multiplier = 1.0
            sex_normalized = "male"
        else:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid sex value: {sex}. Use M/F or male/female",
                    "input_values": {
                        "serum_creatinine_mg_dl": serum_creatinine_mg_dl,
                        "age_years": age_years,
                        "weight_kg": weight_kg,
                        "sex": sex,
                    },
                }
            )

        # Calculate creatinine clearance
        crcl = ((140 - age) * weight * sex_multiplier) / (72 * scr)

        # Determine GFR category
        if crcl >= 90:
            gfr_category = "Normal"
        elif crcl >= 60:
            gfr_category = "Mild decrease"
        elif crcl >= 30:
            gfr_category = "Moderate decrease"
        elif crcl >= 15:
            gfr_category = "Severe decrease"
        else:
            gfr_category = "Kidney failure"

        # Note about ideal body weight (IBW) for very obese patients
        # This is informational only - actual adjustment requires height
        ibw_note = None
        if weight > 120:  # Arbitrary threshold for obesity consideration
            ibw_note = "Consider using ideal body weight for very obese patients"

        return json.dumps(
            {
                "success": True,
                "creatinine_clearance": round(crcl, 1),
                "gfr_category": gfr_category,
                "formula_used": "Cockcroft-Gault",
                "input_values": {
                    "serum_creatinine_mg_dl": scr,
                    "age_years": age,
                    "weight_kg": weight,
                    "sex": sex_normalized,
                },
                "sex_multiplier": sex_multiplier,
                "ibw_note": ibw_note,
            }
        )

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": f"CrCl calculation failed: {str(e)}",
                "input_values": {
                    "serum_creatinine_mg_dl": serum_creatinine_mg_dl,
                    "age_years": age_years,
                    "weight_kg": weight_kg,
                    "sex": sex,
                },
            }
        )


@function_tool
def calculate_date_difference(date1: str, date2: str, unit: str = "days") -> str:
    """Calculate the difference between two dates in various units.

    This function helps agents determine time intervals for:
    - Adverse event duration
    - Time since last dose
    - Study participation length
    - Follow-up intervals
    - Protocol compliance windows

    Supported Units:
    - days: Total calendar days
    - weeks: Total weeks (including partial)
    - months: Approximate months (30.44 days)
    - years: Approximate years (365.25 days)
    - business_days: Weekdays only
    - hours: Total hours
    - minutes: Total minutes

    Special Features:
    - Handles multiple date formats
    - Returns both absolute and signed differences
    - Calculates business days excluding weekends
    - Provides human-readable duration

    Args:
        date1: First date (string)
        date2: Second date (string)
        unit: Unit for difference (default "days")

    Returns:
        JSON string with:
        - difference: Numeric difference in requested unit
        - absolute_difference: Absolute value of difference
        - direction: "future"/"past"/"same" relative to date1
        - days: Always includes difference in days
        - human_readable: Formatted string (e.g., "2 months, 3 days")
        - date1_parsed: Standardized date1
        - date2_parsed: Standardized date2
        - unit: Unit used for calculation
        - success: Boolean indicating if calculation was successful
        - error: Error message if calculation failed
    """

    try:
        # Parse dates
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%d-%b-%Y",
            "%d-%B-%Y",
            "%Y/%m/%d",
        ]

        dt1 = None
        dt2 = None

        for fmt in date_formats:
            if dt1 is None:
                try:
                    dt1 = datetime.strptime(date1, fmt)
                except ValueError:
                    continue
            if dt2 is None:
                try:
                    dt2 = datetime.strptime(date2, fmt)
                except ValueError:
                    continue

        if dt1 is None or dt2 is None:
            return json.dumps(
                {
                    "success": False,
                    "error": "Unable to parse dates",
                    "date1": date1,
                    "date2": date2,
                    "supported_formats": date_formats,
                }
            )

        # Calculate difference
        delta = dt2 - dt1
        days = delta.days
        total_seconds = delta.total_seconds()

        # Determine direction
        if days > 0:
            direction = "future"
        elif days < 0:
            direction = "past"
        else:
            direction = "same"

        # Calculate in requested unit
        unit_lower = unit.lower()
        if unit_lower == "days":
            difference = days
        elif unit_lower == "weeks":
            difference = days / 7
        elif unit_lower == "months":
            difference = days / 30.44  # Average month length
        elif unit_lower == "years":
            difference = days / 365.25  # Account for leap years
        elif unit_lower == "hours":
            difference = total_seconds / 3600
        elif unit_lower == "minutes":
            difference = total_seconds / 60
        elif unit_lower == "business_days":
            # Calculate business days
            business_days = 0
            current = min(dt1, dt2)
            end = max(dt1, dt2)
            while current <= end:
                if current.weekday() < 5:  # Monday = 0, Friday = 4
                    business_days += 1
                current += timedelta(days=1)
            difference = business_days if dt2 >= dt1 else -business_days
        else:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Unsupported unit: {unit}",
                    "supported_units": [
                        "days",
                        "weeks",
                        "months",
                        "years",
                        "hours",
                        "minutes",
                        "business_days",
                    ],
                }
            )

        # Create human-readable format
        abs_days = abs(days)
        if abs_days == 0:
            human_readable = "Same day"
        elif abs_days == 1:
            human_readable = "1 day"
        elif abs_days < 7:
            human_readable = f"{abs_days} days"
        elif abs_days < 30:
            weeks = abs_days // 7
            remaining_days = abs_days % 7
            human_readable = f"{weeks} week{'s' if weeks > 1 else ''}"
            if remaining_days > 0:
                human_readable += (
                    f", {remaining_days} day{'s' if remaining_days > 1 else ''}"
                )
        elif abs_days < 365:
            months = abs_days // 30
            remaining_days = abs_days % 30
            human_readable = f"{months} month{'s' if months > 1 else ''}"
            if remaining_days > 0:
                human_readable += (
                    f", {remaining_days} day{'s' if remaining_days > 1 else ''}"
                )
        else:
            years = abs_days // 365
            remaining_days = abs_days % 365
            human_readable = f"{years} year{'s' if years > 1 else ''}"
            if remaining_days > 30:
                months = remaining_days // 30
                human_readable += f", {months} month{'s' if months > 1 else ''}"

        if direction == "past":
            human_readable += " ago"
        elif direction == "future":
            human_readable += " ahead"

        return json.dumps(
            {
                "success": True,
                "difference": round(difference, 2),
                "absolute_difference": abs(round(difference, 2)),
                "direction": direction,
                "days": days,
                "human_readable": human_readable,
                "date1_parsed": dt1.strftime("%Y-%m-%d"),
                "date2_parsed": dt2.strftime("%Y-%m-%d"),
                "unit": unit,
            }
        )

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": f"Date difference calculation failed: {str(e)}",
                "date1": date1,
                "date2": date2,
                "unit": unit,
            }
        )


# Export all calculation tools
__all__ = [
    "convert_medical_units",
    "calculate_age_at_visit",
    "check_visit_window_compliance",
    "calculate_change_from_baseline",
    "calculate_body_surface_area",
    "calculate_creatinine_clearance",
    "calculate_date_difference",
]
