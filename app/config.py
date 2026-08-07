# --- Class weights ---
# Weight = base severity contribution per confirmed occurrence.
# Higher weight = more dangerous. Tune these to your judgment / domain rules.

HAZARD_CLASSES = {
    "fire": 10,
    "chemical hazard": 8,
    "smoke": 6,
    "water leak": 3,
}

PPE_VIOLATION_CLASSES = {
    "Fall-Detected": 10,
    "No-Hardhat": 7,
    "No-Goggles": 7,
    "No-Mask": 5,
    "No-Safety Vest": 3,
}

# Classes that exist in the PPE model but represent COMPLIANCE, not a
# violation (e.g. "hardhat", "vest" = correctly worn). Not scored — listed
# here just so it's clear they're intentionally excluded, not forgotten.
PPE_COMPLIANT_CLASSES = {
    # "hardhat", "vest", "gloves"
}

# --- Persistence ---
# A class must appear in this many CONSECUTIVE analyzed frames before it's
# counted as a "confirmed" violation. Filters out one-off false positives
# (bad angle, occlusion, motion blur) from actually sustained conditions.
PERSISTENCE_FRAMES = 3

# --- Risk tiers ---
# (upper_bound_inclusive, label) — checked in order, first match wins.
RISK_TIERS = [
    (10, "Low"),
    (30, "Medium"),
    (60, "High"),
    (float("inf"), "Critical"),
]

# --- Detection settings ---
CONFIDENCE_THRESHOLD = 0.25
FRAME_SKIP = 5  # analyze every Nth frame (raise for speed, lower for precision)
