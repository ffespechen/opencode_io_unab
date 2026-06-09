from jinja2 import Environment, FileSystemLoader
import os

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), auto_reload=False)


class Templates:
    def TemplateResponse(self, name, context, status_code=200):
        template = env.get_template(name)
        body = template.render(**context)
        from starlette.responses import HTMLResponse
        return HTMLResponse(body, status_code=status_code)


templates = Templates()
