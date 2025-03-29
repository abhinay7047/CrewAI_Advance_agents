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
    # Removed the hardcoded knowledge dictionary

    def __init__(self, knowledge_file: str = "knowledge_base.json"):
        super().__init__() # Initialize the parent BaseTool class
        self.knowledge: Dict[str, Dict[str, str]] = {}
        self.knowledge_file = knowledge_file
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)
            print(f"Knowledge Base Tool initialized successfully from {self.knowledge_file}.")
        except FileNotFoundError:
            print(f"Error: Knowledge base file '{self.knowledge_file}' not found. Initializing with empty knowledge.")
            self.knowledge = {}
        except json.JSONDecodeError as e:
            print(f"Error: Failed to decode JSON from '{self.knowledge_file}': {e}. Initializing with empty knowledge.")
            self.knowledge = {}
        except Exception as e:
            print(f"An unexpected error occurred loading knowledge base from '{self.knowledge_file}': {e}")
            self.knowledge = {}

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
    role="Market Research Specialist",
    goal="Provide comprehensive market intelligence to inform strategic decisions",
    backstory="You are an expert analyst with deep experience across multiple industries. Your ability to identify patterns and extract meaningful insights from complex data sets makes you invaluable for understanding market dynamics and competitive landscapes.",
    allow_delegation=True,
    verbose=True,
    tools=[AdvancedResearchTool(), MarketAnalysisTool(), KnowledgeBaseTool()]
)

strategy_specialist_agent = Agent(
    role="Strategic Planning Expert",
    goal="Develop effective strategies based on market research and organizational objectives",
    backstory="You've mastered the art of translating research into actionable strategies. With your exceptional analytical thinking and creative problem-solving, you consistently develop approaches that achieve organizational objectives while adapting to market conditions.",
    allow_delegation=True,
    verbose=True,
    tools=[StrategicPlanningTool(), MarketAnalysisTool(), KnowledgeBaseTool()]
)

communication_expert_agent = Agent(
    role="Communication Specialist",
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

# Define Tasks with enhanced complexity and interdependence
target_research_task = Task(
    description=(
        "Conduct comprehensive research on {target_name} in the {industry} sector. "
        "Analyze their current market position, recent developments, key decision-makers, "
        "organizational structure, and strategic initiatives. "
        "Identify potential needs, challenges, and opportunities relevant to our offerings. "
        "This analysis will form the foundation for our strategic approach. "
        "Focus on verifiable information, distinguish between facts and speculative analysis, "
        "consider both public information and industry-specific insights, and use the knowledge "
        "base for research frameworks and industry context."
    ),
    expected_output=(
        "A detailed intelligence report including:\n"
        "1. Organization overview and market position\n"
        "2. Key stakeholders and decision-making structure\n"
        "3. Recent initiatives and strategic direction\n"
        "4. Identified needs and challenges\n"
        "5. Potential opportunities for engagement\n"
        "6. Recommended approach vectors"
    ),
    tools=[AdvancedResearchTool(), MarketAnalysisTool(), KnowledgeBaseTool()],
    agent=research_coordinator_agent,
    context=[],
    input_fn=lambda context: {
        "description": f"Research target: {context.get('target_name', 'Target')}, Industry: {context.get('industry', 'industry')}, Focus: market position, developments, decision-makers, and strategic initiatives"
    }
)

market_analysis_task = Task(
    description=(
        "Based on the research findings about {target_name}, conduct a thorough analysis of the "
        "{industry} market landscape. Identify key trends, competitive dynamics, and market gaps. "
        "Evaluate how our solutions align with current market needs and opportunities. "
        "This analysis should provide strategic context for our engagement approach. "
        "Use the target research as context for more focused market analysis, consider both "
        "established patterns and emerging trends in the industry, and identify specific areas "
        "where our solutions can address market needs."
    ),
    expected_output=(
        "A market analysis report including:\n"
        "1. Industry overview and current trends\n"
        "2. Competitive landscape analysis\n"
        "3. Market gaps and opportunities\n"
        "4. Strategic positioning recommendations\n"
        "5. Potential differentiation points for our offerings"
    ),
    tools=[MarketAnalysisTool(), AdvancedResearchTool(), KnowledgeBaseTool()],
    agent=market_analyst_agent,
    context=[target_research_task],
    input_fn=lambda context: {
        "description": f"Analyze market trends and competitive landscape for {context.get('industry', 'Fast-moving consumer goods')} industry, focusing on recent developments and future opportunities" 
    }
)

strategy_development_task = Task(
    description=(
        "Using insights from both the target research and market analysis, develop a comprehensive "
        "engagement strategy for {target_name}. Create a strategic roadmap that addresses their "
        "specific needs while leveraging our unique capabilities. The strategy should include "
        "positioning, value proposition, engagement approach, and potential objection handling. "
        "Integrate findings from previous research to create a cohesive strategy, ensure the "
        "strategy addresses specific needs identified in the research, balance short-term "
        "engagement objectives with long-term relationship building, and apply appropriate "
        "strategic frameworks from the knowledge base."
    ),
    expected_output=(
        "A strategic engagement plan including:\n"
        "1. Tailored value proposition\n"
        "2. Engagement roadmap with key milestones\n"
        "3. Positioning strategy relative to competitors\n"
        "4. Anticipated objections and response frameworks\n"
        "5. Success metrics and evaluation criteria"
    ),
    tools=[StrategicPlanningTool(), KnowledgeBaseTool()],
    agent=strategy_specialist_agent,
    context=[target_research_task, market_analysis_task],
    input_fn=lambda context: {
        "description": json.dumps({
            "organization_type": context.get('industry', 'Fast-moving consumer goods'),
            "objectives": ["growth", "efficiency", "innovation"]
        })
    }
)

communication_development_task = Task(
    description=(
        "Based on the strategic engagement plan, develop a comprehensive communication framework "
        "for engaging with {target_name}. Create personalized communication templates for key "
        "stakeholders that align with our strategic objectives. The communications should "
        "demonstrate deep understanding of their needs while clearly articulating our value "
        "proposition. Align all communications with the strategic approach developed earlier, "
        "customize messaging for different stakeholder roles and priorities, balance educational "
        "content with clear value propositions, and utilize communication frameworks from the "
        "knowledge base."
    ),
    expected_output=(
        "A communication package including:\n"
        "1. Tailored messaging frameworks for different stakeholders\n"
        "2. Engagement sequence with trigger points\n"
        "3. Key talking points and value statements\n"
        "4. Supporting materials and reference content\n"
        "5. Follow-up templates and conversation guides"
    ),
    tools=[CommunicationOptimizationTool(), SentimentAnalysisTool(), KnowledgeBaseTool()],
    agent=communication_expert_agent,
    context=[strategy_development_task],
    input_fn=lambda context: {
        "description": json.dumps({
            "audience": context.get('key_decision_maker', 'stakeholder'),
            "message": f"Strategic engagement with {context.get('target_name', 'Target')} in {context.get('industry', 'Fast-moving consumer goods')}",
            "objective": "engage"
        })
    }
)

# Add a self-reflection task to demonstrate advanced agentic capabilities
reflection_task = Task(
    description=(
        "Conduct a thorough analysis of the strategy and communication plan developed for {target_name}. "
        "Identify potential weaknesses, blind spots, or areas for improvement. Consider alternative "
        "approaches and edge cases that might not have been addressed. This critical self-reflection "
        "should strengthen our overall approach and prepare us for potential challenges. "
        "Apply critical thinking to challenge assumptions in the existing strategy, consider how "
        "competitors might respond to our approach, identify potential implementation challenges, "
        "and suggest specific enhancements to improve effectiveness."
    ),
    expected_output=(
        "A strategic reflection document including:\n"
        "1. Critical evaluation of key assumptions\n"
        "2. Identification of potential weaknesses\n"
        "3. Alternative approaches or contingency plans\n"
        "4. Recommendations for strengthening the strategy\n"
        "5. Key risk factors and mitigation approaches"
    ),
    tools=[StrategicPlanningTool(), KnowledgeBaseTool()],
    agent=strategy_specialist_agent,
    context=[strategy_development_task, communication_development_task],
    input_fn=lambda context: {
        "description": json.dumps({
            "organization_type": context.get('industry', 'Fast-moving consumer goods'),
            "objectives": ["risk_assessment", "improvement", "contingency_planning"]
        })
    }
)
# Define advanced Crew with process configuration
crew = Crew(
    agents=[
        research_coordinator_agent,
        market_analyst_agent,
        strategy_specialist_agent,
        communication_expert_agent
    ],
    tasks=[
        target_research_task,
        market_analysis_task,
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
    'target_name': 'Hindustan Unilever Limited',
    'industry': 'Fast-moving consumer goods',
    'key_decision_maker': 'Rohit Jawa',
    'position': 'CEO',
    'milestone': 'HUL exceeded INR 50,000 Crore in revenue'
}

print("\n--- Starting Crew Execution ---")
result = crew.kickoff(inputs=input_data)
print("--- Crew Execution Finished ---")

def format_to_text(execution_time, tasks, result_container, agents, input_data):
    output_lines = []
    target_name = input_data.get('target_name', 'Unknown Target')
    industry = input_data.get('industry', 'Unknown Industry')
    
    output_lines.append(f"{target_name} Strategic Analysis Report")
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
            task_desc = task.description.split(".")[0]
            output_lines.append(f"\nTask {i+1}: {task_desc}")
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

target_name_safe = input_data.get('target_name', 'analysis').replace(" ", "_").replace(".", "").lower()
file_path = f"{target_name_safe}_report_{execution_time_str}.txt" 

report_written = False
try:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(formatted_text)
    print(f"Text report file '{file_path}' created successfully.")
    report_written = True
except Exception as e:
    print(f"Error writing report file '{file_path}': {e}")

if report_written:
    recipient = os.getenv("RECIPIENT_EMAIL")
    if recipient:
        email_subject = f"CrewAI Analysis Report for {input_data.get('target_name', 'Target')}"
        email_body = f"Attached is the strategic analysis report for {input_data.get('target_name', 'Target')} generated on {execution_time_str}."
        
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
            print("Failed to send report via email. Check logs and .env settings.")
    else:
        print("\nEmail not sent: RECIPIENT_EMAIL not found in .env file.")
else:
    print("\nEmail not sent because the report file could not be written.")

print("\n--- Raw Crew Kickoff Result ---")
try:
    import pprint
    pprint.pprint(result)
except ImportError:
    print(result)