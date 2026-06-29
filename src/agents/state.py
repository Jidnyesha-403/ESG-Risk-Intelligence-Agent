from typing import List, Dict, Any, TypedDict

class ESGWorkflowState(TypedDict):
    """
    State representing the data passed between agents in the ESG Risk Intelligence workflow.
    """
    company_name: str
    scraped_content: List[Dict[str, Any]]
    risk_classifications: List[Dict[str, Any]]
    rag_context: str
    final_report: str
