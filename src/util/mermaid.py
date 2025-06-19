import os

from src.agents.graph_builder import my_graph

current_directory = os.path.dirname(os.path.abspath(__file__))


def create_mermaid_diagram_files():
    mermaid_md = my_graph.get_graph().draw_mermaid()
    mermaid_md_file = os.path.join(current_directory, "README.md")
    with open(mermaid_md_file, "w") as file:
        file.write('# Mermaid diagram \n')
        file.write('![Mermaid diagram](mermaid.png)\n')
        file.write(f'```mermaid\n{mermaid_md}\n```\n')

    mermaid_png_file = os.path.join(current_directory, "mermaid.png")
    my_graph.get_graph().draw_mermaid_png(output_file_path=mermaid_png_file)
