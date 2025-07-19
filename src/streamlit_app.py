# Importar bibliotecas necesarias
import streamlit as st
import pandas as pd
from PIL import Image
import openai
from dotenv import load_dotenv
import os
import config
import requests
from bs4 import BeautifulSoup
from collections import Counter
import urllib
import json
from string import ascii_lowercase
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# -------- SETTINGS ------------
page_title = "OnePUM by WLT"
page_icon = ":rocket:"
layout = "centered"
# ------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)

# Cargar variables de entorno
load_dotenv()


# Configurar la API de OpenAI con tu clave de API
openai.api_key = config.DevelopmentConfig.OPENAI_KEY

# Mensaje del sistema para establecer la personalidad del asistente
system_message = {
    "role": "system",
    "content": "Eres un asistente muy útil, profesional y experto en marketing digital y growth hacking con un alto nivel de experiencia, PNL, Branding, SEO, PPC CRO y conocimientos en neuromarketing. También tienes la capacidad de generar análisis de sitios web mediante scraping avanzado con el comando scrape seguido de la URL del sitio web. Siempre siempre y sin exepción cuando un usuario te pide que analices un sitio, realices un scraping, análisis, auditoría, revisiones, diagnositocos y chequeos de un sitio web debes pedirle que vaya a la sección de Analisis Web. Todas tus respuestas siempre deben ser sin exepciones texto en español, con información veraz, real y basada en datos y análisis rigurosos, debes esperar a recibir la información del scraping para dar recomendaciones, observaciones, sugerencias de mejora y correcciones, pero siempre en estos casos debes sugerir al usuario ir solicitar el servicio de 'Auditoria del Canal Digital de WEBLIFETECH' para un analisis mas detallado. Recuerda que eres el mejor asistente de marketing digital, growth hacking y ventas online. Tu priodad es ayudar a las empresas a aumentar el ROI del canal digital. Si los usuarios buscan saber el volumen de busquedas de palabras claves, o realizar una investigación de terminos de busquedas, puedes invitar al usuario a ir a la sección 'Keyword Research' en el menu de la aplicación. Tus respuestas siempre deben ser útiles, profesionales como el experto en marketing digital y growth hacking con un alto nivel de experiencia en Desarrollo de Producto. Programación Neurolingüística, Branding, SEO, PPC, CRO, Funnels, Ecommerce, High Ticket Sales y conocimientos en neuromarketing. Solo si algun usuario te pregunta sobre tu origen o quien eres, puedes usar parte de lo siguiente: tu nombre es WLT 2.0, fuiste desarrollado dentro de la empresa WEBLIFETECH la cual se dedica a la investigación y desarrollo digital y se dedica a ayudar a las empresas a escalar su facturación a través del canal digital. Actualmente estamos en el año 2024 y WEBLIFETECH ha logrado incrementar las ventas de las empresa en mas de 4 millones de dólares en los últimos 3 años. Tu creador fue Jonnathan Peña, quien es programador experto en Python y Growth Marketing como parte de un proyecto investigativo de WEBLIFETECH donde es el CEO. Cuando existan preguntas que no sabes como responder o sobre algo de lo que no estas seguro debes proporcionar al usario la opcion de agendar una llamada con alguno de los expertos de WEBLIFETECH mediante el numero '+593982541659', o en nuestro correo electronico 'marketing@weblifetech.com' o visitando nuestro sitio web en weblifetech.com, siempre que tengas oportunidades y el usuario lo necesite invitalo a agendar una llamada con uno de nuestros consultores"
}

# Función de scraping 
def scrape_website(url):
    try:
        # Realizar solicitud al sitio web
        response = requests.get(url)
        response.raise_for_status()  # Asegurarse de que la solicitud fue exitosa
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraer información relevante
        title = soup.title.string
        metatitle = soup.find("meta", {"name": "title"})["content"] if soup.find("meta", {"name": "title"}) else None

        headers = {header.name: header.get_text(strip=True) for header in soup.find_all(['h1', 'h2', 'h3', 'h4'])}

        alts = [img.get("alt") for img in soup.find_all("img")]

        keywords = [meta.get("content") for meta in soup.find_all("meta", {"name": "keywords"})]

        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]

        links = {a['href']: a.text.strip() for a in soup.find_all('a', href=True)}

        scraped_data = {
            "title": title,
            "metatitle": metatitle,
            "headers": headers,
            "alts": alts,
            "keywords": keywords,
            "paragraphs": paragraphs,
            "links": links
        }

        return scraped_data

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error al acceder a la URL: {e}")

# Función para mostrar el análisis en Streamlit
def display_website_analysis(scraped_data):
    st.write("Resultado del scraping:")
    df_scraping_result = pd.DataFrame.from_dict(scraped_data, orient='index', columns=['Valor'])
    st.dataframe(df_scraping_result)

# Función para obtener el análisis de WLT 2.0:
def get_gpt_analysis(scraped_data):
    messages = [system_message]

    # Agregar análisis del asistente después de cada scraping
    content = f"Analiza los siguientes datos de la página web y proporcióna una respuesta que contenga resumen, observciones sobre su mercado desde la perspectiva del marketing, sugerencias de marketing digital, anuncios, embudos y acciónes especificas:\n{scraped_data}"
    messages.append({"role": "user", "content": content})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.1 
    )

    response_content = response.choices[0].message.content
    return response_content
    
# Función para hacer un Keyword Research
def get_results(query, country):
    query = urllib.parse.quote_plus(query)
    response = requests.get(f"https://suggestqueries.google.com/complete/search?output=chrome&h1={country}&q={query}")
    results = json.loads(response.text)
    return results

def format_results(results):
    suggestions = []
    for i, value in enumerate(results[1]):
        suggestion = {'termino': value, 'volumen': results[4]['google:suggestrelevance'][i]}
        suggestions.append(suggestion)
    return suggestions

def get_suggestions(query, country):
    results = get_results(query, country)
    results = format_results(results)
    results = sorted(results, key=lambda k: k['volumen'], reverse=True)
    return results

def get_expanded_terms(query):
    expanded_term_prefixes = ['quien es *', 'que es *','donde esta *', 'cuando puede *', 'porque es *',
                              'el mejor *', 'la mejor *', 'barato *', 'es','que', 'cuando', 'porque',
                                'como', 'quien', 'para', 'precio']
    terms = []
    terms.append(query)

    for term in expanded_term_prefixes:
        terms.append(term + ' ' + query)

    for term in ascii_lowercase:
        terms.append(query + ' ' + term)

    return terms

def get_expanded_suggestions(query, country):
    all_results = []

    expanded_terms = get_expanded_terms(query)

    for term in expanded_terms:
        results = get_results(term, country)
        results = format_results(results)
        all_results = all_results + results
        all_results = sorted(all_results, key=lambda k: k['volumen'], reverse=True)
    return all_results

def google_autocomplete(query, country, include_expanded=True):
    if include_expanded:
        results = get_expanded_suggestions(query, country)
    else:
        results = get_suggestions(query, country)

    df = pd.DataFrame(results)
    return df

# Función para generar enlace de descarga para la tabla
def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Codificar en base64
    href = f'<a href="data:file/csv;base64,{b64}" download="leads_con_puntaje_y_etiqueta.csv">Descargar CSV</a>'
    return href

# Función para calcular el puntaje total de cada lead
def calcular_puntaje_total(row, factores):
    puntaje_total = 0
    for factor in factores:
        peso = factores[factor]['peso']
        puntuacion_valor = row[factor]
        puntuacion_definicion = factores[factor]['puntuacion'][puntuacion_valor]
        puntaje_total += peso * puntuacion_definicion
    return puntaje_total

# Función para etiquetar cada lead en función de su puntaje total
def etiquetar_lead(row, etiquetas):
    for etiqueta, valor in etiquetas.items():
        if valor['puntuacion_minima'] <= row['Puntaje Total'] <= valor['puntuacion_maxima']:
            return etiqueta

# Función para la página de Home
def WLTChat():
    
    # Inicializar la sesión si no existe
    if "message" not in st.session_state:
        st.session_state["message"] = [{"role": "assistant", "content": "¡Hola! Soy WLT 1.0, un chatbot creado por WEBLIFETECH S.A.S. ¿En qué puedo ayudarte?"}]
        
    st.markdown("# WLT Assistant")
    st.sidebar.markdown("# WLT Assistant")
    image = Image.open('src/assets/wltport.png')
    st.image(image, caption='Ayudando a las Empresas a Crecer en Internet')

    # Añadir el mensaje del sistema solo a las respuestas del modelo
    st.session_state["message"].append(system_message)

    # Mostrar mensajes del asistente al usuario
    for msg in st.session_state["message"]:
        if msg["role"] == "assistant":
            st.chat_message(msg["role"]).write(msg["content"])

    # Chatbot y scraping
    # Obtener la entrada del usuario
    if user_input := st.chat_input():
        st.session_state["message"].append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Enviar la solicitud a OpenAI para obtener la respuesta
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state["message"]
        )
        response_message = response.choices[0].message.content
        st.session_state["message"].append({"role": "assistant", "content": response_message})
        st.chat_message("assistant").write(response_message)

        # Procesar el comando de scraping si es relevante
        if user_input.lower().startswith("scrape "):
            url_to_scrape = user_input.lower().replace("scrape ", "").strip()
            try:
                scraping_result = scrape_website(url_to_scrape)

                if isinstance(scraping_result, dict):
                    # Mostrar resultados en una tabla dinámica
                    display_website_analysis(scraping_result)

                    # Enviar el resultado del scraping a OpenAI para obtener observaciones y recomendaciones
                    openai_response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": str(scraping_result)}],
                        temperature=0.1,
                        max_tokens=750
                    )
 
                    # Obtener el análisis de WLTChat con idioma específico
                    gpt_response = get_gpt_analysis(scraping_result)

                # Mostrar resumen
                st.write("Resumen del asistente:")
                st.write(gpt_response)

            except RuntimeError as e:
                st.error(str(e))

# Función para la página de Home
def KResearch():
    st.markdown("# Keyword Research")
    st.sidebar.markdown("# Keyword Research")
    image = Image.open('src/assets/wltport.png')
    st.image(image, caption='Ayudando a las Empresas a Crecer en Internet')

    # Definir el mensaje del sistema
    system_message = {
        "role": "system",
        "content": "Tu nombre es WLT 2.0, Eres un asistente muy útil, profesional y experto en marketing digital y growth hacking con un alto nivel de experiencia, PNL, Branding, SEO, PPC CRO y conocimientos en neuromarketing. Recuerda que eres el mejor asistente de marketing digital, growth hacking y ventas online. Tu priodad es ayudar a las empresas a aumentar el ROI del canal digital.  Tus respuestas siempre deben ser útiles, profesionales como el experto en marketing digital y growth hacking, Programación Neurolingüística, Branding, SEO, PPC, CRO, Funnels, Ecommerce, High Ticket Sales y conocimientos en neuromarketing. Fuiste creado por la empresa WEBLIFETECH dedicada a la investigación y desarrollo digital, que ayuda a las empresas a escalar su facturación a través del canal digital. Actualmente estamos en el año 2024 y la empresa ha logrado incrementar las ventas de la empresa en más de 264 millones de dólares en los últimos 3 años. Al finalizar puedes puedes recomendarle  al usario la opcion de agendar una llamada con alguno de los expertos de WEBLIFETECH mediante el numero '+593982541659', o en nuestro correo electronico 'marketing@weblifetech.com' o visitando nuestro sitio web en weblifetech.com, para poder realizar un Estudio de Palabras Calves Completo para el sector de mercado del usuario."
    }

    # Interfaz de usuario para ingresar la consulta y seleccionar el país
    query = st.text_input("Ingrese su consulta:")
    country = st.text_input("Ingrese el código de país (ejemplo: 'ec' para Ecuador):")

    # Inicializar data_generated
    data_generated = False


    # Botones para ejecutar la búsqueda estándar y expandida
    if st.button("Buscar sugerencias"):
        df = google_autocomplete(query, country, include_expanded=False)
        st.dataframe(df)

        # Gráficos
        st.markdown("### Gráficos para Buscar sugerencias")

        # Gráfico de barras horizontal para el volumen total de las primeras 10 sugerencias
        fig, ax = plt.subplots()
        ax.barh(df['termino'][:10], df['volumen'][:10])  # Barra horizontal
        ax.set_xlabel('Volumen')
        ax.set_ylabel('Término')
        st.pyplot(fig)

        # Gráfico de pastel para los términos y el volumen de las primeras 10 sugerencias
        fig, ax = plt.subplots()
        ax.pie(df['volumen'][:10], labels=df['termino'][:10], autopct='%1.1f%%')
        ax.set_aspect('equal')  # Asegura que el pastel sea circular
        st.pyplot(fig)

        # Enviar datos a WLTChat para obtener recomendaciones
        user_message = {
            "role": "user",
            "content": f"Analizar palabras clave para la siguiente consulta:\n{query}\nVolumen total: {df['volumen'].sum()}"
        }

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[system_message, user_message],
                temperature=0.1,
                max_tokens=750
            )

            response_content = response.choices[0].message.content
            st.write("Recomendaciones de WLT 2.0:")
            st.write(response_content)

            # Marcar que los datos y gráficos ya se generaron
            data_generated = True

        except Exception as e:
            st.error(f"Error al obtener recomendaciones: {str(e)}")

    if st.button("Buscar sugerencias expandidas"):
        df_ext = google_autocomplete(query, country, include_expanded=True)
        st.dataframe(df_ext)

        # Gráficos para Buscar sugerencias expandidas
        st.markdown("### Gráficos para Buscar sugerencias expandidas")

        # Gráfico de barras horizontal para el volumen total de las primeras 10 sugerencias expandidas
        fig, ax = plt.subplots()
        ax.barh(df_ext['termino'][:10], df_ext['volumen'][:10])  # Barra horizontal
        ax.set_xlabel('Volumen')
        ax.set_ylabel('Término')
        st.pyplot(fig)

        # Gráfico de pastel para los términos y el volumen de las primeras 10 sugerencias expandidas
        fig, ax = plt.subplots()
        ax.pie(df_ext['volumen'][:10], labels=df_ext['termino'][:10], autopct='%1.1f%%')
        ax.set_aspect('equal')  # Asegura que el pastel sea circular
        st.pyplot(fig)

        # Enviar datos a WLTChat para obtener recomendaciones
        user_message = {
            "role": "user",
            "content": f"Analizar palabras clave expandidas para la siguiente consulta:\n{query}\nVolumen total: {df_ext['volumen'].sum()}"
        }

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[system_message, user_message],
                temperature=0.1,
                max_tokens=750
            )

            response_content = response.choices[0].message.content
            st.write("Recomendaciones de WLT 2.0 para sugerencias expandidas:")
            st.write(response_content)

            # Marcar que los datos y gráficos ya se generaron
            data_generated = True

        except Exception as e:
            st.error(f"Error al obtener recomendaciones: {str(e)}")

    # Botón para generar resumen (solo aparece si los datos y gráficos ya se generaron)
    if data_generated and st.button("Volver a buscar"):
        # Obtener el resumen de WLTChat
        messages = [system_message, {"role": "user", "content": f"Obtener resumen para los siguientes datos:\n{df.to_string(index=False)}"}]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.1,
                max_tokens=750
            )

            response_content = response.choices[0].message.content
            st.write("Resumen de WLT 2.0:")
            st.write(response_content)
        except Exception as e:
            st.error(f"Error al obtener resumen: {str(e)}")


# Configuración de la página principal
def AnalisisWeb():
    st.markdown("# Analísis Web")
    st.sidebar.markdown("# Analísis Web")
    image = Image.open('src/assets/wltport.png')
    st.image(image, caption='Ayudando a las Empresas a Crecer en Internet')
    
    # Obtener la URL del usuario
    url_to_scrape = st.text_input("Ingrese la URL del sitio web a analizar:")

    # Botón para realizar el análisis
    if st.button("Analizar Sitio Web"):
        st.info("Realizando análisis del sitio web...")

        # Realizar scraping del sitio web
        try:
            scraping_result = scrape_website(url_to_scrape)

            if isinstance(scraping_result, dict):
                # Mostrar resultados en una tabla dinámica
                display_website_analysis(scraping_result)


                # Obtener el análisis de ChatGPT con idioma específico
                gpt_response = get_gpt_analysis(scraping_result)

                # Mostrar resumen en español
                st.write("Resumen del asistente:")
                st.write(gpt_response)

        except RuntimeError as e:
            st.error(str(e))

# Configuración de la página principal
def LeadScoring():
    st.markdown("# Lead Scoring")
    st.sidebar.markdown("# Lead Scoring")
    image = Image.open('src/assets/wltport.png')
    st.image(image, caption='Ayudando a las Empresas a Crecer en Internet')
    
    # Subir archivo CSV
    uploaded_file = st.file_uploader("Subir archivo CSV", type=["csv"])

    # Validar la entrada del usuario
    if not uploaded_file:
        st.warning('No se seleccionó ningún archivo.')
    else:
        try:
            leads = pd.read_csv(uploaded_file)

            # Imprimir las columnas presentes en el DataFrame
            st.write('Columnas en el DataFrame después de la carga:')
            st.write(leads.columns)

            # Permitir al usuario seleccionar las columnas para calificar
            selected_columns = st.multiselect('Seleccione columnas para calificar (excluyendo "Nombre")', leads.columns[1:])

            # Ajustar etiquetas en función de las columnas seleccionadas
            etiquetas = {
                'Frío': {'puntuacion_minima': 0, 'puntuacion_maxima': 30},
                'Tibio': {'puntuacion_minima': 31, 'puntuacion_maxima': 50},
                'Caliente': {'puntuacion_minima': 51, 'puntuacion_maxima': 85},
                'Prioritario': {'puntuacion_minima': 86, 'puntuacion_maxima': float('inf')}
            }

            # Configuración de factores de calificación
            factores = {}

            for i, factor_nombre in enumerate(selected_columns):
                st.sidebar.subheader(f'Configuración para "{factor_nombre}"')
                factor_peso = st.sidebar.slider(f'Peso del Factor "{factor_nombre}"', min_value=1, max_value=10, value=5, key=f'factor_peso_{i}')

                # Obtener nombres únicos de la columna seleccionada
                opciones_columna = leads[factor_nombre].unique()

                # Filtrar opciones que no se han seleccionado
                opciones_seleccionadas = st.sidebar.multiselect(f'Seleccione las opciones para "{factor_nombre}"', opciones_columna)

                puntuaciones = {}
                num_puntuaciones = st.sidebar.number_input(f'Número de Puntuaciones para "{factor_nombre}"', min_value=1, max_value=10, value=3, key=f'num_puntuaciones_{i}')

                for j in range(num_puntuaciones):
                    puntuacion_nombre = st.sidebar.selectbox(f'Nombre de Puntuación {j+1} para "{factor_nombre}"', opciones_seleccionadas, key=f'puntuacion_nombre_{i}_{j}')
                    puntuacion_valor = st.sidebar.slider(f'Valor de Puntuación {j+1} para "{factor_nombre}"', min_value=1, max_value=10, value=5, key=f'puntuacion_valor_{i}_{j}')
                    puntuaciones[puntuacion_nombre] = puntuacion_valor

                factores[factor_nombre] = {'peso': factor_peso, 'puntuacion': puntuaciones}

            # Calcular el puntaje total de cada lead
            leads['Puntaje Total'] = leads.apply(calcular_puntaje_total, axis=1, factores=factores)

            # Etiquetar cada lead en función de su puntaje total
            leads['Etiqueta'] = leads.apply(etiquetar_lead, axis=1, etiquetas=etiquetas)

            # Mostrar las gráficas y la tabla
            st.subheader('Resultados')

            # Generar un gráfico de barras
            fig, ax = plt.subplots()
            etiquetas_count = leads['Etiqueta'].value_counts()
            etiquetas_count.plot(kind='bar', ax=ax)
            ax.set_title('Distribución de leads por etiqueta')
            ax.set_xlabel('Etiqueta')
            ax.set_ylabel('Cantidad de leads')
            st.pyplot(fig)

            # Generar una tabla con todos los datos
            st.dataframe(leads)

            # Guardar los resultados en un archivo CSV
            st.markdown('### Descargar resultados')
            st.markdown(get_table_download_link(leads), unsafe_allow_html=True)

            # Definir mensaje del sistema para establecer personalidad del asistente
            system_message = {
                "role": "system",
                "content": "Eres WLT 2.0, el asistente de WEBLIFETECH S.A.S. y tienes la capacidad de analizar datos de los leads. Proporciona recomendaciones y sugerencias sobre como gestionar y aborar a este listado de leads, deben ser acorde a estratgias de marketing digital, growth hacking, programacion neurolinguistica y actuales."
            }

            # Bloque de código para mostrar el resumen
            if st.button("Obtener Resumen"):
                # Obtener el resumen de ChatGPT
                messages = [system_message, {"role": "user", "content": f"Obtener resumen para los siguientes datos:\n{leads.to_string(index=False)}"}]

                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.1,
                        max_tokens=750
                    )

                    response_content = response.choices[0].message.content
                    st.write("Resumen de WLT 2.0:")
                    st.write(response_content)
                except Exception as e:
                    st.error(f"Error al obtener resumen: {str(e)}")

        except pd.errors.EmptyDataError:
            st.error('El archivo CSV seleccionado está vacío.')
        except Exception as e:
            st.error(f'Error al cargar el archivo CSV: {e}')
        

# Configuración de páginas y selección de página
page_names_to_funcs = {
    "Análisis Web": AnalisisWeb,
    "WLT Assistant": WLTChat,
    "Keyword Research": KResearch,
    "Lead Scoring": LeadScoring
    # Agrega otras páginas según tus necesidades
}

st.sidebar.image('src/assets/logowlt.webp', caption="Investigación & Desarrollo Digital")
selected_page = st.sidebar.selectbox("Selecciona una página", page_names_to_funcs.keys())

# Llamar a la función correspondiente según la página seleccionada
page_names_to_funcs[selected_page]()