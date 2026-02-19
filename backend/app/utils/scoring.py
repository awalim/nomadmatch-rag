# backend/app/utils/scoring.py

def calculate_tax_score(metadata: dict) -> float:
    """
    Calcula la puntuación fiscal (0-10) basada en los metadatos.
    Reglas aproximadas del documento:
      - Tax_Benefit_Years (si existe) puede ser "10" para exención total, etc.
      - Special_Tax_Rate_Percent: porcentaje de impuesto especial.
    Por simplicidad, usamos valores predeterminados según el país.
    """
    # Extraer campos relevantes
    tax_rate = metadata.get("Tax_Rate_Standard_Pct")
    tax_benefits = metadata.get("Tax_Benefits_Premium", "")
    
    # Lógica simple basada en el nivel de impuestos
    tax_level = metadata.get("Tax_Level", "").lower()
    if "very low" in tax_level:
        return 9.5
    elif "low" in tax_level:
        return 8.0
    elif "moderate" in tax_level:
        return 6.0
    elif "high" in tax_level:
        return 3.0
    elif "very high" in tax_level:
        return 1.0
    else:
        return 5.0  # valor por defecto

def calculate_visa_score(metadata: dict) -> float:
    """
    Calcula la puntuación de visado (0-10) según:
      - Digital_Nomad_Visa (Yes/No)
      - EU_NonEU_Intl (0-3)
      - Visa_Duration, etc.
    """
    visa_available = metadata.get("Digital_Nomad_Visa", "").lower()
    if visa_available == "yes":
        base = 8.0
        # Ajustar por duración
        duration = metadata.get("Visa_Duration", "").lower()
        if "long-term" in duration:
            base += 1.5
        elif "medium-term" in duration:
            base += 0.5
        elif "short-term" in duration:
            base -= 0.5
        return min(base, 10.0)
    else:
        return 2.0  # sin visa específica

def overall_score(metadata: dict) -> float:
    """
    Calcula la puntuación global según la fórmula del documento:
        Overall_Score = Tax_Score * 0.6 + Visa_Score * 0.4
    """
    tax_score = calculate_tax_score(metadata)
    visa_score = calculate_visa_score(metadata)
    return round(tax_score * 0.6 + visa_score * 0.4, 2)
