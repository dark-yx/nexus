# Tarea: Creación de Herramienta Personalizada para Meta Ads

## Estado: En Progreso

## Descripción

Crear una herramienta de LangChain personalizada para interactuar con la API de Marketing de Meta (Facebook Ads). La herramienta debe permitir la creación, gestión y optimización de campañas, así como la extracción de datos para análisis.

## Checklist

*   [✓] Investigar la API de Marketing de Meta y su SDK de Python.
*   [✓] Diseñar la estructura de la herramienta, incluyendo los métodos necesarios.
*   [✓] Implementar la lógica para la autenticación y autorización.
*   [✓] Desarrollar los métodos para la gestión de campañas, conjuntos de anuncios y anuncios.
*   [✓] Implementar la funcionalidad para la extracción de informes de rendimiento.
*   [ ] Crear pruebas unitarias para validar el funcionamiento de la herramienta.
*   [ ] Integrar la herramienta con el agente de Meta Ads.

## Resumen

Se ha refactorizado y mejorado la herramienta de Meta Ads. Todas las herramientas ahora devuelven una cadena JSON para una mejor legibilidad. Se han añadido las siguientes herramientas nuevas: `CreateCampaignTool` para crear nuevas campañas y `UpdateCampaignStatusTool` para actualizar su estado. El siguiente paso es crear pruebas unitarias para validar la funcionalidad completa de la herramienta.
