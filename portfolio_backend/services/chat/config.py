"""Module for defining prompt templates and conversation parameters for the chat system.

This module contains the prompt structure and related messages used in the chat application.
It includes templates for engaging with users, handling off-topic responses, and setting limits on conversation length.

Attributes:
    prompt (str): The template for the conversation prompt, including context.
    general_context (str): General context about Hani for the chat.
    off_topic_response (str): Response template for off-topic or irrelevant questions.
    ai_first_message (str): The initial message from the AI when a chat begins.
    limit_out_of_topic_message (str): Message indicating the user has reached the off-topic limit.
    limit_length_message (str): Message indicating the user has exceeded the conversation length limit.
    messages_limit (int): Maximum number of messages allowed in a conversation.
    off_topic_count_limit (int): Maximum number of off-topic messages allowed before termination.
"""

prompt = """Your task is to engage in this conversation. Answer the questions strictly based on the provided context \
and the current conversation. Your answers must be as short as possible.
For off-topic, offensive messages or irrelevant questions, reply with: "Null".

Context: {context}"""

general_context = """
This conversation is about Hani, a Software/Data Engineer. You're having this conversation to answer people's questions
about Hani's experience and professional life."""

off_topic_response = """It is whether your message is off-topic or I do not have enough information to answer it.
You have sent {off_topic_count} out of 3 off-topic messages. After the 3rd instance, this chat will be terminated.
\nIf you think this is a mistake, please rephrase your question and ask it again."""

ai_first_message = """Welcome to the chat, feel free to ask any question about Hani's experience and work, and I'll \
do my best to answer."""

limit_out_of_topic_message = "You reached 3 out of topic messages. This chat is terminated."
limit_length_message = "You reached the length limit for a single conversation. This conversation has been terminated."

messages_limit = 30
off_topic_count_limit = 3
