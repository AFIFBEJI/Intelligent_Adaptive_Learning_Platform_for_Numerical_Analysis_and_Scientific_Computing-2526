# Project Plan

## Phase 1: Setup & Foundations

### Tasks in Phase 1

1. **Research and State of the Art**:
   - Literature review on STEM education and knowledge graphs.
   - Research on LLM validation methods and best practices for integrating GraphRAG.
   - Study on cognitive load reduction using multi-modal integration.

2. **Database Design**:
   - Design schemas for Neo4j (concepts, prerequisites, modules, resources) and PostgreSQL (user management, analytics, mastery mapping).

3. **Infrastructure and DevOps**:
   - Set up Docker Compose for FastAPI, PostgreSQL, Neo4j, and frontend.
   - Configure GitHub workflows for CI/CD pipelines.
   - Implement initial security (password hashing, JWT-based authentication).
   - Configure Python environment with required dependencies.

4. **Implementation and Initial Population**:
   - Develop backend APIs for user registration, authentication, and profile management.
   - Populate Neo4j with initial concepts and relationships (e.g., Interpolation, Integration, ODEs).
   - Create a basic frontend interface (TypeScript + Vite).

## Phase 2: Adaptive Learning & AI Integration

### Tasks in Phase 2

1. **Adaptive Assessment & Profiling**:
   - Create a question bank covering fundamentals (linear algebra, differential calculus, Python programming).
   - Implement progression algorithm to adjust question difficulty based on student performance and Neo4j prerequisites.
   - Update user profiles in PostgreSQL in real-time (scores, response times, mastered concepts).

2. **Graph Extension & Multi-level Content**:
   - Complete the Neo4j graph for Interpolation, Numerical Integration, and ODEs modules.
   - Use Neo4j PRE_REQUIRES relations to generate personalized learning paths based on pedagogical dependencies.
   - Develop multiple versions of course content (simplified, standard, rigorous) tailored to student profiles.
   - Prepare content in Markdown/JSON with LaTeX tags for RAG indexing.

3. **AI Tutoring with RAG**:
   - Set up RAG pipeline using LangChain to connect LLMs (GPT-4/Claude/Gemini) to verified course documents.
   - Inject Neo4j metadata (mastery levels, prerequisites) into LLM prompts for contextual responses.
   - Implement strict system prompts to enforce LaTeX notation and restrict answers to numerical analysis.
   - Integrate SymPy/NumPy checks to validate LLM-generated numerical results.

4. **Visualization & Interactive Tools**:
   - Produce scripted Manim animations illustrating algorithm dynamics (e.g., Newton's method, splines).
   - Integrate interactive components like JSXGraph, Desmos, or GeoGebra for real-time curve manipulation.
   - Use NumPy and SciPy in the backend for validating student calculations and providing feedback.

## Phase 3: Remediation, UI, and Validation

### Tasks in Phase 3

1. **Remediation Intelligence & Algorithms**:
   - Develop logic to classify errors (calculation vs. conceptual) in student responses.
   - Implement targeted remediation using Neo4j to extract specific resources (Manim videos, AI tutorials) for conceptual errors.
   - Design recommendation algorithms to calculate the "best next node" in the graph based on mastery scores.

2. **User Interface & Analytics**:
   - Finalize the TypeScript UI using OOP principles, ensuring responsive design across devices.
   - Develop mastery dashboards to track progress and visualize skill levels by module.
   - Optimize API communications between frontend and backend for fast loading of interactive tools (JSXGraph, WebGL).

3. **Testing & Reliability**:
   - Perform unit testing to ensure AI tutor answers and NumPy/SciPy calculations are mathematically accurate.
   - Conduct system stability tests on Docker architecture and JWT/PostgreSQL sessions under load.
   - Execute usability audits to ensure the TypeScript interface is intuitive and interactive tools load without latency.

## Phase 4: Evaluation & Publication

### Tasks in Phase 4

1. **Experimental Study & Data Collection**:
   - Organize a user study with 25-30 students to validate adaptive learning effectiveness.
   - Measure quantitative metrics: learning gains (pre/post-test scores), time to mastery, engagement (AI tutor interactions, Manim viewing time).
   - Collect qualitative data: surveys and interviews on AI explanations clarity and visualization usefulness.

2. **Statistical Analysis & Comparison**:
   - Analyze data using statistical tools to compare adaptive platform performance vs. traditional teaching.
   - Assess cognitive load reduction from multi-modal integration (theory, Manim animations, interactive tools).
   - Interpret results to identify strengths of Neo4j-LLM integration and beneficial adaptation modules.

3. **Writing & Valorization**:
   - Write a structured scientific article (IMRaD) for submission to journals like IEEE Transactions on Learning Technologies.
   - Produce a comprehensive PFE report covering design, AI implementation, and user study conclusions.
   - Create an interactive presentation with Manim demos and Neo4j graph visualizations.

