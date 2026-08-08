# Class weights:
# Weight = base severity contribution per confirmed occurrence. Higher weight means higher severity
HAZARD_CLASSES = {
    "fire": 10,
    "chemical hazard": 8,
    "smoke": 6,
    "water leak": 3,
}

PPE_VIOLATION_CLASSES = {
    "Fall-Detected": 10,
    "NO-Hardhat": 7,
    "NO-Goggles": 7,
    "NO-Mask": 5,
    "NO-Safety Vest": 3,
}

# Compliance check (not scored)
PPE_COMPLIANT_CLASSES = {
    # "hardhat", "vest", "gloves"
}

# Amount of frames persisting before being marked a violation
PERSISTENCE_FRAMES = 3

# Risk Rating logic
RISK_TIERS = [
    (10, "Low"),
    (30, "Medium"),
    (60, "High"),
    (float("inf"), "Critical"),
]

CONFIDENCE_THRESHOLD = 0.25
FRAME_SKIP = 5  # to minimize resource costs, can be adjusted for frames being skipped
