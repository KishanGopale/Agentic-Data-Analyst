# 🤖 Agentic Data Analyst

Agentic Data Analyst is a **multi-agent AI system** that analyzes sales data using natural language questions.

Instead of writing SQL queries or manually creating charts, users can simply ask:

> "Why did sales drop in March?"

The system automatically:
- Understands the question
- Queries the database
- Processes the data
- Generates charts
- Produces AI insights
- Creates a professional report

This project demonstrates **Agentic AI architecture**, where multiple specialized AI agents collaborate to solve complex analytical tasks.

---

# 🚀 Features

✅ Natural Language Data Analysis  
Ask questions in plain English.

✅ Multi-Agent AI Workflow  
Multiple agents collaborate to analyze data.

✅ Automated SQL Generation  
The system generates and executes SQL queries automatically.

✅ AI-Generated Insights  
LLM analyzes the data and explains patterns.

✅ Automated Charts  
Bar, line, pie, scatter and area charts generated automatically.

✅ Professional Reports  
Complete analysis report generated in Markdown.

✅ Memory System  
Uses vector database to remember past analyses.

---

# 🧠 Agent Architecture

The system is built using **6 specialized AI agents** orchestrated with **LangGraph**.

### 1️⃣ Planner Agent
- Understands the user question
- Creates analysis plan
- Generates SQL queries

### 2️⃣ SQL Agent
- Validates SQL queries
- Executes them safely on SQLite database

### 3️⃣ Data Agent
- Processes results using Pandas
- Performs aggregations and statistics

### 4️⃣ Visualization Agent
- Generates charts using matplotlib or plotly

### 5️⃣ Insight Agent
- Uses LLM to detect trends, patterns, anomalies

### 6️⃣ Report Agent
- Generates final structured report

---

# 🧰 Tech Stack

### AI / LLM
- LangGraph
- LangChain
- Google Gemini API

### Backend
- Python
- FastAPI
- SQLite
- Pandas
- NumPy

### Visualization
- Matplotlib
- Plotly

### Memory
- ChromaDB (Vector Database)

### Frontend
- React
- Vite
- CSS

---

# 📊 Dataset

The project uses a **sample sales dataset (250 rows)**.

Columns include:

| Column | Description |
|------|------|
| date | Sale date |
| product | Product name |
| region | Sales region |
| quantity | Units sold |
| unit_price | Price per unit |
| sales | Total sale amount |
| profit | Profit earned |

Products include:

- Laptop
- Smartphone
- Tablet
- Headphones
- Monitor
- Keyboard
- Mouse
- Webcam

---

# ⚙️ Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/agentic-data-analyst.git
cd agentic-data-analyst

