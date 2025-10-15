import reflex as rx
from app.core.settings import settings
from typing import TypedDict


class HreflangLink(TypedDict):
    rel: str
    href: str
    hreflang: str


class SeoState(rx.State):
    """Manages SEO metadata for public-facing pages."""

    meta_title: str = "Colabe Test Labo"
    meta_description: str = "The next-generation test automation platform."
    canonical_url: str = ""
    hreflang_links: list[HreflangLink] = []
    og_title: str = "Colabe Test Labo"
    og_description: str = "The next-generation test automation platform."
    og_image: str = f"{settings.PUBLIC_BASE_URL}/placeholder.svg"

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
        parts = path.strip("/").split("/")
        if parts and parts[0] in settings.PUBLIC_LOCALES.split(","):
            return "/" + "/".join(parts[1:])
        return path

    @rx.event
    def on_public_page_load(self):
        """Event handler to set SEO metadata when a public page loads."""
        base_url = settings.PUBLIC_BASE_URL
        path = self.path_without_lang
        if path == "/":
            self.canonical_url = f"{base_url}/"
        else:
            self.canonical_url = f"{base_url}{path}"
        self.hreflang_links = []
        locales = settings.PUBLIC_LOCALES.split(",")
        for lang in locales:
            if lang == settings.EDGE_REGION_DEFAULT:
                href = f"{base_url}{path}"
            else:
                href = f"{base_url}/{lang}{path}"
            self.hreflang_links.append(
                {"rel": "alternate", "href": href, "hreflang": lang}
            )
        self.hreflang_links.append(
            {"rel": "alternate", "href": f"{base_url}{path}", "hreflang": "x-default"}
        )
        page_title = path.strip("/").replace("/", " ").replace("-", " ").title()
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