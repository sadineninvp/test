"""
Web Tools - Web search and URL fetching functionality
"""

from typing import Dict, Any, Optional
from .logger import ActionLogger


class WebTools:
    """
    Web search and URL fetching tools
    """
    
    def __init__(self, logger: Optional[ActionLogger] = None):
        """
        Initialize web tools
        
        Args:
            logger: ActionLogger instance (creates new if not provided)
        """
        self.logger = logger or ActionLogger()
    
    def web_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search the web using DuckDuckGo and return results.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 5)
            
        Returns:
            Dict with:
                - success: bool
                - results: List of search results
                - query: str
        """
        try:
            from ddgs import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                
                if not results:
                    self.logger.log(
                        action_type="web_search",
                        action=f"web_search('{query}')",
                        result="No results found",
                        success=False
                    )
                    return {
                        "success": False,
                        "results": [],
                        "query": query,
                        "error": f"No results found for '{query}'"
                    }
                
                # Format results
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        "title": result.get('title', 'No title'),
                        "body": result.get('body', 'No description'),
                        "url": result.get('href', 'No URL')
                    })
                
                # Log the action
                self.logger.log(
                    action_type="web_search",
                    action=f"web_search('{query}')",
                    result=f"Found {len(formatted_results)} results",
                    success=True,
                    metadata={"max_results": max_results, "results_count": len(formatted_results)}
                )
                
                return {
                    "success": True,
                    "results": formatted_results,
                    "query": query,
                    "count": len(formatted_results)
                }
                
        except ImportError:
            error_msg = "Error: ddgs package not installed. Run: pip install ddgs"
            self.logger.log(
                action_type="web_search",
                action=f"web_search('{query}')",
                result=None,
                success=False,
                error_message=error_msg
            )
            return {
                "success": False,
                "results": [],
                "query": query,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Error searching web: {str(e)}"
            self.logger.log(
                action_type="web_search",
                action=f"web_search('{query}')",
                result=None,
                success=False,
                error_message=error_msg
            )
            return {
                "success": False,
                "results": [],
                "query": query,
                "error": error_msg
            }
    
    def fetch_url(self, url: str) -> Dict[str, Any]:
        """
        Fetch and extract text content from a URL.
        
        Args:
            url: URL to fetch (must start with http:// or https://)
            
        Returns:
            Dict with:
                - success: bool
                - content: str (extracted text)
                - url: str
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                error_msg = "Error: URL must start with http:// or https://"
                self.logger.log(
                    action_type="fetch_url",
                    action=f"fetch_url('{url}')",
                    result=None,
                    success=False,
                    error_message=error_msg
                )
                return {
                    "success": False,
                    "content": "",
                    "url": url,
                    "error": error_msg
                }
            
            # Fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, timeout=1800, headers=headers)  # 30 minutes
            response.raise_for_status()
            
            # Parse HTML and extract text
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "meta", "link"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            cleaned_text = '\n'.join(lines)
            
            # Limit to 10000 characters
            if len(cleaned_text) > 10000:
                cleaned_text = cleaned_text[:10000] + "\n\n[Content truncated to 10000 characters]"
            
            # Log the action
            self.logger.log(
                action_type="fetch_url",
                action=f"fetch_url('{url}')",
                result=f"Fetched {len(cleaned_text)} characters",
                success=True,
                metadata={"content_length": len(cleaned_text)}
            )
            
            return {
                "success": True,
                "content": cleaned_text,
                "url": url,
                "content_length": len(cleaned_text)
            }
            
        except ImportError:
            error_msg = "Error: Required packages not installed. Run: pip install requests beautifulsoup4"
            self.logger.log(
                action_type="fetch_url",
                action=f"fetch_url('{url}')",
                result=None,
                success=False,
                error_message=error_msg
            )
            return {
                "success": False,
                "content": "",
                "url": url,
                "error": error_msg
            }
        except requests.exceptions.Timeout:
            error_msg = f"Error: Request to {url} timed out"
            self.logger.log(
                action_type="fetch_url",
                action=f"fetch_url('{url}')",
                result=None,
                success=False,
                error_message=error_msg
            )
            return {
                "success": False,
                "content": "",
                "url": url,
                "error": error_msg
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching {url}: {str(e)}"
            self.logger.log(
                action_type="fetch_url",
                action=f"fetch_url('{url}')",
                result=None,
                success=False,
                error_message=error_msg
            )
            return {
                "success": False,
                "content": "",
                "url": url,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Error processing {url}: {str(e)}"
            self.logger.log(
                action_type="fetch_url",
                action=f"fetch_url('{url}')",
                result=None,
                success=False,
                error_message=error_msg
            )
            return {
                "success": False,
                "content": "",
                "url": url,
                "error": error_msg
            }

