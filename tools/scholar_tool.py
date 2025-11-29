"""
Google Scholar search tool for supplementary literature discovery.
Complements PubMed with broader academic sources.
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def search_scholar(query: str, max_results: int = 6) -> Dict[str, Any]:
    """
    Search Google Scholar for academic publications.
    
    Args:
        query: Search terms
        max_results: Maximum number of results to retrieve
        
    Returns:
        Dictionary containing search status and papers list
    """
    try:
        url = "https://scholar.google.com/scholar"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        params = {
            "q": query,
            "hl": "en",
            "as_ylo": 2024,
            "as_yhi": 2025
        }

        response = requests.get(url, params=params, headers=headers, timeout=12)
        
        if response.status_code != 200:
            logger.warning(f"Scholar returned status {response.status_code}")
            return {
                "status": "error",
                "message": f"HTTP {response.status_code}",
                "papers": []
            }

        soup = BeautifulSoup(response.text, "html.parser")
        papers = []

        for item in soup.select(".gs_r.gs_or.gs_scl")[:max_results]:
            title_tag = item.select_one(".gs_rt a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            
            snippet = item.select_one(".gs_rs")
            snippet_text = snippet.get_text(strip=True) if snippet else "No abstract available"
            
            info = item.select_one(".gs_a")
            info_text = info.get_text(strip=True) if info else ""
            
            year = "2024"
            for part in info_text.split("-"):
                part = part.strip()
                if part.isdigit() and 2023 <= int(part) <= 2025:
                    year = part
                    break

            papers.append({
                "title": title,
                "link": link,
                "snippet": snippet_text,
                "year": year,
                "source": "Google Scholar",
                "info": info_text
            })

        logger.info(f"Scholar search returned {len(papers)} results")
        
        return {
            "status": "success",
            "papers": papers,
            "total_found": len(papers)
        }

    except Exception as e:
        logger.error(f"Scholar search failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "papers": []
        }


# Test function
if __name__ == "__main__":
    result = search_scholar("pembrolizumab melanoma 2024", max_results=5)
    
    if result["status"] == "success":
        print(f"Found {len(result['papers'])} papers")
        for i, paper in enumerate(result["papers"], 1):
            print(f"\n{i}. {paper['title']}")
            print(f"   Year: {paper['year']}")
            print(f"   Link: {paper['link'][:60]}...")
    else:
        print(f"Search failed: {result.get('message', result.get('error'))}")