import os
from typing import TypedDict, Annotated, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.pydantic_v1 import BaseModel
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .tools import get_place_information, generate_llms_txt_for_place
from ...models.place import Place

# LangChain이 Pydantic V1을 사용하므로, V2 모델을 V1으로 변환하는 설정
Place.model_rebuild(force=True)

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    place_id: str
    category: str  # 카테고리 상태 추가
    tool_outputs: dict 

class Agent:
    def __init__(self):
        llm = ChatOpenAI(model="gpt-4o")
        self.tools = [get_place_information, generate_llms_txt_for_place]
        self.model = llm.bind_tools(self.tools)
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("llm", self.call_llm)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.set_entry_point("llm")
        workflow.add_conditional_edges(
            "llm",
            self.should_continue,
            {"continue": "tools", "end": "__end__"},
        )
        workflow.add_edge("tools", "llm")
        return workflow.compile()

    def call_llm(self, state: AgentState):
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {"messages": [response]}

    def should_continue(self, state: AgentState):
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "continue"
        return "end"

    def run(self, place_id: str, query: str, category: str):
        """에이전트를 실행합니다."""
        initial_query = f"장소 ID '{place_id}' (카테고리: {category})에 대한 요청: {query}"
        
        initial_state = AgentState(
            messages=[("user", initial_query)],
            place_id=place_id,
            category=category, # 초기 상태에 카테고리 설정
            tool_outputs={}
        )
        final_state = self.graph.invoke(initial_state)
        return final_state['messages'][-1].content

agent = Agent()
