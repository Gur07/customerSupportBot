import streamlit as st
import pandas as pd
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

def classify_ticket(ticket):
    """Classify ticket using Gemini LLM"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a ticket classification system. Analyze the ticket and return a JSON with:
        - topic_tags: List of relevant tags from [How-to, Product, Connector, Lineage, API/SDK, SSO, Glossary, Best practices, Sensitive data]
        - sentiment: One of [Frustrated, Curious, Angry, Neutral]
        - priority: One of [P0 (High), P1 (Medium), P2 (Low)]
        
        Return only valid JSON with these exact keys."""),
        ("user", "Ticket ID: {id}\nSubject: {subject}\nBody: {body}")
    ])
    
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({
            "id": ticket["id"],
            "subject": ticket["subject"],
            "body": ticket["body"]
        })
        return result
    except Exception as e:
        return {"error": str(e)}