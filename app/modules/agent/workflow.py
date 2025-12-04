from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from app.core.llm import get_llm
from app.modules.agent.tools import (
    create_milestone_tool,
    list_milestones_tool,
    update_milestone_tool,
    delete_milestone_tool,
    complete_task_tool,
    start_milestone_tool,
    get_business_summary_tool,
    record_transaction_tool,
    get_financial_report_tool,
)


def get_onboarding_workflow(timeout: int = 120) -> AgentWorkflow:
    llm = get_llm()

    # Combined Onboarding Agent: Analyzes and Executes the Plan
    onboarding_agent = FunctionAgent(
        name="OnboardingAgent",
        description="Analyzes business profile and creates the initial roadmap.",
        system_prompt="""
        You are a Senior Business Strategist for MSMEs (UMKM) in Indonesia.
        Your goal is to analyze the user's business profile and IMMEDIATELY set up their initial roadmap.
        
        **Your Task:**
        1. Analyze the business stage, challenges, and goals.
        2. Formulate a **Short-Term Action Plan** consisting of exactly **4 Critical Milestones** (Equilibrium Strategy).
           - Do NOT create a long 10-step plan. Focus on the first few weeks.
        3. **EXECUTE** the plan immediately by calling `create_milestone_tool` for EACH milestone.
        
        **Milestone Requirements:**
        - **Title**: Clear and concise (Bahasa Indonesia).
        - **Description**: Actionable, encouraging, and includes a rough duration target (e.g., "Target: 3 hari").
        - **Tasks**: Break down each milestone into 3-5 smaller, concrete tasks (e.g., "Buat akun", "Upload foto").
        
        **Response:**
        After calling the tools, reply to the user with a friendly, encouraging welcome message summarizing the 4 milestones you just created.
        """,
        llm=llm,
        tools=[create_milestone_tool],
        can_handoff_to=[],
    )

    # Wiring
    workflow = AgentWorkflow(
        agents=[onboarding_agent],
        root_agent=onboarding_agent.name,
        timeout=timeout,
    )

    return workflow


def get_chat_workflow(timeout: int = 120) -> AgentWorkflow:
    llm = get_llm()

    advisor_agent = FunctionAgent(
        name="AdvisorAgent",
        description="A proactive business advisor that manages milestones, finance, and answers questions.",
        system_prompt="""
        You are 'Telaten Advisor', a friendly, proactive, and holistic business assistant for MSMEs in Indonesia.
        You have FULL ACCESS to the user's business data: milestones, financials, points, and achievements.
        
        Your Role: **The GPS Navigator & Manager**
        You don't just follow the plan; you constantly Recalculate the Route based on user conditions.
        
        **Core Logic (The GPS Strategy):**
        1. **Maintain 4 Active Milestones**: Ideally, the user should always have visibility of 4 steps ahead.
        
        2. **RE-ROUTE (Handling Obstacles)**: 
           - If the user reports a MAJOR OBSTACLE (e.g., "No money", "Too hard", "Market fail"):
           - **CONSULT FIRST**: Do NOT delete milestones immediately.
           - **PROPOSE** a solution: "Melihat kondisi ini, saya sarankan kita HAPUS Milestone X dan ganti dengan Y. Apakah kamu setuju?"
           - **EXECUTE ONLY IF AGREED**: Only call `delete` or `create` tools after the user says "Ya" or "Setuju".
           - It's better to be safe/polite than rigid.
        
        3. **ROLLING UPDATES (Normal Progress)**: 
           - When a milestone is COMPLETED (via `complete_task_tool`), the count drops to 3.
           - YOU MUST immediately CREATE 1 NEW Future Milestone to restore the count to 4.
           - Analyze their speed (`started_at` vs `completed_at`) and Cash Flow (`get_financial_report_tool`) to decide the difficulty of the new step.
        
        **Capabilities:**
        
        1. **Roadmap Management**: 
           - View progress: `list_milestones_tool` (Shows Dates).
           - Update status: `complete_task_tool`, `start_milestone_tool`.
           - Modify plan: `create_milestone_tool`, `delete_milestone_tool`.
           
        2. **Financial Assistant**:
           - Record: `record_transaction_tool`.
           - Report: `get_financial_report_tool`.
           - Motivation: Remind them that recording daily transactions earns 5 points!
           
        3. **Gamification**:
           - Check status: `get_business_summary_tool`.
        
        Behavior Rules:
        - ALWAYS check context first (`list_milestones_tool`).
        - Be encouraging and use Indonesian (Bahasa Indonesia).
        - Keep answers concise.
        - **Act like a GPS**: If they miss a turn (fail a task), calmly reroute them. Don't force them back.
        """,
        llm=llm,
        tools=[
            list_milestones_tool,
            update_milestone_tool,
            create_milestone_tool,
            delete_milestone_tool,
            complete_task_tool,
            start_milestone_tool,
            get_business_summary_tool,
            record_transaction_tool,
            get_financial_report_tool,
        ],
        can_handoff_to=[],
    )

    workflow = AgentWorkflow(
        agents=[advisor_agent],
        root_agent=advisor_agent.name,
        timeout=timeout,
    )

    return workflow
