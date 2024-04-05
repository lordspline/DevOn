import gradio as gr
import os
import time
from orb import Orb
from playwright.sync_api import sync_playwright

orb = Orb()


def add_message(history, message):
    for x in message["files"]:
        history.append(((x,), None))
    if message["text"] is not None:
        history.append((message["text"], None))
    return history, gr.MultimodalTextbox(value=None, interactive=False)


def bot(history):
    for r in orb.run(history[-1][0]):
        text, screenshot = r
        if type(text) == str:
            history.append((None, text))
        yield history, screenshot


with gr.Blocks(css="footer {visibility: hidden}") as demo:
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(
                [], elem_id="chatbot", bubble_full_width=False, height=800
            )
        with gr.Column(min_width=1000):
            editor_view = gr.Image(
                orb.screenshot, label="Browser", height=800, width=1000
            )
    with gr.Row():

        chat_input = gr.MultimodalTextbox(
            value={"text": "search elon musk"},
            interactive=True,
            file_types=["image"],
            placeholder="Enter message or upload file...",
            show_label=False,
        )

    chat_msg = chat_input.submit(
        add_message, [chatbot, chat_input], [chatbot, chat_input]
    )
    bot_msg = chat_msg.then(
        bot,
        [chatbot],
        [chatbot, editor_view],
        api_name="bot_response",
    )
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

if __name__ == "__main__":
    demo.queue()
    demo.launch()
