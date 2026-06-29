import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

def train_and_save_model():
    # 1. Define synthetic training data
    # We will train three separate pipelines: one for E, one for S, one for G.
    # Each will predict 'Low', 'Medium', or 'High' risk.
    
    # --- Environmental Training Data ---
    e_data = [
        # Low risk E
        ("The company launched a new carbon-neutral product line and expanded its solar array.", "Low"),
        ("Our facilities achieved 100% renewable energy use this quarter.", "Low"),
        ("We are investing in reforestation and reducing water waste in manufacturing.", "Low"),
        ("The firm is committed to net-zero carbon emissions by 2030.", "Low"),
        # Medium risk E
        ("The company paid a minor fine for exceeding wastewater discharge limits briefly.", "Medium"),
        ("An audit noted rising greenhouse gas emissions due to expanded logistics operations.", "Medium"),
        ("A small oil leak was reported at the site but was quickly contained with minimal damage.", "Medium"),
        ("Critics point out the company still relies heavily on natural gas for heating.", "Medium"),
        # High risk E
        ("A massive toxic waste spill contaminated the city's main water reservoir, causing an ecological disaster.", "High"),
        ("The corporate refinery exploded, releasing toxic chemicals and violating EPA regulations majorly.", "High"),
        ("Systemic dumping of illegal chemical waste led to a class-action lawsuit and criminal charges.", "High"),
        ("The coal plant was shut down due to continuous, severe air pollution violations.", "High"),
    ]
    
    # --- Social Training Data ---
    s_data = [
        # Low risk S
        ("The organization was ranked as a top employer for diversity and inclusion.", "Low"),
        ("We increased employee benefits and introduced mental health support programs.", "Low"),
        ("The company donated school supplies and funded local community centers.", "Low"),
        ("All supply chain partners certified they meet strict fair labor standards.", "Low"),
        # Medium risk S
        ("Employees staged a brief walkout over salary adjustments, ending after negotiations.", "Medium"),
        ("A workplace safety audit flagged minor hazards in the packing department.", "Medium"),
        ("There were reports of rising employee turnover in the customer service division.", "Medium"),
        ("Contract workers complained about lack of overtime pay, prompting a review.", "Medium"),
        # High risk S
        ("An investigation uncovered child labor and forced labor at three major supplier factories.", "High"),
        ("A factory collapse due to ignored safety codes resulted in multiple worker fatalities.", "High"),
        ("The company faced a massive lawsuit alleging systemic gender and racial discrimination.", "High"),
        ("Severe union-busting activities and harassment of union leaders were confirmed.", "High"),
    ]
    
    # --- Governance Training Data ---
    g_data = [
        # Low risk G
        ("The board appointed three new independent directors to improve oversight.", "Low"),
        ("We released our annual corporate ethics compliance training completion report.", "Low"),
        ("Shareholders approved new executive compensation limits tied to ESG targets.", "Low"),
        ("The audit committee operates fully independently with certified financial experts.", "Low"),
        # Medium risk G
        ("The company paid a settlement to resolve a dispute over delayed financial disclosures.", "Medium"),
        ("Regulators requested information regarding a brief delay in filing annual results.", "Medium"),
        ("Minor accounting discrepancies were found and corrected in the audit.", "Medium"),
        ("Shareholders questioned the dual role of the chairman and CEO in the annual meeting.", "Medium"),
        # High risk G
        ("The Chief Executive Officer was arrested and charged with insider trading and fraud.", "High"),
        ("An investigation exposed a widespread bribery scheme involving senior executives and government officials.", "High"),
        ("The CFO resigned after admitting to embezzling millions of dollars from corporate accounts.", "High"),
        ("Systemic money laundering through shell companies led to a federal investigation and heavy sanctions.", "High"),
    ]
    
    # Helper to train a pipeline
    def train_pipeline(data):
        texts, labels = zip(*data)
        # We use a simple TF-IDF + Logistic Regression pipeline
        # Using a small C to regularize and handle small data, or large C to fit the small data exactly
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english', min_df=1)),
            ('clf', LogisticRegression(C=10.0, max_iter=200, random_state=42))
        ])
        pipeline.fit(texts, labels)
        return pipeline

    print("Training E, S, and G classifiers...")
    model_e = train_pipeline(e_data)
    model_s = train_pipeline(s_data)
    model_g = train_pipeline(g_data)
    
    # Package into a single dictionary
    esg_model = {
        'E': model_e,
        'S': model_s,
        'G': model_g
    }
    
    # Save the models
    os.makedirs(os.path.join("src", "resources"), exist_ok=True)
    model_path = os.path.join("src", "resources", "esg_classifier.joblib")
    joblib.dump(esg_model, model_path)
    print(f"Model saved successfully to {model_path}!")

if __name__ == "__main__":
    train_and_save_model()
