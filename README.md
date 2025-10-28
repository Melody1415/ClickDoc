# ClickDoc  
**Your AI-powered coding companion for smarter documentation and analysis**  
🔗 **Live Demo:** [https://clickdoc.onrender.com](https://clickdoc.onrender.com)  
📘 **User Guide:** [Click to view the User Guide](#) 

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Framework-green?logo=flask)
![Groq](https://img.shields.io/badge/AI-Groq%20LLaMA%203.3-orange?logo=ai)
![Render](https://img.shields.io/badge/Deployed%20on-Render-purple?logo=render)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Overview
**ClickDoc** is an AI-assisted web application that helps developers and teams **automatically generate, analyze, and understand documentation** for their code.  

Upload your project files, and ClickDoc will intelligently:
- Generate clean, markdown-based documentation    
- Visualize project structures and relationships   
- Provide an **AI chatbot** that can answer questions about your code  

All powered by **LLaMA 3.3** through the **Groq API**.

---

## Features

### 1. Intelligent File Management
- Upload one or multiple source code files directly through the web interface.  
- Files are securely stored in session memory.  
- Automatic redirection to the interactive dashboard after upload.  

### 2. Document-Based AI Chatbot
- **Context-aware assistant:** Ask questions directly about your uploaded code.  
- Understands file contents and provides meaningful explanations.  
- Supports real-time conversations about specific functions or logic.  

### 3. Function Documentation Generator
- Generate structured documentation for uploaded files in markdown format.  
- Includes key sections like:
  - Code structure overview  
  - Function list and details  
  - Parameters, return values, and examples  
- Supports **Regenerate**, **Export**, and **Save** options for flexible documentation handling.  

### 4. Code Relationship & Validation Tools
- Analyze **function dependencies** and detect inconsistencies.  
- Validate logic flow and highlight potential unused functions.  
- Helps developers quickly understand code organization and structure.  

### 5. Visualization & Diagram Generation
- Automatically generate diagrams for:
  - Function relationships  
  - Folder and file structure  
  - System and module architecture  
- Ideal for reports, presentations, or quick visual understanding of large projects.  

---

## Tech Stack

- **Flask:**  Lightweight Python web framework used for building the backend, managing routes, and handling requests between the user interface and AI modules.

- **Python:**  Core programming language powering the backend logic, AI integrations, and session management.

- **Groq API:**  Used as the main Large Language Model (LLM) engine for text generation, document-based question answering.

- **Context-Aware AI Model:**  Enhances chatbot accuracy by referencing relevant code sections before generating responses.

- **Flask Session:**  Manages temporary storage of uploaded files per user session for secure and lightweight data handling.

- **HTML, CSS, and JavaScript:**  Frontend technologies for creating responsive, user-friendly pages that connect seamlessly with Flask routes.

- **python-dotenv:**  Handles environment variables securely, such as API keys and configuration settings.

- **Mermaid.js:** Used to generate visual diagrams from analyzed code.

---

## Codenection 2025 Project Submission
- **Track:** Track 3 – Industry Collaboration  
- **Problem Statement:** Developers spend too much time writing and reading lengthy documentation. It is often hard to search, lacks visuals, and creates confusion.  
- **Team Members:** Tang Jasmine, Melody Lu Yi En, Thang Qi Jian, Hoh Wen Hao
