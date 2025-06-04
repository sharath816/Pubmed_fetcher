import requests
import xml.etree.ElementTree as ET
import csv
import re
import os
import pandas as pd
from typing import List, Dict 

PUBMED_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def fetch_paper_ids(query: str) -> List[str]:
    """Fetch PubMed IDs for a given query."""
    params = {"db": "pubmed", "term": query, "retmode": "xml", "retmax": "10"}
    response = requests.get(PUBMED_API_URL, params=params)
    
    if response.status_code != 200:
        raise Exception("Error fetching PubMed IDs")

    root = ET.fromstring(response.content)
    return [id_elem.text for id_elem in root.findall(".//Id")]

def fetch_paper_details(pubmed_ids: List[str]) -> List[Dict[str, str]]:
    """Fetch paper details from PubMed using a list of PubMed IDs."""
    if not pubmed_ids:
        return [] #if id is not present

    params = {"db": "pubmed", "id": ",".join(pubmed_ids), "retmode": "xml"}
    response = requests.get(PUBMED_FETCH_URL, params=params)
    
    if response.status_code != 200:
        raise Exception("Error fetching paper details")

    root = ET.fromstring(response.content)
    papers = []

    for article in root.findall(".//PubmedArticle"):
        title = article.find(".//ArticleTitle").text or "N/A"
        pub_date = article.find(".//PubDate/Year")
        pub_date = pub_date.text if pub_date is not None else "Unknown"
        
        authors = []
        companies = []
        corresponding_email = "N/A"

        for author in article.findall(".//Author"):
            last_name = author.find("LastName")
            first_name = author.find("ForeName")
            affiliation = author.find("AffiliationInfo/Affiliation")

            if last_name is not None and first_name is not None:
                author_name = f"{first_name.text} {last_name.text}"
                authors.append(author_name)

            if affiliation is not None:
                affiliation_text = affiliation.text.lower()
                if any(word in affiliation_text for word in ["pharma", "biotech", "laboratories", "inc"]):
                    companies.append(affiliation.text)

        for email in article.findall(".//AffiliationInfo/Affiliation"):
            if re.match(r"[^@]+@[^@]+\.[^@]+", email.text or ""):
                corresponding_email = email.text
                break

        if companies:
            papers.append({
                "PubmedID": article.find(".//PMID").text,
                "Title": title,
                "Publication Date": pub_date,
                "Non-academic Author(s)": ", ".join(authors),
                "Company Affiliation(s)": ", ".join(companies),
                "Corresponding Author Email": corresponding_email
            })

    return papers

def save_to_csv(papers: List[Dict[str, str]], filename: str):
    """Save the extracted data into a properly formatted CSV file."""
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if not papers:
        print("No data available to save.")
        return

    df = pd.DataFrame(papers)

    df.to_csv(filename, index=False, encoding="utf-8", sep=",")  

    print(f"Results successfully saved to {filename} in tabular format.") 
