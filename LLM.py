import os
from pydantic import BaseModel
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

# Thiết lập biến môi trường cho GROQ_API_KEY
os.environ['GROQ_API_KEY'] = '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'

# Thiết lập bộ nhớ cho cuộc hội thoại
conversational_memory_length = 50
memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)

class UserInput(BaseModel):
    message: str

def query_llm(user_input: UserInput):
    groq_api_key = os.environ['GROQ_API_KEY']
    model = 'llama3-8b-8192'
    groq_chat = ChatGroq(
        groq_api_key=groq_api_key,
        model_name=model,
        temperature=0
    )

    system_prompt = 'Xin chào, Tôi có thể giúp gì cho bạn?'

    if user_input.message:
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=system_prompt
                ),
                MessagesPlaceholder(
                    variable_name="chat_history"
                ),
                HumanMessagePromptTemplate.from_template(
                    "{human_input}"
                ),
            ]
        )

        conversation = LLMChain(
            llm=groq_chat,
            prompt=prompt,
            verbose=False,
            memory=memory
        )

        response = conversation.predict(human_input=user_input.message)
        return response

if __name__ == "__main__":
    user_input = UserInput(message="Bạn có thể cho tôi biết về bệnh vàng lá ?")
    response = query_llm(user_input)
    print(response)
