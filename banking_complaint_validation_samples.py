"""Validation retail banking complaint samples for prompt/eval experiments.

Each sample contains exactly one positive keyword from
banking_complaint_class_keywords.py.
"""

COMPLAINT_SAMPLES = [
    {
        "sample_number": 1,
        "class_label": "Card Payment Dispute",
        "complaint_text": "I submitted a chargeback after the electronics store kept the returned item and the payment.",
    },
    {
        "sample_number": 2,
        "class_label": "Card Payment Dispute",
        "complaint_text": "The merchant descriptor on my card statement lists a shop I have never visited.",
    },
    {
        "sample_number": 3,
        "class_label": "Card Payment Dispute",
        "complaint_text": "The promised provisional credit for my disputed airfare has not appeared.",
    },
    {
        "sample_number": 4,
        "class_label": "Card Charge Review",
        "complaint_text": "A pending authorisation from the pharmacy is still reducing my card limit after the receipt settled.",
    },
    {
        "sample_number": 5,
        "class_label": "Card Charge Review",
        "complaint_text": "The cinema placed a duplicate hold on my card for the same ticket purchase.",
    },
    {
        "sample_number": 6,
        "class_label": "Card Charge Review",
        "complaint_text": "The motel confirmed a preauth reversal, but my available balance has not recovered.",
    },
    {
        "sample_number": 7,
        "class_label": "Card Security Concern",
        "complaint_text": "I received alerts for card not present purchases while my physical card was locked away.",
    },
    {
        "sample_number": 8,
        "class_label": "Card Security Concern",
        "complaint_text": "A tokenised wallet I do not recognise was linked to my debit card overnight.",
    },
    {
        "sample_number": 9,
        "class_label": "Card Security Concern",
        "complaint_text": "There is a suspicious tap at a convenience store from a city I have not visited.",
    },
    {
        "sample_number": 10,
        "class_label": "Account Access Issue",
        "complaint_text": "Biometric lockout keeps stopping me from opening mobile banking after I replaced my screen.",
    },
    {
        "sample_number": 11,
        "class_label": "Account Access Issue",
        "complaint_text": "The one time passcode expires before the text message reaches my phone.",
    },
    {
        "sample_number": 12,
        "class_label": "Account Access Issue",
        "complaint_text": "Device binding fails when I try to approve this tablet for internet banking.",
    },
    {
        "sample_number": 13,
        "class_label": "Account Review Request",
        "complaint_text": "The KYC refresh page asks for my passport again even though I uploaded it yesterday.",
    },
    {
        "sample_number": 14,
        "class_label": "Account Review Request",
        "complaint_text": "I need to provide source of funds for a property deposit before settlement.",
    },
    {
        "sample_number": 15,
        "class_label": "Account Review Request",
        "complaint_text": "Enhanced due diligence questions are holding up my new company account.",
    },
    {
        "sample_number": 16,
        "class_label": "Account Restriction Notice",
        "complaint_text": "A debit freeze was placed on my account after I tried to pay my supplier.",
    },
    {
        "sample_number": 17,
        "class_label": "Account Restriction Notice",
        "complaint_text": "The account hold is stopping rent payments even though deposits still arrive.",
    },
    {
        "sample_number": 18,
        "class_label": "Account Restriction Notice",
        "complaint_text": "An AML block message appears whenever I attempt an overseas transfer.",
    },
    {
        "sample_number": 19,
        "class_label": "Transfer Processing Delay",
        "complaint_text": "My Osko pending transfer has not reached the plumber after an hour.",
    },
    {
        "sample_number": 20,
        "class_label": "Transfer Processing Delay",
        "complaint_text": "The app showed NPP timeout after I sent payroll to a staff member.",
    },
    {
        "sample_number": 21,
        "class_label": "Transfer Processing Delay",
        "complaint_text": "The transfer was delayed because the cut off time was applied to a same-day payment.",
    },
    {
        "sample_number": 22,
        "class_label": "Transfer Detail Error",
        "complaint_text": "I entered the wrong BSB for a school fee payment and need help recovering it.",
    },
    {
        "sample_number": 23,
        "class_label": "Transfer Detail Error",
        "complaint_text": "The PayID mismatch warning showed a name I did not recognise before I sent money.",
    },
    {
        "sample_number": 24,
        "class_label": "Transfer Detail Error",
        "complaint_text": "The beneficiary name differs from the invoice and the supplier cannot find the funds.",
    },
    {
        "sample_number": 25,
        "class_label": "Loan Payment Issue",
        "complaint_text": "A direct debit dishonour was recorded even though the repayment account had enough money.",
    },
    {
        "sample_number": 26,
        "class_label": "Loan Payment Issue",
        "complaint_text": "The arrears notice arrived after I made the catch-up payment at the branch.",
    },
    {
        "sample_number": 27,
        "class_label": "Loan Payment Issue",
        "complaint_text": "My repayment holiday approval is missing from the loan account notes.",
    },
    {
        "sample_number": 28,
        "class_label": "Loan Rate Query",
        "complaint_text": "Please calculate the break cost before I refinance with another lender.",
    },
    {
        "sample_number": 29,
        "class_label": "Loan Rate Query",
        "complaint_text": "The fixed rate expiry reminder has the wrong date for my mortgage split.",
    },
    {
        "sample_number": 30,
        "class_label": "Loan Rate Query",
        "complaint_text": "The comparison rate on the loan variation form is higher than expected.",
    },
]
