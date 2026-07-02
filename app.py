import streamlit as st
import json
from pipelines.classifier import classify_ticket
from pipelines.rag_pipeline import RAGPipeline

st.set_page_config(page_title="Atlan Helpdesk Copilot", layout="wide")

st.header("Atlan Helpdesk Copilot")

# Initialize session state
if 'classifications' not in st.session_state:
    st.session_state['classifications'] = {}
if 'tickets' not in st.session_state:
    st.session_state['tickets'] = []
if 'rag' not in st.session_state:
    try:
        with st.spinner("Loading RAG pipeline..."):
            st.session_state['rag'] = RAGPipeline()
            st.success("✓ RAG Pipeline loaded successfully")
    except Exception as e:
        st.error(f"Failed to load RAG pipeline: {e}")
        st.session_state['rag'] = None

# Sidebar for RAG query
with st.sidebar:
    st.subheader("📚 Ask Documentation")
    doc_query = st.text_area("Search Atlan docs", placeholder="e.g., How to connect Snowflake?")
    if st.button("Search Docs"):
        if doc_query and st.session_state['rag']:
            with st.spinner("Searching documentation..."):
                try:
                    result = st.session_state['rag'].query(doc_query)
                    
                    st.markdown("### Answer")
                    st.write(result['answer'])
                    
                    st.markdown("### Sources")
                    for i, source in enumerate(result['sources'], 1):
                        st.markdown(f"**{i}. [{source['title']}]({source['url']})**")
                        st.caption(f"Relevance: {source['score']:.2%}")
                except Exception as e:
                    st.error(f"Error searching docs: {e}")

# Main content
uploaded_file = st.file_uploader("Upload sample_tickets.csv", type=["csv", "json"])

if uploaded_file:
    tickets = json.load(uploaded_file)
    st.session_state['tickets'] = tickets
    
    # Filters
    st.subheader("Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        priority_filter = st.multiselect(
            "Priority",
            ["P0 (High)", "P1 (Medium)", "P2 (Low)"],
            default=[]
        )
    
    with col2:
        tag_filter = st.multiselect(
            "Topic Tags",
            ["How-to", "Product", "Connector", "Lineage", "API/SDK", "SSO", "Glossary", "Best practices", "Sensitive data"],
            default=[]
        )
    
    with col3:
        sentiment_filter = st.multiselect(
            "Sentiment",
            ["Frustrated", "Curious", "Angry", "Neutral"],
            default=[]
        )
    
    # Display tickets
    for ticket in tickets:
        # Get or create classification (caching)
        if ticket['id'] not in st.session_state['classifications']:
            with st.spinner(f"Classifying {ticket['id']}..."):
                try:
                    st.session_state['classifications'][ticket['id']] = classify_ticket(ticket)
                except Exception as e:
                    st.error(f"Classification failed for {ticket['id']}: {e}")
                    continue
        
        classification = st.session_state['classifications'][ticket['id']]
        
        # Apply filters
        if priority_filter and classification.get('priority') not in priority_filter:
            continue
        if tag_filter and not any(tag in classification.get('topic_tags', []) for tag in tag_filter):
            continue
        if sentiment_filter and classification.get('sentiment') not in sentiment_filter:
            continue
        
        # Display with styled badges
        with st.expander(f"{ticket['id']}: {ticket['subject']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Body:**")
                st.write(ticket['body'])
                
                # Get RAG suggestion button
                if st.button(f"Get Docs Suggestion", key=f"rag_{ticket['id']}"):
                    if st.session_state['rag']:
                        with st.spinner("Searching documentation..."):
                            try:
                                query = f"{ticket['subject']} {ticket['body']}"
                                result = st.session_state['rag'].query(query)
                                
                                st.markdown("---")
                                st.markdown("### 📖 Suggested Answer from Docs")
                                st.write(result['answer'])
                                
                                st.markdown("**Sources:**")
                                for i, source in enumerate(result['sources'], 1):
                                    st.markdown(f"{i}. [{source['title']}]({source['url']})")
                            except Exception as e:
                                st.error(f"Error getting docs suggestion: {e}")
                    else:
                        st.warning("RAG pipeline not loaded")
            
            with col2:
                st.write("**Classification:**")
                
                # Priority badge
                priority = classification.get('priority', 'Unknown')
                priority_colors = {
                    'P0 (High)': 'red',
                    'P1 (Medium)': 'orange',
                    'P2 (Low)': 'green'
                }
                color = priority_colors.get(priority, 'gray')
                st.markdown(f"**Priority:** :{color}[{priority}]")
                
                # Sentiment badge
                sentiment = classification.get('sentiment', 'Unknown')
                sentiment_colors = {
                    'Angry': 'red',
                    'Frustrated': 'orange',
                    'Curious': 'blue',
                    'Neutral': 'gray'
                }
                color = sentiment_colors.get(sentiment, 'gray')
                st.markdown(f"**Sentiment:** :{color}[{sentiment}]")
                
                # Topic tags
                st.write("**Tags:**")
                tags = classification.get('topic_tags', [])
                if tags:
                    tag_html = " ".join([f'<span style="background-color: #e0e0e0; padding: 3px 8px; border-radius: 3px; margin: 2px; display: inline-block; font-size: 12px;">{tag}</span>' for tag in tags])
                    st.markdown(tag_html, unsafe_allow_html=True)

# New ticket submission with interactive response flow
st.markdown("---")
st.subheader("Submit New Ticket")
col1, col2 = st.columns(2)

with col1:
    new_ticket_subject = st.text_input("Subject")
    new_ticket_body = st.text_area("Description")

with col2:
    st.info("📋 Submit a ticket to see:\n- Internal Analysis (Classification)\n- Final Response (RAG-generated answer)")

if st.button("Submit & Process Ticket", type="primary"):
    if new_ticket_subject and new_ticket_body:
        # Generate new ticket ID
        new_id = f"TICKET-{len(st.session_state['tickets']) + 248}"
        
        new_ticket = {
            "id": new_id,
            "subject": new_ticket_subject,
            "body": new_ticket_body
        }
        
        # CHECKPOINT 1: Classification
        st.markdown("---")
        st.subheader("🔍 Step 1: Internal Analysis")
        
        with st.spinner("Classifying ticket..."):
            try:
                classification = classify_ticket(new_ticket)
                st.session_state['classifications'][new_id] = classification
                st.session_state['tickets'].append(new_ticket)
                
                # Display classification as JSON
                st.json(classification)
                st.success("✓ Classification complete")
                
            except Exception as e:
                st.error(f"❌ Classification failed: {e}")
                st.stop()
        
        # CHECKPOINT 2: Determine if RAG should run
        topic_tags = classification.get('topic_tags', [])
        rag_eligible_tags = ['How-to', 'Product', 'Best practices', 'API/SDK', 'SSO']
        should_run_rag = any(tag in rag_eligible_tags for tag in topic_tags)
        
        st.markdown("---")
        st.subheader("📝 Step 2: Final Response")
        
        if should_run_rag:
            # CHECKPOINT 3: Run RAG pipeline
            st.info(f"✓ Ticket tagged with: {', '.join([t for t in topic_tags if t in rag_eligible_tags])} - Running RAG pipeline...")
            
            if st.session_state['rag']:
                with st.spinner("Generating response from documentation..."):
                    try:
                        query = f"{new_ticket_subject} {new_ticket_body}"
                        result = st.session_state['rag'].query(query)
                        
                        # Display answer
                        st.markdown("### 📖 Generated Answer")
                        st.write(result['answer'])
                        
                        # Display sources
                        st.markdown("### 🔗 Sources")
                        for i, source in enumerate(result['sources'], 1):
                            st.markdown(f"**{i}. [{source['title']}]({source['url']})**")
                            st.caption(f"Relevance: {source['score']:.2%}")
                        
                        st.success(f"✓ Ticket {new_id} processed successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ RAG pipeline failed: {e}")
                        st.warning("Ticket classified but automatic response generation failed.")
            else:
                st.error("❌ RAG pipeline not loaded. Cannot generate automatic response.")
        else:
            # CHECKPOINT 4: Non-RAG eligible ticket
            st.warning(f"⚠️ This ticket has been classified as **{', '.join(topic_tags)}** and routed to the appropriate team.")
            st.info("Tickets with tags like 'Connector', 'Lineage', 'Glossary', or 'Sensitive data' require specialized handling and have been forwarded to the relevant department.")
        
        # Add rerun button to see updated ticket list
        if st.button("View Updated Ticket List"):
            st.rerun()
            
    else:
        st.warning("⚠️ Please fill in both subject and description")