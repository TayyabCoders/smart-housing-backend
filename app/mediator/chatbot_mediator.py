"""
Chatbot Mediator
"""


class ChatbotMediator:

    def __init__(self, chatbot_service):
        self.chatbot_service = chatbot_service

    async def ask(self, query: str):
        return await self.chatbot_service.ask(query)
