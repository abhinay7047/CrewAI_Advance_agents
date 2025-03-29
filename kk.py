# --- Start of Updated Code ---

from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from crewai.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun
import os
from typing import Dict, Any, List
import json
from datetime import datetime

# Import necessary Pydantic components
from pydantic import BaseModel, Field

load_dotenv()

# Pydantic schema for tool input
class ToolInputSchema(BaseModel):
    input_data: str = Field(..., description="The input data, query, or context for the tool")

# Base tool class - Using args_schema and adjusted _run
class EnhancedBaseTool(BaseTool):
    args_schema: type[BaseModel] = ToolInputSchema  # Define the expected input structure

    # _run expects the *value* of the 'input_data' field after validation
    def _run(self, input_data: str) -> str:
        """
        Executes the tool's logic after input validation.
        Receives the validated string directly from the 'input_data' field.
        """
        try:
            # 'input_data' here is the string value passed after Pydantic validation
            result = self.execute_tool_logic(input_data)
            return result
        except Exception as e:
            tool_name = getattr(self, 'name', 'Unknown Tool')
            # Log the error with more context
            error_message = f"Error executing tool '{tool_name}'. Input (first 50 chars): '{input_data[:50]}...'. Error: {str(e)}"
            print(f"\n*** TOOL EXECUTION ERROR ***\n{error_message}\n**************************\n")
            # Return a meaningful error string for the agent
            return f"Tool Error: Failed to execute {tool_name}. Details: {str(e)}"

    # This method must be implemented by subclasses
    def execute_tool_logic(self, input_data: str) -> str:
        """The core logic of the tool, implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement execute_tool_logic")

    # Metadata method (optional but good practice)
    def get_metadata(self) -> Dict[str, Any]:
        tool_name = getattr(self, 'name', 'Base Tool')
        return {
            "tool_name": tool_name,
            "last_updated": datetime.now().isoformat(),
            "reliability_score": 0.95 # Example score
        }

# --- Tool Implementations ---
# (These inherit from the updated EnhancedBaseTool but their logic remains the same,
# as execute_tool_logic always expected a string)

class AdvancedResearchTool(EnhancedBaseTool):
    name: str = "Advanced Research Tool"
    description: str = "Performs comprehensive research on organizations, individuals, and industry trends using multiple online sources."

    def execute_tool_logic(self, query: str) -> str:
        """Executes a DuckDuckGo search based on the input query."""
        print(f"\n[{self.name}] Received query: {query}")
        search_tool = DuckDuckGoSearchRun()
        try:
            results = search_tool.run(query)
            if not results or "error" in results.lower():
                return f"Could not retrieve reliable search results for '{query}'."
            # Basic formatting/summarization placeholder
            processed_results = (
                f"Research Findings for '{query}':\n\n"
                f"{results}\n\n"
                f"--- End of Search Results ---\n"
                f"Key insights might include: recent news, financial performance indicators, "
                f"strategic announcements, and key personnel changes (extracted from above)."
            )
            print(f"[{self.name}] Completed research for: {query}")
            return processed_results
        except Exception as e:
            error_msg = f"Error during DuckDuckGo search execution for '{query}': {str(e)}"
            print(f"[{self.name}] {error_msg}")
            return error_msg

class MarketAnalysisTool(EnhancedBaseTool):
    name: str = "Market Analysis Tool"
    description: str = "Analyzes market trends, competitor landscapes, and industry developments for a given industry sector."

    def execute_tool_logic(self, industry: str) -> str:
        """Provides a mock market analysis for the specified industry."""
        print(f"\n[{self.name}] Analyzing industry: {industry}")
        # Simulating analysis based on industry name
        analysis = (
            f"Market Analysis for '{industry}' industry:\n\n"
            f"1. Growth & Transformation: The '{industry}' sector shows signs of [significant transformation/stable growth/emerging disruption].\n"
            f"2. Key Trends: Dominant trends include [AI adoption/sustainability focus/digital customer engagement/supply chain optimization].\n"
            f"3. Competitive Dynamics: Landscape features [established leaders facing new challengers/high fragmentation/consolidation activity].\n"
            f"4. Consumer/Client Behavior: Trends indicate shifts towards [digital channels/personalized experiences/value-consciousness/sustainability demands].\n"
            f"5. Regulatory Factors: Note increasing focus on [data privacy/environmental regulations/compliance standards] impacting operations.\n\n"
            f"(Note: This is a generalized analysis. Deeper research required for specifics)."
        )
        print(f"[{self.name}] Completed analysis for: {industry}")
        return analysis

class SentimentAnalysisTool(EnhancedBaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = "Analyzes sentiment (positive, negative, neutral) expressed in text, such as communications or public feedback."

    def execute_tool_logic(self, text: str) -> str:
        """Performs a basic keyword-based sentiment analysis."""
        print(f"\n[{self.name}] Analyzing sentiment for text (first 100 chars): {text[:100]}...")
        positive_words = ["growth", "innovation", "success", "strong", "increase", "profit", "opportunity", "positive", "good", "excellent"]
        negative_words = ["decline", "struggle", "loss", "failure", "problem", "decrease", "challenge", "risk", "weak", "poor", "negative"]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        score = positive_count - negative_count
        sentiment = "Neutral"
        comment = "Recommend balanced approach focusing on factual information and value proposition."

        if score > 1:
            sentiment = "Positive"
            comment = f"Positive sentiment detected (Score: {score}). Key indicators suggest opportunities or strengths."
        elif score < 0:
            sentiment = "Negative"
            comment = f"Negative sentiment detected (Score: {score}). Potential concerns or challenges may need addressing."

        result = f"Sentiment Analysis Result: {sentiment}. {comment}"
        print(f"[{self.name}] Sentiment result: {sentiment} (Score: {score})")
        return result


class StrategicPlanningTool(EnhancedBaseTool):
    name: str = "Strategic Planning Tool"
    description: str = "Develops strategic recommendations based on input context like market research, organizational type, and objectives."

    def execute_tool_logic(self, context_data: str) -> str:
        """Generates strategic recommendations based on JSON input string."""
        print(f"\n[{self.name}] Developing strategy based on context: {context_data[:150]}...")
        try:
            data = json.loads(context_data)
            org_type = data.get("organization_type", "general")
            objectives = data.get("objectives", ["growth", "efficiency"])
            # Example: Add context use
            target_info = data.get("target_info", "the organization")
            market_context = data.get("market_context", "current market conditions")
        except json.JSONDecodeError:
            print(f"[{self.name}] Warning: Input was not valid JSON. Using default values.")
            org_type = "general"
            objectives = ["growth", "efficiency"]
            target_info = "the organization"
            market_context = "current market conditions"
        except Exception as e:
             print(f"[{self.name}] Error processing input: {e}. Using default values.")
             org_type = "general"
             objectives = ["growth", "efficiency"]
             target_info = "the organization"
             market_context = "current market conditions"


        strategies = {
            "growth": f"Expand market presence for {target_info} through targeted digital campaigns and strategic partnerships, considering {market_context}.",
            "efficiency": f"Implement process automation and data-driven decision-making within {target_info} to improve operational effectiveness.",
            "innovation": f"Establish cross-functional innovation teams and rapid prototyping processes focusing on future market needs relevant to {target_info}.",
            "customer_retention": f"Develop personalized engagement programs and enhance customer success frameworks tailored to {target_info}'s client base.",
            "risk_assessment": f"Conduct a thorough risk assessment focusing on market volatility, competitive threats, and operational vulnerabilities for {target_info}.",
            "improvement": f"Identify key areas for operational or strategic improvement based on performance data and feedback loops within {target_info}.",
            "contingency_planning": f"Develop contingency plans for key identified risks, outlining mitigation steps and alternative actions for {target_info}."
            # Add more specific objectives if needed
        }

        # Filter strategies based on provided objectives
        recommended_strategies = [strategies[obj] for obj in objectives if obj in strategies]

        if not recommended_strategies:
            recommended_strategies = [f"Develop a balanced strategy for {target_info} focusing on sustainable growth and operational excellence."]

        result = (
            f"Strategic Recommendations for {org_type} organization ({target_info}), considering {market_context}:\n\n" +
            "\n".join([f"- {strategy}" for strategy in recommended_strategies])
        )
        print(f"[{self.name}] Strategy generated for objectives: {objectives}")
        return result

class CommunicationOptimizationTool(EnhancedBaseTool):
    name: str = "Communication Optimization Tool"
    description: str = "Analyzes and refines communication content for specific audiences and objectives, provided as a JSON string."

    def execute_tool_logic(self, input_data: str) -> str:
        """Optimizes communication based on audience, message, and objective from JSON input."""
        print(f"\n[{self.name}] Optimizing communication based on input: {input_data[:150]}...")
        try:
            data = json.loads(input_data)
            audience = data.get("audience", "general audience")
            message_summary = data.get("message", "the core message") # Use provided message summary
            objective = data.get("objective", "inform")
        except json.JSONDecodeError:
            print(f"[{self.name}] Warning: Input was not valid JSON. Using default values.")
            audience = "general audience"
            message_summary = input_data # Treat input as message if not JSON
            objective = "inform"
        except Exception as e:
             print(f"[{self.name}] Error processing input: {e}. Using default values.")
             audience = "general audience"
             message_summary = input_data
             objective = "inform"


        # Placeholder enhancements - could be made more dynamic
        enhancements = [
            f"Tailor technical language for {audience}.",
            f"Include specific examples relevant to {audience}'s context.",
            f"Ensure a clear call-to-action aligned with the objective: '{objective}'.",
            f"Highlight value propositions most pertinent to {audience}.",
            f"Structure for clarity and impact, potentially using bullet points or summaries.",
            f"Refine tone to be appropriate for {audience} (e.g., formal, informal, technical)."
        ]

        result = (
            f"Communication Optimization Suggestions for '{audience}' (Objective: {objective}):\n\n"
            f"Based on core message: '{message_summary[:150]}...'\n\n"
            f"Recommended Enhancements:\n" +
            "\n".join([f"- {enhancement}" for enhancement in enhancements])
        )
        print(f"[{self.name}] Generated communication suggestions for: {audience}")
        return result

class KnowledgeBaseTool(EnhancedBaseTool):
    name: str = "Knowledge Base Tool"
    description: str = "Provides access to internal knowledge on frameworks, models, guidelines, and industry insights based on a query string."

    # Knowledge dictionary remains the same...
    knowledge: Dict[str, Dict[str, str]] = {
        "research_frameworks": {
            "competitive_analysis": (
                "Framework for competitive analysis:\n"
                "1. Identify key competitors in the market\n"
                "2. Analyze their product/service offerings\n"
                "3. Evaluate pricing strategies\n"
                "4. Assess market positioning and messaging\n"
                "5. Review strengths and weaknesses\n"
                "6. Identify opportunities for differentiation"
            ),
            "stakeholder_mapping": (
                "Framework for stakeholder mapping:\n"
                "1. Identify all relevant stakeholders\n"
                "2. Categorize by influence and interest levels\n"
                "3. Determine decision-making authority\n"
                "4. Map reporting relationships\n"
                "5. Identify potential champions and blockers\n"
                "6. Develop engagement strategies for each stakeholder type"
            )
        },
        "strategic_models": {
            "swot_analysis": (
                "SWOT Analysis Framework:\n"
                "- Strengths: Internal capabilities and resources that provide advantages\n"
                "- Weaknesses: Internal limitations that may hinder progress\n"
                "- Opportunities: External factors that could be leveraged for benefit\n"
                "- Threats: External factors that could negatively impact performance"
            ),
            "value_proposition": (
                "Value Proposition Framework:\n"
                "1. Identify the customer segment\n"
                "2. Define the key problems/needs to be addressed\n"
                "3. Outline the benefits of your solution\n"
                "4. Explain why your solution is uniquely capable\n"
                "5. Provide evidence to support claims\n"
                "6. Frame in terms of customer outcomes"
            )
        },
        "communication_guidelines": {
            "stakeholder_messaging": (
                "Guidelines for stakeholder messaging:\n"
                "1. C-Level: Focus on strategic impact, ROI, and competitive advantage\n"
                "2. Directors: Emphasize operational efficiency and departmental benefits\n"
                "3. Managers: Highlight implementation processes and team advantages\n"
                "4. End Users: Showcase ease of use and individual productivity gains\n"
                "5. Financial stakeholders: Stress cost savings and revenue potential"
            ),
            "objection_handling": (
                "Framework for handling objections:\n"
                "1. Listen fully to understand the true concern\n"
                "2. Validate the concern as legitimate\n"
                "3. Ask questions to clarify the specific issue\n"
                "4. Provide relevant information to address the concern\n"
                "5. Confirm that the response satisfies the concern\n"
                "6. Move the conversation forward constructively"
            )
        },
        "industry_insights": {
            "technology": "The technology sector is characterized by rapid innovation, frequent disruption, and short product lifecycles. Key trends include AI integration, cloud computing, edge computing, cybersecurity enhancement, and sustainability initiatives.",
            "fast-moving consumer goods": "The FMCG sector focuses on brand building, supply chain efficiency, consumer trends (health, sustainability), and retail partnerships. Digital marketing and e-commerce are crucial growth drivers.", # Added FMCG
            "financial_services": "Financial services are experiencing digital transformation through fintech innovation, blockchain adoption, and changing regulatory landscapes. Focus areas include customer experience, data security, and personalized services.",
            "healthcare": "Healthcare is evolving with telemedicine expansion, data-driven diagnostics, personalized medicine, and value-based care models. Regulatory compliance and patient privacy remain core considerations.",
            "retail": "Retail is navigating omnichannel experiences, supply chain optimization, and experiential shopping innovations. Key factors include personalization, sustainability, and seamless digital integration."
        }
    }

    def execute_tool_logic(self, query: str) -> str:
        """Searches the internal knowledge base for relevant information."""
        print(f"\n[{self.name}] Received query: {query}")
        query_lower = query.lower().strip()

        # Direct match check first (more specific)
        for category, subcategories in self.knowledge.items():
            for subcategory_key, content in subcategories.items():
                 # Match variations like "swot analysis", "swot", "analysis swot"
                if subcategory_key.replace("_", " ") in query_lower:
                    print(f"[{self.name}] Found direct match: {category}/{subcategory_key}")
                    return f"Knowledge Base Result ({subcategory_key.replace('_', ' ').title()}):\n\n{content}"

        # Broader category check
        matched_category = None
        for category in self.knowledge.keys():
            if category.replace("_", " ") in query_lower:
                matched_category = category
                break

        if matched_category:
            available_subcategories = ", ".join([k.replace("_", " ") for k in self.knowledge[matched_category].keys()])
            print(f"[{self.name}] Found category match: {matched_category}. Suggesting subcategories.")
            return (f"Found knowledge related to '{matched_category.replace('_', ' ')}'. "
                    f"Specific topics available: {available_subcategories}. "
                    f"Please refine your query with one of these topics (e.g., 'competitive analysis framework', 'SWOT analysis model').")

        # Check industry insights separately
        if "industry insight" in query_lower or "industry trend" in query_lower:
             for industry_key, insight in self.knowledge["industry_insights"].items():
                  if industry_key.replace("_", " ") in query_lower:
                       print(f"[{self.name}] Found industry insight: {industry_key}")
                       return f"Industry Insights ({industry_key.replace('_', ' ').title()}):\n\n{insight}"

        # If no match
        available_categories = ", ".join([k.replace("_", " ") for k in self.knowledge.keys()])
        print(f"[{self.name}] No specific match found.")
        return (f"No specific match found in the Knowledge Base for '{query}'. "
                f"Available top-level categories: {available_categories}. "
                f"Try asking about a specific framework (e.g., 'SWOT analysis'), guideline ('stakeholder messaging'), or industry ('technology industry trends').")


# --- Agent Definitions ---
# (No changes needed here)
research_coordinator_agent = Agent(...)
market_analyst_agent = Agent(...)
strategy_specialist_agent = Agent(...)
communication_expert_agent = Agent(...)


# --- Task Definitions ---
# **CRITICAL CHANGE**: Wrap the output of input_fn in {"input_data": ...}

target_research_task = Task(
    description=(
        "Conduct comprehensive research on {target_name} in the {industry} sector. "
        "Analyze their current market position, recent developments (including milestones like '{milestone}'), "
        "key decision-makers (like {key_decision_maker}, {position}), organizational structure, and strategic initiatives. "
        "Identify potential needs, challenges, and opportunities relevant to our offerings. Use the Advanced Research Tool primarily. "
        "Consult the Knowledge Base for relevant research frameworks (like competitive analysis or stakeholder mapping) and industry insights if needed."
    ),
    expected_output=(
        "A detailed intelligence report on {target_name} including:\n"
        "1. Organization Overview: Size, structure, main business lines.\n"
        "2. Market Position: Market share (if available), key competitors, perceived strengths/weaknesses.\n"
        "3. Key Stakeholders: Identify key decision-makers beyond the CEO if possible, reporting structure insights.\n"
        "4. Recent Developments & Strategy: Summarize recent news, announcements, strategic shifts (mention '{milestone}').\n"
        "5. Needs & Challenges: Infer potential pain points based on research (e.g., digital transformation needs, competitive pressure).\n"
        "6. Opportunities: Suggest potential areas where our offerings could provide value.\n"
        "7. Recommended Next Steps: Initial thoughts on engagement approach vectors."
    ),
    tools=[AdvancedResearchTool(), KnowledgeBaseTool()], # Focus tools
    agent=research_coordinator_agent,
    context=[],
    # **MODIFIED input_fn**
    input_fn=lambda context: {
        "input_data": (
            f"Comprehensive research request for: {context['target_name']} ({context['industry']} sector). "
            f"Key contact: {context['key_decision_maker']} ({context['position']}). "
            f"Notable milestone: {context['milestone']}. "
            f"Focus on: market position, recent developments, decision-making structure, strategy, needs, challenges, opportunities."
        )
    }
)

market_analysis_task = Task(
    description=(
        "Analyze the {industry} market landscape, considering the context of {target_name} (from previous research). "
        "Identify key market trends (e.g., technology, consumer behavior), competitive dynamics, and potential market gaps or opportunities. "
        "Use the Market Analysis Tool and supplement with Advanced Research Tool for recent news or specific competitor data if needed. "
        "Check Knowledge Base for general industry insights."
    ),
    expected_output=(
        "A concise market analysis report for the {industry} industry, relevant to {target_name}, including:\n"
        "1. Industry Trends: Top 3-5 trends impacting the sector.\n"
        "2. Competitive Landscape: Major players, competitive intensity, and {target_name}'s relative position.\n"
        "3. Market Opportunities: Potential gaps or emerging areas where solutions could be valuable.\n"
        "4. Strategic Considerations: How market dynamics might influence engagement with {target_name}."
    ),
    tools=[MarketAnalysisTool(), AdvancedResearchTool(), KnowledgeBaseTool()],
    agent=market_analyst_agent,
    context=[target_research_task],
    # **MODIFIED input_fn**
    input_fn=lambda context: {
        # Pass the industry name to the MarketAnalysisTool primarily
        "input_data": context.get('industry', 'general industry')
    }
)

strategy_development_task = Task(
    description=(
        "Develop a strategic engagement plan for {target_name}, using insights from the target research and market analysis tasks. "
        "Define a tailored value proposition, outline an engagement approach, and consider potential objections. "
        "Use the Strategic Planning Tool, providing context about the organization type ({industry}) and desired objectives (e.g., growth, efficiency). "
        "Consult the Knowledge Base for strategic models (like value proposition framework) or objection handling frameworks."
    ),
    expected_output=(
        "A strategic engagement plan document for {target_name} including:\n"
        "1. Tailored Value Proposition: How our offerings specifically address {target_name}'s likely needs/challenges.\n"
        "2. Engagement Approach: Recommended sequence of interactions or key themes.\n"
        "3. Positioning: How to position our solution against potential alternatives or competitors.\n"
        "4. Objection Handling: Anticipated objections and potential responses (using KB framework).\n"
        "5. Key Success Metrics (Initial): How to measure successful engagement."
    ),
    tools=[StrategicPlanningTool(), KnowledgeBaseTool()],
    agent=strategy_specialist_agent,
    context=[target_research_task, market_analysis_task],
    # **MODIFIED input_fn**
    input_fn=lambda context: {
        # Pass JSON string containing context to StrategicPlanningTool
        "input_data": json.dumps({
            "organization_type": context.get('industry', 'general'), # Use industry as proxy for type
            "objectives": ["growth", "efficiency", "innovation"], # Define desired strategic outcomes
            "target_info": f"{context.get('target_name', 'Target Organization')}",
            "market_context": f"Operating in the {context.get('industry', 'relevant')} market, considering recent trends and competitive landscape."
            # Could potentially add summarized findings from previous tasks here if memory isn't sufficient
        })
    }
)

communication_development_task = Task(
    description=(
        "Based on the strategic engagement plan, develop specific communication points and potentially draft initial outreach message frameworks for engaging with key stakeholders at {target_name}, such as {key_decision_maker}. "
        "Use the Communication Optimization Tool, providing context on the audience and objective. "
        "Analyze the sentiment of potential messaging using the Sentiment Analysis Tool. "
        "Consult the Knowledge Base for stakeholder messaging guidelines."
    ),
    expected_output=(
        "A communication guidance document including:\n"
        "1. Key Talking Points: Core messages aligned with the value proposition for stakeholders like {key_decision_maker}.\n"
        "2. Messaging Frameworks: Templates or outlines for initial outreach (e.g., email, LinkedIn message).\n"
        "3. Tone and Style Recommendations: Guidance on appropriate communication style.\n"
        "4. Sentiment Check Summary: Analysis of the proposed messaging tone."
    ),
    tools=[CommunicationOptimizationTool(), SentimentAnalysisTool(), KnowledgeBaseTool()],
    agent=communication_expert_agent,
    context=[strategy_development_task],
    # **MODIFIED input_fn**
    input_fn=lambda context: {
        # Pass JSON string containing context to CommunicationOptimizationTool
        "input_data": json.dumps({
            "audience": f"{context.get('key_decision_maker', 'Key Stakeholder')} at {context.get('target_name', 'Target')}",
            "message": f"Initial strategic engagement outreach based on developed plan, focusing on value proposition related to growth/efficiency/innovation in the {context.get('industry', 'industry')} sector.", # Summarize message intent
            "objective": "Initiate engagement / Schedule exploratory call" # Define clear objective
        })
    }
)

reflection_task = Task(
    description=(
        "Critically review the developed strategy and communication approach for {target_name}. "
        "Identify potential weaknesses, risks, or overlooked considerations. Challenge assumptions made. "
        "Use the Strategic Planning Tool with objectives like 'risk_assessment' and 'improvement'. "
        "Consult Knowledge Base for frameworks like SWOT analysis if relevant to identify internal/external factors."
    ),
    expected_output=(
        "A concise reflection memo including:\n"
        "1. Identified Weaknesses/Risks: Potential gaps or challenges in the current plan.\n"
        "2. Challenged Assumptions: Key assumptions that might need validation.\n"
        "3. Alternative Considerations: Suggestions for alternative tactics or contingency plans.\n"
        "4. Recommended Adjustments: Specific, actionable recommendations to strengthen the plan."
    ),
    tools=[StrategicPlanningTool(), KnowledgeBaseTool()], # Strategic Planning tool can be used for reflection too
    agent=strategy_specialist_agent, # Strategy specialist performs reflection
    context=[strategy_development_task, communication_development_task],
    # **MODIFIED input_fn**
    input_fn=lambda context: {
        # Pass JSON string for context to StrategicPlanningTool
        "input_data": json.dumps({
            "organization_type": context.get('industry', 'general'),
            "objectives": ["risk_assessment", "improvement", "contingency_planning"], # Objectives guiding reflection
            "target_info": f"The strategy for {context.get('target_name', 'Target')}",
            "market_context": f"Reviewing the plan within the {context.get('industry', 'relevant')} market context and potential competitor reactions."
        })
    }
)

# --- Crew Definition ---
crew = Crew(
    agents=[
        research_coordinator_agent,
        market_analyst_agent,
        strategy_specialist_agent,
        communication_expert_agent # Strategy Specialist handles reflection
    ],
    tasks=[
        target_research_task,
        market_analysis_task,
        strategy_development_task,
        communication_development_task,
        reflection_task
    ],
    verbose=2, # Use verbose=2 for detailed logs including agent thoughts and tool calls
    memory=True,
    process=Process.sequential
)

# --- Input Data ---
input_data = {
    'target_name': 'Hindustan Unilever Limited',
    'industry': 'Fast-moving consumer goods',
    'key_decision_maker': 'Rohit Jawa',
    'position': 'CEO',
    'milestone': 'HUL exceeded INR 50,000 Crore in revenue'
}

# --- Execution ---
print("🚀 Kicking off the Crew...")
result = crew.kickoff(inputs=input_data)
print("\n✅ Crew execution finished.")

# --- Output Formatting and Saving ---
# (Using the robust format_to_text function from previous answers)
def format_to_text(execution_time, tasks, task_outputs, agents, input_data):
    output_lines = []
    target_name = input_data.get('target_name', 'Unknown Target')
    industry = input_data.get('industry', 'Unknown Industry')

    output_lines.append(f"{target_name} Strategic Analysis Report")
    output_lines.append(f"Industry: {industry}")
    output_lines.append(f"Generated on: {execution_time}")
    output_lines.append("=" * 50)
    output_lines.append("")

    if not task_outputs:
         output_lines.append("No task outputs generated. The crew execution might have failed or produced no results.")
         print("\n⚠️ WARNING: No task outputs found in the result object.")
    else:
        print(f"\n📝 Formatting {len(task_outputs)} task outputs for report...")
        for i, task_output in enumerate(task_outputs):
            # Ensure index is within bounds of tasks list
            task_desc = f"Unknown Task {i+1}"
            if i < len(tasks) and hasattr(tasks[i], 'description'):
                 task_desc = tasks[i].description.split(".")[0] # Shorten to first sentence
            else:
                 print(f"Warning: Could not retrieve description for task index {i}")


            output_lines.append(f"## Task: {task_desc}") # Using Markdown style header
            output_lines.append("-" * 40)

            output_content = None
            if task_output is not None:
                # Prioritize 'raw', then 'result', then check if it's a string directly
                if hasattr(task_output, 'raw') and task_output.raw:
                    output_content = task_output.raw
                    print(f"   - Task {i+1}: Using raw output.")
                elif hasattr(task_output, 'result') and task_output.result:
                     output_content = task_output.result
                     print(f"   - Task {i+1}: Using result output.")
                elif isinstance(task_output, str):
                     output_content = task_output
                     print(f"   - Task {i+1}: Output is a direct string.")
                elif hasattr(task_output, 'exported_output') and task_output.exported_output: # Less common
                     output_content = task_output.exported_output
                     print(f"   - Task {i+1}: Using exported_output.")
                else:
                    # If it's some other object, try converting to string
                    try:
                        output_content = str(task_output)
                        print(f"   - Task {i+1}: Output is an object, converting to string.")
                    except Exception:
                        print(f"   - Task {i+1}: Output object could not be converted to string.")


            if output_content:
                # Basic cleaning and formatting
                lines = str(output_content).strip().split('\n')
                output_lines.append("### Output:")
                for line in lines:
                    line_strip = line.strip()
                    if line_strip:
                        # Add simple list formatting if starts with common markers
                        if line_strip.startswith(("- ", "* ", "1. ", "2. ", "3. ", "4. ", "5. ")):
                            output_lines.append(line_strip)
                        elif line_strip.endswith(":") and len(line_strip) < 50: # Treat short lines ending in ':' as headers
                            output_lines.append(f"\n**{line_strip}**")
                        else:
                            output_lines.append(f"  {line_strip}") # Indent regular lines
            else:
                output_lines.append("  *No valid output content found for this task.*")
                # print(f"Debug: Task {i} raw output object type: {type(task_output)}, value: {task_output}") # Debugging line

            output_lines.append("\n" + "-"*40 + "\n") # Add spacing between tasks

    output_lines.append("## Execution Metadata")
    output_lines.append("-" * 40)
    agent_roles = [agent.role for agent in agents if hasattr(agent, 'role')]
    output_lines.append(f"- **Agents Used:** {', '.join(agent_roles)}")
    output_lines.append(f"- **Tasks Defined:** {len(tasks)}")
    output_lines.append(f"- **Tasks with Output Objects:** {len(task_outputs) if task_outputs else 0}")

    return "\n".join(output_lines)

# Generate and save text file
execution_time = datetime.now().isoformat()
print("\n💾 Generating report file...")

# Ensure result.tasks_output exists, otherwise pass empty list
tasks_output_list = result.tasks_output if result and hasattr(result, 'tasks_output') else []

formatted_text = format_to_text(execution_time, crew.tasks, tasks_output_list, crew.agents, input_data)

target_name_file = input_data.get('target_name', 'analysis').replace(" ", "_").lower()
file_path = f"{target_name_file}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt" # Add timestamp

try:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(formatted_text)
    print(f"\n📄 Text report saved successfully to '{file_path}'.")
except Exception as e:
    print(f"\n❌ Error writing report file: {e}")

# Optional: Print final raw result for debugging
# print("\n--- Final Crew Result Object ---")
# print(result)

# --- End of Updated Code ---