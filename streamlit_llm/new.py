import gradio as gr

# Define the sidebar content
def sidebar_content():
    with gr.Column():
        gr.Markdown("# Sidebar")
        gr.Button("Option 1")
        gr.Button("Option 2")
        gr.Button("Option 3")

# Define the main content
def main_content():
    with gr.Column():
        gr.Markdown("# Main Interface")
        gr.Textbox(label="Input")
        gr.Button("Submit")

# Create the layout with a sidebar and main interface
def create_layout():
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=1):  # Sidebar with a scale of 1
                sidebar_content()
            with gr.Column(scale=3):  # Main content with a larger scale
                main_content()
    return demo

# Instantiate and launch the interface
demo = create_layout()
demo.launch()
