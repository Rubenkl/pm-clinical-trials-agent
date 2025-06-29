
# Keynote summary: Raja at Nvidia GDC

## Own notes
- Goal of  AI:
	- How to make more clinical trials successfull
		- Connect all data from all clinical trials to each other (private & public domain)
		- This is the basic for agentic AI. Connected all data!
- Goal of **Agentic** AI.
	- Clinical trials are very complex. 
		- Document generation
		- document extraction
		- Multiple processes in place for multiple countries
	- end-goal: So to eventually instead of 1 person running a clinical trial you get **8** persons running a clinical trial as the agent can do many of these tasks. How can we get to this?

Of course. Here is a summary of the keynote "Advancing Health and Improving Patient Outcomes With AI."

### Summary of the Keynote

This keynote, delivered by Raja and Khaldoun from IQVIA, outlines how the convergence of data, AI, and domain expertise is creating a revolution in healthcare. The speakers discuss the historical evolution of medicine, the current applications of AI, the practical challenges of implementation, and the future vision for a hyper-personalized healthcare system.

---

### Key Points:

**1. The Evolution of Medicine: A Journey to NNT=1**
Raja framed the history of medicine in terms of "Numbers Needed to Treat" (NNT)—how many patients must be treated for one to benefit.
*   **1950s-1990s:** The era of small molecules and placebo trials. **NNT was ~100:1**.
*   **2000s:** Targeted therapies and biologics improved effectiveness. **NNT improved to ~20:1**.
*   **2015-Present:** Personalized and gene therapies, fueled by real-world data, further refined treatment. **NNT is now ~5:1**.
*   **The AI Revolution (Future):** The ultimate goal is to achieve an **NNT of 1:1**, where every treatment is perfectly tailored to the individual patient.

**2. AI's Core Applications in Healthcare**
The speakers identified four key problem areas where AI offers significant promise:
*   **Faster Discovery:** Using AI to design new molecules and antibodies, increasing the probability of success in drug development.
*   **Efficient Clinical Trials:** Reducing the time and cost (currently ~$3.5 billion per drug) of clinical trials by using AI to predict outcomes, optimize site selection, and accelerate workflows with **agentic AI**.
*   **Better Evidence & Personalization:** Generating stronger evidence for payers and healthcare providers. An example was a model for non-small cell lung cancer that identified optimal treatment sequences which physicians were not consistently following, leading to better survival outcomes.
*   **Improved Patient Journeys:** Enabling earlier diagnosis, creating personalized treatment plans, and coordinating care more effectively.

**3. The Three Pillars of Practical AI Implementation**
Khaldoun emphasized that realizing AI's potential requires focusing on three practical realities:
*   **Connected Data:** No single data source is sufficient. Value is unlocked only when disparate data—clinical trials, publications, real-world patient data, pricing, regulatory info—is connected to create a 360-degree view.
*   **Implicit Domain Knowledge:** Technology alone is not enough. It must be infused with the specialized knowledge of medical professionals, scientific principles, and established workflows. This "tacit knowledge" is critical.
*   **Validation and Reliability:** AI models must be rigorously validated not just for technical accuracy but also for real-world usability, safety, and ethical and regulatory compliance.

**4. Bridging General AI with Specific Healthcare Knowledge**
A core theme was making powerful but generalist AI models (like LLMs) effective in the highly specialized field of healthcare.
*   **The Challenge:** Healthcare uses a vast and complex language, captured in over 6 million ontological terms (compared to ~50,000 words in English). Out-of-the-box LLMs fail at specific healthcare tasks.
*   **A Practical Solution: Ontology-RAG:** The speakers presented a compelling example where standard LLMs scored nearly 0% on a medical code mapping task (ICD-9 to ICD-10). By simply adding a Retrieval-Augmented Generation (RAG) system that queries a healthcare ontology, the accuracy jumped to **nearly 90%**. This demonstrates a simple yet powerful way to make AI immediately useful.
*   **Future Work:** The next step is to move beyond RAG by fine-tuning models to directly embed this ontological knowledge, enhancing their native reasoning capabilities for healthcare.

**5. Key Insights from the Q&A**
*   **Partnerships (NVIDIA):** Collaboration is key to providing the necessary hardware and software infrastructure to build and deploy advanced models, especially for **agentic AI**.
*   **Business Strategy:** The most practical starting point is to connect accessible data (public data, internal operational data) to solve high-impact problems, like accelerating literature reviews from weeks to minutes.
*   **Bridging Knowledge Gaps:** There is a significant gap between academic research and community practice. AI can help bridge this by integrating diverse data sources, including social media ("social listening") and real-world evidence, to create a more complete picture of patient health.


---

Of course. This is a great topic to focus on for your interview. Based on the keynote, here is a detailed breakdown of what was said about making clinical trials more efficient, structured for your interview preparation.

### High-Level Summary

The core message is that AI can fundamentally overhaul the clinical trial process, which is currently slow, expensive (~$3.5 billion per drug), and has a high failure rate (95%). Their vision is to use AI to **increase the probability of success** while simultaneously **reducing cost and time to market**. They are moving from a reactive process to a predictive, simulated, and automated one.

---

### Key Strategies for More Efficient Clinical Trials

Here are the specific strategies and technologies they discussed, which you should be familiar with.

#### 1. **Connecting Data to Create a Foundational Layer**
This is the absolute starting point for all their AI efforts.
*   **What they're doing:** They are building a massive, interconnected data asset that links every clinical trial from the last 20 years with every product on the market.
*   **Data Sources Mentioned (08:02 - 08:28):**
    *   Clinical trial data (e.g., from clinicaltrials.gov)
    *   Publications and medical congress abstracts
    *   Chemistry and biology data
    *   Regulatory information (approvals, etc.)
    *   Proprietary data on reimbursement, pricing, and drug uptake in over 50 countries.
*   **Why it's important:** This connected data serves as the "base on which this AI will work" (08:36). Without it, accurate prediction is impossible.

#### 2. **Simulating and Predicting Trial Outcomes**
Once the data is connected, they can use it to predict what will happen *before* the trial even starts.
*   **What they predict (08:43 - 09:40):**
    *   **Efficacy Outcomes:** Predicting a trial's results, such as Kaplan-Meier survival curves in oncology. They mention startups are already showing good results in this area.
    *   **Trial Feasibility:** Predicting if a trial design is viable, including selecting the right sites and estimating the time to completion.
    *   **Regulatory & Commercial Outcomes:** Simulating the likelihood of regulatory approval and forecasting commercial success (e.g., how quickly the drug will be adopted, its peak market share).
*   **The Goal:** To create an **"end-to-end... feasibility to commercial success prediction"** (09:40). This allows companies to de-risk their investments.

#### 3. **Using Agentic AI to Accelerate the Workforce**
This is a key initiative they highlighted, with a specific timeline.
*   **The Problem:** Clinical trials are incredibly complex, involving massive amounts of **document generation**, **information extraction**, and complex processes (09:56 - 10:03).
*   **The Solution: Agentic AI.** These are AI agents designed to automate these complex, multi-step tasks. They can handle the operational burden, freeing up the human workforce.
*   **Timeline:** They are actively working on this and **"hope to bring some early agents out towards the end of this year"** (10:07). This is a crucial, concrete detail for an interview.
*   **NVIDIA Partnership:** The Q&A revealed their work on agentic AI is part of a collaboration with NVIDIA, leveraging their hardware and software to build these agents (23:14).

#### 4. **Improving Planning to Minimize Delays**
This is a practical, operational benefit of their predictive models.
*   **What they're doing:** Using **"better predictive planning to minimize amendments and delays in clinical trials"** (09:47).
*   **Why it's important:** Trial amendments (changes to the protocol) are a major source of cost overruns and delays. Predicting potential issues allows for a more robust initial plan.

---

### Potential Interview Questions & Talking Points for You


**You could ask the interviewer:**

*   "You spoke about using agentic AI to accelerate the clinical trial workforce. Could you elaborate on which specific workflows—perhaps around document generation or site coordination—you see as the most promising initial targets for these agents?"
*   "The vision for an end-to-end predictive model from feasibility to commercial success is incredibly powerful. What do you see as the biggest challenge in building trust with pharma companies to rely on these simulations for multi-billion dollar decisions?"
*   "Regarding the connected data foundation, how do you navigate the challenge of standardizing data that comes from so many different sources, countries, and formats to make it usable for AI?"


Excellent. This is a crucial clarification and exactly the kind of critical thinking required for a top-tier product manager. You've correctly identified that the generic LLM research, while interesting, is not a reliable source for IQVIA's specific plans.

Let's ground everything in the single source of truth: the keynote. You are 100% correct in your analysis. Raja's comments are not two separate ideas; they are two sides of the same coin.

*   **The Goal (The "What"):** "Better predictive planning to minimize amendments and delays in clinical trials."
*   **The Method (The "How"):** "Accelerate clinical trial workforce with agentic AI" that handles "document generation" and "information extraction."

**Conclusion & The First Use Case:** The first agent they are building is almost certainly a **Clinical Trial Protocol Optimization Agent**. Its function is to use AI to analyze, extract information from, and provide predictive insights on draft protocols to reduce the number of costly, time-consuming amendments.

This directly addresses Raja's concern about your lack of clinical trial knowledge. He's signaling that to succeed, you need to understand the world of protocol design. Let's get you up to speed.