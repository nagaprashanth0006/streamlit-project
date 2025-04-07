from rag_pipeline import build_query_engine
import gradio as gr

query_engine = build_query_engine()


def rag_chat(prompt):
    return str(query_engine.query(prompt))


gr.ChatInterface(rag_chat).launch(server_name="0.0.0.0", server_port=7860)
