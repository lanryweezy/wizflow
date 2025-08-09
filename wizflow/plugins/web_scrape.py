"""
Web Scrape Action Plugin for WizFlow
"""

from typing import Dict, Any, List
from .base import ActionPlugin


class WebScrapePlugin(ActionPlugin):
    """
    An action plugin to scrape content from websites.
    """

    @property
    def name(self) -> str:
        return "web_scrape"

    @property
    def required_imports(self) -> List[str]:
        return ["import requests", "from bs4 import BeautifulSoup"]

    def get_function_definition(self) -> str:
        return '''
def scrape_web(url, selector=None, variables={}, creds={}):
    """Scrape web content"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        if selector:
            elements = soup.select(selector)
            content = [elem.get_text().strip() for elem in elements]
        else:
            content = soup.get_text().strip()

        logger.info(f"🕷️  Scraped content from {url}")
        if content:
            return {"scraped_content": content}
        return None
    except Exception as e:
        logger.error(f"❌ Web scraping failed: {e}")
        return None
'''

    def get_function_call(self, config: Dict[str, Any]) -> str:
        url = self._resolve_template(config.get('url', 'https://example.com'))
        selector = self._resolve_template(config.get('selector'))

        call_parts = [f"url={url}"]
        if config.get('selector'):
            call_parts.append(f"selector={selector}")

        return f"scrape_web({', '.join(call_parts)}, variables=variables, creds=credentials)"
