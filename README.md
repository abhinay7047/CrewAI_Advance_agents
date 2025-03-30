# Advanced Business Analysis CrewAI Agent

This project implements an advanced multi-agent system using the CrewAI framework to perform comprehensive business analysis on a target organization.

## Overview

The system leverages multiple specialized agents, each equipped with custom tools, to execute a sequential workflow:

1.  **Target Research:** Gathers information about the target company (`Research Coordinator`).
2.  **Financial Analysis:** Analyzes the company's financial health (`Financial Analyst`).
3.  **Competitor Analysis:** Identifies and profiles key competitors (`Competitor Analyst`).
4.  **Market Analysis:** Analyzes the relevant market landscape, incorporating competitor data (`Market Analyst`).
5.  **Strategy Development:** Formulates an engagement strategy, incorporating all prior analysis (`Strategy Expert`).
6.  **Communication Planning:** Develops tailored communication approaches based on the strategy (`Comms Expert`).
7.  **Reflection:** Critically evaluates the overall generated plan, considering all preceding analysis (`Strategy Expert`).

The final output is a detailed text report summarizing the findings and recommendations, which can optionally be sent via email.

## Features

*   **Multi-Agent System:** Utilizes distinct agents for research coordination, financial analysis, competitor analysis, market analysis, strategy, and communication.
*   **Custom Tools:** Implements specialized tools for:
    *   Web Research (using DuckDuckGo)
    *   Market Analysis (simulated)
    *   Sentiment Analysis (basic keyword-based)
    *   Strategic Planning (rule-based)
    *   Communication Optimization (rule-based)
    *   Knowledge Base Retrieval (loads from `knowledge_base.json`)
*   **Dynamic Knowledge Base:** Loads best practices and frameworks from an external `knowledge_base.json` file.
*   **Sequential Workflow:** Defines a clear, step-by-step process using CrewAI's `Process.sequential`.
*   **Configuration:** Uses a `.env` file for API keys and email settings.
*   **Output Reporting:** Generates a structured text report (`.txt` file).
*   **Email Notification:** Optionally sends the generated report via email using SMTP.
*   **Error Handling:** Includes basic error handling within tools and the email function.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create and configure the `.env` file:**
    Create a file named `.env` in the project root and add the following variables:

    ```dotenv
    # Required for CrewAI (uses OpenAI models by default)
    OPENAI_API_KEY="your_openai_api_key"
    # OPENAI_MODEL_NAME="gpt-4" # Optional: Specify a model like gpt-4

    # Required for Email Functionality (Sender Details)
    EMAIL_ADDRESS="your_sender_email@example.com"
    EMAIL_PASSWORD="your_email_password_or_app_password"
    SMTP_SERVER="smtp.example.com"
    SMTP_PORT="587" # or 465 for SSL
    # RECIPIENT_EMAIL is now prompted for in the terminal
    ```

    *   Replace placeholders with your actual sender credentials.
    *   For Gmail with 2FA, you'll need to generate an "App Password".
    *   Ensure the SMTP server and port are correct for your email provider.

5.  **Verify `knowledge_base.json`:**
    Ensure the `knowledge_base.json` file exists in the project root. It contains the data used by the `KnowledgeBaseTool`.

## Usage

1.  **Activate the virtual environment** (if not already active):
    *   Windows: `.venv\Scripts\activate`
    *   macOS/Linux: `source .venv/bin/activate`

2.  **Modify Input Data (Optional):**
    Open `advance_agent.py` and change the values in the `input_data` dictionary (around line 560) if you want to analyze a different target.
    ```python
    input_data = {
        'company_name': 'New Target Company', # Replaces 'target_name'
        'industry': 'Their Industry'
    }
    ```

3.  **Run the script:**
    ```bash
    python advance_agent.py
    ```

4.  **Output:**
    *   The script will print detailed logs of the agent interactions to the console (`verbose=True`).
    *   A text report file named `<company_name_safe>_report_<timestamp>.txt` will be generated in the project root.
    *   **Email Prompt:** After generating the report, the script will ask you to enter the recipient's email address in the terminal.
    *   If a valid email is entered and sender settings in `.env` are correct, the script will attempt to send the report file.

## Configuration Details

*   **`.env` File:**
    *   `OPENAI_API_KEY`: Essential for the underlying LLMs used by CrewAI.
    *   `EMAIL_ADDRESS`/`EMAIL_PASSWORD`: Credentials for the email account sending the report.
    *   `SMTP_SERVER`/`SMTP_PORT`: Your email provider's SMTP details.
    *   ~~`RECIPIENT_EMAIL`~~: (Removed - prompted for in terminal)
*   **`knowledge_base.json`:** Stores structured information (frameworks, guidelines, insights) accessed by the `KnowledgeBaseTool`. You can modify or extend this file with more relevant data.
*   **`input_data` (in `advance_agent.py`):** Dictionary defining the target company name and industry for the analysis.

## Code Structure

*   **`advance_agent.py`:** The main script containing all logic.
    *   Imports and Setup (`load_dotenv`)
    *   `ToolInputSchema`: Pydantic schema for tool inputs.
    *   `EnhancedBaseTool`: Custom base class for tools, adding common structure.
    *   Tool Classes (`AdvancedResearchTool`, `MarketAnalysisTool`, etc.): Definitions of specific tools.
    *   `KnowledgeBaseTool`: Loads data from `knowledge_base.json`.
    *   `send_email_with_attachment`: Function to handle email sending.
    *   Agent Definitions (`Research Coordinator`, `Financial Analyst`, `Competitor Analyst`, `Market Analyst`, `Strategy Expert`, `Comms Expert`): Configuration of CrewAI agents with roles, goals, and assigned tools.
    *   Task Definitions (`target_research_task`, `financial_analysis_task`, `competitor_analysis_task`, etc.): Configuration of CrewAI tasks with descriptions, expected outputs, assigned agents, and context.
    *   Crew Definition: Assembles agents and tasks into a `Crew` object with a sequential process.
    *   Input Data: Dictionary specifying the analysis target.
    *   Execution (`crew.kickoff()`): Starts the agent workflow.
    *   Output Formatting (`format_to_text`): Creates the text report content.
    *   File Writing & Email Sending: Saves the report and triggers email.

## Customization

*   **Target:** Modify the `input_data` dictionary in `advance_agent.py`.
*   **Knowledge:** Edit or add entries to `knowledge_base.json`.
*   **Tools:** Modify the logic within existing tool classes or add new `EnhancedBaseTool` subclasses.
*   **Agents/Tasks:** Adjust agent roles, goals, tools, or task descriptions and sequences within `advance_agent.py`.
*   **LLM:** Set the `OPENAI_MODEL_NAME` environment variable in `.env` to use a different OpenAI model.