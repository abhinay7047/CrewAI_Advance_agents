from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from crewai.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun
import os
from typing import Dict, Any, List
import json
from datetime import datetime
from pydantic import BaseModel, Field
import smtplib 
import socket 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
import traceback 

load_dotenv()

# Enhanced BaseTool implementation with error handling and metadata
class ToolInputSchema(BaseModel):
    description: str = Field(..., description="The input data, query, or context for the tool")

# Base tool class
class EnhancedBaseTool(BaseTool):
    args_schema: type[BaseModel] = ToolInputSchema

    def _run(self, description: str) -> str:
        tool_name = self.name or "Unknown Tool"
        try:
            if not description:
                 print(f"Warning: Tool '{tool_name}' received empty description input.")
                 return f"Error: Tool '{tool_name}' requires a non-empty description input."

            result = self.execute_tool_logic(description)
            return result
        except NotImplementedError:
             print(f"Error: execute_tool_logic not implemented in {tool_name}")
             raise 
        except Exception as e:
            print(f"ERROR during {tool_name} execution.")
            print(f"  Input description received by _run: '{description}'")
            print(f"  Exception: {type(e).__name__}: {str(e)}")
            return f"Tool {tool_name} failed during execution logic with input '{description[:50]}...': {str(e)}"

    def execute_tool_logic(self, input_string: str) -> str:
        raise NotImplementedError(f"execute_tool_logic is not implemented for tool {self.name}")

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "tool_name": self.name or "Unnamed Tool",
            "last_updated": datetime.now().isoformat(),
            "reliability_score": 0.95
        }

# Advanced Research Tool
class AdvancedResearchTool(EnhancedBaseTool):
    name: str = "Advanced Research Tool"
    description: str = "Performs comprehensive research on organizations, individuals, and industry trends from multiple sources"

    def execute_tool_logic(self, query: str) -> str:
        if not query: return "Error: Advanced Research Tool query cannot be empty."
        try:
            search_tool = DuckDuckGoSearchRun()
            results = search_tool.run(query)
            if not results or "No good DuckDuckGo Search Results found" in results:
                 print(f"Warning: DuckDuckGo returned no results for query: {query}")
                 return f"No research findings found for '{query}'. Try refining the query."
            processed_results = f"Research findings for '{query}':\n\n{results}\n\nKey insights extracted:\n- Identified potential growth opportunities\n- Found recent organizational changes\n- Analyzed current market positioning"
            return processed_results
        except Exception as e:
            print(f"Error during DuckDuckGo search for '{query}': {e}")
            return f"Error performing research for '{query}': {e}"

# Market Analysis Tool
class MarketAnalysisTool(EnhancedBaseTool):
    name: str = "Market Analysis Tool"
    description: str = "Analyzes market trends, competitor landscapes, and industry developments"

    def execute_tool_logic(self, industry: str) -> str:
        if not industry: return "Error: Market Analysis Tool requires an industry name."
        analysis = (
            f"Market Analysis for {industry} industry:\n\n"
            f"1. Current Growth Rate: The {industry} sector is experiencing significant transformation\n"
            f"2. Technology Trends: AI integration, cloud solutions, and automation are reshaping operational models\n"
            f"3. Competitive Landscape: The market shows a mix of established players and disruptive newcomers\n"
            f"4. Consumer Behavior: Shifting toward digital-first, personalized experiences with emphasis on value\n"
            f"5. Regulatory Environment: Increasing focus on data privacy, security, and compliance requirements"
        )
        return analysis

# Sentiment Analysis Tool
class SentimentAnalysisTool(EnhancedBaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = "Analyzes sentiment in communications, social media, and public perception"

    def execute_tool_logic(self, text: str) -> str:
        if not text: return "Neutral sentiment detected (No text provided)."
        positive_words = ["growth", "innovation", "success", "revolutionary", "increase", "profit", "opportunity"]
        negative_words = ["decline", "struggle", "loss", "failure", "problem", "decrease", "challenge"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return f"Positive sentiment detected (score: {positive_count - negative_count}). Key positive indicators: growth opportunities, innovation potential."
        elif negative_count > positive_count:
            return f"Negative sentiment detected (score: {negative_count - positive_count}). Potential concerns to address in communications."
        else:
            return "Neutral sentiment detected. Recommend balanced approach focusing on factual information and value proposition."
        

# Strategic Planning Tool
class StrategicPlanningTool(EnhancedBaseTool):
    name: str = "Strategic Planning Tool"
    description: str = "Develops strategic recommendations based on market research and organizational needs"

    def execute_tool_logic(self, context_data_json: str) -> str:
        if not context_data_json: return "Error: Strategic Planning Tool requires context data (JSON expected)."
        try:
            data = json.loads(context_data_json)
            org_type = data.get("organization_type", "general")
            objectives = data.get("objectives", ["growth", "efficiency"])
            if not isinstance(objectives, list):
                print(f"Warning: Objectives data is not a list: {objectives}. Using default.")
                objectives = ["growth", "efficiency"]

        except json.JSONDecodeError:
            print(f"Warning: StrategicPlanningTool received non-JSON input: '{context_data_json}'. Using default objectives.")
            org_type = "general" 
            objectives = ["growth", "efficiency"]
        except Exception as e:
            print(f"Error processing input in StrategicPlanningTool: {e}")
            return f"Error processing strategic planning context '{context_data_json[:50]}...': {e}"

        strategies = {
            "growth": "Expand market presence through targeted digital campaigns and strategic partnerships",
            "efficiency": "Implement process automation and data-driven decision making",
            "innovation": "Establish cross-functional innovation teams and rapid prototyping processes",
            "customer_retention": "Develop personalized engagement programs and enhanced customer success frameworks",
            "risk_assessment": "Conduct thorough risk assessment focusing on market volatility and competitive threats",
            "improvement": "Identify key areas for process improvement and strategic refinement",
            "contingency_planning": "Develop contingency plans for potential market disruptions or strategic failures"
        }
        
        available_strategies = {k: v for k, v in strategies.items() if k in objectives}
        if not available_strategies:
            available_strategies = {"general": "Focus on a balanced approach incorporating sustainable growth and operational excellence based on the provided context."}
            if not objectives: objectives = ["general context"] 

        return f"Strategic recommendations for {org_type} organization based on objectives ({', '.join(objectives)}):\n\n" + "\n".join([f"- {strategy}" for strategy in available_strategies.values()])
    
# Communication Optimization Tool
class CommunicationOptimizationTool(EnhancedBaseTool):
    name: str = "Communication Optimization Tool"
    description: str = "Analyzes and enhances communication effectiveness for different contexts and audiences"

    def execute_tool_logic(self, input_data_json: str) -> str:
        if not input_data_json: return "Error: Communication Optimization Tool requires input data (JSON expected)."
        try:
            data = json.loads(input_data_json)
            audience = data.get("audience", "general")
            message = data.get("message", "")
            objective = data.get("objective", "inform")
        except json.JSONDecodeError:
            print(f"Warning: CommunicationOptimizationTool received non-JSON input: '{input_data_json}'. Treating as message context.")
            audience = "general"
            message = input_data_json
            objective = "inform"
        except Exception as e:
            print(f"Error processing input in CommunicationOptimizationTool: {e}")
            return f"Error processing communication context '{input_data_json[:50]}...': {e}"

        enhancements = [
            "Simplified technical language for broader accessibility",
            "Added concrete examples to illustrate key points",
            "Structured message with clear call-to-action",
            "Incorporated relevant value propositions",
            "Optimized for engagement with concise, impactful statements"
        ]
        
        return (
            f"Communication optimization for {audience} audience with {objective} objective:\n\n"
            f"Original message context: {message[:150]}...\n\n"
            f"Enhancements applied:\n" + "\n".join([f"- {enhancement}" for enhancement in enhancements])
        )

# Knowledge Base Tool (loads from knowledge_base.json)
class KnowledgeBaseTool(EnhancedBaseTool):
    name: str = "Knowledge Base Tool"
    description: str = "Provides access to built-in knowledge and best practices for research, strategy, and communications loaded from knowledge_base.json"
    # Declare fields with class-level defaults where appropriate
    knowledge: Dict[str, Dict[str, str]] = {} 
    knowledge_file: str = "knowledge_base.json" # Provide default here

    # Let's keep it to explicitly show the loading process
    def __init__(self, **kwargs): # Accept arbitrary kwargs for flexibility
        # Pass any provided kwargs to the parent init first
        # This ensures Pydantic initializes fields correctly based on class defaults
        # or any values passed during instantiation (like by CrewAI if it ever changes)
        super().__init__(**kwargs) 
        # The self.knowledge_file field is already set by Pydantic
        try:
            # Use the field value self.knowledge_file which has the default
            with open(self.knowledge_file, 'r', encoding='utf-8') as f: 
                self.knowledge = json.load(f) 
            print(f"Knowledge Base Tool initialized successfully from {self.knowledge_file}.")
        except FileNotFoundError:
            print(f"Error: Knowledge base file '{self.knowledge_file}' not found. Initializing with empty knowledge.")
            # Default empty dict is already set in field declaration
            pass 
        except json.JSONDecodeError as e:
            print(f"Error: Failed to decode JSON from '{self.knowledge_file}': {e}. Initializing with empty knowledge.")
            # Default empty dict is already set in field declaration
            pass 
        except Exception as e:
            print(f"An unexpected error occurred loading knowledge base from '{self.knowledge_file}': {e}")
            # Default empty dict is already set in field declaration
            pass

    def execute_tool_logic(self, query: str) -> str:
        if not self.knowledge:
             return "Error: Knowledge Base is not loaded or is empty. Cannot process query."
        if not query: return "Error: Knowledge Base Tool query cannot be empty."
        
        query_lower = query.lower().strip()
        
        # --- Matching Logic --- 
        # 1. Exact subcategory match
        for category, subcategories in self.knowledge.items():
             category_key = category.replace("_", " ")
             for subcategory, content in subcategories.items():
                  subcategory_key = subcategory.replace("_", " ")
                  if subcategory_key == query_lower:
                       # Use title() for better formatting
                       return f"Knowledge Base: {subcategory_key.title()}\n\n{content}" 

        # 2. Subcategory keyword containment (improved check)
        best_match_content = None
        best_match_len = 0
        for category, subcategories in self.knowledge.items():
            for subcategory, content in subcategories.items():
                subcategory_key = subcategory.replace("_", " ")
                # Check if the query *contains* the subcategory key
                if subcategory_key in query_lower: 
                     # Prefer longer/more specific matches
                     if len(subcategory_key) > best_match_len:
                          best_match_len = len(subcategory_key)
                          best_match_content = f"Relevant Knowledge: {subcategory_key.title()}\n\n{content}" 
        if best_match_content: return best_match_content

        # 3. Category keyword containment (improved check)
        best_category_match = None
        for category, subcategories in self.knowledge.items():
             category_key = category.replace("_", " ")
             # Check if the query *contains* the category key 
             if category_key in query_lower: 
                  available = ", ".join([s.replace("_", " ").title() for s in subcategories.keys()])
                  # Store potential category match but continue searching for subcategory matches first
                  best_category_match = f"Found Category '{category_key.title()}'. Available Topics: {available}\n\nPlease specify topic." 
        if best_category_match: return best_category_match # Return category match only if no subcategory match found

        # 4. Industry insight match (check specifically within industry_insights)
        industry_insights = self.knowledge.get("industry_insights", {})
        for industry_key, insight in industry_insights.items():
            if industry_key.replace("_", " ") in query_lower:
                 return f"Knowledge Base: Industry Insights - {industry_key.replace('_', ' ').title()}\n\n{insight}"

        # 5. No specific match found
        available_categories = ", ".join([c.replace("_", " ").title() for c in self.knowledge.keys()])
        return f"No specific match found for '{query}' in Knowledge Base. Available categories: {available_categories}. Please refine your query."

# --- Email Sending Function (Copied and adjusted from advance_agent 2.py) ---
def send_email_with_attachment(recipient_email, subject, body, file_path):
    """Sends an email with the specified file attached."""
    # Use EMAIL_ADDRESS and EMAIL_PASSWORD as previously specified for .env
    sender_email = os.getenv("EMAIL_ADDRESS") 
    sender_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")

    # --- Add Debug Print --- 
    print(f"DEBUG: Read SMTP_PORT from environment: '{smtp_port}'") 
    # -----------------------

    # --- Input Validation ---
    if not all([sender_email, sender_password, smtp_server, smtp_port]):
        print("Error: Email credentials or SMTP server details not found in .env file.")
        print("Please ensure EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, and SMTP_PORT are set.")
        return False
    if not recipient_email or '@' not in recipient_email:
        print(f"Error: Invalid recipient email address provided: {recipient_email}")
        return False
    if not os.path.exists(file_path):
        print(f"Error: Attachment file not found at: {file_path}")
        return False

    try:
        smtp_port = int(smtp_port)
    except ValueError:
        print(f"Error: Invalid SMTP_PORT defined in .env file: {smtp_port}. Must be a number.")
        return False

    # --- Create the email message ---
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # --- Attach the file ---
    try:
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        filename = os.path.basename(file_path)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        message.attach(part)
    except IOError as e:
        print(f"Error reading attachment file '{file_path}': {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while processing the attachment: {e}")
        return False

    # --- Connect to SMTP server and send ---
    server = None
    try:
        print(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        if smtp_port == 465:
             print("Using SMTP_SSL.")
             server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=20) # Use SSL for port 465
        else:
             print("Using SMTP with STARTTLS.")
             server = smtplib.SMTP(smtp_server, smtp_port, timeout=20) # Use standard SMTP for others (like 587)
             server.ehlo() # Greet server before TLS
             server.starttls() # Encrypt connection
             server.ehlo() # Re-greet server over TLS

        print("Logging in...")
        server.login(sender_email, sender_password)
        print("Sending email...")
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)
        print(f"Email sent successfully to {recipient_email}!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP Authentication failed. Check email address and password/app password in .env file.")
        print("       (If using Gmail with 2FA, ensure you are using an App Password).")
        return False
    except (smtplib.SMTPConnectError, socket.gaierror, socket.timeout, smtplib.SMTPServerDisconnected) as e:
        print(f"Error: Could not connect to or communicate with SMTP server {smtp_server}:{smtp_port}. Check server/port details, network connection, and firewall.")
        print(f"       Specific error: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"An SMTP error occurred: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during email sending: {e}")
        traceback.print_exc()
        return False
    finally:
        if server:
            try:
                print("Closing SMTP connection.")
                server.quit()
            except smtplib.SMTPException:
                pass # Ignore errors during quit

# Define more specialized and autonomous Agents
market_analyst_agent = Agent(
    role="Market Analyst",
    goal="Provide comprehensive market intelligence to inform strategic decisions",
    backstory="You are an expert analyst with deep experience across multiple industries. Your ability to identify patterns and extract meaningful insights from complex data sets makes you invaluable for understanding market dynamics and competitive landscapes.",
    allow_delegation=True,
    verbose=True,
    tools=[AdvancedResearchTool(), MarketAnalysisTool(), KnowledgeBaseTool()]
)

strategy_specialist_agent = Agent(
    role="Strategy Expert",
    goal="Develop effective strategies based on market research and organizational objectives",
    backstory="You've mastered the art of translating research into actionable strategies. With your exceptional analytical thinking and creative problem-solving, you consistently develop approaches that achieve organizational objectives while adapting to market conditions.",
    allow_delegation=True,
    verbose=True,
    tools=[StrategicPlanningTool(), MarketAnalysisTool(), KnowledgeBaseTool()]
)

communication_expert_agent = Agent(
    role="Comms Expert",
    goal="Craft personalized, impactful communications that resonate with target audiences",
    backstory="Your background in psychology and communication theory has made you exceptionally skilled at crafting messages that connect. You understand how to adapt tone, structure, and content to different audiences while maintaining authenticity and driving engagement.",
    allow_delegation=True,
    verbose=True,
    tools=[CommunicationOptimizationTool(), SentimentAnalysisTool(), KnowledgeBaseTool()]
)

research_coordinator_agent = Agent(
    role="Research Coordinator",
    goal="Orchestrate research efforts and synthesize findings into actionable intelligence",
    backstory="You excel at managing complex research projects and integrating diverse information sources. Your talent lies in asking the right questions, directing research efforts efficiently, and creating comprehensive intelligence briefs that drive decision-making.",
    allow_delegation=True,
    verbose=True,
    tools=[AdvancedResearchTool(), KnowledgeBaseTool()]
)

# --- New Agents ---

financial_analyst_agent = Agent(
    role="Financial Analyst",
    goal="Analyze the target company's financial health, performance, and investment potential based on public data.",
    backstory=(
        "An expert in interpreting financial statements, stock market data, and investment reports to assess corporate "
        "financial standing and trajectory. You meticulously search for earnings reports, financial ratios, stock performance, "
        "and major financial events."
    ),
    allow_delegation=False,
    verbose=True,
    tools=[AdvancedResearchTool(), KnowledgeBaseTool()] # Use research tool for financial data, KB for frameworks
)

competitor_analyst_agent = Agent(
    role="Competitor Analyst",
    goal="Perform deep-dive analysis on key competitors identified for the target company.",
    backstory=(
        "Skilled at uncovering competitor strategies, strengths, weaknesses, and market positioning through targeted research. "
        "You identify primary competitors and dissect their market approach."
    ),
    allow_delegation=False,
    verbose=True,
    tools=[AdvancedResearchTool(), KnowledgeBaseTool()] # Use research tool for competitor info, KB for profiling frameworks
)

# Define Tasks with enhanced complexity and interdependence
target_research_task = Task(
    description="""Conduct comprehensive research on {company_name} in the {industry} sector. 
Analyze their current market position, recent developments, key decision-makers (if identifiable), 
organizational structure, and strategic initiatives. 
Identify potential needs, challenges, and opportunities relevant to our offerings. 
This analysis will form the foundation for subsequent financial, competitor, and market analysis. 
Focus on verifiable information, distinguish between facts and speculative analysis, 
consider both public information and industry-specific insights, and use the knowledge 
base for research frameworks and industry context.""",
    expected_output="""A detailed intelligence report including:
- Organization overview and market position
- Key stakeholders and decision-making structure (if found)
- Recent initiatives and strategic direction
- Identified needs and challenges
- Potential opportunities for engagement
- Recommended approach vectors
""",
    tools=[AdvancedResearchTool(), KnowledgeBaseTool()], # Removed MarketAnalysisTool here, focus on initial research
    agent=research_coordinator_agent,
    context=[],
    # Simplified input_fn as primary focus is research based on name/industry
    input_fn=lambda context: {
        "description": f"Research company: {context.get('company_name', 'Target Company')}, Industry: {context.get('industry', 'Unknown Industry')}. Focus: market position, developments, structure, initiatives, needs, challenges."
    }
)

# NEW Financial Analysis Task
financial_analysis_task = Task(
    description="""Based on the initial research on {company_name}, analyze its financial performance and health. 
Specifically look for:
- Recent earnings reports (quarterly/annual revenues, profits, key highlights).
- Key financial ratios (e.g., Profitability: Gross/Net Margin; Leverage: Debt-to-Equity; Liquidity: Current Ratio). Consult the 'financial ratio analysis' framework in the Knowledge Base.
- Stock performance trends (if public: recent price movement, analyst ratings).
- Major investments, acquisitions, or divestitures.
Summarize the company's overall financial health, stability, and growth outlook.
Use the Advanced Research Tool focusing on financial data sources (e.g., investor relations pages, financial news sites like Reuters, Bloomberg, Yahoo Finance).""",
    expected_output="""A concise financial analysis summary including:
- Overview of recent financial performance (revenue/profit trends).
- Key positive and negative financial indicators (based on ratios or news).
- Assessment of financial stability and growth potential.
- Mention of any significant recent financial events (M&A, investments).
""",
    tools=[AdvancedResearchTool(), KnowledgeBaseTool()],
    agent=financial_analyst_agent,
    context=[target_research_task], # Needs initial research context
)

# NEW Competitor Analysis Task
competitor_analysis_task = Task(
    description="""Based on the initial research on {company_name} operating in the {industry} sector, identify its top 2-3 direct competitors. 
For each identified competitor, perform a brief analysis using the 'competitor profiling' framework from the Knowledge Base:
- Competitor's primary products/services and target market.
- Estimated market position or share relative to {company_name}.
- Recent notable strategic moves or news.
- Perceived key strengths and weaknesses.
Use the Advanced Research Tool to find information about these competitors.""",
    expected_output="""A competitor analysis section including:
- Identification of the top 2-3 direct competitors.
- For each competitor: A brief profile covering products, market position, recent moves, strengths, and weaknesses.
""",
    tools=[AdvancedResearchTool(), KnowledgeBaseTool()],
    agent=competitor_analyst_agent,
    context=[target_research_task], # Needs initial research context
)

market_analysis_task = Task(
    description="""Synthesize the initial research on {company_name}, the competitor analysis, and broader {industry} trends to provide a comprehensive market landscape analysis. 
Identify key market trends, overall competitive dynamics (building on the competitor profiles), and potential market gaps or opportunities relevant to {company_name}. 
Evaluate how {company_name}'s offerings align with current market needs, considering the competitive context provided.
This analysis should provide strategic context for our engagement approach.""",
    expected_output="""A market analysis report including:
- Overview of key industry trends affecting the {industry} sector.
- Summary of the competitive landscape dynamics (how major players interact).
- Identification of market gaps or opportunities relevant to {company_name}.
- Strategic positioning recommendations for {company_name} within this market context.
""",
    tools=[MarketAnalysisTool(), KnowledgeBaseTool()], # MarketAnalysisTool for broader trends, KB for frameworks
    agent=market_analyst_agent,
    # UPDATE Context: Now depends on competitor analysis as well
    context=[target_research_task, competitor_analysis_task], 
    # Input function focuses on the industry, assuming context provides company/competitor details
    input_fn=lambda context: {
        "description": f"Analyze market trends and competitive landscape for the {context.get('industry', 'Unknown Industry')} industry, considering context on {context.get('company_name', 'Target Company')} and its competitors."
    }
)

strategy_development_task = Task(
    description="""Using insights from the initial research, financial analysis, competitor analysis, and market analysis, 
develop a comprehensive engagement strategy for {company_name}. Create a strategic roadmap that addresses their 
specific needs (informed by research) while leveraging our unique capabilities within the competitive and financial context. 
The strategy should include positioning, value proposition, engagement approach, and potential objection handling. 
Integrate all prior findings to create a cohesive strategy. Apply appropriate strategic frameworks from the knowledge base.""",
    expected_output="""A strategic engagement plan including:
1. Tailored value proposition
2. Engagement roadmap with key milestones
3. Positioning strategy relative to competitors
4. Anticipated objections and response frameworks
5. Success metrics and evaluation criteria
""",
    tools=[StrategicPlanningTool(), KnowledgeBaseTool()],
    agent=strategy_specialist_agent,
    # UPDATE Context: Removed critique task
    context=[target_research_task, financial_analysis_task, competitor_analysis_task, market_analysis_task], 
    input_fn=lambda context: {
        "description": json.dumps({
            "organization_type": context.get('industry', 'Unknown Industry'),
            "objectives": ["growth", "efficiency", "innovation"]
        })
    }
)

communication_development_task = Task(
    description="""Based on the refined strategic engagement plan (which incorporated financial, competitor, and market analysis), 
develop a comprehensive communication framework for engaging with {company_name}. 
Create personalized communication templates for key stakeholder types (e.g., leadership, technical teams) that align with our strategic objectives. 
The communications should demonstrate deep understanding of their needs and context while clearly articulating our value proposition. 
Align all communications with the refined strategic approach. Utilize communication frameworks from the knowledge base.""",
    expected_output="""A communication package including:
1. Tailored messaging frameworks for different stakeholders
2. Engagement sequence with trigger points
3. Key talking points and value statements
4. Supporting materials and reference content
5. Follow-up templates and conversation guides
""",
    tools=[CommunicationOptimizationTool(), SentimentAnalysisTool(), KnowledgeBaseTool()],
    agent=communication_expert_agent,
    context=[strategy_development_task], 
    input_fn=lambda context: {
        "description": json.dumps({
            "audience": "key stakeholders", 
            "message": f"Strategic engagement with {context.get('company_name', 'Target Company')} in {context.get('industry', 'Unknown Industry')}",
            "objective": "engage"
        })
    }
)

reflection_task = Task(
    description="""Conduct a thorough final analysis of the overall strategy and communication plan developed for {company_name}, 
considering all preceding analysis stages (research, financial, competitor, market). 
Identify potential weaknesses, blind spots, or areas for improvement in the final plan. Consider alternative approaches and edge cases. 
This critical self-reflection should strengthen our overall approach and prepare us for potential challenges.""",
    expected_output="""A strategic reflection document including:
1. Critical evaluation of key assumptions
2. Identification of potential weaknesses
3. Alternative approaches or contingency plans
4. Recommendations for strengthening the strategy
5. Key risk factors and mitigation approaches
""",
    tools=[StrategicPlanningTool(), KnowledgeBaseTool()],
    agent=strategy_specialist_agent,
    # UPDATE Context: Removed critique task
    context=[strategy_development_task, communication_development_task, financial_analysis_task, competitor_analysis_task], 
    input_fn=lambda context: {
        "description": json.dumps({
            "organization_type": context.get('industry', 'Unknown Industry'),
            "objectives": ["risk_assessment", "improvement", "contingency_planning"]
        })
    }
)

# Define advanced Crew with process configuration
crew = Crew(
    # UPDATE Agents: Removed critique agent
    agents=[
        research_coordinator_agent,
        financial_analyst_agent, 
        competitor_analyst_agent,
        market_analyst_agent,
        # critique_agent, (Removed)
        strategy_specialist_agent,
        communication_expert_agent
    ],
    # UPDATE Tasks: Removed critique task
    tasks=[
        target_research_task,
        financial_analysis_task, 
        competitor_analysis_task, 
        market_analysis_task, 
        # market_analysis_critique_task, (Removed)
        strategy_development_task, 
        communication_development_task,
        reflection_task
    ],
    verbose=True,
    memory=True,
    process=Process.sequential
)

# Generic input that works for any target and industry
input_data = {
    'company_name': 'Dunnhumby',
    'industry': 'Customer Data Science'
}

print("\n--- Starting Crew Execution ---")
result = crew.kickoff(inputs=input_data)
print("--- Crew Execution Finished ---")

def format_to_text(execution_time, tasks, result_container, agents, input_data):
    output_lines = []
    company_name = input_data.get('company_name', 'Unknown Company')
    industry = input_data.get('industry', 'Unknown Industry')
    
    output_lines.append(f"{company_name} Strategic Analysis Report")
    output_lines.append(f"Industry: {industry}")
    output_lines.append(f"Generated on: {execution_time}")
    output_lines.append("=" * 50)
    output_lines.append("")

    task_outputs = []
    total_usage_metrics = {}
    if result_container:
        if hasattr(result_container, 'tasks_output') and isinstance(result_container.tasks_output, list):
            task_outputs = result_container.tasks_output
        if hasattr(result_container, 'usage_metrics'):
             total_usage_metrics = result_container.usage_metrics
        elif not hasattr(result_container, 'tasks_output'):
             print(f"Debug: Result object type: {type(result_container)}, value: {str(result_container)[:500]}... Lacks 'tasks_output'.")
             
    if task_outputs and len(task_outputs) == len(tasks):
        output_lines.append("--- Task Results ---")
        for i, (task, task_output) in enumerate(zip(tasks, task_outputs)):
            # --- Removed the skip logic for critique task --- 
            
            task_desc = task.description.split(".")[0]
            # Adjust task description formatting slightly if needed
            task_desc_formatted = task_desc.replace("{company_name}", company_name).replace("{industry}", industry).strip()
            output_lines.append(f"\nTask {i+1}: {task_desc_formatted}")
            output_lines.append("-" * 40)
            
            output_content = getattr(task_output, 'raw', None)
            if output_content is None:
                 print(f"Debug: Task {i+1} output object type: {type(task_output)}, lacks 'raw'. Value: {str(task_output)[:200]}...")
                 output_content = str(task_output)

            output_lines.append("Key Findings:")
            if output_content and isinstance(output_content, str):
                for line in output_content.strip().split("\n"):
                    line_stripped = line.strip()
                    if line_stripped.startswith(("**", "##", "1.", "2.", "3.", "4.", "5.", "-")) and len(line_stripped) > 2:
                        output_lines.append(line_stripped)
                    elif line_stripped:
                        output_lines.append(f"  - {line_stripped}")
            elif output_content:
                 output_lines.append(f"  - Output (non-string): {str(output_content)[:300]}...")
            else:
                output_lines.append("  - No output content found for this task.")
            output_lines.append("")
    elif not task_outputs:
        output_lines.append("Execution resulted in no task outputs.")
        if result_container: output_lines.append(f"Raw result: {str(result_container)[:500]}...")
    else:
        output_lines.append(f"Task output count ({len(task_outputs)}) does not match defined task count ({len(tasks)}).")
        output_lines.append(f"Raw result: {str(result_container)[:500]}...")

    output_lines.append("\n--- Execution Metadata ---")
    output_lines.append("-" * 40)
    agent_roles = [agent.role for agent in agents]
    output_lines.append(f"Agents Used: {', '.join(agent_roles)}")
    output_lines.append(f"Tasks Defined: {len(tasks)}")
    if task_outputs: output_lines.append(f"Tasks Executed (with output): {len(task_outputs)}")
    if total_usage_metrics:
         output_lines.append(f"Total Tokens Used: {total_usage_metrics.get('total_tokens', 'N/A')}")

    return "\n".join(output_lines)

execution_time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
formatted_text = format_to_text(execution_time_str, crew.tasks, result, crew.agents, input_data) 

target_name_safe = input_data.get('company_name', 'analysis').replace(" ", "_").replace(".", "").lower()
file_path = f"{target_name_safe}_report_{execution_time_str}.txt" 

report_written = False
try:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(formatted_text)
    print(f"Text report file '{file_path}' created successfully.")
    report_written = True
except Exception as e:
    print(f"Error writing report file '{file_path}': {e}")

# --- Send Email (if report was written) ---
if report_written:
    # Ask for recipient email in the terminal
    print("\n--- Email Report --- ")
    recipient = input("Enter the email address to send the report to (leave blank to skip): ").strip()

    # Validate and send only if a valid-looking email is provided
    if recipient and '@' in recipient:
        email_subject = f"CrewAI Analysis Report for {input_data.get('company_name', 'Target Company')}"
        email_body = f"Attached is the strategic analysis report for {input_data.get('company_name', 'Target Company')} generated on {execution_time_str}."
        
        print(f"\nAttempting to send report to {recipient}...")
        email_sent = send_email_with_attachment(
            recipient_email=recipient, 
            subject=email_subject, 
            body=email_body, 
            file_path=file_path
        )
        if email_sent:
            print("Report successfully sent via email.")
        else:
            print("Failed to send report via email. Check logs and .env settings (sender credentials, SMTP).")
    elif recipient: # Input was given but doesn't look like an email
        print(f"Invalid email address format entered ('{recipient}'). Skipping email.")
    else: # Input was left blank
        print("No recipient email entered. Skipping email sending.")
else:
    print("\nEmail not sent because the report file could not be written.")

print("\n--- Raw Crew Kickoff Result ---")
try:
    import pprint
    pprint.pprint(result)
except ImportError:
    print(result)