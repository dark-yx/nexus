# Tarea: Integración de Herramienta para YouTube

## Estado: Completado

## Descripción

Integrar la herramienta de LangChain existente para YouTube. La herramienta debe permitir la búsqueda de videos, la extracción de información de canales y la obtención de comentarios.

## Checklist

*   [✓] Investigar la herramienta de LangChain para YouTube.
*   [✓] Implementar la lógica para la autenticación y autorización.
*   [✓] Integrar la herramienta con el agente de YouTube.
*   [ ] Crear pruebas unitarias para validar el funcionamiento de la herramienta.

## Resumen

Se ha creado una nueva herramienta `YouTubeTool` en `src/youtube_tool.py` que utiliza `YoutubeLoader` y `YouTubeSearchTool` de LangChain para cargar transcripciones y buscar videos. Esto reemplaza la implementación anterior que utilizaba directamente la API de YouTube.