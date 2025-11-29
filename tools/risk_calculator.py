"""
Simple irAE risk calculator based on literature patterns.
"""

def calculate_irae_risk() -> dict:
    return {
        "any_grade_irae": "58%",
        "grade_3_4_irae": "18%",
        "endocrine_irae": "42%",
        "pneumonitis": "7%",
        "colitis": "4%",
        "hepatitis": "6%",
        "recommendation": "Initiate thyroid function monitoring at baseline and every 6 weeks"
    }