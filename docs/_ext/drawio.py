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
       :alt: Example of a Draw.io diagram
    """

    has_content = False
    required_arguments = 2  # html and png
    optional_arguments = 1
    final_argument_whitespace = True  # indicating if the final argument may contain whitespace
    option_spec = {
        "alt": str,
    }

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env
        builder = env.app.builder

        # Resolve paths relative to the document
        docdir = Path(env.doc2path(env.docname)).parent
        html_rel = Path(self.arguments[0])
        png_rel = Path(self.arguments[1])
        html_path = (docdir / html_rel).resolve()
        png_path = (docdir / png_rel).resolve()

        alt_text = self.options.get("alt", "")

        container = nodes.container()

        # HTML output -> raw HTML node
        if builder.format == "html":
            # Embed the HTML file contents directly
            try:
                html_content = html_path.read_text(encoding="utf-8")
            except OSError as e:
                msg = self.state_machine.reporter.error(f"Cannot read HTML file: {e}")
                return [msg]
            aria_attribute = f' aria-label="{alt_text}"' if alt_text else ""
            raw_html_node = nodes.raw(
                "",
                f'<div class="drawio-diagram"{aria_attribute}>{html_content}</div>',
                format="html",
            )
            container += raw_html_node
        else:
            # Other outputs -> PNG image node
            image_node = nodes.image(uri=png_path)
            container += image_node

        return [container]


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_directive("drawio", DrawioDirective)

    return {
        "version": "0.2",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
