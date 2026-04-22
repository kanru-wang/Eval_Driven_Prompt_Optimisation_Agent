"""Test retail banking complaint samples for prompt/eval experiments.

Each sample contains exactly one positive keyword from
banking_complaint_class_keywords.py and is unique from the validation samples.
"""

COMPLAINT_SAMPLES = [
    {
        "sample_number": 1,
        "class_label": "Card Payment Dispute",
        "complaint_text": "The travel agent refuses to refund the cancelled tour, so I want a chargeback raised.",
    },
    {
        "sample_number": 2,
        "class_label": "Card Payment Dispute",
        "complaint_text": "A merchant descriptor for an unknown meal delivery service appeared on my statement.",
    },
    {
        "sample_number": 3,
        "class_label": "Card Payment Dispute",
        "complaint_text": "I was told provisional credit would cover the disputed appliance purchase this week.",
    },
    {
        "sample_number": 4,
        "class_label": "Card Charge Review",
        "complaint_text": "The hotel has a pending authorisation even though I paid the final invoice yesterday.",
    },
    {
        "sample_number": 5,
        "class_label": "Card Charge Review",
        "complaint_text": "A duplicate hold from the airport kiosk is tying up money I need today.",
    },
    {
        "sample_number": 6,
        "class_label": "Card Charge Review",
        "complaint_text": "The hire company sent proof of preauth reversal but the funds are still unavailable.",
    },
    {
        "sample_number": 7,
        "class_label": "Card Security Concern",
        "complaint_text": "Two card not present charges appeared after I blocked online purchases.",
    },
    {
        "sample_number": 8,
        "class_label": "Card Security Concern",
        "complaint_text": "My card controls show a tokenised wallet attached to a phone I do not own.",
    },
    {
        "sample_number": 9,
        "class_label": "Card Security Concern",
        "complaint_text": "A suspicious tap happened at a parking meter while I was at work.",
    },
    {
        "sample_number": 10,
        "class_label": "Account Access Issue",
        "complaint_text": "The branch reset my profile, but biometric lockout still appears in the app.",
    },
    {
        "sample_number": 11,
        "class_label": "Account Access Issue",
        "complaint_text": "I cannot complete sign-in because the one time passcode is sent to my old SIM.",
    },
    {
        "sample_number": 12,
        "class_label": "Account Access Issue",
        "complaint_text": "Device binding is stuck after I approved the new phone from my email link.",
    },
    {
        "sample_number": 13,
        "class_label": "Account Review Request",
        "complaint_text": "KYC refresh keeps asking for business registration papers I already supplied.",
    },
    {
        "sample_number": 14,
        "class_label": "Account Review Request",
        "complaint_text": "The bank needs source of funds evidence for a large cheque deposit.",
    },
    {
        "sample_number": 15,
        "class_label": "Account Review Request",
        "complaint_text": "Enhanced due diligence is delaying the account upgrade for my charity.",
    },
    {
        "sample_number": 16,
        "class_label": "Account Restriction Notice",
        "complaint_text": "The debit freeze stopped my business card just before payroll was due.",
    },
    {
        "sample_number": 17,
        "class_label": "Account Restriction Notice",
        "complaint_text": "An account hold appeared after a sale deposit and now I cannot withdraw cash.",
    },
    {
        "sample_number": 18,
        "class_label": "Account Restriction Notice",
        "complaint_text": "The teller said an AML block is why my scheduled transfers were cancelled.",
    },
    {
        "sample_number": 19,
        "class_label": "Transfer Processing Delay",
        "complaint_text": "The Osko pending status remains on a payment for urgent medical costs.",
    },
    {
        "sample_number": 20,
        "class_label": "Transfer Processing Delay",
        "complaint_text": "NPP timeout appeared after I sent the deposit to the auction agent.",
    },
    {
        "sample_number": 21,
        "class_label": "Transfer Processing Delay",
        "complaint_text": "Support says cut off time caused the settlement transfer to wait overnight.",
    },
    {
        "sample_number": 22,
        "class_label": "Transfer Detail Error",
        "complaint_text": "The wrong BSB was saved in my template and the council payment has vanished.",
    },
    {
        "sample_number": 23,
        "class_label": "Transfer Detail Error",
        "complaint_text": "A PayID mismatch appeared for my contractor, but I proceeded and now regret it.",
    },
    {
        "sample_number": 24,
        "class_label": "Transfer Detail Error",
        "complaint_text": "The beneficiary name on the transfer receipt does not match the cleaner's account.",
    },
    {
        "sample_number": 25,
        "class_label": "Loan Payment Issue",
        "complaint_text": "The statement lists direct debit dishonour for a loan payment taken two days later.",
    },
    {
        "sample_number": 26,
        "class_label": "Loan Payment Issue",
        "complaint_text": "An arrears notice was emailed after I paid the overdue instalment online.",
    },
    {
        "sample_number": 27,
        "class_label": "Loan Payment Issue",
        "complaint_text": "The repayment holiday was approved, yet the next loan payment still shows due.",
    },
    {
        "sample_number": 28,
        "class_label": "Loan Rate Query",
        "complaint_text": "I need the break cost figure before deciding whether to sell the unit.",
    },
    {
        "sample_number": 29,
        "class_label": "Loan Rate Query",
        "complaint_text": "My fixed rate expiry notice lists a product I never selected.",
    },
    {
        "sample_number": 30,
        "class_label": "Loan Rate Query",
        "complaint_text": "Can you explain why the comparison rate changed on the refinance quote?",
    },
]
