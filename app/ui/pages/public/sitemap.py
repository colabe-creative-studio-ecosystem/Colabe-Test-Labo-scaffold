import reflex as rx
from app.core.settings import settings
import xml.etree.ElementTree as ET
from datetime import datetime
from fastapi import Response


async def sitemap_index() -> Response:
    """Generates the sitemap index XML."""
    sitemap_index_el = ET.Element(
        "sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    )
    sitemaps = [
        "sitemap-public.xml",
        "sitemap-kb.xml",
        "sitemap-api.xml",
        "sitemap-trust.xml",
    ]
    lastmod = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    for sitemap_path in sitemaps:
        sitemap_el = ET.SubElement(sitemap_index_el, "sitemap")
        ET.SubElement(
            sitemap_el, "loc"
        ).text = f"{settings.PUBLIC_BASE_URL}/{sitemap_path}"
        ET.SubElement(sitemap_el, "lastmod").text = lastmod
    xml_string = ET.tostring(sitemap_index_el, encoding="unicode")
    return Response(
        content=f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_string}',
        headers={"Content-Type": "application/xml"},
    )