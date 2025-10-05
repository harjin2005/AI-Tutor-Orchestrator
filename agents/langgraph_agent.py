from typing import TypedDict, Annotated, Literal, Dict, Any
from langgraph.graph import StateGraph, END
from agents.base_agent import BaseAgent
from agents.parameter_extractor import ParameterExtractor
from tools.educational_tools import NoteMakerTool, FlashcardGeneratorTool, ConceptExplainerTool
from schemas.user_context import UserContext
import operator

class AgentState(TypedDict):
    query: str
    user_context: dict
    extracted_params: dict
    selected_tool: str
    tool_result: dict
    response: str

class LangGraphTutorAgent(BaseAgent):
    """LangGraph-powered Tutor Agent with Parameter Extraction & Tool Orchestration"""
    
    def __init__(self):
        super().__init__()
        self.param_extractor = ParameterExtractor()
        self.note_maker = NoteMakerTool()
        self.flashcard_gen = FlashcardGeneratorTool()
        self.concept_explainer = ConceptExplainerTool()
        self.graph = self._create_graph()

    def _create_graph(self):
        workflow = StateGraph(AgentState)

        # Step 1: Parameter extraction node
        workflow.add_node("parameter_extraction", self._parameter_extraction_node)
        # Step 2: Tool selection node
        workflow.add_node("tool_selection", self._tool_selection_node)
        # Step 3: Tool execution node
        workflow.add_node("tool_execution", self._tool_execution_node)

        # Entry point
        workflow.set_entry_point("parameter_extraction")
        # Graph edges
        workflow.add_edge("parameter_extraction", "tool_selection")
        workflow.add_edge("tool_selection", "tool_execution")
        workflow.add_edge("tool_execution", END)

        return workflow.compile()

    def _parameter_extraction_node(self, state: AgentState) -> AgentState:
        query = state["query"]
        user_context = state.get("user_context", {})
        params = self.param_extractor.extract_parameters(query, user_context)
        return {**state, "extracted_params": params}

        def _tool_selection_node(self, state: AgentState) -> AgentState:
            query = state["query"].lower()
            params = state.get("extracted_params", {})
            if "flashcard" in query or "card" in query:
                tool = "flashcard"
            elif "note" in query or params.get("note_taking_style"):
                tool = "note_maker"
            elif "explain" in query or params.get("concept_to_explain"):
                tool = "concept_explainer"
            else:
                if params.get("subject") in ["computer_science", "coding", "programming"]:
                    tool = "openrouter_agent"
                else:
                    tool = "groq_agent"
            return {**state, "selected_tool": tool}


    def _tool_execution_node(self, state: AgentState) -> AgentState:
        tool = state.get("selected_tool")
        params = state.get("extracted_params", {})
        query = state["query"]

        # Educational/mocked tools
        if tool == "note_maker":
            result = self.note_maker.generate_notes(params)
        elif tool == "flashcard":
            result = self.flashcard_gen.generate_flashcards(params)
        elif tool == "concept_explainer":
            result = self.concept_explainer.explain_concept(params)
        # AI agents if requested
        elif tool == "groq_agent":
            resp = self.call_groq(query, model="llama-3.3-70b-versatile")
            result = {"response": resp, "model_used": "groq_llama_academic"}
        elif tool == "openrouter_agent":
            resp = self.call_openrouter(query)
            result = {"response": resp, "model_used": "openrouter_coding"}
        else:
            result = {"response": "No suitable tool found.", "model_used": "none"}

        # Universal response: either tool output or AI
        return {**state, "tool_result": result,
                "response": result.get("response", str(result)),
                "model_used": result.get("model_used", tool)}

    async def process(self, query: str) -> dict:
        # Use static user context for demo (can fetch dynamically if needed)
        user_context = UserContext().dict()
        initial_state = {
            "query": query,
            "user_context": user_context,
            "extracted_params": {},
            "selected_tool": "",
            "tool_result": {},
            "response": ""
        }
        result = await self.graph.ainvoke(initial_state)
        return {
            "agent": "tutor_langgraph",
            "response": result["response"],
            "tool_result": result.get("tool_result", {}),
            "selected_tool": result.get("selected_tool", ""),
            "extracted_params": result.get("extracted_params", {}),
            "model_used": result.get("model_used", "")
        }
