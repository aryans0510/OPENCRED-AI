# creditvision_ai_app.py
import streamlit as st
import pandas as pd
import numpy as np # For financial calculations if needed, though simple math might suffice

# --- Configuration & Constants ---
CIVIL_SCORE_MIN = 300
CIVIL_SCORE_MAX = 900
ANNUAL_INTEREST_RATE_DEFAULT = 0.09 # 9% p.a. default base
MAX_EMI_TO_INCOME_RATIO = 0.45 # Max 45% of monthly income can be EMI

JOB_TYPES = [
    "Gig Worker (e.g., Delivery, Driver)",
    "Farmer / Agricultural Worker",
    "Small Shop Owner / Local Business",
    "Salaried (Formal Employment)",
    "Freelancer / Consultant (Irregular Income)",
    "Other"
]

LOAN_TENURES_YEARS = [5, 10, 15, 20, 25, 30]

# --- Core Logic Functions ---

def simulate_alt_data_features(job_type):
    """
    Simulates alternative data features based on job type.
    Returns a dictionary of features, each scored 0.0 to 1.0.
    These features are conceptual and simplified for the demo.
    """
    features = {
        "income_stability_proxy": 0.5,      # e.g., regularity of income streams
        "digital_transaction_volume": 0.5,  # e.g., use of digital payments
        "social_reputation_proxy": 0.5,     # e.g., online reviews, community standing (highly conceptual)
        "asset_ownership_proxy": 0.5,       # e.g., vehicle, equipment, land (simplified)
        "skill_versatility_proxy": 0.5      # e.g., ability to adapt to different work
    }

    if job_type == "Gig Worker (e.g., Delivery, Driver)":
        features.update({
            "income_stability_proxy": 0.6,
            "digital_transaction_volume": 0.7,
            "social_reputation_proxy": 0.65, # Platform ratings
            "skill_versatility_proxy": 0.7
        })
    elif job_type == "Farmer / Agricultural Worker":
        features.update({
            "income_stability_proxy": 0.4, # Seasonal income
            "asset_ownership_proxy": 0.7,  # Land, equipment
            "social_reputation_proxy": 0.6, # Local community standing
            "digital_transaction_volume": 0.3
        })
    elif job_type == "Small Shop Owner / Local Business":
        features.update({
            "income_stability_proxy": 0.65,
            "digital_transaction_volume": 0.75,
            "social_reputation_proxy": 0.7,  # Customer reviews, local presence
            "asset_ownership_proxy": 0.6
        })
    elif job_type == "Salaried (Formal Employment)":
        features.update({
            "income_stability_proxy": 0.9,
            "digital_transaction_volume": 0.8,
            "asset_ownership_proxy": 0.6,
            "skill_versatility_proxy": 0.7
        })
    elif job_type == "Freelancer / Consultant (Irregular Income)":
        features.update({
            "income_stability_proxy": 0.55,
            "digital_transaction_volume": 0.85,
            "social_reputation_proxy": 0.75, # Online portfolio, client testimonials
            "skill_versatility_proxy": 0.8
        })
    # "Other" uses default values

    return features

def generate_civil_score(alt_data_features):
    """
    Generates a Civil Score (300-900) based on simulated alternative data.
    """
    # Simple averaging of feature scores (0-1 scale)
    if not alt_data_features:
        avg_feature_score = 0.5 # Default
    else:
        avg_feature_score = sum(alt_data_features.values()) / len(alt_data_features)

    # Scale to 300-900 range
    # score = MIN_SCORE + (NORMALIZED_AVG * (MAX_SCORE - MIN_SCORE))
    civil_score = int(CIVIL_SCORE_MIN + (avg_feature_score * (CIVIL_SCORE_MAX - CIVIL_SCORE_MIN)))
    
    # Ensure score is within bounds, though calculation should keep it there
    civil_score = max(CIVIL_SCORE_MIN, min(civil_score, CIVIL_SCORE_MAX))
    return civil_score

def calculate_loan_interest_rate(civil_score):
    """
    Estimates an annual interest rate based on the civil score.
    Higher score = slightly lower rate. This is a simplified model.
    """
    # Score influences rate: e.g., for every 100 points above 600, rate decreases by 0.5%
    # For every 100 points below 600, rate increases by 0.5%
    # Base rate is ANNUAL_INTEREST_RATE_DEFAULT
    
    score_diff_from_mid = (civil_score - (CIVIL_SCORE_MIN + (CIVIL_SCORE_MAX - CIVIL_SCORE_MIN) / 2)) / 100
    rate_adjustment = - (score_diff_from_mid * 0.0025) # 0.25% adjustment per 100 points from mid-range score (600)
    
    estimated_annual_rate = ANNUAL_INTEREST_RATE_DEFAULT + rate_adjustment
    
    # Cap interest rates to a reasonable range (e.g., 7% to 15%)
    estimated_annual_rate = max(0.07, min(estimated_annual_rate, 0.15))
    return estimated_annual_rate

def calculate_max_loan_and_emi(monthly_income, annual_interest_rate, loan_tenure_years):
    """
    Calculates the maximum loan amount based on permissible EMI and other factors.
    Also calculates EMI for that max loan.
    """
    max_permissible_emi = monthly_income * MAX_EMI_TO_INCOME_RATIO
    
    monthly_interest_rate = annual_interest_rate / 12
    number_of_payments = loan_tenure_years * 12

    if monthly_interest_rate == 0: # Avoid division by zero if rate is 0 (unlikely for loans)
        max_loan_amount = max_permissible_emi * number_of_payments
    else:
        # Formula for Present Value of an Annuity (Loan Amount)
        # P = EMI * [1 - (1 + r)^-n] / r
        try:
            max_loan_amount = max_permissible_emi * (1 - (1 + monthly_interest_rate)**-number_of_payments) / monthly_interest_rate
        except OverflowError: # Handle potential math overflow with very large n or small r
            max_loan_amount = 0 # Or some other fallback

    # For the calculated max_loan_amount, the EMI will be max_permissible_emi
    # However, let's recalculate EMI for the actual loan amount to be precise,
    # as max_loan_amount might be rounded or adjusted.
    
    if max_loan_amount <= 0:
        return 0, 0

    # EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
    if monthly_interest_rate == 0:
        actual_emi = max_loan_amount / number_of_payments if number_of_payments > 0 else 0
    else:
        try:
            numerator = max_loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate)**number_of_payments)
            denominator = ((1 + monthly_interest_rate)**number_of_payments) - 1
            if denominator == 0: # Avoid division by zero
                 actual_emi = max_loan_amount / number_of_payments if number_of_payments > 0 else 0 # Approx if tenure is short and rate is effectively 0
            else:
                actual_emi = numerator / denominator
        except OverflowError:
            actual_emi = monthly_income # Fallback to a high number or handle appropriately

    return round(max_loan_amount, 2), round(actual_emi, 2)


def get_mock_bank_loan_options(max_loan_calculated, calculated_emi, civil_score, loan_tenure_years, base_annual_interest_rate):
    """
    Generates a list of mock bank loan offers.
    """
    options = []
    
    # Bank 1: "Inclusive Housing Finance" - targets underserved
    bank1_rate_adj = 0.005 # Slightly higher base rate
    bank1_interest_rate = min(0.16, max(0.075, base_annual_interest_rate + bank1_rate_adj - (civil_score - 600)/100 * 0.001)) # Rate benefits less from high score
    bank1_loan_amount = round(max_loan_calculated * np.random.uniform(0.90, 0.98), -3) # Offers slightly less, rounded
    _, bank1_emi = calculate_max_loan_and_emi(0, bank1_interest_rate, loan_tenure_years) # Pass 0 for income as we use loan amount
    
    # Recalculate EMI for bank1_loan_amount
    monthly_rate_b1 = bank1_interest_rate / 12
    num_payments_b1 = loan_tenure_years * 12
    if monthly_rate_b1 > 0 and num_payments_b1 > 0:
        if ((1 + monthly_rate_b1)**num_payments_b1) - 1 > 0: # check denominator
            bank1_emi_recalc = (bank1_loan_amount * monthly_rate_b1 * (1 + monthly_rate_b1)**num_payments_b1) / (((1 + monthly_rate_b1)**num_payments_b1) - 1)
        else:
            bank1_emi_recalc = bank1_loan_amount / num_payments_b1 if num_payments_b1 > 0 else 0
    else:
        bank1_emi_recalc = bank1_loan_amount / num_payments_b1 if num_payments_b1 > 0 else 0


    if bank1_loan_amount > 10000: # Only add if loan amount is somewhat substantial
        options.append({
            "bank_name": "Inclusive Housing Finance Ltd.",
            "loan_product_name": "Sahay Home Loan",
            "offered_loan_amount": bank1_loan_amount,
            "interest_rate_pa": round(bank1_interest_rate * 100, 2),
            "tenure_years": loan_tenure_years,
            "estimated_emi": round(bank1_emi_recalc, 2),
            "notes": "Focuses on financial inclusion, flexible documentation (simulated)."
        })

    # Bank 2: "Progressive National Bank" - standard bank
    bank2_rate_adj = -0.002 # Slightly more competitive
    bank2_interest_rate = min(0.14, max(0.07, base_annual_interest_rate + bank2_rate_adj - (civil_score - 650)/100 * 0.002)) # Better rate for good scores
    bank2_loan_amount = round(max_loan_calculated * np.random.uniform(0.95, 1.0), -3) # Offers closer to max
    
    # Recalculate EMI for bank2_loan_amount
    monthly_rate_b2 = bank2_interest_rate / 12
    num_payments_b2 = loan_tenure_years * 12
    if monthly_rate_b2 > 0 and num_payments_b2 > 0:
        if ((1 + monthly_rate_b2)**num_payments_b2) - 1 > 0: # check denominator
            bank2_emi_recalc = (bank2_loan_amount * monthly_rate_b2 * (1 + monthly_rate_b2)**num_payments_b2) / (((1 + monthly_rate_b2)**num_payments_b2) - 1)
        else:
            bank2_emi_recalc = bank2_loan_amount / num_payments_b2 if num_payments_b2 > 0 else 0
    else:
        bank2_emi_recalc = bank2_loan_amount / num_payments_b2 if num_payments_b2 > 0 else 0

    if bank2_loan_amount > 10000:
        options.append({
            "bank_name": "Progressive National Bank",
            "loan_product_name": "MyFirstHome Loan",
            "offered_loan_amount": bank2_loan_amount,
            "interest_rate_pa": round(bank2_interest_rate * 100, 2),
            "tenure_years": loan_tenure_years,
            "estimated_emi": round(bank2_emi_recalc, 2),
            "notes": "Competitive rates, standard processing (simulated)."
        })
    
    # Ensure at least one option if max_loan_calculated was positive, even if basic
    if not options and max_loan_calculated > 0:
         options.append({
            "bank_name": "Generic Lender Co.",
            "loan_product_name": "Basic Home Loan",
            "offered_loan_amount": round(max_loan_calculated * 0.9, -3), # 90% of calculated
            "interest_rate_pa": round(base_annual_interest_rate * 100, 2) + 1.0, # Slightly higher rate
            "tenure_years": loan_tenure_years,
            "estimated_emi": calculated_emi * 1.05, # Approx
            "notes": "A basic loan option (simulated)."
        })


    return options


def generate_ai_explanation(civil_score, max_loan_amount, emi, bank_options, job_type, income):
    """
    Generates a mock AI-powered explanation.
    """
    score_rating = "fair"
    if civil_score >= 800: score_rating = "excellent"
    elif civil_score >= 740: score_rating = "very good"
    elif civil_score >= 670: score_rating = "good"
    elif civil_score < 580: score_rating = "poor, requiring improvement"


    explanation = f"Namaste! Here's an overview of your home loan possibilities with CreditVision AI:\n\n"
    explanation += f"**1. Your Financial Snapshot:**\n"
    explanation += f"- **Occupation:** {job_type}\n"
    explanation += f"- **Monthly Income:** ₹{income:,.0f}\n"
    explanation += f"- **CreditVision AI Score:** Your score is {civil_score} (out of {CIVIL_SCORE_MAX}), which is considered {score_rating} based on our alternative data assessment. This score reflects factors like your income patterns and digital engagement, helping lenders understand your creditworthiness even without a traditional credit history.\n\n"

    explanation += f"**2. Estimated Loan Eligibility:**\n"
    explanation += f"- You might qualify for a maximum home loan of approximately **₹{max_loan_amount:,.0f}**.\n"
    explanation += f"- For this amount, your estimated Equated Monthly Instalment (EMI) would be around **₹{emi:,.0f}**.\n"
    explanation += f"This estimation is based on your income, your CreditVision AI score, and standard lending guidelines, assuming up to {MAX_EMI_TO_INCOME_RATIO*100:.0f}% of your income can go towards EMI.\n\n"

    if bank_options:
        explanation += f"**3. Recommended Loan Options (Simulated):**\n"
        for i, option in enumerate(bank_options):
            explanation += f"   **Option {i+1}: {option['bank_name']} - {option['loan_product_name']}**\n"
            explanation += f"   - Loan Amount: ₹{option['offered_loan_amount']:,.0f}\n"
            explanation += f"   - Interest Rate: {option['interest_rate_pa']:.2f}% p.a.\n"
            explanation += f"   - EMI: ₹{option['estimated_emi']:,.0f} for {option['tenure_years']} years.\n"
            explanation += f"   - *Why this might fit you:* {option['notes']}\n\n"
        explanation += f"These are illustrative options. The actual terms may vary. Your CreditVision AI score helps these lenders consider you more favorably.\n\n"
    else:
        explanation += f"**3. Loan Options:**\nBased on the current inputs, specific bank offers couldn't be generated. This might be due to a very low estimated loan eligibility. Consider adjusting your inputs or exploring options for improving your financial profile.\n\n"

    explanation += f"**4. Next Steps & Disclaimer:**\n"
    explanation += f"- Use this information as a guide. Approach banks with your CreditVision AI summary.\n"
    explanation += f"- Always verify terms directly with lenders before making any decisions.\n"
    explanation += f"- CreditVision AI aims for financial inclusion. We encourage responsible borrowing.\n\n"
    explanation += f"We hope this helps you on your journey to owning a home!"
    return explanation

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="CreditVision AI")

st.title("🏠 CreditVision AI – Inclusive Credit & Home Loan Recommender")
st.markdown("""
*Empowering India's financially invisible with access to fair housing loans through AI-driven insights from alternative data.*
""")
st.markdown("---")

# --- User Inputs ---
st.sidebar.header("👤 Your Details")
monthly_income = st.sidebar.number_input(
    "Monthly Income (in ₹)", 
    min_value=5000, 
    max_value=500000, 
    value=25000, 
    step=1000,
    help="Enter your approximate average monthly income."
)
job_type = st.sidebar.selectbox(
    "Primary Occupation / Job Type", 
    options=JOB_TYPES, 
    index=0,
    help="Select the category that best describes your main source of income."
)
loan_tenure_years = st.sidebar.selectbox(
    "Desired Home Loan Tenure (Years)",
    options=LOAN_TENURES_YEARS,
    index=2, # Default to 15 years
    help="How long would you prefer to repay the loan?"
)

st.sidebar.markdown("---")
run_button = st.sidebar.button("🚀 Get My Loan Insights", type="primary")
st.sidebar.markdown("---")
st.sidebar.markdown("""
**About CreditVision AI:**
We use simulated alternative data signals (like digital footprint, income stability proxies) to generate a credit score for individuals who may have thin or no formal credit files. Our goal is to promote financial inclusion. *This is a demo application.*
""")


# --- Main Panel for Results ---
if run_button:
    if monthly_income <= 0:
        st.error("Monthly Income must be a positive value.")
    else:
        st.header("📈 Your Personalized Loan Insights")
        
        with st.spinner("Analyzing your profile with CreditVision AI..."):
            # 1. Simulate Alt Data
            alt_data = simulate_alt_data_features(job_type)
            
            # 2. Generate Civil Score
            civil_score = generate_civil_score(alt_data)
            
            # 3. Determine Interest Rate
            annual_interest_rate = calculate_loan_interest_rate(civil_score)
            
            # 4. Estimate Max Loan and EMI
            max_loan, emi = calculate_max_loan_and_emi(monthly_income, annual_interest_rate, loan_tenure_years)

            # 5. Get Mock Bank Options
            bank_options = []
            if max_loan > 0 : # Only get bank options if eligible for some loan
                 bank_options = get_mock_bank_loan_options(max_loan, emi, civil_score, loan_tenure_years, annual_interest_rate)


        # --- Display Results ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Your Credit Profile (Simulated)")
            st.metric(label="CreditVision AI Score", value=f"{civil_score} / {CIVIL_SCORE_MAX}",
                      help=f"Based on alternative data signals for a {job_type}. Higher is better.")
            
            st.caption("Alternative Data Features Considered (Illustrative):")
            # Display alt_data features in a more readable way
            alt_data_df = pd.DataFrame(alt_data.items(), columns=['Feature', 'Normalized Score (0-1)'])
            st.dataframe(alt_data_df, use_container_width=True, hide_index=True)


        with col2:
            st.subheader("💰 Estimated Loan Eligibility")
            if max_loan > 0 and emi > 0:
                st.metric(label="Max Home Loan You May Qualify For", value=f"₹ {max_loan:,.0f}")
                st.metric(label=f"Estimated EMI (for {loan_tenure_years} years)", value=f"₹ {emi:,.0f}/month")
                st.write(f"At an estimated annual interest rate of: {annual_interest_rate*100:.2f}% p.a.")
            else:
                st.warning("Based on the inputs, it's unlikely to qualify for a significant loan amount with standard lenders. Consider exploring micro-finance options or ways to improve your financial profile.")
        
        st.markdown("---")

        if max_loan > 0 and bank_options:
            st.subheader("🏦 Recommended Home Loan Options (Simulated)")
            for i, option in enumerate(bank_options):
                with st.expander(f"{option['bank_name']} - {option['loan_product_name']} (Est. EMI: ₹{option['estimated_emi']:,.0f})", expanded=i==0):
                    st.markdown(f"**Offered Loan Amount:** ₹ {option['offered_loan_amount']:,.0f}")
                    st.markdown(f"**Interest Rate:** {option['interest_rate_pa']:.2f}% p.a.")
                    st.markdown(f"**Tenure:** {option['tenure_years']} years")
                    st.markdown(f"**Estimated EMI:** ₹ {option['estimated_emi']:,.0f}")
                    st.markdown(f"*Notes:* _{option['notes']}_")
            st.markdown("---")
        elif max_loan > 0:
             st.info("Could not find specific bank package recommendations at this moment, but your general eligibility is noted above.")


        st.subheader("💬 AI-Powered Explanation (Simulated)")
        explanation_text = generate_ai_explanation(civil_score, max_loan, emi, bank_options, job_type, monthly_income)
        st.text_area("Loan Eligibility & Recommendation Logic:", value=explanation_text, height=400, 
                     help="This explanation outlines how your profile was assessed and why certain recommendations are made.")
        
        st.download_button(
            label="📥 Download Loan Summary (Text)",
            data=explanation_text,
            file_name=f"CreditVisionAI_LoanSummary_{monthly_income}_{job_type.replace(' ','')}.txt",
            mime="text/plain"
        )
        st.markdown("---")

else:
    st.info("Please enter your details in the sidebar and click 'Get My Loan Insights' to proceed.")
    st.markdown
