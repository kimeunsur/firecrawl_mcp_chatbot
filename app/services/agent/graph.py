import os
from typing import TypedDict, Annotated, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.pydantic_v1 import BaseModel
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .tools import get_place_information
from ...models.place import Place

# LangChain이 Pydantic V1을 사용하므로, V2 모델을 V1으로 변환하는 설정
Place.model_rebuild(force=True)

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    place_id: str
    place_info: Optional[Place]
    final_answer: Optional[str]

class Agent:
    def __init__(self):
        # .env 파일에 OPENAI_API_KEY가 설정되어 있어야 합니다.
        llm = ChatOpenAI(model="gpt-4o")
        tools = [get_place_information]
        self.model = llm.bind_tools(tools)
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # 1. LLM 노드 정의
        workflow.add_node("llm", self.call_llm)
        # 2. Tool 실행 노드 정의
        workflow.add_node("tools", ToolNode([get_place_information]))

        # 3. 엣지(Edge) 정의
        workflow.set_entry_point("llm")
        workflow.add_conditional_edges(
            "llm",
            self.should_continue,
            {
                "continue": "tools",
                "end": "__end__",
            },
        )
        workflow.add_edge("tools", "llm")

        return workflow.compile()

    def call_llm(self, state: AgentState):
        """LLM을 호출하여 다음 행동을 결정합니다."""
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {"messages": [response]}

    def should_continue(self, state: AgentState):
        """LLM의 응답을 보고 Tool을 호출할지, 끝낼지 결정합니다."""
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "continue"
        return "end"

    def run(self, place_id: str, query: str):
        """에이전트를 실행합니다."""
        initial_state = AgentState(
            messages=[("user", query)],
            place_id=place_id,
            place_info=None,
            final_answer=None
        )
        # stream() 대신 invoke()를 사용하여 최종 결과만 받음
        final_state = self.graph.invoke(initial_state)
        # 최종 답변은 마지막 AI 메시지의 content
        return final_state['messages'][-1].content

# 싱글턴 인스턴스로 생성하여 API에서 재사용
agent = Agent()
