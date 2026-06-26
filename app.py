import streamlit as st
import anthropic
import json
import base64

st.set_page_config(page_title="Contract Risk Spotter", layout="wide")
st.title("⚖️ Contract Risk Spotter")
st.caption("Enterprise-grade AI for IT Agencies.")

SYSTEM_PROMPT = """You are a ruthless legal analyst for IT agencies. Read the document and identify risky clauses. If it limits liability, forces auto-renewal, or assigns IP unfairly, tag HIGH RISK. If unusual but manageable, tag MEDIUM RISK. Output ONLY a JSON array of objects with keys: risk_level, summary, citation, raw_quote. No markdown."""

# YOUR PRIVATE KEY (Safe because repo is Private)
API_KEY = "sk-ant-dummy-key-for-github"

uploaded_file = st.file_uploader("Upload Contract (Max 50 pages)", type=["pdf"])

if st.button("Analyze Contract", type="primary") and uploaded_file:
    with st.spinner("Analyzing document..."):
        try:
            pdf_bytes = uploaded_file.read()
            pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")
            client = anthropic.Anthropic(api_key=API_KEY)
            
            msg = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": [
                    {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
                    {"type": "text", "text": "Analyze this contract."}
                ]}]
            )
            
            text = msg.content[0].text.strip()
            if text.startswith("```"): text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            risks = json.loads(text)
            
            # --- ENTERPRISE UI ---
            high_count = sum(1 for r in risks if r["risk_level"] == "HIGH RISK")
            med_count = sum(1 for r in risks if r["risk_level"] == "MEDIUM RISK")
            
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            col1.metric(label="Total Risks", value=len(risks))
            col2.metric(label="High Risk", value=high_count, delta="Danger")
            col3.metric(label="Medium Risk", value=med_count)
            st.markdown("---")
            
            for r in risks:
                if r["risk_level"] == "HIGH RISK":
                    st.error(f"**{r['risk_level']}** | 📌 {r['citation']}")
                else:
                    st.warning(f"**{r['risk_level']}** | 📌 {r['citation']}")
                    
                st.write(r["summary"])
                with st.expander("View Raw Proof"):
                    st.text(r["raw_quote"])
                st.divider()
                
        except Exception as e:
            st.error(f"Error: {e}")
