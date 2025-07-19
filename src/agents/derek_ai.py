
from .funnel_agent.main import analizar_embudo
from .keyword_agent.main import run_keyword_research

class DerekAI:
    def __init__(self):
        self.agents = {
            'funnel': analizar_embudo,
            'keywords': run_keyword_research
        }

    def orchestrate(self, user_input, user_id, db):
        intent = self.understand_intent(user_input)
        if intent in self.agents:
            agent = self.agents[intent]
            # La data para los agentes debe ser extraída del user_input
            data = {}
            return agent(data, user_id, db)
        else:
            return "No se pudo entender la solicitud."

    def understand_intent(self, user_input):
        if 'funnel' in user_input.lower() or 'embudo' in user_input.lower():
            return 'funnel'
        elif 'keyword' in user_input.lower() or 'palabra clave' in user_input.lower():
            return 'keywords'
        else:
            return None
