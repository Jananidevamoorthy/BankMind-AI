# 🎥 BankMind AI: Demonstration Video Script & Presentation Plan
## 5–10 Minute Walkthrough for AI/ML Internship Evaluation

---

### Timing Breakdown Overview

| Section | Topic | Duration | Target Timestamp |
| :---: | :--- | :---: | :---: |
| **1** | Introduction & Problem Statement | 1 min | 0:00 – 1:00 |
| **2** | Dashboard Overview & Persona Setup | 1 min | 1:00 – 2:00 |
| **3** | Use Case 1: Account Balance Enquiry | 45 sec | 2:00 – 2:45 |
| **4** | Use Case 2: Transaction History Retrieval | 45 sec | 2:45 – 3:30 |
| **5** | Use Case 3: Explainable Fraud Risk Assessment | 1 min 15 sec | 3:30 – 4:45 |
| **6** | Use Case 4: Transparent Loan Eligibility Evaluation | 1 min 15 sec | 4:45 – 6:00 |
| **7** | Use Case 5: Real Multi-Agent Collaboration Workflow | 1 min 30 sec | 6:00 – 7:30 |
| **8** | Execution Trace & Multi-Agent Architecture Deep Dive | 1 min 15 sec | 7:30 – 8:45 |
| **9** | Limitations, Security Guardrails & Future Improvements | 45 sec | 8:45 – 9:30 |

---

### Detailed Step-by-Step Script

#### 1. Introduction & Problem Statement (0:00 – 1:00)
- **Visual**: Show project title slide or web dashboard header at `http://localhost:8501`.
- **Narration**:
  > *"Hello everyone! My name is [Your Name], and today I am excited to present **BankMind AI: A Multi-Agent Intelligent Banking Automation System**, built for my AI/ML internship assignment.*
  > 
  > *In modern banking, conversational AI must balance two competing demands: natural conversational interaction, and absolute financial precision. Generic LLM chatbots frequently hallucinate numbers, invent non-existent account balances, or fail to follow strict underwriting rules.*
  > 
  > *To solve this, I designed BankMind AI around a Decoupled Multi-Agent Architecture. A central Supervisor Agent coordinates three specialized domain agents—the Customer Banking Agent, the Risk and Fraud Agent, and the Credit and Loan Agent. Crucially, the system enforces a strict data boundary: AI models never generate financial facts—they only interpret verified records returned by simulated banking API tools.*
  > 
  > *Let's jump into the live application."*

---

#### 2. Dashboard Tour & Customer Persona Setup (1:00 – 2:00)
- **Visual**: Navigate to Streamlit dashboard sidebar and metric cards.
- **Narration**:
  > *"Here is the BankMind AI web dashboard built with Streamlit and Plotly. At the top, we see our simulated demo mode badge and active AI engine indicator. In the sidebar, we can switch between five synthetic customer personas—each representing diverse credit profiles, from prime high-earners to subprime applicants.*
  > 
  > *Currently, we have **Sarah Jenkins** selected. Notice the real-time financial snapshot in the top banner: her available checking balance is $14,850.50, her credit score is 760, and we have quick action presets for all five required use cases.*
  > 
  > *Across the top, we have five specialized tabs: the AI Banking Assistant, Spending Analytics, Fraud Lab, Loan Studio, and System Architecture logs."*

---

#### 3. Use Case 1: Account Balance Enquiry (2:00 – 2:45)
- **Visual**: In Tab 1 (AI Assistant), click *"Use Case 1: Balance Enquiry"* button or type: `"Show my account balance."`
- **Narration**:
  > *"Let's test Use Case 1. The customer asks: 'Show my account balance.'*
  > 
  > *The Supervisor Agent immediately classifies the intent as a `BALANCE_ENQUIRY`, extracts the active customer ID `CUST1001`, and invokes the **Customer Banking Agent**. The Banking Agent calls the simulated banking API function `get_account_balance()`, retrieves the ledger balance, and formats an empathetic response.*
  > 
  > *Notice that Sarah's balance of $14,850.50 USD is mathematically grounded from our ledger—not an LLM guess."*

---

#### 4. Use Case 2: Transaction History Retrieval (2:45 – 3:30)
- **Visual**: In Tab 1, click *"Use Case 2: Transaction History"* button or type: `"Show my last 5 transactions."`
- **Narration**:
  > *"Now for Use Case 2: 'Show my last 5 transactions.'*
  > 
  > *The Supervisor extracts the numeric limit parameter (5) and routes the request to the **Customer Banking Agent**. The agent executes `get_recent_transactions()`, sorting records chronologically from newest to oldest.*
  > 
  > *If we switch over to the **Account & Spending Analytics** tab, we can also see these transactions rendered visually using interactive Plotly donut and timeline charts."*

---

#### 5. Use Case 3: Explainable Fraud Risk Assessment (3:30 – 4:45)
- **Visual**: In Tab 1, enter: `"Check transaction TXN1005 for suspicious activity."` Then click into **Tab 3: Risk & Fraud Lab**.
- **Narration**:
  > *"Now let's examine Use Case 3: Fraud Risk Assessment on transaction `TXN1005`.*
  > 
  > *Here, the Supervisor routes exclusively to the **Risk and Fraud Detection Agent**. This agent applies a hybrid risk model: first, a rule-based heuristic score from 0 to 100, and second, an ensemble Scikit-Learn Random Forest model that predicts a calibrated probability of fraud.*
  > 
  > *Notice the result: TXN1005 is classified as **HIGH RISK** with a heuristic score of 70/100 and a 100% ML anomaly probability. Why? The agent explains the exact contributing factors:*
  > *1. High monetary amount of $4,850 exceeding retail norms.*
  > *2. High-risk merchant category: 'Cryptocurrency' via Wire Transfer.*
  > 
  > *Crucially, the agent recommends: 'Flag for Fraud Analyst review and place a temporary hold'—it flags for human review rather than making an unverified automatic block."*

---

#### 6. Use Case 4: Transparent Loan Eligibility Evaluation (4:45 – 6:00)
- **Visual**: In Tab 1, enter: `"Am I eligible for a $15,000 personal loan?"` Then switch persona to **Elena Rostova (`CUST1003`)** and test again.
- **Narration**:
  > *"For Use Case 4, we evaluate loan underwriting. The user asks: 'Am I eligible for a $15,000 personal loan?'*
  > 
  > *The Supervisor routes to the **Credit and Loan Agent**. For Sarah Jenkins, the agent evaluates three transparent underwriting benchmarks: minimum income over $3,000, Debt-to-Income ratio under 45%, and credit score over 650. Sarah passes all three, receiving a preliminary approval with an estimated APR of 6.49%.*
  > 
  > *Now, let's demonstrate transparent rejection reasoning by switching our persona in the sidebar to **Elena Rostova (`CUST1003`)**.*
  > 
  > *When we assess Elena, the agent declines the loan and itemizes every specific failure: her monthly income of $2,400 is below the $3,000 threshold, her DTI ratio of 75% exceeds the 45% ceiling, and her credit score of 590 is subprime.*
  > 
  > *Every evaluation clearly displays our educational simulation disclaimer."*

---

#### 7. Use Case 5: Real Multi-Agent Collaboration (6:00 – 7:30)
- **Visual**: Select Sarah Jenkins (`CUST1001`), enter: `"Review my recent transactions and identify suspicious ones."` Expand the **Multi-Agent Execution Trace** accordion.
- **Narration**:
  > *"Now for the centerpiece of our project—Use Case 5: Real Multi-Agent Collaboration.*
  > 
  > *Here, the user asks: 'Review my recent transactions and identify suspicious ones.' Notice that neither the Banking Agent nor the Risk Agent can answer this alone.*
  > 
  > *Watch the Supervisor orchestrate this workflow:*
  > *Step 1: The Supervisor invokes the **Customer Banking Agent** to call `get_recent_transactions()` and retrieve Sarah's ledger records.*
  > *Step 2: The Supervisor takes that raw transaction payload and passes it directly to the **Risk and Fraud Detection Agent**, which iterates through each record, computing heuristic points and ML anomaly probabilities.*
  > *Step 3: The Supervisor synthesizes a unified report: it flags `TXN1005` as High Risk while confirming the other transactions are clean.*
  > 
  > *This is authentic agent collaboration—data generated by one agent is passed as input to another."*

---

#### 8. Execution Trace & Multi-Agent Architecture (7:30 – 8:45)
- **Visual**: In Tab 5 (Multi-Agent Architecture & Trace Logs), show the full JSON execution trace.
- **Narration**:
  > *"Let's inspect the Execution Trace that BankMind AI generates for every single request. Under Tab 5, we can see the complete audit trail:*
  > *- The original user prompt.*
  > *- The detected intent and extracted entities.*
  > *- The routing engine: showing whether it executed via the LLM or our zero-downtime deterministic heuristic fallback.*
  > *- The list of invoked agents: showing both `CustomerBankingAgent` and `RiskAndFraudAgent`.*
  > *- The itemized tool calls with raw input parameters and status codes.*
  > 
  > *This guarantees full auditing compliance for banking operations."*

---

#### 9. Limitations, Security & Conclusion (8:45 – 9:30)
- **Visual**: Show `README.md` and terminal running `pytest`.
- **Narration**:
  > *"To summarize our security and engineering safeguards:*
  > *1. 100% synthetic deterministic data ensures zero risk of privacy violations.*
  > *2. Zero-downtime fallback means the system never fails if cloud LLM APIs are offline.*
  > *3. All 37 unit tests across our five test suites pass with zero regressions.*
  > 
  > *For future work, we plan to connect this architecture to Open Banking API sandboxes and implement real-time human-in-the-loop fraud verification via SMS push prompts.*
  > 
  > *Thank you for watching the BankMind AI demonstration!"*
