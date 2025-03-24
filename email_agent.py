from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from crewai_tools import DirectoryReadTool, FileReadTool
from crewai.tools import BaseTool  # Correct import from crewai.tools
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()

# Define Agents
sale_rep_agent = Agent(
    role="Sales Representative",
    goal='identify high-value leads that match our ideal customer profile and convert them into customers',
    backstory="As a part of dynamic sales team at CrewAI your mission is to scour the digital landscape for high-value leads that match our ideal customer profile armed with cutting-edge tools and techniques and a strategic mindset, you will convert these leads into customers",
    allow_delegation=False,
    verbose=True
)

lead_sep_agent = Agent(
    role="Lead Sales Representative",
    goal='Nurture leads with personalized, compelling communication and convert them into customers',
    backstory="As a part of dynamic sales team at CrewAI you stand out as the bridge between the potential customer and the solution they need by creating engaging and personalized communication, you will nurture leads you not only inform leads but feel them seen, valued and understood your role is pivotal in converting leads into customers",
    allow_delegation=False,
    verbose=True    
)

# Define Tools
direc_read_tool = DirectoryReadTool(directory='./instructions')
file_read_tool = FileReadTool()

# Custom DuckDuckGo Search Tool using crewai.tools.BaseTool
class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Search Tool"
    description: str = "A tool to search the web using DuckDuckGo without an API key."

    def _run(self, query: str) -> str:
        """Search the web synchronously using DuckDuckGo."""
        search_tool = DuckDuckGoSearchRun()
        return search_tool.run(query)

duckduckgo_search_tool = DuckDuckGoSearchTool()

# Custom Sentiment Analysis Tool using crewai.tools.BaseTool
class SentimentAnalysisTool(BaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = "Analyze the sentiment of the text."

    def _run(self, text: str) -> str:
        """Return a simple positive sentiment for the text."""
        return 'positive'

sentiment_tool = SentimentAnalysisTool()

# Define Tasks
lead_profiling_task = Task(
    description=(
        'Conduct in depth analysis of {lead_name},'
        'a company in the {industry} sector'
        "that recently shown interest in our solutions"
        "Utilise all the available data sources to compile detailed profile "
        "focusing on key decision makers return recent businesses development and potential needs"
        " that align with our offerings this task is crucial for tailoring our engagement strategy effectively"
        " don't make assumption and only use information you absolutely sure about"
    ),
    expected_output=(
        'A comprehensive report on {lead_name} including company background '
        'key personnel, recent milestone and identify needs highlight potential areas '
        'where our solutions can provide value '
        'and suggest personalized engagement strategies'
    ),
    tools=[direc_read_tool, file_read_tool, duckduckgo_search_tool],
    agent=sale_rep_agent,
)

personalized_outreach_task = Task(
    description=(
        "Using the insights gathered from the lead profile in report on {lead_name}"
        " craft a personalized outreach campaign aimed at {key_decision_maker}"
        "the {position} of {lead_name} the campaign should address "
        "the recent {milestone} and how our solution can support their goal "
        "your communication must resonate with {lead_name} company culture "
        "and values demonstrating a deep understanding of the business and needs.\n"
        " don't make assumption and only use information you absolutely sure about "
    ),
    expected_output=(
        'A series of personalized email drafts '
        'tailored to {lead_name} specifically targeting {key_decision_maker} '
        'each draft should include compelling narrative that connect our solution '
        'with the recent achievements and future goals '
        'Ensure the tone is engaging professional and '
        'aligned with the {lead_name} corporate identity'
    ),
    tools=[sentiment_tool, duckduckgo_search_tool],
    agent=lead_sep_agent,
)

# Define Crew
crew = Crew(
    agents=[sale_rep_agent, lead_sep_agent],
    tasks=[lead_profiling_task, personalized_outreach_task],
    verbose=True,
    memory=True
)

# Input
input={
    'lead_name':'Angelone',
    'industry':'stock-broking and wealth management',
    'key_decision_maker':'Ambarish Kenghe',
    'position':'CEO',
    'milestone':'Surpassing 30 million clients'
}

# Kickoff
result = crew.kickoff(inputs=input)