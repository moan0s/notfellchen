from __future__ import annotations

from pathlib import Path

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import ExtensionMetadata


class DrawioDirective(SphinxDirective):
    """A directive to show a drawio diagram!

    Usage:
    .. drawio::
       example-diagram.drawio.html
       example-diagram.drawio.png
    """

    has_content = False
    required_arguments = 2  # html and png

    def run(self) -> list[nodes.Node]:
        html_path = self.arguments[0]
        png_path = self.arguments[1]

        env = self.state.document.settings.env

        docdir = Path(env.doc2path(env.docname)).parent
        html_rel = Path(self.arguments[0])
        png_rel = Path(self.arguments[1])

        html_path = (docdir / html_rel).resolve()
        png_path = (docdir / png_rel).resolve()

        container = nodes.container()

        # HTML output -> raw HTML node
        if self.builder.format == "html":
            # Embed the HTML file contents directly
            raw_html_node = nodes.raw(
                "",
                f'<div class="drawio-diagram">{open(html_path, encoding="utf-8").read()}</div>',
                format="html",
            )
            container += raw_html_node
        else:
            # Other outputs -> PNG image node
            image_node = nodes.image(uri=png_path)
            container += image_node

        return [container]

    @property
    def builder(self):
        # Helper to access the builder from the directive context
        return self.state.document.settings.env.app.builder


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_directive("drawio", DrawioDirective)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
