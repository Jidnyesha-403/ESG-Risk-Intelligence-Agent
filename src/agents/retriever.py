import os
from typing import Dict, Any, List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def retrieve_benchmarks(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 3 (RAG Retriever): Searches a ChromaDB vector store of historical ESG
    benchmark reports to compare current risk against industry standards.
    """
    company_name = state.get("company_name", "")
    scraped_content = state.get("scraped_content", [])
    
    print(f"RAG Retriever Agent: Retrieving ESG benchmarks for '{company_name}'...")
    
    # 1. Infer industry based on keywords from company name and scraped content
    combined_texts = f"{company_name} " + " ".join([item.get("snippet", "") + " " + item.get("title", "") for item in scraped_content])
    combined_texts_lower = combined_texts.lower()
    
    industry = "technology"  # default
    if any(k in combined_texts_lower for k in ["oil", "gas", "refinery", "pipeline", "petroleum", "energy", "utility", "electric", "power"]):
        industry = "energy"
    elif any(k in combined_texts_lower for k in ["bank", "finance", "invest", "lending", "loan", "security", "credit", "asset"]):
        industry = "finance"
    elif any(k in combined_texts_lower for k in ["retail", "apparel", "clothing", "store", "supermarket", "consumer", "brand", "packaging"]):
        industry = "retail"
    elif any(k in combined_texts_lower for k in ["factory", "manufactur", "heavy industry", "automotive", "car", "steel", "chemical", "machinery"]):
        industry = "manufacturing"
        
    print(f"RAG Retriever Agent: Inferred industry is '{industry}'.")
    
    persist_directory = "./chroma_db"
    rag_context = ""
    
    # Check if DB directory exists
    if os.path.exists(persist_directory):
        try:
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            db = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
            
            # Retrieve documents
            # First, try to filter by the inferred industry
            results = db.similarity_search(
                f"ESG risk factors and performance benchmarks for {industry} industry",
                k=2,
                filter={"industry": industry}
            )
            
            # If no results, do a broad similarity search
            if not results:
                results = db.similarity_search(
                    f"ESG risk factors and performance benchmarks for {company_name}",
                    k=2
                )
                
            if results:
                rag_context = "\n\n".join([doc.page_content for doc in results])
                print(f"RAG Retriever Agent: Retrieved {len(results)} benchmark documents.")
            else:
                print("RAG Retriever Agent: No benchmark documents found in ChromaDB.")
                
        except Exception as e:
            print(f"RAG Retriever Agent error querying database: {e}. Using fallback benchmark.")
            rag_context = get_fallback_benchmark(industry)
    else:
        print("RAG Retriever Agent: ChromaDB directory not found. Using fallback benchmark.")
        rag_context = get_fallback_benchmark(industry)
        
    if not rag_context:
        rag_context = get_fallback_benchmark(industry)
        
    return {"rag_context": rag_context}

def get_fallback_benchmark(industry: str) -> str:
    """
    Returns hardcoded benchmark data if database lookup fails.
    """
    benchmarks = {
        "technology": (
            "Technology Industry ESG Benchmark (Fallback):\n"
            "- Environmental: Focuses on data center energy consumption and hardware supply chain emissions.\n"
            "- Social: Focuses on supplier factory labor audits and diversity and inclusion metrics.\n"
            "- Governance: Focuses on data privacy, cybersecurity, and board independent audit controls."
        ),
        "energy": (
            "Energy & Utilities ESG Benchmark (Fallback):\n"
            "- Environmental: Focuses on carbon intensity (Scope 1 and 2), methane leakages, and clean transition plans.\n"
            "- Social: Focuses on operational health and safety, zero employee fatalities, and community relations.\n"
            "- Governance: Focuses on linking executive compensation to decarbonization targets."
        ),
        "finance": (
            "Financial Services ESG Benchmark (Fallback):\n"
            "- Environmental: Focuses on financed emissions (Scope 3 Category 15) and fossil fuel policies.\n"
            "- Social: Focuses on fair lending, financial inclusion, and community investing.\n"
            "- Governance: Focuses on anti-money laundering (AML) controls, transparency, and greenwashing risks."
        ),
        "retail": (
            "Retail & Consumer Goods ESG Benchmark (Fallback):\n"
            "- Environmental: Focuses on sustainable material sourcing and plastic packaging waste reduction.\n"
            "- Social: Focuses on labor rights/fair wages in the supplier network and supply chain audits.\n"
            "- Governance: Focuses on supply chain traceability and transparent marketing."
        ),
        "manufacturing": (
            "Manufacturing & Heavy Industry ESG Benchmark (Fallback):\n"
            "- Environmental: Focuses on air emissions, waste management, and recycling of hazardous waste.\n"
            "- Social: Focuses on employee injury rates, workplace safety compliance, and labor training.\n"
            "- Governance: Focuses on quality control audits, product safety, and risk disclosures."
        )
    }
    return benchmarks.get(industry, benchmarks["technology"])
