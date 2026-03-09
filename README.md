# Intelligent Adaptive Learning Platform for Numerical Analysis and Scientific Computing (25-26)

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![Neo4j](https://img.shields.io/badge/Neo4j-graphDB-orange)
![Angular](https://img.shields.io/badge/Angular%20%7C%20React-frontend-red)
![License](https://img.shields.io/badge/license-MIT-%23ff0000)

[![Status](https://img.shields.io/badge/Status-Active_Development-blue.svg)]()
[![Methodology](https://img.shields.io/badge/Methodology-Agile%2FScrum-brightgreen.svg)]()
[![Deployment](https://img.shields.io/badge/Deployment-Docker-blue.svg)]()

> **Project Context:** Final Year R&D Undergraduate Internship (PFE) - Academic Year 2025/2026  
> **Institution:** ESPRIT School of Engineering  
> **Principal Investigator / Supervisor:** Afif Beji, Eng. MSc.  
> **Intern:** Yassine Ben Necib<br>


An AI-driven adaptive learning platform designed to support the study of **Numerical Analysis and Scientific Computing** through personalized learning paths, knowledge graphs, and intelligent tutoring.

This project is developed as part of a **Final Year R&D Internship (PFE)** at **ESPRIT School of Engineering** and aims to produce both:

- a **functional educational prototype**
- a **research contribution suitable for publication** in an international peer-reviewed journal.

---

## 📌 Project Overview

**Adaptive Numerical Analysis & Scientific Computing 2526** is a neuro-symbolic platform engineered for **universal mastery**. Its core mission is to ensure that any student—regardless of their prior background or mathematical level—can fully grasp complex STEM concepts through a hyper-personalized learning experience. Developed as a Final Year R&D Internship (PFE) at **ESPRIT School of Engineering**, this project serves as both a high-performance educational tool and a research contribution to the field of AI-driven pedagogy.

### 🔍 The Challenge
Traditional *one-size-fits-all* engineering curricula often fail to account for the **heterogeneous mathematical backgrounds** of students. This leads to high failure rates in Numerical Analysis due to:
* **Knowledge Gaps:** Inability to connect fundamental prerequisites (e.g., Taylor Series) to complex algorithms (e.g., Newton-Raphson).
* **AI Hallucinations:** Standard LLMs frequently provide inaccurate or unverified steps in precision-heavy STEM domains.

### 💡 Our Solution
To address these gaps, this platform implements a **Knowledge-Graph-Augmented AI architecture** that provides:

* **Dynamic Learning Pathways:** A Neo4j-powered Knowledge Graph that constructs personalized curricula tailored to individual student progress and gaps.
* **GraphRAG Tutoring:** An intelligent tutor that grounds LLM responses (Gemini/GPT-4/Claude) in verified symbolic nodes to ensure absolute mathematical rigor.
* **Interactive Visualization:** Real-time algorithmic demonstrations using **Manim** (server-side) and **JSXGraph** (client-side) to make abstract convergence and error analysis intuitive.

By combining symbolic reasoning with generative AI, the system transforms Numerical Analysis into a transparent, interactive, and mathematically grounded learning experience.

## 🏗️ System Architecture

The platform operates on a hybrid neuro-symbolic framework, integrating structured mathematical logic with generative AI across four core layers:

### 1. Symbolic Layer: The Knowledge Graph (Neo4j)
The backbone of the platform is a pedagogical **Knowledge Graph** that models the conceptual structure of Numerical Analysis.
* **Nodes:** Represent **Concepts** (e.g., *LU Decomposition*, *Newton-Raphson*), **Modules** (e.g., *Solving Linear Systems*, *Root-Finding Methods*), and **Learning Resources**.
* **Pedagogical Logic:** Explicit relationships such as `REQUIRES`, `PART_OF`, and `REMEDIATES_TO` allow the system to calculate the optimal path for any student, ensuring that no learner attempts an algorithm without the necessary mathematical prerequisites.

### 2. Adaptive Assessment Engine
To achieve universal mastery, the engine continuously calibrates the learning path via **Diagnostic Quizzes**:
* **Gap Detection:** Identifies missing prerequisites in real-time.
* **Dynamic Difficulty:** Adjusts question complexity based on the learner's competency profile.
* **Data Persistence:** Competency states and analytics are managed via **PostgreSQL**.

### 3. Neural Layer: GraphRAG AI Tutoring
The tutoring system utilizes **Graph-Augmented Retrieval (GraphRAG)** to provide mathematically rigorous explanations while eliminating hallucinations.
* **Orchestration:** Powered by **LangChain**, integrating **Gemini, GPT-4, and Claude**.
* **RAG Pipeline:** Context is pulled directly from curated materials and Knowledge Graph metadata to ground every AI response.
* **Verification:** Formulas are rendered via **MathJax (LaTeX)**, while numerical claims are validated using **NumPy, SciPy, and SymPy**.

### 4. Interactive & Visualization Layer
Abstract algorithms are transformed into intuitive experiences through programmatic visualization:
* **Manim Animations:** Server-side generated videos illustrating the convergence mechanics of **multivariate optimization** (e.g., First-Order Gradient Descent landscapes) and the step-by-step evolution of **iterative solvers** like the **Gauss-Seidel** method.
* **Interactive Sandboxes:** High-fidelity client-side exploration environments leveraging **JSXGraph**, **Desmos**, and **GeoGebra**. These sandboxes facilitate guided, hands-on exercises that bridge numerical methods to **real-world CS engineering applications**:
    * **Linear Regression:** Estimating the **price of a house from its size** by fitting a straight line through historical size–price data, or modeling **computational resource consumption** to optimize predictive autoscaling in cloud environments.
    * **Newton & Lagrange Interpolation:** Using a small set of measured points (e.g., temperature at 08:00, 12:00, 16:00) to build a smooth polynomial that **passes exactly through those points**. The polynomial can then be evaluated at intermediate values (e.g., 10:00) to estimate unmeasured data.
    * **First-Order Gradient Descent:** Minimizing cost functions during the weight optimization phase of neural network training.

## 🛠️ Technology Stack

The platform is built on a scalable, modular architecture designed for high-performance AI orchestration and mathematical precision:

| Category | Technologies |
| :--- | :--- |
| **Backend & API** | FastAPI (Python 3.10+), Pydantic |
| **Frontend** | Angular / React, TypeScript, Tailwind CSS |
| **Intelligence Layer** | LangChain (GraphRAG), Gemini / GPT-4 / Claude |
| **Databases** | Neo4j (Graph Logic), PostgreSQL (User Analytics) |
| **Scientific Computing** | NumPy, SciPy, SymPy |
| **Math Rendering** | MathJax (LaTeX) / LaTeX |
| **Visualization & Math** | Manim, JSXGraph.js |
| **DevOps, Infrastructure & Version Control** | Docker, Nginx, Git, GitHub Actions (CI/CD) |

## 🔄 Methodology: Agile / Scrum

Development is structured around an overlapping, iterative **Agile (Scrum)** methodology. Rather than a traditional Waterfall approach, the system is built in functional increments. Backend API development, Knowledge Graph population, and UI component construction occur concurrently in sprints, allowing for continuous integration and early beta testing.

## 📂 Repository Structure & Architecture

To maintain separation of concerns between the web application, the AI orchestration, and the mathematical engines, this project strictly adheres to the following domain-driven directory structure:

```text
project-root
│
├── backend/                  # FastAPI web server and business logic
│   ├── api/                  # REST endpoints and routing
│   ├── models/               # Pydantic and database models
│   ├── services/             # Core application services
│   └── auth/                 # JWT Authentication and security
│
├── frontend/                 # Frontend SPA (Angular / React)
│   ├── components/           # Reusable UI and JSXGraph wrappers
│   ├── pages/                # Main application views/routes
│   └── services/             # API client and state management
│
├── knowledge_graph/          # Neo4j symbolic logic
│   ├── schema/               # Graph ontology definitions
│   └── population_scripts/   # Cypher scripts for curriculum seeding
│
├── rag_pipeline/             # AI & LLM Orchestration (LangChain)
│   ├── prompts/              # System prompts and constraints
│   └── retrieval/            # GraphRAG logic and embedding generation
│
├── animations/               # Visualizations
│   └── manim_scripts/        # Python scripts for programmatic video generation
│
├── docker/                   # Containerization infrastructure
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── init-scripts/         # Database initialization scripts
│
├── docs/                     # Specifications, literature review, and architecture diagrams
│
└── tests/                    # Unit, integration, and mathematical accuracy tests
    ├── backend/
    ├── frontend/
    └── rag_evaluation/

