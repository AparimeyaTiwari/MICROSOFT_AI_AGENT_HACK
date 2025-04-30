# 🇮🇳 LAWGIC – Indian Legal Law Agent

**LAWGIC** is a smart, multilingual legal assistant tailored for the Indian legal ecosystem. It helps users understand legal matters by accepting various input formats (text, file, and soon voice), processing them intelligently, and returning human-like legal assistance powered by advanced AI technologies.

---

## 🧩 Key Features

### 🧑‍⚖️ Legal Query Support
- Accepts **text** or **documents** (images, PDFs, etc.).
- Uses **Azure Computer Vision OCR** to extract text from non-text files.
- Upcoming support for **voice input** via **Azure Speech Services (TTS)**.

### 🌐 Multilingual Capability
- Input in any Indian language is **translated to English** using **Azure Translator**.
- Final AI-generated response is **translated back to the original language**.

### 🧠 AI-Powered Legal Insights
- Uses **Azure AI Search** to compare query vectors with indexed legal documents.
- Legal documents are stored in **Azure Blob Storage**, and mapped using **semantic indexes**.
- Final output is generated using **OpenAI GPT models** based on the retrieved content.

### 📍 Find Nearby Lawyers
- Uses **Google Maps API** to find lawyers based on:
  - **IP Address**
  - **Geocode (lat-long)**
  - **Manual location input**

### 🧠 Modular Kernels with Semantic Kernel
- **Translator Kernel** – Handles language detection, translation to/from English.
- **Lawyer Kernel** – Manages semantic search and legal reasoning using LLMs.
- **Nearby Lawyers Kernel** – Finds legal professionals around a location.

---

## 🧱 System Architecture

```text
User Input (Text / File / Future: Voice)
        ↓
If File → OCR via Azure Computer Vision → Extracted Text
        ↓
Azure Translate → English Text
        ↓
Translator Kernel → Vector Embedding
        ↓
→ Azure AI Indexes (Mapped to PDFs in Azure Blob)
        ↓
→ Retrieved Context → Lawyer Kernel → OpenAI LLM Response
        ↓
Azure Translate → Translated Back to Original Language
        ↓
Chainlit UI Displays Output

(Parallel optional process)
        ↓
Nearby Lawyers Kernel → Google Maps API (based on IP/Geocode/Manual Input)
        ↓
→ List of Legal Professionals
