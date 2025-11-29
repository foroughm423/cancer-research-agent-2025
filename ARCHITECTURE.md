# System Architecture

## Overview

The Oncology Clinical Decision Support System employs a hierarchical multi-agent architecture where a Supervisor Agent coordinates four specialized sub-agents to execute a complete clinical research workflow.

---

## System Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                         User Input                           │
│              (Cancer type, treatment, date range)            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   SUPERVISOR AGENT                           │
│               (Workflow Orchestrator)                        │
│   - Routes queries to specialist agents                     │
│   - Aggregates results                                      │
│   - Manages error handling                                  │
└──┬───────┬────────┬────────┬───────────────────────────────┘
   │       │        │        │
   ▼       ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌─────────────┐
│ Lit  │ │ Ana  │ │ Doc  │ │  Clinical   │
│Agent │ │Agent │ │Agent │ │  Reasoner   │
└──┬───┘ └──┬───┘ └──┬───┘ └──────┬──────┘
   │        │        │            │
   ▼        ▼        ▼            ▼
┌─────┐  ┌────┐  ┌────┐      ┌──────┐
│PubMed│  │Stats│  │Risk│      │GRADE │
│ API  │  │Tool │  │Calc│      │System│
└─────┘  └────┘  └────┘      └──────┘
   │        │        │            │
   └────────┴────────┴────────────┘
                  │
                  ▼
          ┌───────────────┐
          │ Memory Service│
          │   (SQLite)    │
          └───────────────┘
                  │
                  ▼
     ┌──────────────────────────┐
     │  Clinical Decision Report │
     └──────────────────────────┘
```

---

## Component Details

### 1. Supervisor Agent

**Role**: Central coordinator for the clinical workflow

**Responsibilities**:
- Receives user queries
- Routes tasks to appropriate specialist agents
- Aggregates results from multiple agents
- Handles error recovery
- Generates final clinical report

**Implementation**: `agents/supervisor.py`

**Key Methods**:
- `process_query()`: Main workflow execution
- `_format_literature_output()`: Literature display
- `_display_clinical_report()`: Final report generation

---

### 2. Literature Agent

**Role**: Automated medical literature retrieval

**Data Sources**:
- PubMed (primary, via pymed library)
- Google Scholar (secondary, via web scraping)

**Workflow**:
1. Parse user query (cancer type, treatment, date range)
2. Search PubMed with structured queries
3. Filter by publication date (2018-2025)
4. Extract metadata (title, authors, journal, PMID, abstract)
5. Return structured results

**Implementation**: `agents/literature_agent.py`

**Output Format**:
```python
{
    "status": "success",
    "papers": [
        {
            "title": "...",
            "authors": ["..."],
            "journal": "...",
            "year": 2024,
            "pmid": "...",
            "abstract": "..."
        }
    ],
    "total_found": 12
}
```

---

### 3. Analysis Agent

**Role**: Statistical survival analysis

**Capabilities**:
- Kaplan-Meier survival estimation
- Log-rank hypothesis testing
- Survival curve visualization

**Data**: Simulated clinical trial data (pembrolizumab vs nivolumab in melanoma)

**Workflow**:
1. Load survival data (time-to-event)
2. Fit Kaplan-Meier estimators per treatment group
3. Compute log-rank test statistic and p-value
4. Generate publication-quality survival curves (300 DPI)
5. Save figure to `outputs/figures/`

**Implementation**: `agents/analysis_agent.py`, `tools/stats_tool.py`

**Libraries**: lifelines, matplotlib

---

### 4. Doctor Agent

**Role**: Physician approval simulation (Human-in-the-Loop)

**Workflow**:
1. Receive AI-generated recommendation
2. Evaluate confidence score and p-value
3. Apply clinical decision rules:
   - Approve if p < 0.05 and confidence > 70%
   - Modify if evidence is weak
   - Reject if safety concerns
4. Generate clinical comment
5. Log decision to memory

**Implementation**: `agents/doctor_agent.py`

**Decision Logic**:
```python
if confidence < 0.70:
    decision = "modify"
elif p_value > 0.05:
    decision = "modify"
else:
    decision = "approve"
```

---

### 5. Clinical Reasoner

**Role**: GRADE-based recommendation generation

**GRADE Methodology**:
- Evidence quality assessment
- Benefit-harm balance
- Confidence scoring
- Recommendation strength (1A, 1B, 2C)

**Input Factors**:
- P-value (statistical significance)
- Number of publications (evidence quantity)
- Median survival benefit (clinical significance)

**Output**:
```python
{
    "recommendation": "Pembrolizumab preferred...",
    "grade": "1A",
    "strength_of_recommendation": "Strong recommendation",
    "confidence_score": 0.94,
    "rationale": "p=0.0083, 12 publications, OS benefit 22 months"
}
```

**Implementation**: `agents/clinical_reasoner.py`

---

## Tool Ecosystem

### PubMed Tool

**File**: `tools/pubmed_tool.py`

**Function**: `search_pubmed(query, max_results, min_year)`

**Technology**: pymed library (PubMed API wrapper)

**Rate Limits**: Respects NCBI's 3 requests/second guideline

---

### Statistics Tool

**File**: `tools/stats_tool.py`

**Function**: `perform_survival_analysis()`

**Key Operations**:
- Kaplan-Meier estimation (lifelines.KaplanMeierFitter)
- Log-rank test (lifelines.statistics.logrank_test)
- Matplotlib visualization with confidence intervals

**Output**: PNG figure + statistical metrics

---

### Risk Calculator

**File**: `tools/risk_calculator.py`

**Function**: `calculate_irae_risk()`

**Data**: Based on published clinical trial safety data

**Output**:
```python
{
    "any_grade_irae": "58%",
    "grade_3_4_irae": "18%",
    "pneumonitis": "7%",
    "recommendation": "Monitor thyroid function..."
}
```

---

## Data Flow

### Request Flow
```
1. User submits query via Streamlit UI
2. Supervisor Agent receives query
3. Literature Agent searches PubMed (parallel execution)
4. Analysis Agent performs survival analysis (parallel execution)
5. Clinical Reasoner generates GRADE recommendation
6. Doctor Agent reviews and approves
7. Supervisor aggregates results
8. Memory Service logs session
9. UI displays clinical report
```

### Data Persistence

**Storage**: SQLite database (`memory/cancer_research.db`)

**Schema**:
```sql
CREATE TABLE research_memory (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    query TEXT,
    cancer_type TEXT,
    findings JSON,
    timestamp DATETIME
);
```

**Operations**:
- `save_research()`: Store research session
- `save_doctor_review()`: Log physician decision
- `search_by_cancer_type()`: Retrieve past queries

---

## Technology Stack

### Backend
- **Python 3.9+**: Core language
- **Google Gemini 2.5 Flash**: LLM for clinical reasoning (REST API)
- **SQLite**: Persistent storage

### Libraries
- **pymed 0.8.9**: PubMed API client
- **lifelines 0.27.8**: Survival analysis
- **matplotlib 3.9.2**: Visualization
- **beautifulsoup4 4.12.3**: Google Scholar scraping
- **streamlit 1.51.0**: Web UI framework

### Architecture Patterns
- **Multi-Agent System**: Supervisor pattern with specialized agents
- **Tool-Based Design**: Agents invoke tools via function calls
- **Memory Service**: Centralized persistence layer
- **REST API Integration**: Direct HTTP calls to Gemini (no framework lock-in)

---

## Deployment Considerations

### Local Execution
- Single-machine deployment
- No external dependencies beyond Python libraries
- Suitable for research environments

### Scalability
- Modular design allows horizontal scaling
- Agents can be deployed as microservices
- Database can be upgraded to PostgreSQL for production

### Security
- API keys stored in environment variables
- No sensitive data in logs
- Patient data (if integrated) should follow HIPAA guidelines

---

## Performance Characteristics

- **Literature Search**: 2-5 seconds (depends on PubMed API)
- **Survival Analysis**: <1 second (local computation)
- **LLM Reasoning**: 1-3 seconds (Gemini API latency)
- **Total Workflow**: 5-10 seconds end-to-end

---

## Error Handling

### Failure Modes
1. **PubMed API timeout**: Retry with exponential backoff
2. **LLM rate limit**: Queue request, retry after delay
3. **Invalid user input**: Validate and prompt for correction
4. **Database write failure**: Log error, continue workflow

### Logging
- All agent actions logged to console (INFO level)
- Errors logged with full stack traces (ERROR level)
- Physician decisions logged to database for audit trail

---

## Future Architecture Enhancements

- **Agent-to-Agent (A2A) Protocol**: Enable direct agent communication
- **Evaluation Framework**: Automated testing with clinical test cases
- **Real-Time Updates**: WebSocket integration for streaming results
- **Cloud Deployment**: Containerization with Docker, deployment to Google Cloud Run

---

## References

- Google ADK Documentation (Agent Development Kit concepts)
- GRADE Working Group Methodology
- PubMed/NCBI E-utilities API Guide
- Lifelines Documentation (survival analysis)