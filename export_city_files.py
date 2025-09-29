import pandas as pd
from fpdf import FPDF

def generate_ghg_excel(city_name, city_data):
    ghg_data = city_data.get("GHG", {})
    if not ghg_data:
        # Option 1: Create a DataFrame with a message
        df = pd.DataFrame([{"message": "No GHG data available"}])
    else:
        df = pd.DataFrame([ghg_data])
    file_name = f"{city_name}_ghg_inventory.xlsx"
    df.to_excel(file_name, index=False)
    return file_name

def generate_ghg_pdf(city_name, city_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"{city_name} - GHG Inventory", ln=True, align='C')
    pdf.ln(10)
    ghg_data = city_data.get("GHG", {})
    if not ghg_data:
        pdf.cell(200, 10, txt="No GHG data available", ln=True)
    else:
        for k, v in ghg_data.items():
            pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    file_name = f"{city_name}_ghg_inventory.pdf"
    pdf.output(file_name)
    return file_name
