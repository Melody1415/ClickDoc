# 🧠 ClickDoc  
**Your AI-powered coding companion for smarter documentation and analysis**  
🔗 **Live Demo:** [https://clickdoc.onrender.com](https://clickdoc.onrender.com)

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Framework-green?logo=flask)
![Groq](https://img.shields.io/badge/AI-Groq%20LLaMA%203.3-orange?logo=ai)
![Render](https://img.shields.io/badge/Deployed%20on-Render-purple?logo=render)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Overview
**ClickDoc** is an AI-assisted web application that helps developers and teams **automatically generate, analyze, and understand documentation** for their code.  

Upload your project files, and ClickDoc will intelligently:
- Generate markdown-based documentation ✍️  
- Visualize relationships between functions 🔗  
- Allow real-time interaction through a **document-based chatbot** 🤖  

All powered by **LLaMA 3.3** through the **Groq API**.

---

## ✨ Features

### 🗂️ 1. Intelligent File Management
- Upload one or multiple source code files directly through the web interface.  
- Files are stored in session memory for quick cross-feature access.  
- Automatic redirection to the interactive dashboard after upload.  

### 🤖 2. Document-Based AI Chatbot
- **Context-aware assistant:** Ask questions directly about your uploaded documents.  
- **Code understanding:** The chatbot reads your code and provides clear, accurate explanations.  
- **Multi-turn memory:** Keeps conversation context within each session.  
- **Smart mode:** Offers balanced technical and beginner-friendly responses.  

### 🧾 3. Function Documentation Generator
- **AI-generated markdown documentation** for each uploaded file.  
- Comprehensive structure includes:
  - 🧩 Code Structure Overview  
  - 🧠 General Code Purpose and Usage  
  - 📋 List of Functions  
  - 🧮 Function Details (Parameters, Returns, Examples)  
- Supports **Regenerate**, **Export**, and **Save** functions for easy revision and reuse.  

### 🧠 4. Validation & Relationship Mapping
- Analyze **function relationships**, dependencies, and logic flow.  
- Detect inconsistencies or unused functions.  
- Simplifies understanding of large or collaborative projects.  

### 🧩 5. Smart Visualization Tools
- Generate visual representations using **Mermaid.js**:  
  - 📊 Architecture diagrams  
  - 🪶 Folder structures  
  - 🔄 Function relationships  
- Automatically generated from code logic — perfect for documentation and presentations.  

### ⚙️ 6. Modular System Design
ClickDoc uses a **modular Flask architecture**, with each module serving a distinct role:

| Module | Description |
|---------|-------------|
| `dashboard` | File management and upload dashboard |
| `generate` | AI-driven documentation generation |
| `validation` | Code consistency and structure validation |
| `relationship` | Function and module mapping |
| `diagram` | Visualization tools using Mermaid.js |
| `chatbot` | Document-based conversational assistant |
| `tech_stack` & `setup` | System configuration and info |

---

## 🧰 Tech Stack

- **Flask:**  Lightweight Python web framework used for building the backend, managing routes, and handling requests between the user interface and AI modules.

- **Python:**  Core programming language powering the backend logic, AI integrations, and session management.

- **Groq API:**  Used as the main Large Language Model (LLM) engine for text generation and document-based question answering.

- **Retrieval-Augmented Generation (RAG):**  Enhances chatbot accuracy by retrieving relevant document sections before generating responses, ensuring context-aware answers.

- **Flask Blueprints:**  Modular structure allowing clean separation of app components — includes dashboards, chatbot logic, setup, validation, and diagram generation.

- **Flask Session:**  Manages temporary storage of uploaded files per user session for secure and lightweight data handling.

- **HTML, CSS, and JavaScript:**  Frontend technologies for creating responsive, user-friendly pages that connect seamlessly with Flask routes.

- **python-dotenv:**  Handles environment variables securely, such as API keys and configuration settings.

---

## 🎯 Goal
> To simplify and automate the code documentation process by combining AI-driven code understanding, visualization, and interactive Q&A into one unified web platform.

---

## 🧪 Example Workflow
1. Upload your Python script(s) on the home page.  
2. Click **“Generate Documentation”** to create AI-written markdown.  
3. Use the **Chatbot** to ask:
   - “What does `process_data()` do?”
   - “Show me an example of error handling in this file.”
4. Visualize relationships using **diagram tools**.  
5. Regenerate or export your documentation anytime.  

---

## 🚀 Codenection 2025 Project Submission
- **Track:** Track 3 – Industry Collaboration  
- **Problem Statement:** Developers spend too much time writing and reading lengthy documentation. It is often hard to search, lacks visuals, and creates confusion.  
- **Team Members:** Tang Jasmine, Melody Lu Yi En, Thang Qi Jian, Hoh Wen Hao
