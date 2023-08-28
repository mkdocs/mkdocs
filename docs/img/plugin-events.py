# Run this to re-generate 'plugin-events.svg'.
# Requires `pip install graphviz`.

import contextlib
import pathlib
import re

from graphviz import Digraph

graph = Digraph("MkDocs", format="svg")
graph.attr(compound="true", bgcolor="transparent")
graph.graph_attr.update(fontname="inherit", tooltip=" ")
graph.node_attr.update(fontname="inherit", tooltip=" ", style="filled")
graph.edge_attr.update(fontname="inherit", tooltip=" ")


def strip_suffix(name):
    return re.sub(r"_.$", "", name)


subgraph_to_first_node = {}
subgraph_to_last_node = {}


def node(g, name, **kwargs):
    if "_point" in name:
        kwargs.setdefault("shape", "point")
    else:
        kwargs.setdefault("fillcolor", "#77ff7788")
        kwargs.setdefault("color", "#00000099")
    kwargs.setdefault("label", strip_suffix(name))

    g.node(name, **kwargs)

    subgraph_to_first_node.setdefault(g.name, name)
    subgraph_to_last_node[g.name] = name


def edge(g, a, b, dashed=False, **kwargs):
    if kwargs.get("style") == "dashed":
        kwargs.setdefault("penwidth", "1.5")

    if a in subgraph_to_last_node:
        kwargs.setdefault("ltail", a)
        a = subgraph_to_last_node[a]
    if b in subgraph_to_first_node:
        kwargs.setdefault("lhead", b)
        b = subgraph_to_first_node[b]

    if a.startswith(("on_", "placeholder_")):
        a += ":s"
    else:
        node(g, a.split(":")[0])
    if b.startswith(("on_", "placeholder_")):
        b += ":n"
    else:
        node(g, b.split(":")[0])

    g.edge(a, b, **kwargs)


def ensure_order(a, b):
    edge(graph, a, b, style="invis")


@contextlib.contextmanager
def cluster(g, name, **kwargs):
    assert name.startswith("cluster_")
    kwargs.setdefault("label", strip_suffix(name)[len("cluster_") :])
    kwargs.setdefault("bgcolor", "#dddddd55")
    kwargs.setdefault("pencolor", "#00000066")
    with g.subgraph(name=name) as c:
        c.attr(**kwargs)
        yield c


def event(g, name, parameters):
    with cluster(
        g, f"cluster_{name}", href=f"#{name}", bgcolor="#ffff3388", pencolor="#00000088"
    ) as c:
        label = "|".join(f"<{p}>{p}" for p in parameters.split())
        node(c, name, shape="record" if parameters else "point", label=label, fillcolor="#ffffff55")


def placeholder_cluster(g, name):
    with cluster(g, name) as c:
        node(c, f"placeholder_{name}", label="...", fillcolor="transparent", color="transparent")


event(graph, "on_startup", "command dirty")

with cluster(graph, "cluster_build", bgcolor="#dddddd11") as g:
    event(g, "on_config", "config")
    event(g, "on_pre_build", "config")
    event(g, "on_files", "files config")
    event(g, "on_nav", "nav config files")

    edge(g, "load_config", "on_config:config")
    edge(g, "on_config:config", "on_pre_build:config")
    edge(g, "on_config:config", "get_files")
    edge(g, "get_files", "on_files:files")
    edge(g, "on_files:files", "get_nav")
    edge(g, "get_nav", "on_nav:nav")
    edge(g, "on_files:files", "on_nav:files")

    with cluster(g, "cluster_populate_page") as c:
        event(c, "on_pre_page", "page config files")
        event(c, "on_page_read_source", "page config")
        event(c, "on_page_markdown", "markdown page config files")
        event(c, "on_page_content", "html page config files")

        edge(c, "on_pre_page:page", "on_page_read_source:page", style="dashed")
        edge(c, "cluster_on_page_read_source", "on_page_markdown:markdown", style="dashed")
        edge(c, "on_page_markdown:markdown", "render_p", style="dashed")
        edge(c, "render_p", "on_page_content:html", style="dashed")

    edge(g, "on_nav:files", "pages_point_a", arrowhead="none")
    edge(g, "pages_point_a", "on_pre_page:page", style="dashed")
    edge(g, "pages_point_a", "cluster_populate_page")

    for i in 2, 3:
        placeholder_cluster(g, f"cluster_populate_page_{i}")
        edge(g, "pages_point_a", f"cluster_populate_page_{i}", style="dashed")
        edge(g, f"cluster_populate_page_{i}", "pages_point_b", style="dashed")

    event(g, "on_env", "env config files")

    edge(g, "on_page_content:html", "pages_point_b", style="dashed")
    edge(g, "pages_point_b", "on_env:files")

    edge(g, "pages_point_b", "pages_point_c", arrowhead="none")
    edge(g, "pages_point_c", "on_page_context:page", style="dashed")

    with cluster(g, "cluster_build_page") as c:
        event(c, "on_page_context", "context page config nav")
        event(c, "on_post_page", "output page config")

        edge(c, "get_context", "on_page_context:context")
        edge(c, "on_page_context:context", "render")
        edge(c, "get_template", "render")
        edge(c, "render", "on_post_page:output")
        edge(c, "on_post_page:output", "write_file")

    edge(g, "on_nav:nav", "cluster_build_page")
    edge(g, "on_env:env", "cluster_build_page")

    for i in 2, 3:
        placeholder_cluster(g, f"cluster_build_page_{i}")
        edge(g, "pages_point_c", f"cluster_build_page_{i}", style="dashed")

    event(g, "on_post_build", "config")

event(graph, "on_serve", "server config")
event(graph, "on_shutdown", "")


ensure_order("on_startup", "cluster_build")
ensure_order("on_pre_build", "on_files")
ensure_order("on_nav", "cluster_populate_page")
ensure_order("cluster_populate_page_2", "cluster_populate_page_3")
ensure_order("on_page_content", "on_env")
ensure_order("pages_point_c", "cluster_build_page")
ensure_order("cluster_build_page_2", "cluster_build_page_3")
ensure_order("cluster_build_page", "on_post_build")
ensure_order("on_post_build", "on_serve")
ensure_order("on_serve", "on_shutdown")


data = graph.pipe()
data = data[data.index(b"<svg ") :]
pathlib.Path(__file__).with_suffix(".svg").write_bytes(data)
