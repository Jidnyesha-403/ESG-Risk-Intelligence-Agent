import os
from typing import Dict, Any, List
from urllib.parse import urlparse
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

def generate_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 4 (Report Generator): Uses Llama 3.1 via Groq API to synthesize a structured,
    one-page ESG Risk Report with citations, risk scores, and benchmark comparisons.
    """
    company_name = state.get("company_name", "")
    scraped_content = state.get("scraped_content", [])
    risk_classifications = state.get("risk_classifications", [])
    rag_context = state.get("rag_context", "")
    
    print(f"Report Generator Agent: Generating final ESG Risk Report for '{company_name}'...")
    
    # Calculate quantitative aggregate risk counts for prompt context
    e_counts = {"Low": 0, "Medium": 0, "High": 0}
    s_counts = {"Low": 0, "Medium": 0, "High": 0}
    g_counts = {"Low": 0, "Medium": 0, "High": 0}
    
    for rc in risk_classifications:
        e_counts[rc.get("E_risk", "Low")] += 1
        s_counts[rc.get("S_risk", "Low")] += 1
        g_counts[rc.get("G_risk", "Low")] += 1
        
    def calculate_score(counts):
        total = sum(counts.values())
        if total == 0:
            return "Low"
        # Weighting: High = 3, Medium = 2, Low = 1
        weighted_sum = counts["Low"] * 1 + counts["Medium"] * 2 + counts["High"] * 3
        avg = weighted_sum / total
        if avg >= 2.33:
            return "High"
        elif avg >= 1.5:
            return "Medium"
        else:
            return "Low"
            
    avg_e = calculate_score(e_counts)
    avg_s = calculate_score(s_counts)
    avg_g = calculate_score(g_counts)
    
    # Format classification context for the LLM
    classifications_summary = ""
    for idx, rc in enumerate(risk_classifications, 1):
        link = rc.get("link", "#")
        try:
            domain = urlparse(link).netloc
            if domain.startswith("www."):
                domain = domain[4:]
            if not domain:
                domain = "web-source"
        except Exception:
            domain = "web-source"
            
        classifications_summary += (
            f"[{idx}] Title: {rc.get('title')}\n"
            f"Domain: {domain}\n"
            f"Link: {link}\n"
            f"Snippet: {rc.get('snippet')}\n"
            f"Classified Risks -> E: {rc.get('E_risk')}, S: {rc.get('S_risk')}, G: {rc.get('G_risk')}\n\n"
        )
        
    # Groq API details
    api_key = os.environ.get("GROQ_API_KEY")
    
    report_markdown = ""
    
    if api_key and api_key.strip() and api_key != "your_groq_api_key_here":
        try:
            print("Using Groq API to generate report...")
            llm = ChatGroq(
                model_name="llama-3.1-8b-instant",
                groq_api_key=api_key,
                temperature=0.2
            )
            
            system_prompt = (
                "You are an expert ESG (Environmental, Social, and Governance) Risk Analyst. "
                "Your task is to synthesize a structured, executive-ready, one-page ESG Risk Report for a company. "
                "Include risk badges/scores, list recent news items, quote historical industry benchmarks, "
                "and explain key risks and comparisons to benchmarks. Always cite your sources with numerical markers corresponding to the news links provided."
            )
            
            user_prompt = f"""
Generate an ESG Risk Report for the company: **{company_name}**.

Here is the data gathered by the other agents:

1. RECENT NEWS SNIPPETS AND CLASSIFIED RISKS:
{classifications_summary}

2. QUANTITATIVE SCORE SUMMARY (derived by classifier agent):
- Environmental (E) Risk Level: {avg_e} (Low counts: {e_counts['Low']}, Med: {e_counts['Medium']}, High: {e_counts['High']})
- Social (S) Risk Level: {avg_s} (Low counts: {s_counts['Low']}, Med: {s_counts['Medium']}, High: {s_counts['High']})
- Governance (G) Risk Level: {avg_g} (Low counts: {g_counts['Low']}, Med: {g_counts['Medium']}, High: {g_counts['High']})

3. HISTORICAL INDUSTRY ESG BENCHMARK STANDARDS (from ChromaDB):
{rag_context}

---
Requirements for the report:
- Write it in clean, professional markdown.
- Include a clear header: "ESG RISK INTELLIGENCE REPORT: {company_name}".
- Output a structured executive summary.
- List individual sections for Environmental (E), Social (S), and Governance (G). In each, summarize the current findings, cite the source number (e.g., [1], [2]), and contrast it against the historical industry benchmark.
- CRITICAL: Add clear visual dividers (`---`) between the Environmental (E), Social (S), and Governance (G) dimension analysis sections in the report body.
- Conclude with a 'Strategic Recommendations' section for the company's management.
- Provide a 'Sources & Citations' footer at the bottom as a numbered reference list where each citation is on its own line formatted EXACTLY like this:
  [1] [Source Title](URL) — domain.com (Risk Classification: E: Medium, S: Low, G: High)
- Keep it concise, high-impact, and fitting in a single page or view.
"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = llm.invoke(messages)
            report_markdown = post_process_report(response.content, company_name, risk_classifications)
            print("Report generated successfully using Groq.")
            
        except Exception as e:
            print(f"Error using Groq API: {e}. Falling back to rule-based template generation.")
            report_markdown = get_fallback_report(company_name, avg_e, avg_s, avg_g, risk_classifications, rag_context)
    else:
        print("Groq API Key not configured. Using rule-based template generation.")
        report_markdown = get_fallback_report(company_name, avg_e, avg_s, avg_g, risk_classifications, rag_context)
        
    return {"final_report": report_markdown}

def post_process_report(report_markdown: str, company_name: str, risk_classifications: List[Dict[str, Any]]) -> str:
    """
    Ensures visual dividers exist between E, S, G sections and replaces/appends
    the exact numbered citation list format requested.
    """
    import re
    
    # 1. Clean existing sources section if present
    cleaned = re.split(r'(?i)\n(?:\#+\s*|\*\*)?sources?\s*(?:&|and)?\s*citations?', report_markdown)[0].strip()
    
    # 2. Add visual dividers before major section headings if not already present
    headers = [
        r"(?i)\n+(\#+|\*\*)[^\n]*environmental[^\n]*",
        r"(?i)\n+(\#+|\*\*)[^\n]*social[^\n]*",
        r"(?i)\n+(\#+|\*\*)[^\n]*governance[^\n]*",
        r"(?i)\n+(\#+|\*\*)[^\n]*strategic recommendations[^\n]*"
    ]
    for h_pat in headers:
        def add_divider(match):
            matched_text = match.group(0)
            if "---" in matched_text:
                return matched_text
            return f"\n\n---\n{matched_text.lstrip()}"
        cleaned = re.sub(h_pat, add_divider, cleaned, count=1)

    # 3. Format citations perfectly
    citation_lines = ["\n\n---\n\n## 🔗 Sources & Citations\n"]
    for idx, rc in enumerate(risk_classifications, 1):
        link = rc.get("link", "#").strip()
        title = rc.get("title", "No Title").strip()
        try:
            domain = urlparse(link).netloc
            if domain.startswith("www."):
                domain = domain[4:]
            if not domain:
                domain = "web-source"
        except Exception:
            domain = "web-source"
            
        e_r = rc.get("E_risk", "Low")
        s_r = rc.get("S_risk", "Low")
        g_r = rc.get("G_risk", "Low")
        
        citation_lines.append(f"[{idx}] [{title}]({link}) — {domain} (Risk Classification: E: {e_r}, S: {s_r}, G: {g_r})")
        
    return cleaned + "\n" + "\n".join(citation_lines)

def get_fallback_report(company_name: str, e_risk: str, s_risk: str, g_risk: str, risk_classifications: List[Dict[str, Any]], rag_context: str) -> str:
    """
    Generates a beautifully formatted markdown report using a deterministic template
    when Groq LLM API is unavailable.
    """
    e_badge = "🟢 LOW" if e_risk == "Low" else ("🟡 MEDIUM" if e_risk == "Medium" else "🔴 HIGH")
    s_badge = "🟢 LOW" if s_risk == "Low" else ("🟡 MEDIUM" if s_risk == "Medium" else "🔴 HIGH")
    g_badge = "🟢 LOW" if g_risk == "Low" else ("🟡 MEDIUM" if g_risk == "Medium" else "🔴 HIGH")
    
    # Extract benchmark info
    benchmark_lines = rag_context.split('\n')
    industry_info = benchmark_lines[0] if benchmark_lines else "General Standards"
    
    # Format E, S, G details based on the scraped content and classifications
    e_findings = []
    s_findings = []
    g_findings = []
    citations = []
    
    for idx, rc in enumerate(risk_classifications, 1):
        link = rc.get("link", "#")
        title = rc.get("title", "No Title")
        try:
            domain = urlparse(link).netloc
            if domain.startswith("www."):
                domain = domain[4:]
            if not domain:
                domain = "web-source"
        except Exception:
            domain = "web-source"
            
        e_r = rc.get("E_risk", "Low")
        s_r = rc.get("S_risk", "Low")
        g_r = rc.get("G_risk", "Low")
        
        citations.append(f"[{idx}] [{title}]({link}) — {domain} (Risk Classification: E: {e_r}, S: {s_r}, G: {g_r})")
        
        # Environmental
        if e_r != "Low" or "environment" in title.lower() or "carbon" in rc.get("snippet", "").lower():
            e_findings.append(f"- **{title}**: {rc.get('snippet')} (Risk: {e_r}) [{idx}]")
        # Social
        if s_r != "Low" or "labor" in title.lower() or "safety" in rc.get("snippet", "").lower():
            s_findings.append(f"- **{title}**: {rc.get('snippet')} (Risk: {s_r}) [{idx}]")
        # Governance
        if g_r != "Low" or "board" in title.lower() or "governance" in title.lower() or "audit" in rc.get("snippet", "").lower():
            g_findings.append(f"- **{title}**: {rc.get('snippet')} (Risk: {g_r}) [{idx}]")
            
    # Add generic if empty
    if not e_findings:
        e_findings.append("- No significant environmental controversies or announcements found in recent search summaries.")
    if not s_findings:
        s_findings.append("- No significant labor, community, or social controversies found in recent search summaries.")
    if not g_findings:
        g_findings.append("- Board structure and disclosure schedules remain stable with no major compliance incidents.")

    e_findings_str = "\n".join(e_findings)
    s_findings_str = "\n".join(s_findings)
    g_findings_str = "\n".join(g_findings)
    citations_str = "\n".join(citations)
    
    report = f"""# ESG Risk Intelligence Report: {company_name}

## 📊 Executive Risk Score Dashboard
| ESG Dimension | Aggregated Risk Score | Industry Benchmark Context |
| :--- | :---: | :--- |
| **Environmental (E)** | {e_badge} | Compared against {industry_info} |
| **Social (S)** | {s_badge} | Compared against {industry_info} |
| **Governance (G)** | {g_badge} | Compared against {industry_info} |

---

## 🍃 Environmental (E) Dimension Analysis
### Recent Findings
{e_findings_str}

### Industry Benchmark Comparison
The retrieved benchmark indicates that low-risk companies in this sector target concrete carbon neutrality and low emission intensity. {company_name} is currently aligned with these targets unless flagged as Medium/High above due to recent incidents or regulatory investigations.

---

## 👥 Social (S) Dimension Analysis
### Recent Findings
{s_findings_str}

### Industry Benchmark Comparison
Industry standards dictate that high-performing companies must run 100% independent audits of supply chain facilities and maintain zero workplace fatalities. Any labor disputes, safety audits, or worker union concerns flagged above should be mitigated immediately to maintain industry standards.

---

## 🏛️ Governance (G) Dimension Analysis
### Recent Findings
{g_findings_str}

### Industry Benchmark Comparison
Corporate governance guidelines require strong independent director representation, rigorous audit controls, and executive compensation tied to sustainability performance metrics. Governance risks remain low unless recent disclosures indicate regulatory friction, executive scandals, or financial audits discrepancies.

---

## 💡 Strategic Recommendations
1. **Controversy Management**: Establish a dedicated ESG response taskforce to investigate and publicly address any specific controversies flagged with "Medium" or "High" risk in this analysis.
2. **Benchmark Alignment**: Formally align emissions reporting and labor audits to match the standards set in the historical {industry_info} benchmarks.
3. **Groq Integration Note**: To leverage dynamic, AI-synthesized analysis, ensure a valid `GROQ_API_KEY` is specified in your environment or Streamlit UI settings.

---

## 🔗 Sources & Citations
{citations_str}
"""
    return report
