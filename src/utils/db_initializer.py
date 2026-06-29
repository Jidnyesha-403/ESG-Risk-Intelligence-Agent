import os
import shutil
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

def initialize_db():
    persist_directory = "./chroma_db"
    
    # If the directory already exists, clear it first for a clean start
    if os.path.exists(persist_directory):
        print(f"Clearing existing database at {persist_directory}...")
        try:
            shutil.rmtree(persist_directory)
        except Exception as e:
            print(f"Error clearing directory: {e}")
            
    print("Initializing embeddings model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Define benchmark documents
    benchmarks = [
        Document(
            page_content=(
                "Technology Industry ESG Benchmark (2025-2026):\n"
                "Key Risks: Energy-intensive data centers (Scope 2 emissions), e-waste management, "
                "hardware supply chain labor standards, and data privacy/cybersecurity governance.\n"
                "- Environmental Standard: Low risk is defined by a Power Usage Effectiveness (PUE) below 1.2 "
                "and at least 90% renewable energy sourcing. Medium risk includes rising Scope 3 emissions from "
                "supply chains. High risk is indicated by unmitigated data center growth fueled by fossil fuels.\n"
                "- Social Standard: Low risk requires strict supplier audits covering 100% of tier-1 hardware factories "
                "and solid diversity metrics. High risk corresponds to human rights abuses or safety issues at chip factories.\n"
                "- Governance Standard: Low risk demands transparent data usage disclosures and independent board audits. "
                "High risk involves antitrust convictions or major data breaches involving user data leakages."
            ),
            metadata={"industry": "technology", "sector": "Technology, Media & Telecom"}
        ),
        Document(
            page_content=(
                "Energy, Oil & Gas ESG Benchmark (2025-2026):\n"
                "Key Risks: Greenhouse gas (GHG) footprint (Scope 1 and 2), methane leakages, environmental degradation, "
                "worker health and safety, and transition-risk planning.\n"
                "- Environmental Standard: Low risk requires a concrete transition plan to net-zero by 2045, "
                "methane leakage rates below 0.15% of throughput, and minimal water footprint. Medium risk indicates "
                "compliance with standard environmental laws but no active clean energy transition. High risk refers to "
                "recurrent toxic spills and heavy carbon intensity without offset plans.\n"
                "- Social Standard: Low risk requires zero fatalities in operations and robust local community outreach. "
                "High risk entails severe safety compliance failures leading to major workplace accidents.\n"
                "- Governance Standard: Low risk requires executive compensation tied to decarbonization targets. "
                "High risk is marked by regulatory fines for hidden emissions or corruption in securing drilling rights."
            ),
            metadata={"industry": "energy", "sector": "Energy & Utilities"}
        ),
        Document(
            page_content=(
                "Financial Services and Banking ESG Benchmark (2025-2026):\n"
                "Key Risks: Financed emissions (Scope 3 Category 15), ESG integration in lending/investing, "
                "anti-money laundering (AML) controls, and executive compensation governance.\n"
                "- Environmental Standard: Low risk banks have explicit policies phase-out financing for thermal coal "
                "and new oil/gas exploration, alongside active green bond underwriting. Medium risk banks have general "
                "sustainability pledges but continue to fund fossil-fuel legacy projects. High risk banks face major "
                "investments in high-polluting sectors with zero restrictions.\n"
                "- Social Standard: Low risk involves strong community reinvestment and transparent consumer lending. "
                "High risk is associated with predatory lending or financing projects that violate indigenous lands.\n"
                "- Governance Standard: Low risk requires absolute transparency in lobbying expenditures and strong AML controls. "
                "High risk features greenwashing fraud, insider trading scandals, or severe AML compliance failures."
            ),
            metadata={"industry": "finance", "sector": "Financials"}
        ),
        Document(
            page_content=(
                "Retail, Apparel & Consumer Goods ESG Benchmark (2025-2026):\n"
                "Key Risks: Sustainable material sourcing (cotton, palm oil), plastic packaging waste, "
                "human rights/fair wages in agricultural and apparel supply chains, and safety product recalls.\n"
                "- Environmental Standard: Low risk means using 100% organic/recycled materials and a circular "
                "packaging pipeline. Medium risk is marked by slow progress in reducing single-use plastics. "
                "High risk involves heavy chemical runoff from textile dying and high plastic intensity.\n"
                "- Social Standard: Low risk is achieved by auditing 100% of supplier factories for living wage standards. "
                "High risk is marked by sweatshop labor, child labor, or unsafe working environments in supply chain factories.\n"
                "- Governance Standard: Low risk requires transparent reporting of product recalls and supply chain traceability. "
                "High risk includes deceptive advertising or masking labor violations in supply networks."
            ),
            metadata={"industry": "retail", "sector": "Consumer Discretionary/Staples"}
        ),
        Document(
            page_content=(
                "Manufacturing & Heavy Industry ESG Benchmark (2025-2026):\n"
                "Key Risks: Scope 1 emissions, waste management (hazardous waste), occupational health and safety, "
                "and product quality control.\n"
                "- Environmental Standard: Low risk is marked by high energy efficiency, waste-to-energy conversion, "
                "and strict hazardous waste recycling. High risk corresponds to illegal chemical dumping or massive sulfur dioxide emissions.\n"
                "- Social Standard: Low risk features low injury rates and structured employee upskilling programs. "
                "High risk corresponds to unsafe operating conditions, lack of safety gear, and worker exploitation.\n"
                "- Governance Standard: Low risk requires comprehensive quality management systems and transparent risk reporting. "
                "High risk is characterized by product safety cover-ups, corruption, and systemic tax avoidance."
            ),
            metadata={"industry": "manufacturing", "sector": "Industrials"}
        )
    ]
    
    print("Creating and seeding Chroma vector database...")
    db = Chroma.from_documents(
        documents=benchmarks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print(f"Database initialized and persisted successfully to {persist_directory}!")

if __name__ == "__main__":
    initialize_db()
