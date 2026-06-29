from langgraph.graph import StateGraph, START, END
from src.agents.state import ESGWorkflowState
from src.agents.collector import collect_data
from src.agents.classifier import classify_risks
from src.agents.retriever import retrieve_benchmarks
from src.agents.generator import generate_report

def create_esg_workflow():
    # 1. Initialize StateGraph with our state schema
    workflow = StateGraph(ESGWorkflowState)
    
    # 2. Add nodes representing each agent step
    workflow.add_node("collect_data", collect_data)
    workflow.add_node("classify_risks", classify_risks)
    workflow.add_node("retrieve_benchmarks", retrieve_benchmarks)
    workflow.add_node("generate_report", generate_report)
    
    # 3. Add edges defining the linear sequential flow
    workflow.add_edge(START, "collect_data")
    workflow.add_edge("collect_data", "classify_risks")
    workflow.add_edge("classify_risks", "retrieve_benchmarks")
    workflow.add_edge("retrieve_benchmarks", "generate_report")
    workflow.add_edge("generate_report", END)
    
    # 4. Compile into a single runnable graph
    return workflow.compile()

def run_esg_pipeline(company_name: str, groq_api_key: str = None) -> dict:
    """
    Orchestrator entrypoint: Runs the full ESG multi-agent pipeline for a company.
    """
    # Create the workflow graph
    app = create_esg_workflow()
    
    # Temporarily set Groq API key in environment if provided via UI
    import os
    old_groq_key = os.environ.get("GROQ_API_KEY")
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key
        
    initial_state = {
        "company_name": company_name,
        "scraped_content": [],
        "risk_classifications": [],
        "rag_context": "",
        "final_report": ""
    }
    
    try:
        # Run graph execution
        final_state = app.invoke(initial_state)
    finally:
        # Restore original Groq API key in environment
        if old_groq_key is not None:
            os.environ["GROQ_API_KEY"] = old_groq_key
        elif "GROQ_API_KEY" in os.environ and groq_api_key:
            del os.environ["GROQ_API_KEY"]
            
    return final_state
