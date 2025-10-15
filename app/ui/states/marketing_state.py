import reflex as rx
from typing import TypedDict


class HeaderLink(TypedDict):
    text: str
    href: str


class MarketingState(rx.State):
    current_lang: str = "en"
    header_links: list[HeaderLink] = []

    @rx.var
    def home_link(self) -> str:
        return f"/{self.current_lang}" if self.current_lang != "en" else "/"

    @rx.event
    def on_load(self):
        path = self.router.page.path.strip("/")
        if path and path.split("/")[0] in ["en", "es"]:
            self.current_lang = path.split("/")[0]
        else:
            self.current_lang = "en"
        self._update_header_links()

    def _update_header_links(self):
        lang_prefix = f"/{self.current_lang}" if self.current_lang != "en" else ""
        self.header_links = [
            {"text": "Pricing", "href": f"{lang_prefix}/pricing"},
            {"text": "Features", "href": f"{lang_prefix}/features"},
            {"text": "Demos", "href": f"{lang_prefix}/demos"},
            {"text": "Customers", "href": f"{lang_prefix}/customers"},
            {"text": "Contact", "href": f"{lang_prefix}/contact"},
        ]

    @rx.event
    def set_language(self, lang: str):
        self.current_lang = lang
        path_parts = self.router.page.path.strip("/").split("/")
        if len(path_parts) > 1 and path_parts[0] in ["en", "es"]:
            new_path = "/" + "/".join([lang] + path_parts[1:])
        else:
            new_path = f"/{lang}{self.router.page.path}"
        if new_path == "/en":
            new_path = "/"
        if self.router.page.path == "/":
            new_path = f"/{lang}"
        return rx.redirect(new_path)