import os
from dotenv import load_dotenv
from src.agents.graph import run_esg_pipeline

def main():
    load_dotenv()
    print("Starting integration test for ESG multi-agent pipeline...")
    
    # We will test using "Tesla" as the target company
    # The pipeline should fallback gracefully if GROQ_API_KEY is not set.
    company_name = "Tesla"
    
    # Check if Groq key exists, otherwise print a notice
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if not groq_key:
        print("Note: GROQ_API_KEY not found in environment. The pipeline will use rule-based fallback template report.")
    else:
        print("GROQ_API_KEY found. Running pipeline with Llama 3.1 LLM.")
        
    print(f"Running pipeline for '{company_name}'...")
    try:
        results = run_esg_pipeline(company_name, groq_key)
        
        print("\n--- Pipeline Run Results ---")
        print(f"Company: {results.get('company_name')}")
        print(f"Scraped Items Count: {len(results.get('scraped_content', []))}")
        print(f"Classified Items Count: {len(results.get('risk_classifications', []))}")
        print(f"RAG Context Length: {len(results.get('rag_context', ''))} characters")
        print("\n--- Final Report saved to test_report.md ---")
        with open("test_report.md", "w", encoding="utf-8") as f:
            f.write(results.get("final_report", ""))
        print("----------------------------\n")
        
        # Verify basic expected keys
        assert results.get("company_name") == company_name, "Company name mismatch!"
        assert len(results.get("scraped_content", [])) > 0, "No content scraped!"
        assert len(results.get("risk_classifications", [])) > 0, "No content classified!"
        assert len(results.get("rag_context", "")) > 0, "RAG context is empty!"
        assert len(results.get("final_report", "")) > 0, "Final report is empty!"
        
        print("Success: All pipeline stages executed correctly!")
    except Exception as e:
        print(f"Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
