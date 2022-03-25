import os
import webbrowser

from jinja2 import Environment, FileSystemLoader

ROOT_DIRECTORY = os.path.abspath(os.path.dirname(__file__) + "/..")
HTML_ROOT_DIRECTORY = f"{ROOT_DIRECTORY}/html"
TEMPLATE_DIRECTORY = f"{HTML_ROOT_DIRECTORY}/templates"
HTML_INDEX_FILE = f"{HTML_ROOT_DIRECTORY}/schedule.html"

GRAPH_ROOT_DIRECTORY_NAME = "graphs"
HTML_GRAPH_ROOT_DIRECTORY = f"{HTML_ROOT_DIRECTORY}/{GRAPH_ROOT_DIRECTORY_NAME}"

PRECEDING_GRAPH_FILE_NAME = "preceding-graph.html"
PRECEDING_GRAPH_FILE_PATH = f"{HTML_GRAPH_ROOT_DIRECTORY}/{PRECEDING_GRAPH_FILE_NAME}"

POLYGRAPH_FILE_NAME = "all-polygraph.html"
POLYGRAPH_FILE_PATH = f"{HTML_GRAPH_ROOT_DIRECTORY}/{POLYGRAPH_FILE_NAME}"
POLYGRAPH_COMPATIBLE_DAG_FILE_NAME = "polygraph-compatible-dag.html"
POLYGRAPH_COMPATIBLE_DAG_FILE_PATH = f"{HTML_GRAPH_ROOT_DIRECTORY}/{POLYGRAPH_COMPATIBLE_DAG_FILE_NAME}"


def generate_view(**variables):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIRECTORY))

    for file_name in ("schedule", "analysis"):
        with open(f"{HTML_ROOT_DIRECTORY}/{file_name}.html", 'w') as file:
            template = env.get_template(f"{file_name}.j2.html")
            file.write(template.render(
                **variables,
                graph_directory_name=GRAPH_ROOT_DIRECTORY_NAME,
                preceding_graph_file_name=PRECEDING_GRAPH_FILE_NAME,
                polygraph_file_name=POLYGRAPH_FILE_NAME,
                polygraph_compatible_graph_file_name=POLYGRAPH_COMPATIBLE_DAG_FILE_NAME,
            ))


def open_index_html():
    webbrowser.open(HTML_INDEX_FILE)
