import reflex as rx
from app.core.settings import settings
from typing import TypedDict


class HreflangLink(TypedDict):
    rel: str
    href: str
    hreflang: str


class NavLink(TypedDict):
    text: str
    href: str


class SeoState(rx.State):
    """Manages SEO metadata for public-facing pages."""

    meta_title: str = "Colabe Test Labo"
    meta_description: str = "The next-generation test automation platform."
    canonical_url: str = ""
    hreflang_links: list[HreflangLink] = []
    og_title: str = "Colabe Test Labo"
    og_description: str = "The next-generation test automation platform."
    og_image: str = f"{settings.PUBLIC_BASE_URL}/placeholder.svg"
    public_nav_links: list[NavLink] = []

    @rx.var
    def current_lang(self) -> str:
        """Determines the current language from the URL path."""
        path = self.router.page.path
        parts = path.strip("/").split("/")
        if parts and parts[0] in settings.PUBLIC_LOCALES.split(","):
            return parts[0]
        return settings.EDGE_REGION_DEFAULT

    @rx.var
    def path_without_lang(self) -> str:
        """Returns the URL path without the language prefix."""
        path = self.router.page.path
        lang = self.current_lang
        if path.startswith(f"/{lang}"):
            return path[len(lang) + 1 :]
        return path

    @rx.event
    def on_public_page_load(self):
        """Event handler to set SEO metadata when a public page loads."""
        base_url = settings.PUBLIC_BASE_URL
        path = self.path_without_lang
        self.canonical_url = f"{base_url}{path}"
        self.hreflang_links = []
        for lang in settings.PUBLIC_LOCALES.split(","):
            self.hreflang_links.append(
                {
                    "rel": "alternate",
                    "href": f"{base_url}/{lang}{path}",
                    "hreflang": lang,
                }
            )
        self.hreflang_links.append(
            {"rel": "alternate", "href": f"{base_url}{path}", "hreflang": "x-default"}
        )
        page_title = path.strip("/").replace("-", " ").title()
        if not page_title:
            page_title = "Home"
        self.meta_title = f"{page_title} | Colabe"
        self.og_title = self.meta_title
        self.meta_description = f"Learn about {page_title} at Colabe Test Labo."
        self.og_description = self.meta_description
        if settings.OG_IMAGE_FUNCTION_URL:
            self.og_image = f"{settings.OG_IMAGE_FUNCTION_URL}?title={self.meta_title}"
        else:
            self.og_image = f"{settings.PUBLIC_BASE_URL}/placeholder.svg"
        lang = self.current_lang
        self.public_nav_links = [
            {"text": "Who We Are", "href": f"/{lang}/who-we-are"},
            {"text": "Adapters", "href": f"/{lang}/adapters/python"},
            {"text": "Playbooks", "href": f"/{lang}/playbooks/web-perf"},
            {"text": "Integrations", "href": f"/{lang}/integrations/github"},
        ]