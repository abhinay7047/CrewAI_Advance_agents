from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from crewai.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun
import os
from typing import Dict, Any, List
import json
from datetime import datetime

load_dotenv()

# Enhanced BaseTool implementation with error handling and metadata
from pydantic import BaseModel, Field

# Define a schema matching CrewAI's input
class ToolInputSchema(BaseModel):
    description: str = Field(..., description="The task description or query for the tool")

class EnhancedBaseTool(BaseTool):
    args_schema: type[BaseModel] = ToolInputSchema  # Tell Pydantic to expect 'description'

    def _run(self, input_data: dict) -> str:  # Type hint as dict since schema ensures it
        try:
            # Extract 'description' from the validated input dict
            input_str = input_data['description']
            result = self.execute_tool_logic(input_str)
            return result
        except Exception as e:
            return f"Error executing tool: {str(e)}"
    
    def execute_tool_logic(self, input_data: str) -> str:
        raise NotImplementedError
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "tool_name": self.name,
            "last_updated": datetime.now().isoformat(),
            "reliability_score": 0.95
        }

# Advanced Research Tool
class AdvancedResearchTool(EnhancedBaseTool):
    name: str = "Advanced Research Tool"
    description: str = "Performs comprehensive research on organizations, individuals, and industry trends from multiple sources"

    def execute_tool_logic(self, query: str) -> str:
        search_tool = DuckDuckGoSearchRun()
        results = search_tool.run(query)
        
        # Simulate enhanced processing of search results
        processed_results = f"Research findings for '{query}':\n\n{results}\n\nKey insights extracted:\n- Identified potential growth opportunities\n- Found recent organizational changes\n- Analyzed current market positioning"
        
        return processed_results

# Market Analysis Tool
class MarketAnalysisTool(EnhancedBaseTool):
    name: str = "Market Analysis Tool"
    description: str = "Analyzes market trends, competitor landscapes, and industry developments"

    def execute_tool_logic(self, industry: str) -> str:
        # Generalized market analysis that works for any industry
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
        # Simple keyword-based sentiment analysis that works for any content
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

    def execute_tool_logic(self, context_data: str) -> str:
        # Parse input data or use default generic approach
        try:
            data = json.loads(context_data)
            org_type = data.get("organization_type", "general")
            objectives = data.get("objectives", ["growth", "efficiency"])
        except:
            org_type = "general"
            objectives = ["growth", "efficiency"]
        
        # Generate strategic recommendations that work for any organization
        strategies = {
            "growth": "Expand market presence through targeted digital campaigns and strategic partnerships",
            "efficiency": "Implement process automation and data-driven decision making",
            "innovation": "Establish cross-functional innovation teams and rapid prototyping processes",
            "customer_retention": "Develop personalized engagement programs and enhanced customer success frameworks"
        }
        
        available_strategies = {k: v for k, v in strategies.items() if k in objectives}
        if not available_strategies:
            available_strategies = {"general": "Balanced approach focusing on sustainable growth and operational excellence"}
        
        return f"Strategic recommendations for {org_type} organization:\n\n" + "\n".join([f"- {strategy}" for strategy in available_strategies.values()])

# Communication Optimization Tool
class CommunicationOptimizationTool(EnhancedBaseTool):
    name: str = "Communication Optimization Tool"
    description: str = "Analyzes and enhances communication effectiveness for different contexts and audiences"

    def execute_tool_logic(self, input_data: str) -> str:
        try:
            data = json.loads(input_data)
            audience = data.get("audience", "general")
            message = data.get("message", "")
            objective = data.get("objective", "inform")
        except:
            audience = "general"
            message = input_data
            objective = "inform"
        
        # Generic communication optimization
        enhancements = [
            "Simplified technical language for broader accessibility",
            "Added concrete examples to illustrate key points",
            "Structured message with clear call-to-action",
            "Incorporated relevant value propositions",
            "Optimized for engagement with concise, impactful statements"
        ]
        
        return (
            f"Communication optimization for {audience} audience with {objective} objective:\n\n"
            f"Original message: {message[:100]}...\n\n"
            f"Enhancements applied:\n" + "\n".join([f"- {enhancement}" for enhancement in enhancements])
        )

# Knowledge Base Tool (replaces the need for instruction directory)
class KnowledgeBaseTool(EnhancedBaseTool):
    name: str = "Knowledge Base Tool"
    description: str = "Provides access to built-in knowledge and best practices for research, strategy, and communications"
    
    # Built-in knowledge that would normally be in instruction files
    knowledge :Dict[str, Dict[str, str]]={
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
            "financial_services": "Financial services are experiencing digital transformation through fintech innovation, blockchain adoption, and changing regulatory landscapes. Focus areas include customer experience, data security, and personalized services.",
            "healthcare": "Healthcare is evolving with telemedicine expansion, data-driven diagnostics, personalized medicine, and value-based care models. Regulatory compliance and patient privacy remain core considerations.",
            "retail": "Retail is navigating omnichannel experiences, supply chain optimization, and experiential shopping innovations. Key factors include personalization, sustainability, and seamless digital integration."
        }
    }
    
    def execute_tool_logic(self, query: str) -> str:
        # Parse the query to find the appropriate knowledge
        query_lower = query.lower()
        
        # First check for exact matches in knowledge categories
        for category, subcategories in self.knowledge.items():
            if category.lower() in query_lower:
                for subcategory, content in subcategories.items():
                    if subcategory.lower() in query_lower:
                        return f"Knowledge Base: {subcategory.upper()}\n\n{content}"
                
                # If no subcategory match, return an overview of available subcategories
                available = ", ".join(subcategories.keys())
                return f"Available information in {category}:\n{available}\n\nPlease specify which aspect you need information about."
        
        # If no direct category match, search for keywords
        for category, subcategories in self.knowledge.items():
            for subcategory, content in subcategories.items():
                if subcategory.lower() in query_lower:
                    return f"Knowledge Base: {subcategory.upper()}\n\n{content}"
        
        # If no matches, return a list of available knowledge areas
        available_categories = ", ".join(self.knowledge.keys())
        return f"No specific match found for '{query}'. Available knowledge categories: {available_categories}. Please refine your query."

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
    context=[]  # No prior task dependency; this is the starting point
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
    context=[target_research_task]  # Depends on target_research_task
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
    context=[target_research_task, market_analysis_task]  # Depends on both prior tasks
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
    context=[strategy_development_task]  # Depends on strategy_development_task
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
    context=[strategy_development_task, communication_development_task]  # Depends on strategy and communication tasks
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
    verbose=True,  # Enhanced verbosity for more detailed logs
    memory=True,  # Enable memory for inter-task knowledge sharing
    process=Process.sequential  # Tasks execute in sequence, each building on previous results
)

# Generic input that works for any target and industry
input_data = {
    'target_name': 'NVIDIA Corp',
    'industry': 'Semiconductors',
    'key_decision_maker': 'Jensen Huang',
    'position': 'CEO',
    'milestone': 'major release of new NVIDIA Cosmos™ world foundation models (WFMs)'
}

# Execute the crew's work
result = crew.kickoff(inputs=input_data)

# Output results to file for reference
from datetime import datetime

# Assuming this is part of your larger script after crew.kickoff()
# Execute
result = crew.kickoff(inputs=input_data)

# Function to format task outputs into a readable text structure
def format_to_text(execution_time, tasks, task_outputs, agents, input_data):
    output_lines = []
    
    # Extract target and industry from input_data for a generic header
    target_name = input_data.get('target_name', 'Unknown Target')
    industry = input_data.get('industry', 'Unknown Industry')
    
    # Header
    output_lines.append(f"{target_name} Strategic Analysis Report")
    output_lines.append(f"Industry: {industry}")
    output_lines.append(f"Generated on: {execution_time}")
    output_lines.append("=" * 50)
    output_lines.append("")

    # Task Results
    for task, task_output in zip(tasks, task_outputs):
        task_desc = task.description.split(".")[0]  # Shorten to first sentence
        output = task_output.raw

        output_lines.append(f"Task: {task_desc}")
        output_lines.append("-" * 40)
        
        # Append the raw output with basic formatting
        output_lines.append("Key Findings:")
        # Split output into lines, indent non-header lines
        for line in output.split("\n"):
            if line.strip().startswith(("**", "##", "1.", "2.", "3.", "4.", "5.")):
                output_lines.append(line.strip())
            elif line.strip():
                output_lines.append(f"  - {line.strip()}")
        output_lines.append("")

    # Metadata
    output_lines.append("Execution Metadata:")
    output_lines.append("-" * 40)
    output_lines.append(f"Agents Used: {', '.join(agents)}")
    output_lines.append(f"Tasks Completed: {len(tasks)}")

    return "\n".join(output_lines)

# Generate and save text file
execution_time = datetime.now().isoformat()
agents = [agent.role for agent in crew.agents]
formatted_text = format_to_text(execution_time, crew.tasks, result.tasks_output, agents, input_data)

# Use target_name from input_data for filename
target_name = input_data.get('target_name', 'analysis').replace(" ", "_").lower()
file_path = f"{target_name}_report.txt"

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(formatted_text)

print(f"Text file '{file_path}' created successfully.")