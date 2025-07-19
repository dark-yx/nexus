# Master Plan de Desarrollo - Nexus AI

Este documento describe el plan de desarrollo completo y cronológico del proyecto, desde su concepción hasta el estado actual y los pasos futuros.

## Fase 0: Establecimiento de la Gobernanza del Proyecto (Completada)

*   [✓] Creación de `GEMINI.md` con las reglas y protocolos de desarrollo.
*   [✓] Creación de `ai_docs/master_plan.md` para la planificación y seguimiento.
*   [✓] Creación de `ai_docs/dev_log.md` para la bitácora de desarrollo.
*   [✓] Creación del directorio `ai_docs/tasks/` para el seguimiento de tareas individuales.

## Fase 1: Refactorización y Robustecimiento de Herramientas (En Progreso)

*   [✓] **Investigación y Validación Externa (Completada):**
    *   [✓] Se confirmó mediante investigación que no existen herramientas pre-construidas de LangChain para las APIs de Google Ads, GA4, GSC, HubSpot y Meta Ads.
    *   [✓] Se validó que el enfoque de crear **herramientas personalizadas** es la mejor práctica recomendada por la comunidad de LangChain.
    *   [✓] No se encontraron plataformas MCP (Multi-Channel Platform) que ofrezcan una alternativa viable a las integraciones directas con las APIs.
*   [ ] **Implementación de Autenticación Robusta (Pendiente):**
    *   [ ] **Google APIs (Ads, GA4, GSC):** Refactorizar la autenticación para implementar un flujo OAuth2 completo y seguro, permitiendo a los usuarios conectar sus propias cuentas.
    *   [ ] **HubSpot & Meta Ads:** Reemplazar la autenticación basada en tokens de entorno por un sistema de gestión de credenciales multi-usuario.
*   [ ] **Desarrollo Iterativo de Herramientas (Pendiente):**
    *   Para cada herramienta (`GoogleAds`, `GoogleAnalytics4`, `GoogleSearchConsole`, `HubSpot`, `MetaAds`):
        *   [ ] **Ampliación de Funcionalidad:** Implementar capacidades completas de CRUD (Crear, Leer, Actualizar, Eliminar) donde la API lo permita.
        *   [ ] **Visualización de Datos:** Añadir funciones para generar visualizaciones (tablas, gráficos) de los datos obtenidos.
        *   [ ] **Pruebas Unitarias:** Desarrollar un conjunto de pruebas exhaustivo para garantizar la fiabilidad de cada herramienta.
        *   [ ] **Refactorización:** Mejorar la calidad del código, la documentación y la gestión de errores.
*   [ ] **Finalización de la Refactorización (Pendiente):**
    *   [ ] Integrar las herramientas robustecidas en la arquitectura de agentes.
    *   [ ] Eliminar los módulos y scripts antiguos una vez que la nueva arquitectura esté completamente verificada.

## Fase 2: Sistema de Lead Scoring 360° (Pendiente)

*   [ ] **Agente de Procesamiento de Datos:**
    *   [ ] Capacidad para ingestar archivos CSV y Excel.
    *   [ ] Limpieza y normalización de datos.
    *   [ ] Identificación de entidades (nombre, empresa, cargo, etc.).
*   [ ] **Agente de Enriquecimiento de Datos:**
    *   [ ] Conexión con herramientas de búsqueda web (LangChain).
    *   [ ] Búsqueda de información adicional sobre leads (industria, tendencias, etc.).
*   [ ] **Agente de Calificación (Scoring):**
    *   [ ] Asignación de pesos y puntajes a los atributos de los leads.
    *   [ ] Generación de una calificación global.
*   [ ] **Agente de Personalización:**
    *   [ ] Generación de recomendaciones personalizadas por lead.
    *   [ ] Creación de un plan de comunicación.
    *   [ ] Redacción de un blog personalizado.
*   [ ] **Agente de Visualización:**
    *   [ ] Creación de gráficos y tablas para la visualización de datos.
*   [ ] **Interfaz de Usuario (CRM Agentificado):**
    *   [ ] Tabla de leads con filtros y búsqueda.
    *   [ ] Panel de control individual por lead.
    *   [ ] Funcionalidad para editar y agregar datos manualmente.

## Fase 3: Verificación y Despliegue (Pendiente)

*   [ ] **Pruebas de Integración:**
    *   [ ] Asegurar el correcto funcionamiento de todo el sistema multi-agente.
*   [ ] **Auditoría Documental:**
    *   [ ] Verificar que toda la documentación esté actualizada y sincronizada con el código final.
*   [ ] **Pruebas de Despliegue:**
    *   [ ] Realizar un despliegue de prueba en un entorno controlado.
*   [ ] **Ajustes Finales:**
    *   [ ] Corregir cualquier bug o error encontrado durante las pruebas.