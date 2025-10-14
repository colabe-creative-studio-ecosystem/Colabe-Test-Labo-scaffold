import reflex as rx
from typing import TypedDict, Literal
import json
from pathlib import Path
from app.ui.states.auth_state import AuthState


class DeepLink(TypedDict):
    type: str
    route: str
    focus_selector: str


class Article(TypedDict):
    slug: str
    title: str
    summary: str
    category: str
    tags: list[str]
    lang: str
    version: str
    updated_at: str
    content_html: str
    deep_links: list[DeepLink]


class FaqItem(TypedDict):
    slug: str
    question: str
    answer_html: str
    category: str
    lang: str
    quick_answer: bool


class SettingResult(TypedDict):
    id: str
    title: str
    route: str
    focus_selector: str
    purpose: str


class ApiDocResult(TypedDict):
    operation_id: str
    summary: str
    path: str
    method: str


SearchResultType = Literal["article", "faq", "setting", "api"]


class SearchResult(TypedDict):
    type: SearchResultType
    title: str
    summary: str
    route: str
    score: float
    data: Article | FaqItem | SettingResult | ApiDocResult


class KBState(AuthState):
    search_query: str = ""
    lang: str = "en"
    _articles: list[Article] = []
    _faqs: list[FaqItem] = []
    _settings: list[SettingResult] = []
    _api_docs: list[ApiDocResult] = []
    _synonyms = {
        "a11y": "accessibility",
        "sweep": "scan",
        "budget": "threshold",
        "perf": "performance",
    }
    _is_loaded: bool = False

    def _load_content(self):
        if self._is_loaded and (not self.search_query):
            return
        kb_content_path = Path(f"knowledge/kb_content_{self.lang}.json")
        if kb_content_path.exists():
            with open(kb_content_path, "r") as f:
                content = json.load(f)
                self._articles = content.get("articles", [])
                self._faqs = content.get("faq_items", [])
        help_registry_path = Path("knowledge/help_registry.json")
        if help_registry_path.exists():
            with open(help_registry_path, "r") as f:
                self._settings = json.load(f)
        openapi_spec_path = Path("knowledge/openapi_spec_stub.json")
        if openapi_spec_path.exists():
            with open(openapi_spec_path, "r") as f:
                spec = json.load(f)
                self._api_docs = []
                for path, methods in spec.get("paths", {}).items():
                    for method, details in methods.items():
                        if "operationId" in details:
                            self._api_docs.append(
                                {
                                    "operation_id": details["operationId"],
                                    "summary": details.get("summary", ""),
                                    "path": path,
                                    "method": method.upper(),
                                }
                            )
        self._is_loaded = True

    @rx.event
    def on_load_kb_content(self):
        self._load_content()

    @rx.var
    def guide_categories(self) -> dict[str, list[Article]]:
        self._load_content()
        categories = {}
        for article in self._articles:
            cat = article["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(article)
        return categories

    @rx.var
    def faq_categories(self) -> list[tuple[str, list[FaqItem]]]:
        self._load_content()
        categories = {}
        for faq in self._faqs:
            cat = faq.get("category", "General")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(faq)
        return sorted(categories.items())

    @rx.var
    def current_article(self) -> Article | None:
        self._load_content()
        slug = self.router.page.params.get("slug", "")
        for article in self._articles:
            if article["slug"] == slug:
                return article
        return None

    @rx.var
    def search_results(self) -> list[SearchResult]:
        if not self.search_query.strip():
            return []
        self._load_content()
        query = self.search_query.lower().strip()
        for key, value in self._synonyms.items():
            query = query.replace(key, value)
        results = []
        for article in self._articles:
            score = 0
            if query in article["title"].lower():
                score += 10
            if query in article["summary"].lower():
                score += 5
            if score > 0:
                results.append(
                    {
                        "type": "article",
                        "title": article["title"],
                        "summary": article["summary"],
                        "route": f"/kb/guides/{article['slug']}",
                        "score": score,
                        "data": article,
                    }
                )
        for faq in self._faqs:
            if query in faq["question"].lower():
                results.append(
                    {
                        "type": "faq",
                        "title": faq["question"],
                        "summary": faq["answer_html"][:150] + "...",
                        "route": f"/kb/faq#{faq['slug']}",
                        "score": 8,
                        "data": faq,
                    }
                )
        for setting in self._settings:
            score = 0
            if query in setting["title"].lower():
                score += 12
            if query in setting["purpose"].lower():
                score += 6
            if score > 0:
                results.append(
                    {
                        "type": "setting",
                        "title": setting["title"],
                        "summary": setting["purpose"],
                        "route": setting["route"],
                        "score": score,
                        "data": setting,
                    }
                )
        for api_doc in self._api_docs:
            score = 0
            if query in api_doc["operation_id"].lower():
                score += 9
            if query in api_doc["summary"].lower():
                score += 4
            if score > 0:
                results.append(
                    {
                        "type": "api",
                        "title": api_doc["summary"],
                        "summary": f"{api_doc['method']} {api_doc['path']}",
                        "route": f"/api-docs#{api_doc['operation_id']}",
                        "score": score,
                        "data": api_doc,
                    }
                )
        return sorted(results, key=lambda x: x["score"], reverse=True)

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query
        if not query:
            self._is_loaded = False
        else:
            self._load_content()

    @rx.event
    def set_lang(self, lang: str):
        self.lang = lang
        self._is_loaded = False
        self._load_content()

    @rx.event
    def go_to_and_focus(self, route: str, selector: str):
        yield rx.redirect(route)
        yield rx.call_script(
            f"\n            setTimeout(() => {{\n                const el = document.querySelector('{selector}');\n                if (el) {{\n                    el.focus();\n                    el.style.transition = 'all 0.3s ease-in-out';\n                    el.style.boxShadow = '0 0 0 3px var(--accent-cyan)';\n                    setTimeout(() => {{ el.style.boxShadow = ''; }}, 2000);\n                }}\n            }}, 500);\n            "
        )