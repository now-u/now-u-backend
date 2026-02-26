from django.template.loader import get_template
from unfold.widgets import TEXTAREA_CLASSES, PROSE_CLASSES, UnfoldAdminTextareaWidget

from now_u_api.settings import BASE_URL

class MarkdownEditorWidget(UnfoldAdminTextareaWidget):
    def render(self, name, value, attrs=None, renderer=None, **kwargs):
        template = get_template("markdown_editor.html")

        return template.render(
            {
                "value": value,
                "field_name": name,
                "attrs": attrs,
                "input_class": " ".join(TEXTAREA_CLASSES),
                "prose_class": " ".join(TEXTAREA_CLASSES + PROSE_CLASSES),
                "base_url": BASE_URL,
            }
        )
