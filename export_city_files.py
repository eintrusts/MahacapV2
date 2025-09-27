import pandas as pd
from fpdf import FPDF

def generate_ghg_excel(city_name, city_data):
    df = pd.DataFrame([city_data["GHG"]])
    file_name = f"{city_name}_ghg_inventory.xlsx"
    df.to_excel(file_name, index=False)
    return file_name

def generate_ghg_pdf(city_name, city_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"{city_name} - GHG Inventory", ln=True, align='C')
    pdf.ln(10)
    for k, v in city_data["GHG"].items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    file_name = f"{city_name}_ghg_inventory.pdf"
    pdf.output(file_name)
    return file_name
