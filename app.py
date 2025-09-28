import streamlit as st
import pandas as pd

# Data for England, Wales, Northern Ireland
england_nw_data = {
    "Region": ["England/Wales/Northern Ireland"]*4,
    "Band": ["Personal Allowance", "Basic Rate", "Higher Rate", "Additional Rate"],
    "Income Range (Â£)": ["Up to 12,570", "12,571 to 50,270", "50,271 to 125,140", "Over 125,140"],
    "Tax Rate (%)": [0, 20, 40, 45]
}

# Data for Scotland
scotland_data = {
    "Region": ["Scotland"]*7,
    "Band": ["Personal Allowance", "Starter Rate", "Basic Rate", "Intermediate Rate",
             "Higher Rate", "Advanced Rate", "Top Rate"],
    "Income Range (Â£)": ["Up to 12,570", "12,571 to 15,397", "15,398 to 27,491",
                         "27,492 to 43,662", "43,663 to 75,000", "75,001 to 125,140", "Over 125,140"],
    "Tax Rate (%)": [0, 19, 20, 21, 42, 45, 48]
}

# Combine the data
df = pd.concat([pd.DataFrame(england_nw_data), pd.DataFrame(scotland_data)], ignore_index=True)


def calculate_gift_aid_tax(annual_earnings, gift_aid_amount, region, tax_bands_df):
    """
    Calculates the tax relief due to Gift Aid based on annual earnings, gift aid, and region.

    Args:
        annual_earnings (float): The user's annual earnings.
        gift_aid_amount (float): The amount of gift aid donated.
        region (str): The user's region ('UK (England, Wales, Northern Ireland)' or 'Scotland').
        tax_bands_df (pd.DataFrame): DataFrame containing tax band information.

    Returns:
        float: The calculated tax relief amount.
    """
    # Adjust region name to match DataFrame
    if region == 'UK (England, Wales, Northern Ireland)':
        region_filter = 'England/Wales/Northern Ireland'
    else:
        region_filter = 'Scotland'

    region_df = tax_bands_df[tax_bands_df['Region'] == region_filter].copy()

    # Function to calculate tax for a given income
    def calculate_tax(income, tax_df):
        tax_due = 0
        remaining_income = income

        for index, row in tax_df.iterrows():
            income_range = row['Income Range (Â£)']
            tax_rate = row['Tax Rate (%)'] / 100.0

            # Parse income range
            if 'Up to' in income_range:
                upper_bound = float(income_range.replace('Up to ', '').replace(',', ''))
                lower_bound = 0
            elif 'Over' in income_range:
                lower_bound = float(income_range.replace('Over ', '').replace(',', ''))
                upper_bound = float('inf')
            else:
                lower_lower, upper_bound = map(float, income_range.replace(',', '').split(' to '))
                lower_bound = lower_lower - 1 # Adjust for the lower bound being inclusive


            band_taxable_amount = 0
            if remaining_income > lower_bound:
                band_taxable_amount = min(remaining_income - lower_bound, upper_bound - lower_bound)
                if band_taxable_amount < 0:
                    band_taxable_amount = 0

            tax_due += band_taxable_amount * tax_rate
            if remaining_income <= upper_bound:
                 break # Stop if all remaining income is within or below the current band


        return tax_due

    # Calculate tax on original earnings
    tax_on_original_earnings = calculate_tax(annual_earnings, region_df)

    # Calculate tax on adjusted earnings after Gift Aid (grossed up)
    grossed_up_gift_aid = gift_aid_amount * 1.25
    adjusted_earnings = annual_earnings - grossed_up_gift_aid
    tax_on_adjusted_earnings = calculate_tax(adjusted_earnings, region_df)

    # Calculate tax relief
    tax_relief = tax_on_original_earnings - tax_on_adjusted_earnings

    return tax_relief


st.title("Gift Aid Tax Calculator")

annual_earnings = st.number_input("Annual Earnings (Â£)", min_value=0.0, value=0.0)
gift_aid_amount = st.number_input("Gift Aid Amount (Â£)", min_value=0.0, value=0.0)
region = st.radio("Region", ["UK (England, Wales, Northern Ireland)", "Scotland"])

if st.button("Calculate Tax Relief"):
    tax_relief = calculate_gift_aid_tax(annual_earnings, gift_aid_amount, region, df)
    st.info(f"Your calculated tax relief is Â£{tax_relief:,.2f}")
