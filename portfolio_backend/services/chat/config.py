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
