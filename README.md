# 🇮🇳 LAWGIC – Indian Legal Law Agent

**LAWGIC** is an intelligent, multimodal legal assistant tailored for the Indian legal ecosystem. It combines Azure’s AI capabilities, OpenAI’s LLMs, and geolocation services to simplify access to legal support across formats, languages, and regions. Whether it’s understanding a scanned legal document or finding the nearest lawyer — LAWGIC has you covered.

---

## ❓ Why LAWGIC?

India’s legal system is vast and multifaceted — accessible primarily to those well-versed in English or legal jargon. LAWGIC is designed to break the barriers of:

- **Language Diversity**: Most citizens prefer regional languages, while legal documents are often in English or Hindi.
- **Limited Legal Awareness**: Legal procedures and documents are not easy to interpret for the common public.
- **Geographic Constraints**: Professional legal help isn't uniformly available across rural and remote areas.
- **Document Accessibility**: Legal resources often exist as scanned files, making searchability and comprehension difficult.

LAWGIC provides a unified solution to these challenges by using AI to enable multimodal, multilingual, and location-aware access to legal information.

---

## 🧩 Key Features

### 🧑‍⚖️ Multimodal Legal Query Input
- Accepts **text** input directly via a clean UI built using **Chainlit**.
- Accepts **files** such as images or PDFs; uses **Azure Computer Vision OCR** to extract text.
- Future-ready for **voice input** using **Azure Speech Services (TTS)**.

### 🌐 Multilingual Translation Support
- Input can be in **any Indian language**.
- Translated to **English** using **Azure Translator** before processing.
- The final legal response is **translated back into the original language**.

### 🧠 AI-Powered Legal Reasoning
- The translated query is **embedded into a vector**.
- Compared semantically with indexed legal PDFs (stored in **Azure Blob**) using **Azure AI Search**.
- Relevant content is retrieved and passed to **Azure OpenAI's LLM** for precise legal answers.
- Output is **translated back** to the original input language and displayed on the UI.

### 📍 Find Nearby Lawyers
- Supports 3 types of location input:
  - **IP address**
  - **Geocode** (latitude and longitude)
  - **Manual entry** (city/state)
- Uses the **Google Maps API** to fetch and display nearby legal professionals.

---

## 🧠 Modular Plugins with Semantic Kernel

LAWGIC uses **Semantic Kernel** to orchestrate three core modular plugins that handle all the functionality in a clean and extendable architecture:

### 1. 🈂️ Translator Plugin
**Purpose**: Enables multilingual interaction.

**Responsibilities**:
- Detects language of user input.
- Translates to English before semantic embedding.
- Translates final output from English back to the original input language.

**Powered By**:
- Azure Translator
- Semantic Kernel orchestration

---

### 2. 📄 Lawyer AI Plugin
**Purpose**: Powers the core legal intelligence.

**Responsibilities**:
- Converts the translated query into a vector.
- Compares it against legal document indexes created from PDFs in Azure Blob via **Azure AI Search**.
- Passes matched content (context) to **Azure OpenAI LLM**.
- Generates a clear, accurate legal explanation or answer.

**Powered By**:
- Azure Cognitive Search (vector index)
- Azure Blob Storage (legal PDFs)
- Azure OpenAI (LLM)
- Semantic Kernel (query + context prompting)

---

### 3. 📍 Nearby Lawyers Plugin
**Purpose**: Connects users with nearby lawyers.

**Responsibilities**:
- Accepts IP, geocode, or manual location input.
- Queries **Google Maps API** to fetch lawyer data.
- Returns names, contact info, and directions to local legal professionals.

**Powered By**:
- Google Maps API
- Geolocation tools
- Semantic Kernel (handles input mapping and output formatting)

---

### 🔄 Semantic Kernel Orchestration

- Each plugin is **independently callable**, promoting modularity and ease of maintenance.
- Semantic Kernel handles the flow from **input → translation → embedding → LLM reasoning → final translation/output**.
- Allows future addition of plugins like:
  - Court Status Checker
  - Document Summarizer
  - Live Chat with Legal Experts

---

## 🧠 System Architecture

```text
User Input (Text / File / Future: Voice)
        ↓
If File → OCR via Azure Computer Vision → Extracted Text
        ↓
Azure Translator → English Translation
        ↓
→ Translator Plugin (Semantic Kernel)
        ↓
Vector Embedding of Query
        ↓
→ Azure AI Search Indexes (Linked to PDFs in Azure Blob Storage)
        ↓
→ Lawyer Plugin (Semantic Kernel)
        ↓
Relevant Context → Azure OpenAI LLM → Legal Output
        ↓
Azure Translator → Back to Original Language
        ↓
→ Displayed on Chainlit UI

(Parallel optional process)
        ↓
Nearby Lawyers Plugin (Semantic Kernel)
        ↓
→ Google Maps API (IP / Geocode / Manual Input)
        ↓
→ List of Lawyers Based on Location
