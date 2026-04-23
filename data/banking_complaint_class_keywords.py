"""Dummy class keyword dictionaries for retail banking complaint classification.

Each SHAP-like score is in the range [-1.0, 1.0], where positive values
indicate evidence for the class and negative values indicate evidence against it.
"""

CLASS_KEYWORD_DICTIONARIES = [
    {
        "class_name": "Card Payment Dispute",
        "keywords": [
            ("chargeback", 0.94),
            ("merchant descriptor", 0.88),
            ("provisional credit", 0.84),
            ("cash advance", -0.79),
        ],
    },
    {
        "class_name": "Card Charge Review",
        "keywords": [
            ("pending authorisation", 0.91),
            ("duplicate hold", 0.86),
            ("preauth reversal", 0.82),
            ("chargeback", -0.76),
        ],
    },
    {
        "class_name": "Card Security Concern",
        "keywords": [
            ("card not present", 0.93),
            ("tokenised wallet", 0.87),
            ("suspicious tap", 0.81),
            ("pending authorisation", -0.74),
        ],
    },
    {
        "class_name": "Account Access Issue",
        "keywords": [
            ("biometric lockout", 0.92),
            ("one time passcode", 0.88),
            ("device binding", 0.84),
            ("source of funds", -0.81),
        ],
    },
    {
        "class_name": "Account Review Request",
        "keywords": [
            ("kyc refresh", 0.94),
            ("source of funds", 0.89),
            ("enhanced due diligence", 0.86),
            ("biometric lockout", -0.78),
        ],
    },
    {
        "class_name": "Account Restriction Notice",
        "keywords": [
            ("debit freeze", 0.93),
            ("account hold", 0.88),
            ("aml block", 0.85),
            ("kyc refresh", -0.72),
        ],
    },
    {
        "class_name": "Transfer Processing Delay",
        "keywords": [
            ("osko pending", 0.91),
            ("npp timeout", 0.87),
            ("cut off time", 0.82),
            ("wrong bsb", -0.77),
        ],
    },
    {
        "class_name": "Transfer Detail Error",
        "keywords": [
            ("wrong bsb", 0.94),
            ("payid mismatch", 0.89),
            ("beneficiary name", 0.83),
            ("npp timeout", -0.75),
        ],
    },
    {
        "class_name": "Loan Payment Issue",
        "keywords": [
            ("direct debit dishonour", 0.93),
            ("arrears notice", 0.88),
            ("repayment holiday", 0.81),
            ("break cost", -0.78),
        ],
    },
    {
        "class_name": "Loan Rate Query",
        "keywords": [
            ("break cost", 0.92),
            ("fixed rate expiry", 0.87),
            ("comparison rate", 0.82),
            ("arrears notice", -0.80),
        ],
    },
]
