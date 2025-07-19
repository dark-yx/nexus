import json
from flask import session
from db import get_user_history, save_web_analysis, save_conversation
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    context: Annotated[dict, "The current context of the conversation"]
    user_id: Annotated[str, "The user ID"]

class ContextAgent:
    def __init__(self, db_connection):
        self.db = db_connection
        self.llm = ChatOpenAI(model="gpt-4")
        self.graph = self._build_graph()
        
    def _build_graph(self):
        """Construye el grafo de LangGraph para el manejo de contexto"""
        # Definir el nodo de procesamiento de contexto
        def process_context(state: AgentState) -> AgentState:
            messages = state["messages"]
            context = state["context"]
            user_id = state["user_id"]
            
            # Obtener historial del usuario
            history = get_user_history(self.db, user_id)
            
            # Actualizar el contexto con el historial
            context["history"] = history
            
            return {"messages": messages, "context": context, "user_id": user_id}
        
        # Crear el grafo
        workflow = StateGraph(AgentState)
        
        # Agregar nodos
        workflow.add_node("process_context", process_context)
        
        # Definir el flujo
        workflow.add_edge("process_context", END)
        
        # Compilar el grafo
        return workflow.compile()
        
    def get_current_context(self):
        """Obtiene el contexto actual de la sesión"""
        context = {
            'current_tool': session.get('current_tool'),
            'last_analysis': session.get('last_analysis'),
            'user_id': session.get('user_id')
        }
        return context
        
    def get_analysis_history(self, user_id):
        """Obtiene el historial de análisis del usuario"""
        return get_user_history(self.db, user_id)
        
    def process_context(self, user_id, current_path):
        """Procesa el contexto actual y lo formatea para el chatbot"""
        # Crear estado inicial
        initial_state = {
            "messages": [],
            "context": self.get_current_context(),
            "user_id": user_id
        }
        
        # Ejecutar el grafo
        final_state = self.graph.invoke(initial_state)
        
        context = final_state["context"]
        context_info = ""
        
        # Agregar información de la herramienta actual
        if context['current_tool']:
            context_info += f"\nHerramienta actual: {context['current_tool']['name']}\n"
            context_info += f"Descripción: {context['current_tool']['description']}\n"
            context_info += f"Capacidades: {', '.join(context['current_tool']['capabilities'])}\n"
            
        # Agregar información del último análisis
        if context['last_analysis']:
            context_info += f"\nÚltimo análisis:\n"
            context_info += f"Herramienta: {context['last_analysis'].get('tool', 'No especificada')}\n"
            
            if context['last_analysis'].get('url'):
                context_info += f"URL analizada: {context['last_analysis']['url']}\n"
                
            if context['last_analysis'].get('summary'):
                context_info += f"Resumen: {context['last_analysis']['summary']}\n"
                
            if context['last_analysis'].get('data'):
                data = context['last_analysis']['data']
                context_info += "\nDatos del análisis:\n"
                for key, value in data.items():
                    if isinstance(value, (list, dict)):
                        context_info += f"{key}: {json.dumps(value, indent=2)}\n"
                    else:
                        context_info += f"{key}: {value}\n"
                        
        # Agregar información del historial
        if context.get('history'):
            context_info += "\nHistorial de análisis recientes:\n"
            for item in context['history'][:3]:  # Mostrar solo los 3 más recientes
                context_info += f"- {item['tool']}: {item['summary'][:100]}...\n"
                
        return context_info 