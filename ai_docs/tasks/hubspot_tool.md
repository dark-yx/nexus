# Tarea: Creación de Herramienta Personalizada para HubSpot

## Estado: En Progreso

## Descripción

Crear una herramienta de LangChain personalizada para interactuar con la API de HubSpot. La herramienta debe permitir la creación, gestión y actualización de contactos, empresas y negocios, así como la extracción de datos para análisis.

## Checklist

*   [✓] Investigar la API de HubSpot y su cliente de Python.
*   [✓] Diseñar la estructura de la herramienta, incluyendo los métodos necesarios.
*   [✓] Implementar la lógica para la autenticación y autorización.
*   [✓] Desarrollar los métodos para la gestión de contactos, empresas y negocios.
*   [✓] Implementar la funcionalidad para la extracción de informes de rendimiento.
*   [ ] Crear pruebas unitarias para validar el funcionamiento de la herramienta.
*   [ ] Integrar la herramienta con el agente de HubSpot.

## Resumen

Se ha refactorizado y mejorado la herramienta de HubSpot. Todas las herramientas ahora devuelven una cadena JSON para una mejor legibilidad. Se han añadido las siguientes herramientas nuevas: `GetCompaniesTool` para obtener una lista de empresas, `UpdateCompanyTool` para actualizar empresas y `UpdateDealTool` para actualizar negocios. El siguiente paso es crear pruebas unitarias para validar la funcionalidad completa de la herramienta.
