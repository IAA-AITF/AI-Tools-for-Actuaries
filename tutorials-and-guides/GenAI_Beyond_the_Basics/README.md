## GenAI Beyond the Basics: Advanced Concepts for Actuaries  
# Tutorial Notebook

### Description  
This tutorial notebook introduces advanced Generative AI (GenAI) concepts for actuaries who want to move beyond simple chat interfaces and start building programmatic, production-ready solutions. Using realistic actuarial examples, it shows how Large Language Models (LLMs) can be integrated via APIs and extended with:

- **Structured Outputs** for reliable, machine-readable results  
- **Function Calling** to connect models with deterministic tools (e.g. mortality tables in a database)  
- **Fine-Tuning** to improve performance on specialised actuarial tasks  
- **Retrieval-Augmented Generation (RAG)** to inject external knowledge such as annual reports

Throughout the notebook, you will work with example data sets (mortality tables and synthetic car insurance policies) and see how these GenAI “building blocks” can be combined into richer workflows such as real-time claim assessment or multi-agent systems.

---

### Getting Started  

You can run this notebook locally (with Python 3.13) or on an online platform (Colab, Kaggle, etc.). Clone the repository, install dependencies, and launch Jupyter:

```bash
git clone <repo-url>
cd <repo-directory>
pip install -r requirements.txt
jupyter notebook GenAI_Beyond_the_Basics.ipynb
```

Alternatively, upload `GenAI_Beyond_the_Basics.ipynb` and `requirements.txt` to Colab and install dependencies there.

> _To run the examples, you will need a valid API key of OpenAI (e.g. set via an environment variable such as `OPENAI_API_KEY`). The notebook can surely be adjusted so that it also works with other LLM providers._

---

### Contents  
- **`GenAI_Beyond_the_Basics.ipynb`** — Main Jupyter notebook with code, explanations, and exercises  
- **`GenAI_Beyond_the_Basics.html`** — Static HTML export of the notebook for quick browsing  
- **`requirements.txt`** — List of Python packages and versions required to run the notebook  
- **`mortality_tables.sqlite`** — Example SQLite database with mortality tables used in function-calling examples  
- **`riscbac_en_first10.jsonl`** — Synthetic sample of car insurance policies used in fine-tuning and classification examples  

> _All policy data in `riscbac_en_first10.jsonl` is synthetic and provided solely for demonstration. You can replace or extend these assets with your own datasets as needed._

---

### Table of Contents  
1. **Introduction and Key Takeaways**  

2. **Using LLMs via API**  

3. **Structured Outputs**  
   3.1 Concept and Purpose  
   3.2 Use Case: Structured Data Extraction from Policy Documents  
   3.3 Further Applications and Resources  

4. **Function Calling**  
   4.1 Concept and Purpose  
   4.2 Use Case: Mortality Data Retrieval from Database via Function Calling  
   4.3 Further Applications and Resources  

5. **Fine-Tuning**  
   5.1 Concept and Purpose  
   5.2 Use Case: Improving Car Damage Classification by Fine-Tuning Vision-Enabled LLMs  
   5.3 Further Applications and Resources  

6. **Retrieval-Augmented Generation (RAG)**  
   6.1 Concept and Purpose  
   6.2 Use Case: Extracting KPIs from Annual Reports with RAG  
   6.3 Further Applications and Resources  

7. **Outlook**  
   7.1 Combining GenAI Building Blocks: Real-Time Hail-Claim Assessment  
   7.2 Multi-Agent Systems: From Single Models to Collaborative AI Agents  

---

### Key Takeaways for Actuarial Practice  
- **APIs as a Gateway to GenAI**  
  Learn how to integrate LLM calls into Python workflows so that GenAI becomes a standard component in actuarial tools rather than a standalone interface.

- **Structured Outputs and Auditability**  
  Use JSON schemas and structured outputs to ensure responses can be validated, stored, and reused in downstream actuarial models and dashboards.

- **Function Calling for “Thinking + Doing”**  
  Let the model decide *what* information is needed, while deterministic functions (e.g. database lookups for mortality tables) handle *how* to get it—bridging narrative prompts and hard actuarial calculations.

- **Fine-Tuning for Actuarial Specialisation**  
  Explore how fine-tuned, domain-specific models can improve accuracy in tasks such as car damage classification, underwriting text review, or claims triage.

- **RAG for Knowledge-Rich Use Cases**  
  Combine LLMs with document stores to extract KPIs from long annual reports or regulatory texts without hitting context limits.

- **Blueprints for Future Systems**  
  See how these building blocks can be combined into end-to-end solutions such as real-time hail-claim assessment or multi-agent setups where specialised AI agents collaborate.

---

### Data and Example Assets  
- **Mortality tables**: Accessible via `mortality_tables.sqlite` and used in the function-calling section to demonstrate how LLMs can trigger precise queries against actuarial data sources.  
- **Synthetic car insurance policies**: Stored in `riscbac_en_first10.jsonl` and used for classification and fine-tuning examples around car damage and policy information.

These assets are intentionally small and self-contained, making it easy to plug in your own company-specific or publicly available data.

---

### Author  
Simon Hatzesberger (<a href="mailto:simon.hatzesberger@gmail.com">simon.hatzesberger@gmail.com</a>)

---

### Version History  
- **1.0** (December 4, 2025) — Initial release

---

### License  
This project is licensed under the MIT License.
