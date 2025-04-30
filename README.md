# LAWGIC ⚖️ – AI-Powered Indian Legal Law Agent

LAWGIC is a modular, multilingual AI-powered legal assistant built specifically for the Indian legal ecosystem. Designed with accessibility and clarity in mind, LAWGIC helps users understand, query, and navigate legal documents and laws. Whether you're reading a lease agreement, seeking clarity on IPC sections, or looking for a lawyer nearby, LAWGIC simplifies the experience with natural language and smart retrieval.

---

## 📑 Table of Contents
1. [Key Features](#-key-features)
2. [Modular Plugins with Semantic Kernel](#-modular-plugins-with-semantic-kernel)
3. [Architecture Overview](#-architecture-overview)
4. [Software Stack](#-software-stack)
5. [Environment Variables](#-environment-variables)
6. [Setup & Development](#-setup--development)
7. [Usage Guide](#-usage-guide)
8. [What's Next?](#-whats-next)
9. [Attribution](#-attribution)
10. [Contact](#-contact)

---

## 🧩 Key Features

### 📁 Multi-Modal Input
- Accepts **text**, **PDF**, **images**, and soon **speech input**.
- Uses **Azure Computer Vision OCR** to extract text from uploaded files.
- Supports input in **any Indian or global language**.

### 🌐 Multilingual Translation
- Automatically detects the input language.
- Translates to **English** using **Azure Translator** for internal processing.
- Final output is translated **back to the original language** for user-friendly delivery.

### 🧠 AI-Powered Legal Insights
- Translated input is vectorized and compared with **Azure AI Search indexes**.
- Legal documents are stored in **Azure Blob Storage**, indexed semantically.
- Retrieved content is passed to **Azure OpenAI LLM** for legal reasoning and answer generation.
- Ensures accuracy and context relevance by grounding answers in legal documents.

### 📍 Nearby Legal Help
- Provides a list of **nearby lawyers** using **Google Maps API**.
- Supports three location modes: `IP Address`, `Geocode`, and `Manual Input`.

---

## 🧠 Modular Plugins with Semantic Kernel
LAWGIC leverages **Semantic Kernel** to orchestrate specialized plugins that work together to fulfill complex legal tasks.

### 🔁 Translator Plugin
- Handles **language detection** and **bi-directional translation** (Input to English, Output to Original).
- Uses **Azure Translator** under the hood.

### ⚖️ Lawyer AI Plugin
- Converts translated query to vector using **Azure OpenAI Embeddings**.
- Searches semantic index from **Azure AI Search** linked to PDFs in **Azure Blob**.
- Sends retrieved context to **Azure LLM** (ChatGPT) to generate an accurate, grounded legal response.

### 📍 Nearby Lawyers Plugin
- Processes user’s IP, geocode, or manual input to determine location.
- Fetches relevant legal professionals nearby via **Google Maps API**.
- Presents result directly in the Chainlit UI.

---

## 🏗️ Architecture Overview

### Input Handling:
- `Text`, `Image`, and `PDF` inputs → processed using **Azure Computer Vision**.
- Optional: Future integration with **Azure Speech-to-Text**.

### Processing Pipeline:
1. Extracted/typed input is translated to English.
2. Query is converted to vector using Azure Embeddings.
3. Azure AI Search compares it to document indexes.
4. Top-matching content passed to Azure LLM.
5. Answer generated and translated back to original language.

### Output:
- Delivered in native language.
- Cleanly presented via **Chainlit UI**.

---

## 🖥️ Software Stack

### Frontend:
- **Chainlit** (Python-based UI)

### Backend & AI Orchestration:
- **Python**
- **Semantic Kernel (Plugins + Planner)**
- **Azure OpenAI Service** (Embeddings + LLM)
- **Azure Computer Vision** (OCR)
- **Azure Translator** (Language Translation)
- **Google Maps API** (Nearby Lawyer Search)

### Storage:
- **Azure Blob Storage** (Legal Document PDFs)
- **Azure AI Search** (Indexing & Semantic Search)

---

## 🔧 Environment Variables
Before running the system, configure the following:

```env
AZURE_CV_ENDPOINT=<your_computer_vision_endpoint>
AZURE_CV_KEY=<your_computer_vision_key>
AZURE_TRANSLATOR_KEY=<your_translator_key>
AZURE_TRANSLATOR_ENDPOINT=<your_translator_endpoint>
AZURE_TRANSLATOR_REGION=<your_translator_region>
AZURE_OPENAI_KEY=<your_openai_key>
AZURE_OPENAI_ENDPOINT=<your_openai_endpoint>
AZURE_OPENAI_DEPLOYMENT=<your_openai_deployment_name>
AZURE_AI_SEARCH_ENDPOINT=<your_ai_search_endpoint>
AZURE_AI_SEARCH_KEY=<your_ai_search_key>
AZURE_BLOB_CONNECTION_STRING=<your_blob_storage_key>
GOOGLE_MAPS_API_KEY=<your_google_maps_key>
```

---

## 🛠️ Setup & Development

### Prerequisites:
- Python >= 3.10
- Azure resources (OpenAI, Computer Vision, Translator, AI Search, Blob Storage)

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/lawgic.git
cd lawgic
```

### 2. Create & Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
- Create a `.env` file using the template and insert your Azure & Google credentials.

### 5. Run the App
```bash
chainlit run main.py --port 8000
```

---

## 🚀 Usage Guide

### Step 1: Input Your Query
- Upload a document OR type your legal question.
- Supports Indian languages and English.

### Step 2: Let LAWGIC Analyze
- Text is extracted (if needed) and translated.
- Semantic search locates relevant laws.
- Azure LLM generates an appropriate legal response.

### Step 3: Get Results
- The answer is translated back to your preferred language.
- Displayed with legal references (if available).
- Use the **Nearby Lawyer** button to find help locally.

---

## 📌 What's Next?
- Voice input using Azure Speech (STT).
- Voice output for better accessibility.
- User profiles for history and saved queries.
- Role-based filters for specific legal domains.
- Public-facing legal FAQ database with AI curation.

---

## 🤝 Attribution
- **Icons & Assets**: Lucide, Freepik, Flaticon
- **Libraries & Frameworks**: Chainlit, Azure SDKs, Semantic Kernel, OpenAI
- **Contributors**: Team LAWGIC

---

## 📬 Contact
Have questions or want to collaborate?
- Reach out at: [lawgic.team@yourdomain.com](mailto:lawgic.team@yourdomain.com)

**Note**: LAWGIC is a legal assistive tool. For serious or critical legal matters, always consult a licensed attorney.

