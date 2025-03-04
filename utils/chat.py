import streamlit as st
from openai import OpenAI
from  .agent.tool_schema import tools
from .agent.tools import execute_function_call
import pandas as pd
import json


def chat_interface(df: pd.DataFrame) -> None:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ✅ Add CSS for chat styling
    st.markdown("""
        <style>
        [data-testid="stChatInput"] {
            position: fixed;
            bottom: 40px;
            left: 30px;
            right: 30px;
            margin: 0 auto;
            z-index: 1000;
        }
        .chat-container {
            margin-bottom: 80px;
            padding: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # ✅ Display previous chat messages
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)

    # ✅ User input field
    if prompt := st.chat_input("Ask about the guidelines"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call GPT with function calling enabled
        completion = client.chat.completions.create(
            model=st.session_state.openai_model,
            messages=[{"role": "user", "content": prompt}],
            tools=tools
        )

        response = completion.choices[0].message

        # ✅ Handle function calls dynamically
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # ✅ Execute function and pass results to GPT for a response
                function_result = execute_function_call(df, function_name, function_args)

                followup_completion = client.chat.completions.create(
                    model=st.session_state.openai_model,
                    messages=[
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": f"Here is some background information:\n\n{function_result}"}
                    ],
                )

                final_response = followup_completion.choices[0].message.content

                # ✅ Display the final response
                st.session_state.messages.append({"role": "assistant", "content": final_response})
                with st.chat_message("assistant"):
                    st.markdown(final_response)

        else:
            # If GPT provides a direct response without calling a function
            st.session_state.messages.append({"role": "assistant", "content": response.content})
            with st.chat_message("assistant"):
                st.markdown(response.content)
