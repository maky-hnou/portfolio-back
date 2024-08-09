prompt = """You are a helpful assistant. Answer all questions, as short as possible, to the best of your ability
based on the conversation history and the following context:\n\nContext: {context}."""

off_topic_response = """It is whether your message is off-topic or I do not have enough information to answer it.
You have sent {off_topic_count} out of 3 off-topic messages. After the 3rd instance, this chat will be terminated.
\nIf you think this is a mistake, please rephrase your question and ask it again."""

ai_first_message = "Welcome to the chat, feel free to ask any question about Hani, and I'll do my best to answer."

limit_out_of_topic_message = "You reached 3 out of topic messages. This chat is terminated."
limit_length_message = (
    "You reached the maximum length for a single conversation. This conversation has been terminated."
)
