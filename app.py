"""BankMind AI - Multi-Agent Intelligent Banking Assistant
Chat-Centric Architecture: Supervisor routes each question to specialized agents
and synthesizes the response with visible step-by-step routing transparency.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

# Import modular agents and tools
from agents.supervisor import SupervisorAgent
from agents.banking_agent import CustomerBankingAgent
from agents.fraud_agent import RiskAndFraudAgent
from agents.loan_agent import CreditAndLoanAgent
from tools.banking_api import (
    get_all_customers,
    get_all_transactions,
    get_customer,
    get_account_balance,
    get_recent_transactions
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="BankMind AI | Banking Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# CUSTOM CSS STYLING
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Clean Fintech Aesthetics */
    .chat-app-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 12px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.15);
    }
    .chat-app-title {
        font-size: 1.7rem;
        font-weight: 800;
        margin: 0;
        color: #FFFFFF;
    }
    .chat-app-subtitle {
        font-size: 0.92rem;
        color: #DBEAFE;
        margin-top: 4px;
    }
    
    /* Routing Steps Card */
    .routing-card {
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
        font-size: 0.88rem;
    }
    .step-badge {
        display: inline-block;
        padding: 2px 8px;
        font-size: 0.75rem;
        font-weight: 700;
        border-radius: 9999px;
        margin-right: 6px;
    }
    .badge-supervisor { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
    .badge-banking { background: #DBEAFE; color: #1E40AF; border: 1px solid #BFDBFE; }
    .badge-fraud { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
    .badge-loan { background: #DCFCE7; color: #166534; border: 1px solid #BBF7D0; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "supervisor" not in st.session_state:
    st.session_state.supervisor = SupervisorAgent()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "👋 **Welcome to BankMind AI Chat Assistant!**\n\n"
                "I am your central **Supervisor Agent**. When you ask me a question, I will:\n"
                "1. **Analyze your intent**\n"
                "2. **Route your request** to the specialized domain agent:\n"
                "   - 🏦 **Customer Banking Agent** (Balances, Statements, Transactions)\n"
                "   - 🛡️ **Risk & Fraud Detection Agent** (Transaction Risk, Anomaly Detection)\n"
                "   - 📝 **Credit & Loan Agent** (Income, DTI & Loan Underwriting)\n"
                "3. **Execute verified banking tools** without hallucination\n"
                "4. **Synthesize and retrieve** your personalized answer!\n\n"
                "Click any suggested button below or type your banking request to start."
            ),
            "routing_info": None,
            "trace": None
        }
    ]

# -----------------------------------------------------------------------------
# SIDEBAR: CUSTOMER PERSONA & CONTROLS
# -----------------------------------------------------------------------------
customers = get_all_customers()
cust_map = {c["customer_id"]: f"{c['full_name']} ({c['customer_id']}) - {c['account_type']}" for c in customers}

with st.sidebar:
    st.title("🏦 BankMind AI")
    st.caption("Multi-Agent Banking Automation")
    
    st.markdown("""
    <div style="background-color: #DCFCE7; border: 1px solid #86EFAC; padding: 6px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-align: center; color: #166534; margin-bottom: 14px;">
        🟢 SIMULATED DEMO ENVIRONMENT
    </div>
    """, unsafe_allow_html=True)
    
    provider_name = st.session_state.supervisor.llm_router.get_provider_name()
    st.info(f"**Orchestrator Engine**: `{provider_name}`")
    
    st.markdown("### 👤 Select Active Customer")
    active_cust_id = st.selectbox(
        "Current Persona",
        options=list(cust_map.keys()),
        format_func=lambda x: cust_map[x],
        index=0
    )
    
    cust_profile = get_customer(active_cust_id).get("customer", {})
    
    st.markdown("---")
    st.markdown("### 💳 Customer Profile Snapshot")
    st.write(f"**Account Holder**: **{cust_profile.get('full_name')}**")
    st.write(f"**Account Number**: `{cust_profile.get('account_number')}`")
    st.write(f"**Account Type**: `{cust_profile.get('account_type')}`")
    st.write(f"**Credit Score**: **{cust_profile.get('credit_score')}**")
    st.write(f"**Monthly Income**: ${float(cust_profile.get('monthly_income', 0)):,.2f}")
    st.write(f"**Monthly Debt**: ${float(cust_profile.get('monthly_debt', 0)):,.2f}")
    dti_val = (float(cust_profile.get('monthly_debt', 0)) / max(1.0, float(cust_profile.get('monthly_income', 1)))) * 100
    st.write(f"**DTI Ratio**: **{dti_val:.1f}%**")
    
    st.markdown("---")
    if st.button("🗑️ Reset Chat Conversation"):
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "👋 Chat conversation reset. How may I help you with your banking needs?",
                "routing_info": None,
                "trace": None
            }
        ]
        st.rerun()

# -----------------------------------------------------------------------------
# TOP APP BANNER & QUICK STATS
# -----------------------------------------------------------------------------
bal_info = get_account_balance(active_cust_id)
bal_amount = bal_info.get("account_balance", 0.0) if bal_info.get("success") else 0.0

st.markdown(f"""
<div class="chat-app-header">
    <div class="chat-app-title">BankMind AI: Multi-Agent Banking Assistant</div>
    <div class="chat-app-subtitle">
        Active Customer: <strong>{cust_profile.get('full_name')}</strong> ({active_cust_id}) | 
        Balance: <strong>${bal_amount:,.2f} USD</strong> | 
        Credit Score: <strong>{cust_profile.get('credit_score')}</strong>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PROMINENT QUICK PROMPT BUTTONS
# -----------------------------------------------------------------------------
st.markdown("#### ⚡ Quick Actions (Click any prompt to ask):")
btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns(5)

prompt_to_send = None

with btn_col1:
    if st.button("💰 Check Balance", key="p1"):
        prompt_to_send = "Show my account balance."
with btn_col2:
    if st.button("📜 Last 5 Transactions", key="p2"):
        prompt_to_send = "Show my last 5 transactions."
with btn_col3:
    if st.button("🚨 Check TXN1005 (Fraud)", key="p3"):
        prompt_to_send = "Check transaction TXN1005 for suspicious activity."
with btn_col4:
    if st.button("📋 Loan Eligibility", key="p4"):
        prompt_to_send = "Am I eligible for a $15,000 personal loan?"
with btn_col5:
    if st.button("⚡ Multi-Agent Audit", key="p5"):
        prompt_to_send = "Review my recent transactions and identify suspicious ones."

st.markdown("---")

# -----------------------------------------------------------------------------
# MAIN CHAT MESSAGES FEED
# -----------------------------------------------------------------------------
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        # Visible Supervisor Routing & Execution Walkthrough
        if msg.get("routing_info"):
            r = msg["routing_info"]
            st.markdown(f"""
            <div class="routing-card">
                <div style="font-weight: 700; color: #1E3A8A; margin-bottom: 6px;">
                    🧠 Supervisor Routing & Execution Walkthrough:
                </div>
                <div>1. <strong>Supervisor Detected Intent</strong>: <code>{r['intent']}</code></div>
                <div>2. <strong>Routed To Specialized Agent(s)</strong>: {r['agents_badges']}</div>
                <div>3. <strong>Tool(s) Executed</strong>: {r['tools_str']}</div>
                <div>4. <strong>Supervisor Status</strong>: <em>Retrieved verified result & synthesized final answer</em></div>
            </div>
            """, unsafe_allow_html=True)
            
        # Render conversational response
        st.markdown(msg["content"])
        
        # Technical trace expander
        if msg.get("trace"):
            trace = msg["trace"]
            with st.expander(f"🔬 Technical Audit Trace ({trace['trace_id']})", expanded=False):
                st.json(trace)

# -----------------------------------------------------------------------------
# CHAT INPUT
# -----------------------------------------------------------------------------
chat_input_val = st.chat_input("Ask BankMind AI (e.g., 'What is my balance?', 'Check TXN1005', 'Is there any fraud?')...")
if chat_input_val:
    prompt_to_send = chat_input_val

# -----------------------------------------------------------------------------
# MULTI-AGENT EXECUTION LOGIC
# -----------------------------------------------------------------------------
if prompt_to_send:
    # 1. Append user prompt
    st.session_state.chat_messages.append({
        "role": "user",
        "content": prompt_to_send,
        "routing_info": None,
        "trace": None
    })
    
    # 2. Supervisor routes query and executes specialized agents
    with st.spinner("🧠 Supervisor Agent analyzing intent and routing to specialized agents..."):
        res = st.session_state.supervisor.process_request(
            prompt_to_send,
            current_customer_id=active_cust_id
        )
        
    trace = res.get("trace", {})
    
    # Format routing badge HTML for clear visual representation
    invoked = trace.get("agents_invoked", [])
    badges = []
    for a in invoked:
        if "Banking" in a:
            badges.append(f"<span class='step-badge badge-banking'>🏦 {a}</span>")
        elif "Fraud" in a:
            badges.append(f"<span class='step-badge badge-fraud'>🛡️ {a}</span>")
        elif "Loan" in a:
            badges.append(f"<span class='step-badge badge-loan'>📝 {a}</span>")
        else:
            badges.append(f"<span class='step-badge badge-supervisor'>🧠 {a}</span>")
            
    tools = [f"<code>{tc.get('agent')}.{tc.get('tool')}()</code>" for tc in trace.get("tool_calls", [])]
    
    routing_info = {
        "intent": trace.get("detected_intent", "UNKNOWN"),
        "agents_badges": " ".join(badges) if badges else "<em>None (Handled by Supervisor directly)</em>",
        "tools_str": ", ".join(tools) if tools else "<em>None</em>"
    }
    
    # 3. Append assistant response with routing walkthrough
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": res["response"],
        "routing_info": routing_info,
        "trace": trace
    })
    
    st.rerun()

# -----------------------------------------------------------------------------
# BOTTOM COLLAPSIBLE SECTION: FINANCIAL ANALYTICS & RECENT LEDGER
# -----------------------------------------------------------------------------
with st.expander("📊 View Live Customer Account Analytics & Transaction Ledger", expanded=False):
    tab_a, tab_b = st.tabs(["📈 Spending Analytics", "📜 Transaction History"])
    
    txns = get_recent_transactions(active_cust_id, limit=20).get("transactions", [])
    
    with tab_a:
        if txns:
            df_txns = pd.DataFrame(txns)
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig_pie = px.pie(
                    df_txns,
                    names="category",
                    values="amount",
                    title="Spending by Category",
                    hole=0.4
                )
                st.plotly_chart(fig_pie)
            with col_g2:
                fig_bar = px.bar(
                    df_txns,
                    x="timestamp",
                    y="amount",
                    color="category",
                    title="Transaction Velocity & Amounts"
                )
                st.plotly_chart(fig_bar)
                
    with tab_b:
        if txns:
            st.dataframe(pd.DataFrame(txns)[["transaction_id", "timestamp", "merchant", "amount", "status"]])

# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 0.8rem; color: #94A3B8;">
    BankMind AI • Multi-Agent Intelligent Banking Automation System • 100% Synthetic Educational Simulation
</div>
""", unsafe_allow_html=True)
