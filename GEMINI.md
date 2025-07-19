# GEMINI.md - Constitución Técnica del Proyecto

Este documento establece las reglas, protocolos y flujos de trabajo obligatorios para el desarrollo de este proyecto. Es la fuente de verdad y el documento de mayor jerarquía.

## 1. Reglas Fundamentales

1.  **Jerarquía de Documentación:**
    *   `GEMINI.md`: Constitución y reglas inmutables.
    *   `ai_docs/master_plan.md`: Plan de desarrollo completo y cronológico.
    *   `ai_docs/tasks/[nombre].md`: Tareas individuales y específicas.
    *   `ai_docs/dev_log.md`: Bitácora de cada acción.

2.  **Prohibido Asumir:** Ningún cambio, refactorización o implementación se basará en suposiciones. Toda acción debe estar respaldada por una investigación y validación externa.

3.  **Validación Externa Obligatoria:** Antes de cualquier modificación de código, se debe realizar una búsqueda en Google para validar el enfoque, consultar documentación oficial, buscar soluciones en repositorios (GitHub) y foros (Stack Overflow, etc.). Las referencias deben ser citadas en la bitácora.

4.  **Actualización de Bitácora:** La bitácora (`ai_docs/dev_log.md`) debe ser actualizada **antes y después** de cada acción significativa. Este es un registro inmutable; las entradas solo deben agregarse cronológicamente y nunca deben ser modificadas o eliminadas. Se registrará el timestamp, el agente/ingeniero, la acción realizada y las referencias consultadas.

5.  **Trazabilidad Total:** Cada tarea debe tener un archivo de seguimiento en `ai_docs/tasks/` con una lista de verificación (`✓` para completado).

6.  **Memoria Persistente:** Después de cada investigación, conclusión o avance significativo, se debe actualizar la memoria interna para registrar el nuevo dato, descubrimiento, investigación o hito.

## 2. Flujo de Trabajo

1.  **Análisis y Planificación:**
    *   Comprender los objetivos del proyecto revisando `README.md` y `ai_docs`.
    *   Crear/actualizar el `master_plan.md` con los pasos a seguir.
    *   Crear archivos de tareas individuales en `ai_docs/tasks/`.

2.  **Ejecución de Tareas:**
    *   **Actualizar Bitácora (Inicio):** Registrar la tarea a punto de iniciar.
    *   **Investigación y Validación:** Realizar búsquedas en Google para validar el enfoque.
    *   **Implementación:** Realizar los cambios en el código.
    *   **Actualizar Bitácora (Fin):** Registrar la acción completada, los resultados y las referencias.
    *   **Actualizar Tarea:** Marcar la tarea como completada (`✓`) en su archivo correspondiente y añadir un resumen.

3.  **Verificación y Control de Calidad:**
    *   Revisar el código en busca de bugs o errores.
    *   Validar los hallazgos con investigación externa.
    *   Realizar una auditoría documental para asegurar que `GEMINI.md`, `master_plan.md`, tareas y bitácora estén sincronizados.
    *   No realizar despliegues ni implementaciones sin confirmación explícita del usuario.

## 3. Stack Tecnológico y Arquitectura

*   **Entorno Virtual:** El desarrollo debe realizarse dentro de un entorno virtual `venv`.
*   **Gestor de Paquetes:** Se debe utilizar `pip3` para la instalación de dependencias de Python.
*   **Frontend:** Streamlit, HTML/CSS/JS
*   **Backend:** Python (Flask/App.py)
*   **Base de Datos:** Por definir (actualmente parece ser un sistema de archivos o una base de datos simple).
*   **Lenguajes:** Python, JavaScript, HTML, CSS.

## 4. Protocolos de Algoritmos

*   Cualquier nuevo algoritmo o lógica compleja debe ser documentado en un archivo de tarea y validado mediante investigación antes de su implementación.
*   Se debe priorizar el código limpio, modular y bien documentado.

## 5. Sistema de Seguimiento

*   **Directorio de Tareas:** `ai_docs/tasks/`
*   **Bitácora Central:** `ai_docs/dev_log.md`
*   **Plan Maestro:** `ai_docs/master_plan.md`
