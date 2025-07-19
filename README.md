# NexusMetriks

## Descripción General
NexusMetriks es una plataforma SaaS AI-native para la gestión, análisis, optimización y automatización de marketing digital, diseñada para agencias y empresas que buscan colaboración avanzada y ejecución automatizada. Orquestada por **Derek AI**, un agente cognitivo central, la plataforma integra equipos de agentes autónomos, colaboración humano-IA, y soporte multicanal (web, WhatsApp, Telegram, voz, video, etc.).

## Características Principales
- Orquestación multiagente basada en LangGraph y LangChain
- Colaboración en tiempo real: chats, canales, paneles, tareas y flujos de trabajo
- Ejecución automatizada por agentes (Derek AI y equipos especialistas)
- UI/UX completamente agentificada y personalizable
- Soporte multimodal: texto, voz, video, pizarras y archivos
- Memoria empresarial (RAG, Vector DB, historial de actividades)
- Integración con WhatsApp, Telegram, email, llamadas, CRMs y más
- Seguridad avanzada, multi-tenancy y control granular de permisos

## Arquitectura General
- **Backend:** Python 3.13+, Flask 3.x, FastAPI, LangGraph, LangChain, WebSockets
- **Frontend:** HTML5, CSS3, Bootstrap 6, JavaScript ES2025+, React/Web Components
- **IA y Voz:** OpenAI GPT-4o, Gemini 2.5, Llama 3, Whisper v4, Deepgram, ElevenLabs
- **Vector DB:** ChromaDB, Pinecone, Qdrant, pgvector
- **Integraciones:** WhatsApp API (Baileys), Telegram Bot API, Twilio, WebRTC
- **Despliegue:** Docker, Kubernetes, CI/CD

## Requisitos
- Python Version 3.13+
- Node.js (para microservicios de WhatsApp y WebSockets)
- Docker (opcional, recomendado para producción)

## Instalación y Ejecución Local
1. Instala Python 3.13+ (recomendado usar Pyenv)
   ```bash
   pyenv install 3.13.0
   pyenv global 3.13.0
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source ./venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta la aplicación Flask:
   ```bash
   python src/app.py
   ```

## Colaboración y Trabajo en Equipo
- Crea espacios de trabajo, canales y paneles colaborativos para equipos de marketing, comercial y gerencial.
- Trabaja en tiempo real con otros miembros y agentes, asigna tareas, planifica campañas y ejecuta acciones automatizadas.
- Todo el historial de actividades, decisiones y ejecuciones queda registrado y es auditable.
- Recibe notificaciones inteligentes por chat, email, WhatsApp o llamadas.

## Contribuciones
¡Las contribuciones son bienvenidas! Por favor, abre un issue o pull request para sugerencias, mejoras o reportar problemas.

## Licencia
[MIT](LICENSE)