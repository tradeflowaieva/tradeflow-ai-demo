import streamlit as st
import pandas as pd
from pypdf import PdfReader

st.set_page_config(page_title="TradeFlow AI", page_icon="📦", layout="wide")
st.title("📦 Dustin TradeFlow AI")
st.caption("Proof of Concept — Invoice & Customs Checker")
st.info("Demo only. Customs classifications must be verified by a qualified person.")

uploaded = st.file_uploader("Upload Commercial Invoice (PDF)", type=["pdf"])
if uploaded:
    reader=PdfReader(uploaded)
    text="\n".join((p.extract_text() or "") for p in reader.pages)
    checks = {
        "Invoice number": "invoice" in text.lower(),
        "Invoice date": "date" in text.lower(),
        "Currency": any(x in text.upper() for x in ["EUR","SEK","USD"]),
        "Incoterm": any(x in text.upper() for x in ["DAP","DDP","FCA","EXW","CIP","CPT"]),
        "Country of origin": "origin" in text.lower(),
        "HS/CN code": ("hs/cn" in text.lower() or "hs code" in text.lower()),
        "Gross weight": "gross weight" in text.lower(),
    }
    score=round(sum(checks.values())/len(checks)*100)
    st.metric("Customs Readiness", f"{score}%")
    st.dataframe(pd.DataFrame([{"Check":k,"Status":"✓ OK" if v else "⚠ Missing / verify"} for k,v in checks.items()]), hide_index=True, use_container_width=True)
    st.subheader("Recommendation")
    if all(checks.values()):
        st.success("Document contains the main customs fields. Human verification is still required.")
    else:
        st.warning("Complete or verify missing fields before sending the case to the freight forwarder.")
else:
    st.write("Upload a PDF invoice to begin.")
