
from .tools import generar_embudo_grafico, generar_resumen_embudo
import traceback

def analizar_embudo(data, user_id, db):
    print(f"[DEBUG funnel_agent/main.py] Iniciando analizar_embudo con datos: {data}, user_id: {user_id}")
    try:
        embudo_data = {
            'Clics': int(data.get('clics', 0)),
            'Contactos': int(data.get('contactos', 0)),
            'Leads': int(data.get('leads_validos', 0)),
            'SQL': int(data.get('sql', 0)),
            'Negocios': int(data.get('lead_con_negocios', 0)),
            'Clientes': int(data.get('clientes', 0))
        }
        print(f"[DEBUG funnel_agent/main.py] embudo_data procesado: {embudo_data}")

        print("[DEBUG funnel_agent/main.py] Llamando a generar_embudo_grafico...")
        chart_data = generar_embudo_grafico(embudo_data)
        print(f"[DEBUG funnel_agent/main.py] generar_embudo_grafico devolvió: {'Datos de gráfico presentes' if chart_data else 'Datos de gráfico vacíos o None'}")

        print("[DEBUG funnel_agent/main.py] Llamando a generar_resumen_embudo...")
        resumen = generar_resumen_embudo(embudo_data, user_id, db)
        print(f"[DEBUG funnel_agent/main.py] generar_resumen_embudo devolvió: {'Resumen presente' if resumen else 'Resumen vacío o None'}")

        print(f"[DEBUG funnel_agent/main.py] analizar_embudo va a retornar chart_data y resumen.")
        return chart_data, resumen
    except Exception as e:
        print(f"[ERROR funnel_agent/main.py] Error en analizar_embudo: {str(e)}")
        print(f"[ERROR funnel_agent/main.py] Traceback: {traceback.format_exc()}")
        # Devolver algo que no cause un error de desempaquetado en app.py en caso de fallo aquí
        return None, f"Error interno en analizar_embudo: {str(e)}"
