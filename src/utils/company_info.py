import wikipediaapi
import re
from typing import Dict, Any

def get_company_context(company_name: str, inferred_industry: str = "") -> Dict[str, Any]:
    """
    Fetches company background and short summary from Wikipedia using wikipedia-api.
    Falls back gracefully if page is not found or connection fails.
    """
    cleaned_name = company_name.strip()
    wiki = wikipediaapi.Wikipedia(
        user_agent="ESG-Risk-Intelligence-Agent/1.0 (sustainability-tool@example.com)",
        language="en"
    )
    
    # Try exact company name, or with common suffixes
    search_terms = [cleaned_name, f"{cleaned_name} Inc.", f"{cleaned_name} Corporation", f"{cleaned_name} (company)"]
    page = None
    
    for term in search_terms:
        try:
            p = wiki.page(term)
            if p.exists():
                page = p
                break
        except Exception:
            continue
            
    if not page or not page.exists():
        return {
            "display_name": cleaned_name.title(),
            "industry": inferred_industry.title() if inferred_industry else "Global Enterprise",
            "description": f"{cleaned_name.title()} is a major international corporation operating within the {inferred_industry.title() if inferred_industry else 'global'} market sector."
        }
        
    summary_text = page.summary.strip()
    # Split summary into sentences and take the first two sentences for a concise 2-line summary
    sentences = re.split(r'(?<=[.!?])\s+', summary_text)
    short_desc = " ".join(sentences[:2]) if len(sentences) >= 2 else (sentences[0] if sentences else summary_text[:250])
    
    # Extract clean industry title
    industry_display = inferred_industry.title() if inferred_industry else "Multinational Enterprise"
    if not inferred_industry or inferred_industry.lower() == "technology":
        # Try inferring from page summary keywords
        summary_lower = summary_text.lower()
        if any(k in summary_lower for k in ["automotive", "electric vehicle", "car"]):
            industry_display = "Automotive & Clean Tech"
        elif any(k in summary_lower for k in ["oil", "petroleum", "gas", "energy"]):
            industry_display = "Energy & Utilities"
        elif any(k in summary_lower for k in ["bank", "financial", "insurance"]):
            industry_display = "Financial Services"
        elif any(k in summary_lower for k in ["retail", "apparel", "consumer"]):
            industry_display = "Retail & Consumer Goods"
        elif any(k in summary_lower for k in ["software", "technology", "cloud", "semiconductor"]):
            industry_display = "Technology & Software"

    return {
        "display_name": page.title,
        "industry": industry_display,
        "description": short_desc
    }
