# Day 3 — Python basics (variables, lists, dicts)
# Run: python basics.py

policy_name = "Telemedicine reimbursement pilot"
budget_million = 2.5
is_active = True

patient_medications = ["metformin", "lisinopril", "atorvastatin"]
policy_recommendations = [
    "Expand rural coverage",
    "Add outcome tracking",
    "Quarterly budget review",
]

policy_case = {
    "title": policy_name,
    "budget_million": budget_million,
    "active": is_active,
    "kpis": {"adoption_rate": 0.32, "readmission_delta": -0.05},
}

if __name__ == "__main__":
    # Simple practice
    patient_medications.append("amlodipine")
    policy_recommendations.append("Risk-adjust reimbursement")
    policy_case["active"] = False
    print("Med count:", len(patient_medications))
    print("Top recommendation:", policy_recommendations[0])
    print("Adoption rate:", policy_case["kpis"]["adoption_rate"])
