"""
PubMed search tool using pymed library.
Provides structured search functionality for oncology literature.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
from pymed import PubMed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_pubmed(
    query: str,
    max_results: int = 10,
    min_year: int = 2023
) -> Dict[str, Any]:
    """
    Search PubMed for oncology research papers.
    
    This function serves as a custom tool for agents to search
    medical literature. It handles the PubMed API interaction and
    returns structured results.
    
    Args:
        query: Search terms (e.g., "melanoma immunotherapy pembrolizumab")
        max_results: Maximum papers to return (default: 10)
        min_year: Earliest publication year (default: 2023)
        
    Returns:
        Dictionary containing:
        - status: "success" or "error"
        - papers: List of paper dictionaries with title, authors, abstract, etc.
        - total_found: Number of papers retrieved
        - query: Original search query
        
    Example:
        result = search_pubmed("melanoma immunotherapy 2025", max_results=5)
        if result['status'] == 'success':
            for paper in result['papers']:
                print(paper['title'])
    """
    try:
        logger.info(f"Searching PubMed: '{query}' (max={max_results}, year>={min_year})")
        
        # Initialize PubMed API client
        pubmed = PubMed(tool="OncologyResearchAgent", email="research@example.com")
        
        # Add year filter to query
        search_query = f"{query} AND {min_year}:2025[dp]"
        
        # Execute search
        results = pubmed.query(search_query, max_results=max_results)
        
        papers = []
        for article in results:
            try:
                # Extract publication date
                pub_date = article.publication_date
                if pub_date:
                    if hasattr(pub_date, 'year'):
                        year = pub_date.year
                    else:
                        year = int(str(pub_date)[:4])
                else:
                    year = None
                
                # Extract author list
                authors = []
                if hasattr(article, 'authors') and article.authors:
                    for author in article.authors[:5]:  # Limit to first 5
                        if hasattr(author, 'lastname') and hasattr(author, 'firstname'):
                            name = f"{author['lastname']} {author['firstname']}"
                            authors.append(name)
                
                # Build paper dictionary
                paper = {
                    'title': article.title or 'No title available',
                    'authors': authors if authors else ['Unknown'],
                    'abstract': article.abstract or 'No abstract available',
                    'pmid': article.pubmed_id.split('\n')[0] if article.pubmed_id else 'Unknown',
                    'publication_date': str(pub_date) if pub_date else 'Unknown',
                    'year': year,
                    'journal': article.journal or 'Unknown'
                }
                
                papers.append(paper)
                
            except Exception as e:
                logger.warning(f"Error parsing article: {e}")
                continue
        
        result = {
            'status': 'success',
            'papers': papers,
            'total_found': len(papers),
            'query': query,
            'search_params': {
                'max_results': max_results,
                'min_year': min_year
            }
        }
        
        logger.info(f"Found {len(papers)} papers for '{query}'")
        return result
        
    except Exception as e:
        error_msg = f"PubMed search failed: {str(e)}"
        logger.error(error_msg)
        return {
            'status': 'error',
            'error_message': error_msg,
            'papers': [],
            'total_found': 0,
            'query': query
        }


# Test function
if __name__ == "__main__":
    print("Testing PubMed Tool\n")
    
    result = search_pubmed(
        query="melanoma immunotherapy pembrolizumab",
        max_results=5,
        min_year=2024
    )
    
    if result['status'] == 'success':
        print(f"Search successful")
        print(f"Found {result['total_found']} papers\n")
        
        for i, paper in enumerate(result['papers'], 1):
            print(f"{i}. {paper['title']}")
            print(f"   Authors: {', '.join(paper['authors'][:3])}")
            print(f"   Journal: {paper['journal']} ({paper['year']})")
            print(f"   PMID: {paper['pmid']}")
            print(f"   Abstract: {paper['abstract'][:150]}...")
            print()
    else:
        print(f"Search failed: {result['error_message']}")