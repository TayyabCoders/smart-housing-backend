"""
Chatbot Controller
"""


class ChatbotController:

    def __init__(self, chatbot_mediator):
        self.chatbot_mediator = chatbot_mediator

    async def ask(self, query: str):
        return await self.chatbot_mediator.ask(query)
