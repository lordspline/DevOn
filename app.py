import gradio as gr
import os
import time
from agent import DevOn

image_temp = "https://multion-client-screenshots.s3.us-east-2.amazonaws.com/0cea8653-bf81-41ac-84f2-9b08f8f2f2fa_e9209e98-8863-44e4-bc16-0ed46b1e56ca_remote_screenshot.png"
devon = DevOn(
    editor_image=image_temp, browser_image=image_temp, scratchpad_image=image_temp
)


def add_message(history, message):
    for x in message["files"]:
        history.append(((x,), None))
    if message["text"] is not None:
        history.append((message["text"], None))
    return history, gr.MultimodalTextbox(value=None, interactive=False)


def bot(history):
    for r in devon.run(history[-1][0]):
        text, editor_image, browser_image, scratchpad_image = r
        if type(text) == str:
            history.append((None, text))
        if editor_image is None:
            editor_image = devon.editor_image
            browser_image = devon.browser_image
            scratchpad_image = devon.scratchpad_image
        yield history, editor_image, browser_image, scratchpad_image


with gr.Blocks(css="footer {visibility: hidden}") as demo:
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(
                [], elem_id="chatbot", bubble_full_width=False, height=300
            )

            chat_input = gr.MultimodalTextbox(
                value={"text": "write a basic hello world fastapi server"},
                interactive=True,
                file_types=["image"],
                placeholder="Enter message or upload file...",
                show_label=False,
            )
        with gr.Column():
            editor_view = gr.Image(
                devon.editor_image,
                label="Editor",
            )
    with gr.Row():
        with gr.Column():
            browser_view = gr.Image(
                devon.browser_image,
                label="Browser",
            )
        with gr.Column():
            scratchpad_view = gr.Image(
                devon.scratchpad_image,
                label="Scratchpad",
            )

    chat_msg = chat_input.submit(
        add_message, [chatbot, chat_input], [chatbot, chat_input]
    )
    bot_msg = chat_msg.then(
        bot,
        [chatbot],
        [chatbot, editor_view, browser_view, scratchpad_view],
        api_name="bot_response",
    )
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

    # chatbot.like(print_like_dislike, None, None)

if __name__ == "__main__":
    demo.queue()
    demo.launch()
