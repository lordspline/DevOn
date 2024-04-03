import gradio as gr
import os
import time
import ngrok
from dotenv import load_dotenv

load_dotenv(".env.local")


def new_file(file_name):
    # print(file_explorer)
    new_file_path = os.path.join(os.getcwd(), "dev", file_name)
    open(new_file_path, "w")


def set_current_file(file):
    if file is None:
        return ""
    file_content = ""
    with open(file) as f:
        file_content = f.read()
    return file_content


def update_file(current_file, editor_content):
    with open(current_file, "w") as f:
        f.write(editor_content)
    return current_file, editor_content, ""


with gr.Blocks(css="footer {visibility: hidden}") as demo:
    with gr.Row():
        with gr.Column() as c:
            file_explorer = gr.FileExplorer(file_count="single", root_dir="dev")
            new_file_name = gr.Textbox(label="New File Name")
            new_file_button = gr.Button(
                "Create New File (After creating a new file, you must refresh the page to see the changes.)"
            )

        with gr.Column():
            code_display = gr.Code(
                "Select a file to start",
                language="python",
                label="Code Display (Displays file's current state, cannot edit this.)",
            )
            code_editor = gr.Code(
                "",
                language="python",
                label="Code Editor (Enter the updated code to put in the file here.)",
            )
            update_button = gr.Button("Update File")

    file_explorer.change(set_current_file, file_explorer, code_display)
    update_button.click(
        update_file,
        [file_explorer, code_editor],
        [file_explorer, code_display, code_editor],
    )
    new_file_button.click(new_file, new_file_name)
    # with gr.Row():
    #     save_button = gr.Button("Save Current File")

if __name__ == "__main__":
    demo.queue()
    listener = ngrok.forward(9000, authtoken_from_env=True)
    print(f"Ingress established at {listener.url()}")
    demo.launch(server_port=9000)
