from openai import OpenAI
import os
from typing import List, Dict, Any

# Configurar cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_premium_advice(user_query: str, results: List[Dict[str, Any]]) -> str:
    """
    Genera una respuesta en lenguaje natural usando los resultados premium.
    """
    if not results:
        return "No se encontraron datos premium para tu consulta."

    # Construir contexto con los 3 mejores resultados
    context = ""
    for i, res in enumerate(results[:3], 1):
        meta = res.get("metadata", {})
        context += f"\n--- Ciudad {i} ---\n"
        context += f"Ciudad: {meta.get('city', 'Desconocida')}, {meta.get('country', '')}\n"
        context += f"Visa nómada digital: {'Sí' if meta.get('Digital_Nomad_Visa') == 1 else 'No'}\n"
        context += f"Elegibilidad: {interpret_eu_non_eu(meta.get('EU_NonEU_Intl'))}\n"
        context += f"Años de beneficio fiscal: {meta.get('Tax_Benefit_Years', 'N/A')}\n"
        context += f"Tasa especial de impuestos: {meta.get('Special_Tax_Rate_Percent', 'N/A')}%\n"
        context += f"Ingreso mínimo requerido: {meta.get('Monthly_Income_Requirement_EUR', 'N/A')} EUR/mes\n"
        context += f"Estancia mínima: {meta.get('Min_Stay_Days', 'N/A')} días\n"
        context += f"Estancia máxima: {meta.get('Max_Stay_Months', 'N/A')} meses\n"
        context += f"Zona Schengen: {'Sí' if meta.get('Schengen_Area') == 1 else 'No'}\n"
        context += f"Puntuación fiscal: {meta.get('Tax_Score', 'N/A')}/10\n"
        context += f"Puntuación de visado: {meta.get('Visa_Score', 'N/A')}/10\n"
        context += f"Puntuación global: {meta.get('Overall_Score', 'N/A')}/10\n"

    prompt = f"""
Eres un asistente experto en nómadas digitales que ayuda a encontrar la mejor ciudad europea según sus preferencias.

El usuario pregunta: "{user_query}"

Aquí tienes información detallada de las ciudades más relevantes (ordenadas por relevancia semántica):
{context}

Con base en estos datos, redacta una respuesta útil, clara y en español. Incluye comparaciones entre ciudades si es relevante, destaca los puntos fuertes y menciona requisitos importantes (ingresos, duración, zona Schengen). No inventes datos que no estén en la información proporcionada. Sé conciso pero informativo.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asesor experto en visados y fiscalidad para nómadas digitales."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error al generar respuesta LLM: {e}")
        return "Lo siento, no pude generar una respuesta en este momento."

def interpret_eu_non_eu(value):
    """Convierte el código EU_NonEU_Intl a texto legible."""
    mapping = {
        0: "Solo ciudadanos UE/EEE/Suiza",
        1: "Ciudadanos de la UE y no UE",
        2: "Todos los países",
        3: "Solo no UE"
    }
    return mapping.get(value, "Información no disponible")
