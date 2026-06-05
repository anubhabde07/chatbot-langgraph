import streamlit as st
from langgraph_tool_backend import get_chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid

# ChatBot
chatbot = get_chatbot()


# ************************************** Utility Functions *****************************************
def generate_thread_id():
    return str(uuid.uuid4())


def add_thread(thread_id):
    thread_id = str(thread_id)

    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def reset_chat():
    thread_id = generate_thread_id()

    st.session_state["thread_id"] = thread_id
    st.session_state["message_history"] = []


def load_conversations(thread_id):
    state = chatbot.get_state(
        config={"configurable": {"thread_id": str(thread_id)}}
    ).values

    return state.get("messages", [])


# ************************************** Session State *********************************************
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = [str(t) for t in retrieve_all_threads()]



# **************************************** Sidebar UI ******************************************
st.sidebar.title("LangGraph ChatBot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state["chat_threads"][::-1]:
    short_id = thread_id[:8]

    if st.sidebar.button(short_id, key=thread_id):
        st.session_state["thread_id"] = thread_id

        messages = load_conversations(thread_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            else:
                role = "assistant"

            temp_messages.append({
                "role": role,
                "content": msg.content
            })

        st.session_state["message_history"] = temp_messages


# ******************************************* Main UI ********************************************
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])


user_input = st.chat_input("Type here")

if user_input:
    add_thread(st.session_state['thread_id'])

    thread_id = str(st.session_state["thread_id"])

    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    config = {
        "configurable": {
            "thread_id": thread_id
        },
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        },
        "run_name": "chat_turn",
    }

    with st.chat_message("assistant"):

        status_box = st.status("Thinking...", expanded=True)

        def ai_only_stream():

            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages"
            ):

                # Show actual tool name
                if isinstance(message_chunk, ToolMessage):

                    tool_name = message_chunk.name

                    status_box.write(f"🔧 Using tool: `{tool_name}`")

                # Stream only AI response
                elif isinstance(message_chunk, AIMessage):

                    if message_chunk.content:
                        yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        status_box.update(
            label="Done ✅",
            state="complete",
            expanded=False
        )

    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_message
    })