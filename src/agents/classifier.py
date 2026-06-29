import os
import joblib
from typing import Dict, Any, List

def classify_risks(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 2 (Risk Classifier): Uses the trained Scikit-learn model to classify scraped
    content snippets as Low/Medium/High risk across E, S, and G dimensions separately.
    """
    scraped_content = state.get("scraped_content", [])
    if not scraped_content:
        return {"risk_classifications": []}
        
    print(f"Risk Classifier Agent: Classifying {len(scraped_content)} content snippets...")
    
    model_path = os.path.join("src", "resources", "esg_classifier.joblib")
    model = None
    
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            print("Successfully loaded Scikit-learn ESG model.")
        except Exception as e:
            print(f"Failed to load Scikit-learn model: {e}. Falling back to rule-based classifier.")
    else:
        print("Model file not found. Falling back to rule-based classifier.")
        
    classifications = []
    
    for item in scraped_content:
        text = item.get("snippet", "")
        title = item.get("title", "")
        combined_text = f"{title}. {text}"
        
        if model:
            try:
                e_risk = model['E'].predict([combined_text])[0]
                s_risk = model['S'].predict([combined_text])[0]
                g_risk = model['G'].predict([combined_text])[0]
            except Exception as e:
                print(f"Prediction failed for a snippet: {e}. Using fallback classification.")
                e_risk, s_risk, g_risk = fallback_classifier(combined_text)
        else:
            e_risk, s_risk, g_risk = fallback_classifier(combined_text)
            
        classifications.append({
            "title": title,
            "snippet": text,
            "link": item.get("link", ""),
            "E_risk": e_risk,
            "S_risk": s_risk,
            "G_risk": g_risk
        })
        
    print(f"Risk Classifier Agent: Completed classification for {len(classifications)} snippets.")
    return {"risk_classifications": classifications}

def fallback_classifier(text: str) -> tuple[str, str, str]:
    """
    Rule-based keyword fallback classifier for ESG risks in case the ML model is missing or fails.
    """
    text_lower = text.lower()
    
    # 1. Environmental
    e_risk = "Low"
    e_high_keywords = ["toxic spill", "explosion", "dumping", "severe pollution", "oil spill", "illegal waste"]
    e_med_keywords = ["fine", "exceeding", "increase emission", "greenhouse gas", "coal rely", "carbon footprint"]
    if any(k in text_lower for k in e_high_keywords):
        e_risk = "High"
    elif any(k in text_lower for k in e_med_keywords):
        e_risk = "Medium"
        
    # 2. Social
    s_risk = "Low"
    s_high_keywords = ["child labor", "forced labor", "fatalities", "discrimination", "harassment", "accident", "sweatshop"]
    s_med_keywords = ["protest", "strike", "walkout", "safety audit", "turnover", "workplace safety", "overtime"]
    if any(k in text_lower for k in s_high_keywords):
        s_risk = "High"
    elif any(k in text_lower for k in s_med_keywords):
        s_risk = "Medium"
        
    # 3. Governance
    g_risk = "Low"
    g_high_keywords = ["arrested", "insider trading", "fraud", "bribery", "money laundering", "embezzling", "scandal"]
    g_med_keywords = ["lawsuit", "discrepancies", "delay disclosure", "audit error", "settled", "dispute"]
    if any(k in text_lower for k in g_high_keywords):
        g_risk = "High"
    elif any(k in text_lower for k in g_med_keywords):
        g_risk = "Medium"
        
    return e_risk, s_risk, g_risk
