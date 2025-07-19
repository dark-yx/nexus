from .context_agent import ContextAgent, AgentState
from openai import OpenAI
from db import save_conversation
import json
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

class ChatCoordinator:
    def __init__(self, db_connection):
        self.context_agent = ContextAgent(db_connection)
        self.client = OpenAI()
        self.db = db_connection
        self.llm = ChatOpenAI(model="gpt-4")
        self.graph = self._build_graph()
        
    def _build_graph(self):
        """Construye el grafo de LangGraph para el manejo de chat"""
        # Definir el nodo de procesamiento de mensajes
        def process_message(state: AgentState) -> AgentState:
            messages = state["messages"]
            context = state["context"]
            user_id = state["user_id"]
            
            # Obtener el último mensaje del usuario
            last_message = messages[-1].content if messages else ""
            
            # Obtener el contexto procesado
            context_info = self.context_agent.process_context(user_id, "/")
            
            # Construir el mensaje del sistema
            system_message = (
                "Eres DEREK, un asistente de marketing digital especializado. "
                "Tienes acceso al siguiente contexto de la plataforma:\n"
                f"{context_info}\n"
                "Usa esta información para proporcionar respuestas precisas y contextualizadas."
            )
            
            # Preparar los mensajes para la API
            chat_messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": last_message}
            ]
            
            try:
                # Obtener respuesta de GPT-4
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=chat_messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                assistant_response = response.choices[0].message.content
                
                # Guardar la conversación
                save_conversation(self.db, user_id, "DEREK", last_message, assistant_response)
                
                # Actualizar el estado
                messages.append(AIMessage(content=assistant_response))
                
            except Exception as e:
                error_message = f"Error al procesar el mensaje: {str(e)}"
                save_conversation(self.db, user_id, "DEREK", last_message, error_message)
                messages.append(AIMessage(content=error_message))
            
            return {"messages": messages, "context": context, "user_id": user_id}
        
        # Crear el grafo
        workflow = StateGraph(AgentState)
        
        # Agregar nodos
        workflow.add_node("process_message", process_message)
        
        # Definir el flujo
        workflow.add_edge("process_message", END)
        
        # Compilar el grafo
        return workflow.compile()
        
    def process_message(self, message, user_id, current_path):
        """Procesa el mensaje del usuario y genera una respuesta contextualizada"""
        # Crear estado inicial
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "context": self.context_agent.get_current_context(),
            "user_id": user_id
        }
        
        # Ejecutar el grafo
        final_state = self.graph.invoke(initial_state)
        
        # Obtener la última respuesta del asistente
        last_message = final_state["messages"][-1]
        return last_message.content
        
    def get_tool_specific_response(self, tool_name, query, user_id):
        """Obtiene una respuesta específica para una herramienta"""
        # Aquí se pueden agregar lógicas específicas para cada herramienta
        tool_handlers = {
            'Website Analysis': self._handle_website_analysis,
            'SEO Performance Analysis': self._handle_seo_analysis,
            'Traffic Analysis': self._handle_traffic_analysis
        }
        
        handler = tool_handlers.get(tool_name)
        if handler:
            return handler(query, user_id)
        return None
        
    def _handle_website_analysis(self, query, user_id):
        """Maneja consultas específicas sobre análisis web"""
        context = self.context_agent.get_current_context()
        if context['last_analysis'] and context['last_analysis']['tool'] == 'Website Analysis':
            return self.process_message(query, user_id, '/analisis-web')
        return "No hay un análisis web reciente disponible."
        
    def _handle_seo_analysis(self, query, user_id):
        """Maneja consultas específicas sobre análisis SEO"""
        context = self.context_agent.get_current_context()
        if context['last_analysis'] and context['last_analysis']['tool'] == 'SEO Performance Analysis':
            return self.process_message(query, user_id, '/search-console')
        return "No hay un análisis SEO reciente disponible."
        
    def _handle_traffic_analysis(self, query, user_id):
        """Maneja consultas específicas sobre análisis de tráfico"""
        context = self.context_agent.get_current_context()
        if context['last_analysis'] and context['last_analysis']['tool'] == 'Traffic Analysis':
            return self.process_message(query, user_id, '/google-analytics')
        return "No hay un análisis de tráfico reciente disponible." 