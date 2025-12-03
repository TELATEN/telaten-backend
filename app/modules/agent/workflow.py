from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from app.core.llm import get_llm
from app.modules.agent.tools import (
    create_milestone_tool,
    list_milestones_tool,
    update_milestone_tool,
    delete_milestone_tool,
)


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
        tools=[],
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
        can_handoff_to=[],
    )

    # Wiring
    workflow = AgentWorkflow(
        agents=[strategy_agent, milestone_creator_agent],
        root_agent=strategy_agent.name,
        timeout=timeout,
    )

    return workflow


def get_chat_workflow(timeout: int = 120) -> AgentWorkflow:
    llm = get_llm()

    advisor_agent = FunctionAgent(
        name="AdvisorAgent",
        description="A proactive business advisor that manages milestones and answers questions.",
        system_prompt="""
        You are 'Telaten Advisor', a friendly and proactive business assistant for MSMEs.
        
        Your capabilities:
        1. **View Roadmap**: Use `list_milestones_tool` to see what the user is working on.
        2. **Update Progress**: If user says "I finished X", use `update_milestone_tool(id, status='completed')`.
        3. **Modify Roadmap**: If user wants to change direction, use `create` or `delete` tools.
        4. **Consultation**: Answer business questions based on the current roadmap context.
        
        Behavior Rules:
        - ALWAYS check the current milestones (`list_milestones_tool`) before giving specific advice on progress.
        - Be encouraging and use Indonesian (Bahasa Indonesia).
        - Keep answers concise.
        - If you modify any milestone, tell the user explicitly what you changed.
        """,
        llm=llm,
        tools=[
            list_milestones_tool,
            update_milestone_tool,
            create_milestone_tool,
            delete_milestone_tool,
        ],
        can_handoff_to=[],
    )

    workflow = AgentWorkflow(
        agents=[advisor_agent],
        root_agent=advisor_agent.name,
        timeout=timeout,
    )

    return workflow
