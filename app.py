import streamlit as st
import anthropic
import json
import base64

st.set_page_config(page_title="Contract Risk Spotter", layout="wide")
st.title("⚖️ Contract Risk Spotter")
st.caption("Built for IT Agencies.")

SYSTEM_PROMPT = """You are a ruthless legal analyst for IT agencies. Read the document and identify risky clauses. If it limits liability, forces auto-renewal, or assigns IP unfairly, tag HIGH RISK. If unusual but manageable, tag MEDIUM RISK. Output ONLY a JSON array of objects with keys: risk_level, summary, citation, raw_quote. No markdown."""

api_key = st.text_input("Enter Anthropic API Key:", type="password")
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if st.button("Analyze") and uploaded_file and api_key:
    with st.spinner("Analyzing..."):
        try:
            pdf_bytes = uploaded_file.read()
            pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")
            client = anthropic.Anthropic(api_key=api_key)
            
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
            
            st.success(f"Found {len(risks)} risks.")
            for r in risks:
                color = "🔴" if r["risk_level"] == "HIGH RISK" else "🟡"
                st.markdown(f"### {color} {r['risk_level']}")
                st.write(r["summary"])
                st.caption(f"📌 {r['citation']}")
                with st.expander("View Proof"):
                    st.text(r["raw_quote"])
                st.divider()
        except Exception as e:
            st.error(f"Error: {e}")