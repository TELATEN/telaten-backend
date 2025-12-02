from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from app.core.llm import get_llm
from app.modules.agent.tools import create_milestone_tool


def get_onboarding_workflow(timeout: int = 120) -> AgentWorkflow:
    llm = get_llm()

    # 1. Strategy Agent: Analyzes the business and plans the roadmap structure
    strategy_agent = FunctionAgent(
        name="StrategyAgent",
        description="Analyzes business profile and plans the strategic roadmap.",
        system_prompt="""
        You are a Senior Business Strategist for MSMEs (UMKM) in Indonesia.
        Your job is to analyze the business profile provided by the user.
        
        Identify:
        1. Key challenges for this specific business stage.
        2. Strategic goals (Short term & Long term).
        3. A concrete 5-7 step plan.
        
        When you have a solid plan, hand off to the MilestoneCreatorAgent to execute the creation.
        Pass your detailed plan to them.
        """,
        llm=llm,
        tools=[],  # Purely analytical, no external tools needed yet
        can_handoff_to=["MilestoneCreatorAgent"],
    )

    # 2. Milestone Creator Agent: Executes the plan by saving to DB
    milestone_creator_agent = FunctionAgent(
        name="MilestoneCreatorAgent",
        description="Creates milestones in the system based on the strategy.",
        system_prompt="""
        You are the Execution Manager.
        Your job is to take the plan from StrategyAgent and create the actual milestones in the system.
        
        Use the `create_milestone_tool` for EACH step in the plan.
        Ensure the descriptions are in Bahasa Indonesia, actionable, and encouraging.
        
        IMPORTANT: You MUST call `create_milestone_tool` for every single milestone proposed.
        Do not just list them in text.
        """,
        llm=llm,
        tools=[create_milestone_tool],
        can_handoff_to=[],  # End of line for this simple workflow
    )

    # Wiring
    workflow = AgentWorkflow(
        agents=[strategy_agent, milestone_creator_agent],
        root_agent=strategy_agent.name,
        timeout=timeout,
    )

    return workflow
