import os
import uuid
from dotenv import load_dotenv
from typing import Any, Dict, TypedDict, List
import json
import time
import re
import logging
import redis
import asyncio
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
NO_FILES_SIGNAL = "NO_RELEVANT_FILES"



from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnablePassthrough 
from langchain_community.callbacks.manager import get_openai_callback

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langdetect import detect
from langchain_core.runnables import RunnableLambda

from flows import CIRCUIT_FLOW
from flows import CIRCUIT_MAP
from prompts import ROUTER_PROMPT, SELECTOR_PROMPT, WORKER_PROMPT, SUPERVISOR_PROMPT

from llm import get_llm
from tools import currency_converter_tool # We still need the tool itself

logger = logging.getLogger(__name__)

#  1. Configuration and Setup 
DATA_LAKE_DIR = "data-lake"
MOROCCAN_CITIES = ["agadir", "casablanca", "marrakech", "ouarzazate", "rabat", "tangier", "fez", "essaouira", "chefchaoune", "taroudant", "dakhla", "tafraout", "tiznit"]
CATEGORIES = ["accommodation", "cuisine", "history", "leisure", "safety", "transportation"]
PINECONE_INDEX_NAME = "travel-guide" 

def setup_environment():
    load_dotenv()

#  2. The Router Agent: The New Selector 

def clean_llm_json_output(llm_output: str) -> str:
    """
    Cleans the raw output from an LLM to extract a JSON string.
    It handles cases where the JSON is wrapped in ```json ... ``` blocks.
    """
    # Check if the output is wrapped in a json markdown block
    match = re.search(r"```json\s*([\s\S]*?)\s*```", llm_output)
    if match:
        # If found, return the extracted content
        return match.group(1).strip()
    
    # Otherwise, assume the output is already a clean JSON string
    return llm_output.strip()

def create_router_agent(llm):
    """
    Creates a router agent that decides whether to use a tool or retrieve documents.
    """
    selector_prompt_template = ROUTER_PROMPT
    prompt = ChatPromptTemplate.from_template(selector_prompt_template)

    chain = (
        RunnablePassthrough.assign(
            previous_user_question=lambda x: (
                x.get("chat_history", [])[-3].content
                if len(x.get("chat_history", [])) >= 3 and isinstance(x.get("chat_history", [])[-3], HumanMessage)
                else "No previous question in history."
            ),
            previous_ai_response=lambda x: (
                x.get("chat_history", [])[-2].content
                if len(x.get("chat_history", [])) >= 3 and isinstance(x.get("chat_history", [])[-2], AIMessage)
                else "No previous AI response in history."
            ),      
        )
        | prompt
        | llm.bind_tools([currency_converter_tool])
    )
    return chain

def create_selector_agent(llm, valid_cities: list[str]):
    """
    Creates a selector agent that chooses specific files based on user intention.
    """
    selector_prompt_template = SELECTOR_PROMPT
    prompt = ChatPromptTemplate.from_template(selector_prompt_template)
    
    # This part could be pre-computed, but is here for clarity
    valid_cities_str = "\n".join(sorted(valid_cities))
    
    chain = (
        RunnablePassthrough.assign(
            valid_cities=lambda x: valid_cities_str,
        )
        | prompt
        | llm
    )
    return chain

# --- 3. Worker Agent: The Content Synthesizer (for documents) ---
def create_worker_agent(llm):
    """Creates the agent focused on synthesizing an answer from provided text."""
    worker_prompt = ChatPromptTemplate.from_messages([
        ("system", WORKER_PROMPT),
        ("human", "CONTEXT:\n{context}\n\nUSER QUESTION:\n{input}"),
    ])
    chain = (
        RunnablePassthrough.assign() 
        | worker_prompt 
        | llm
    )
    return chain


# --- 4. Supervisor Agent: The Quality Controller and Refiner ---
def create_supervisor_agent(llm, valid_cities: list[str]):
    """Creates the supervisor agent chain that formats the last turn and current question for context."""
    prompt = ChatPromptTemplate.from_template(SUPERVISOR_PROMPT)
    valid_cities_str = "- ".join(f"- `{city}`" for city in sorted(valid_cities))
    chain = (
        RunnablePassthrough.assign(
            valid_cities=lambda x: valid_cities_str,
            current_user_question=lambda x: x.get("input", ""),
            previous_user_question=lambda x: (
                x.get("chat_history", [])[-3].content
                if len(x.get("chat_history", [])) >= 3 and isinstance(x.get("chat_history", [])[-3], HumanMessage)
                else "This is the first question of the conversation."
            ),
            previous_ai_response=lambda x: (
                x.get("chat_history", [])[-2].content
                if len(x.get("chat_history", [])) >= 2 and isinstance(x.get("chat_history", [])[-2], AIMessage)
                else "No previous AI response in history."
            ),
        )
        | prompt
        | llm
    )
    return chain

# --- 5. Graph Definition and Orchestration ---

class AgentState(TypedDict):
    input: str
    chat_history: List[BaseMessage]
    # Router
    action: str | None
    user_intention: str | None
    # Document Path
    selected_files: List[str]
    retrieved_content: str
    city: str | None
    # Tool Path
    tool_call: Dict | None
    tool_output: str | None
    # Error Flags
    router_error: bool | None
    selector_error: bool | None 
    # Common Path
    initial_response: str
    final_response: str
    map_data: List[Dict] | None
    metrics: Dict[str, Any]

class HierarchicalAgent:
    def __init__(self, checkpointer: AsyncRedisSaver, model_router: str = "gpt-4", model_selector: str = "gpt-4", model_worker: str = "gpt-4", model_supervisor: str = "gpt-4", verbose: bool = False):
        setup_environment()
        self.verbose = verbose
        if self.verbose: logger.info(f"HierarchicalAgent created with verbose={self.verbose}")
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

        try:
            locations_json_string = self.redis_client.get("locations")
            if locations_json_string:
                # If the key exists, parse the JSON string into a dictionary
                self.locations_data = json.loads(locations_json_string)
            else:
                # If the key doesn't exist in Redis, default to an empty dictionary
                self.locations_data = {}
        except json.JSONDecodeError:
            # Handle cases where the data in Redis might be corrupted or not valid JSON
            self.locations_data = {}


        # Models
        self.llm_router = get_llm(model=model_router, temperature=0.3, streaming=False, source="OpenAI")
        self.llm_selector = get_llm(model=model_selector, temperature=0.2, streaming=False, source="OpenAI")
        self.llm_worker = get_llm(model=model_worker, temperature=0.5, streaming=False, source="OpenAI")
        self.llm_supervisor = get_llm(model=model_supervisor, temperature=1, streaming=True, source="OpenAI")

        # ADDED: Initialize embeddings and vector store for fallback
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = PineconeVectorStore.from_existing_index(
            index_name=PINECONE_INDEX_NAME, 
            embedding=self.embeddings
        )

        # 1. Define Agents
        self.router_agent = create_router_agent(self.llm_router)
        self.selector_agent = create_selector_agent(self.llm_selector, MOROCCAN_CITIES)
        self.worker_agent = create_worker_agent(self.llm_worker)
        self.supervisor_agent = create_supervisor_agent(self.llm_supervisor, MOROCCAN_CITIES)

        # 3. Define the Graph
        graph = StateGraph(AgentState)
        graph.add_node("router", self.run_router)
        graph.add_node("selector", self.run_selector)
        graph.add_node("file_retrieval", self.file_retrieval)
        graph.add_node("semantic_fallback", self.semantic_fallback)
        graph.add_node("worker", self.run_worker)
        graph.add_node("run_tool", self.run_tool)
        graph.add_node("supervisor", self.run_supervisor)

        # 4. Define Edges
        graph.set_entry_point("router")
        
        # MODIFIED: Conditional edge logic is now more complex
        graph.add_conditional_edges(
            "router",
            self.decide_after_router,
            {
                "run_tool": "run_tool",
                "selector": "selector",
                "semantic_fallback": "semantic_fallback",
                "go_to_supervisor": "supervisor"
            }
        )

        graph.add_conditional_edges(
            "selector",
            lambda state: "semantic_fallback" if state.get("selector_error") else "file_retrieval"
        )
        graph.add_edge("file_retrieval", "worker")
        graph.add_edge("semantic_fallback", "worker")
        graph.add_edge("worker", "supervisor")
        graph.add_edge("run_tool", "supervisor")
        graph.add_edge("supervisor", END)

        self.memory = checkpointer
        self.graph = graph.compile(checkpointer=self.memory)

    def run_router(self, state: AgentState):
        """Executes the router agent to decide the next step."""
        if self.verbose: logger.info("EXECUTING ROUTER")
        start_time = time.perf_counter()
        router_input = {"input": state["input"], "chat_history": state["chat_history"]}
        response = self.router_agent.invoke(router_input)
        if self.verbose: logger.info(f"ROUTER RESPONSE\n{response.content}")
        end_time = time.perf_counter()

        state["metrics"]["timing_ms"]["router"] = (end_time - start_time) * 1000

        token_usage = response.usage_metadata
        state["metrics"]["tokens"]["router"] = {
            "prompt": token_usage.get("input_tokens", 0),
            "completion": token_usage.get("output_tokens", 0),
            "total": token_usage.get("total_tokens", 0)
        }

        if response.tool_calls:
            if self.verbose: logger.debug(f"ROUTER DECISION: USE TOOL\n{response.tool_calls[0]}")
            return {"tool_call": response.tool_calls[0], "router_error": False, "action": "run_tool"}

        if self.verbose: logger.debug("ROUTER DECISION: RETRIEVE DOCUMENTS")
        
        try:
            raw_content = response.content
            cleaned_content = clean_llm_json_output(raw_content)
            response_json = json.loads(cleaned_content)
            logger.debug(f"ROUTER PARSED JSON:\n{response_json}")
            
            action = response_json.get("action")

            if action == "respond_directly":
                if self.verbose: logger.info("ROUTER DECISION: RESPOND DIRECTLY")
                instruction_as_question = response_json.get("user_intention", "Modify the previous response.")
                return {
                    "action": "respond_directly",
                    "user_intention": instruction_as_question,
                    "router_error": False
                }

            elif action == "retrieve_documents":
                if self.verbose: logger.info("ROUTER DECISION: RETRIEVE DOCUMENTS")
                user_intention = response_json.get("user_intention", state["input"])
                return {
                    "action": "retrieve_documents",
                    "user_intention": user_intention,
                    "router_error": False
                }
            else:
                raise ValueError(f"Router returned unknown or missing action: {action}")

        except (json.JSONDecodeError, AttributeError, ValueError) as e:
            if self.verbose: logger.info(f"ROUTER FAILED, TRIGGERING FALLBACK\nError: {e}\nRaw response: {response.content}")
            return {"router_error": True, "metrics": state["metrics"]}
        
    def run_selector(self, state: AgentState):
        """Executes the selector agent to choose files."""
        if self.verbose: logger.info("EXECUTING SELECTOR")
        start_time = time.perf_counter()
        
        selector_input = {"user_intention": state["user_intention"]}
        response = self.selector_agent.invoke(selector_input)
        if self.verbose: logger.info(f"SELECTOR RESPONSE\n{response.content}")
        end_time = time.perf_counter()
        state["metrics"]["timing_ms"]["selector"] = (end_time - start_time) * 1000
        token_usage = response.usage_metadata
        state["metrics"]["tokens"]["selector"] = {
            "prompt": token_usage.get("input_tokens", 0),
            "completion": token_usage.get("output_tokens", 0),
            "total": token_usage.get("total_tokens", 0)
        }

        try:
            cleaned_content = clean_llm_json_output(response.content)
            response_json = json.loads(cleaned_content)
            selected_files = [item['path'] for item in response_json.get("selected_files", [])]
            
            if not selected_files:
                logger.warning("Selector did not return any files.")
                return {"selected_files": [], "selector_error": True}
            
            if selected_files[0] == NO_FILES_SIGNAL:
                logger.warning("Selector returned NO_FILES_SIGNAL.")
                return {"selected_files": selected_files, "selector_error": True}

            if self.verbose: logger.debug(f"SELECTOR DECISION: {selected_files}")
            return {"selected_files": selected_files, "selector_error": False}
        except (json.JSONDecodeError, AttributeError, ValueError) as e:
            if self.verbose: logger.info(f"SELECTOR FAILED, TRIGGERING FALLBACK\nError: {e}\nRaw response: {response.content}")
            return {"selector_error": True}
        
    def file_retrieval(self, state: AgentState):
        """Reads content from the file paths provided by the selector."""
        if self.verbose: logger.info("EXECUTING FILE RETRIEVAL")
        start_time = time.perf_counter()
        city_selected = False
        city = "rabat"
        content_parts = []
        file_paths = state.get("selected_files", [])
        
        for file_path in file_paths:
            dir_part = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            corrected_dir_part = dir_part.replace('.', '/')
            corrected_relative_path = os.path.join(corrected_dir_part, file_name)
            full_path = os.path.join(DATA_LAKE_DIR, corrected_relative_path)

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    content_parts.append(f"CONTENT FROM: {file_path}\n\n{file_content}")

                    if not city_selected:
                        city = full_path.split('/')[1].lower()
                        if city in MOROCCAN_CITIES:
                            city_selected = True
                        else:
                            city = "rabat"
                            city_selected = True
            except FileNotFoundError:
                logger.warning(f"File not found during retrieval: {full_path}")
            except Exception as e:
                logger.error(f"Error reading file {full_path}: {e}")

        retrieved_content = "\n\n---\n\n".join(content_parts)
        if not retrieved_content:
            retrieved_content = "No relevant documents were found to answer the question."

        end_time = time.perf_counter()
        state["metrics"]["timing_ms"]["file_retrieval"] = (end_time - start_time) * 1000
        state["metrics"]["counters"]["retrieved_files_count"] = len(file_paths)

        return {"retrieved_content": retrieved_content, "city": city, "metrics": state["metrics"]}

    def run_tool(self, state: AgentState):
        if self.verbose: logger.info("EXECUTING TOOL")
        start_time = time.perf_counter()
        tool_call = state["tool_call"]
        if tool_call and tool_call.get("name") == "currency_converter":
            output = currency_converter_tool.invoke(tool_call["args"])
            if self.verbose: logger.debug(f"TOOL OUTPUT\n{output}")
            end_time = time.perf_counter()
            state["metrics"]["timing_ms"]["tool"] = (end_time - start_time) * 1000
            return {"initial_response": output, "metrics": state["metrics"]}
        return {"initial_response": "Error: Tool call failed."}

    def semantic_fallback(self, state: AgentState):
        """Executes semantic search against Pinecone as a fallback."""
        if self.verbose: logger.info("EXECUTING SEMANTIC FALLBACK")
        start_time = time.perf_counter()
        query = state["input"]
        # Retrieve 5 most relevant documents
        results = self.vector_store.similarity_search(query, k=5)
        
        # Format the content for the worker agent
        content = [f" CONTENT FROM SEMANTIC SEARCH (Source: {doc.metadata.get('source', 'N/A')}) \n{doc.page_content}" for doc in results]
        end_time = time.perf_counter()
        state["metrics"]["timing_ms"]["semantic_fallback"] = (end_time - start_time) * 1000
        if self.verbose: 
            logger.debug(f"SEMANTIC FALLBACK RETRIEVED {len(results)} DOCUMENTS")
            for doc in results:
                logger.debug(f"Source: {doc.metadata.get('source', 'N/A')}\nContent Snippet: {doc.page_content[:200]}...\n")

        return {"retrieved_content": "\n\n".join(content), "metrics": state["metrics"]}

    def run_worker(self, state: AgentState):
        if self.verbose: logger.info("EXECUTING WORKER")
        start_time = time.perf_counter()
        query = state["user_intention"] or state["input"]
        worker_input = {"input": query, "context": state["retrieved_content"]}
        response = self.worker_agent.invoke(worker_input)
        if self.verbose: logger.info(f"WORKER RESPONSE\n{response.content}")
        end_time = time.perf_counter()
        state["metrics"]["timing_ms"]["worker"] = (end_time - start_time) * 1000

        token_usage = response.usage_metadata
        state["metrics"]["tokens"]["worker"] = {
            "prompt": token_usage.get("input_tokens", 0),
            "completion": token_usage.get("output_tokens", 0),
            "total": token_usage.get("total_tokens", 0)
        }
        return {"initial_response": response.content, "metrics": state["metrics"]}

    def run_supervisor(self, state: AgentState):
        if self.verbose: logger.info("EXECUTING SUPERVISOR")
        start_time = time.perf_counter()
        if state.get("action") == "respond_directly" and state.get("user_intention"):
            state["initial_response"] = state["user_intention"]
            if self.verbose: logger.debug("SUPERVISOR: Bypassing worker, using router's direct response instruction.")
        supervisor_input = {
            "chat_history": state["chat_history"],
            "input": state["input"], 
            "initial_response": state["initial_response"]
        }
        response = self.supervisor_agent.invoke(supervisor_input)
        if self.verbose: logger.info(f"SUPERVISOR RESPONSE\n{response.content}")
        end_time = time.perf_counter()
        state["metrics"]["timing_ms"]["supervisor"] = (end_time - start_time) * 1000

        token_usage = response.usage_metadata
        state["metrics"]["tokens"]["supervisor"] = {
            "prompt": token_usage.get("input_tokens", 0),
            "completion": token_usage.get("output_tokens", 0),
            "total": token_usage.get("total_tokens", 0)
        }
        return {"final_response": response.content, "metrics": state["metrics"]}

    # MODIFIED: The decision logic now checks for the error flag first
    def decide_after_router(self, state: AgentState) -> str:
        """Decides the next node based on the router's output."""
        if state.get("router_error"):
            return "semantic_fallback"
        elif state.get("tool_call"):
            return "run_tool"
        elif state.get("action") == "respond_directly":
            return "go_to_supervisor"
        elif state.get("action") == "retrieve_documents":
            return "selector"
        else: # Default fallback
            return "semantic_fallback"
    
    async def _stream_circuit_intro(self, user_input: str, session_id: str):
        """
        Streams a structured flow of text and custom circuit link widgets.
        """
        ai_response_content = []
        # 1. Yield metadata as before
        metadata = {"type": "metadata", "data": {"cities": ["rabat"], "selected_files": []}}
        yield f"{json.dumps(metadata)}\n"

        # 2. Iterate through the conversational flow
        for segment in CIRCUIT_FLOW:
            if segment["type"] == "token":
                # Stream text content chunk by chunk for the typewriter effect
                text_content = segment["data"]
                ai_response_content.append(text_content)
                chunk_size = 10
                for i in range(0, len(text_content), chunk_size):
                    chunk = text_content[i:i+chunk_size]
                    event = {"type": "token", "data": chunk}
                    yield f"{json.dumps(event)}\n"
                    await asyncio.sleep(0.04)
            
            elif segment["type"] == "circuit_link":
                # Send the custom widget event as a single message
                yield f"{json.dumps(segment)}\n"
                await asyncio.sleep(0.05) # Small delay after showing a widget

        # 3. Yield end events
        yield f"{json.dumps({'type': 'metrics', 'data': {}})}\n"
        yield f"{json.dumps({'type': 'end', 'data': None})}\n"

        config = {"configurable": {"thread_id": session_id}}
        last_state = await self.graph.aget_state(config)
        history = last_state.values.get("chat_history", []) if last_state else []

        full_ai_message = "".join(ai_response_content)
        new_history = history + [
            HumanMessage(content=user_input),
            AIMessage(content=full_ai_message)
        ]
        await self.graph.aupdate_state(config, {"chat_history": new_history}, as_node="supervisor")

    async def _stream_circuit_details(self, flow: list, user_input: str, session_id: str):
        """
        Streams a structured flow for a detailed circuit view.
        """
        ai_response_content = []
        metadata = {"type": "metadata", "data": {"cities": ["rabat"], "selected_files": []}}
        yield f"{json.dumps(metadata)}\n"

        for segment in flow:
            # For text segments, stream them chunk by chunk
            if segment.get("type") == "token":
                text_content = segment.get("data", "")
                ai_response_content.append(text_content)
                chunk_size = 10
                for i in range(0, len(text_content), chunk_size):
                    chunk = text_content[i:i+chunk_size]
                    event = {"type": "token", "data": chunk}
                    yield f"{json.dumps(event)}\n"
                    await asyncio.sleep(0.04)
            # For special UI commands, send them as a single event
            else:
                yield f"{json.dumps(segment)}\n"
                await asyncio.sleep(0.05)

        yield f"{json.dumps({'type': 'metrics', 'data': {}})}\n"
        yield f"{json.dumps({'type': 'end', 'data': None})}\n"

        config = {"configurable": {"thread_id": session_id}}
        last_state = await self.graph.aget_state(config)
        history = last_state.values.get("chat_history", []) if last_state else []

        full_ai_message = "".join(ai_response_content)
        new_history = history + [
            HumanMessage(content=user_input),
            AIMessage(content=full_ai_message)
        ]
        await self.graph.aupdate_state(config, {"chat_history": new_history}, as_node="supervisor")

    async def stream_response(self, user_input: str, session_id: str, mode: str = "default", circuit: str | None = None):
        """
        Processes user input and streams a structured response.
        Yields a series of JSON strings, each on a new line.
        1. A 'metadata' event with the city.
        2. A series of 'token' events for the text response.
        3. A 'map_data' event with location info (if any).
        4. An 'end' event.
        """
        if mode == "circuit":
            circuit_flow = CIRCUIT_MAP.get(circuit, None)

            if circuit_flow:
                async for event in self._stream_circuit_details(flow=circuit_flow, user_input=user_input, session_id=session_id):
                    yield event
                return
            
            async for event in self._stream_circuit_intro(user_input=user_input, session_id=session_id):
                yield event
            return
        
        config = {"configurable": {"thread_id": session_id}}

        last_state = await self.graph.aget_state(config)
        history = last_state.values.get("chat_history", []) if last_state else []

        graph_input = {
            "input": user_input, 
            "chat_history": history + [HumanMessage(content=user_input)],
            "metrics": {"timing_ms": {}, "tokens": {}, "counters": {}}
            }

        supervisor_started, final_response_content = False, []
        metadata_sent = False

        action_from_router = "retrieve_documents"
        intention_from_router = None
        selected_files_from_selector = []
        city_from_retrieval = "rabat"

        first_token_time = None 
        start_time = time.perf_counter()
        async for event in self.graph.astream_events(graph_input, config=config, version="v1"):
            kind = event["event"]
            if kind == "on_chain_end":
                node_name = event.get("name")
                if node_name == "router":
                    router_output = event["data"]["output"]
                    action_from_router = router_output.get("action", "retrieve_documents")
                    intention_from_router = router_output.get("user_intention", None)

                if node_name == "selector":
                    selector_output = event["data"]["output"]
                    selected_files_from_selector = selector_output.get("selected_files", [])
                
                if node_name == "file_retrieval":
                    retrieval_output = event["data"]["output"]
                    city_from_retrieval = retrieval_output.get("city", "rabat")

            if kind == "on_chain_start" and event.get("name") == "supervisor":
                if not metadata_sent:
                    metadata = {
                        "type": "metadata", 
                        "data": {
                            "action": action_from_router,
                            "user_intention": intention_from_router,
                            "selected_files": selected_files_from_selector,
                            "city": city_from_retrieval
                        }
                    }
                    yield f"{json.dumps(metadata)}\n"
                    metadata_sent = True
                supervisor_started = True

            if kind == "on_chain_end" and event.get("name") == "supervisor":
                supervisor_started = False
                
            if kind == "on_chat_model_stream" and supervisor_started:
                content = event["data"]["chunk"].content
                if content:
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
                    final_response_content.append(content)
                    yield f"{json.dumps({'type': 'token', 'data': content})}\n"
            if kind == "on_chain_end" and event.get("name") == "enricher":
                enricher_output = event["data"]["output"]
                map_data = enricher_output.get("map_data")
                if map_data:
                    yield f"{json.dumps({'type': 'map_data', 'data': {'locations': map_data}})}\n"

        final_state_after_stream = await self.graph.aget_state(config)

        # 2. Safely access the metrics from the state's values
        metrics = final_state_after_stream.values.get("metrics", {})
        end_time = time.perf_counter()
        metrics["timing_ms"]["total_stream_duration"] = (end_time - start_time) * 1000
        if first_token_time:
            metrics["timing_ms"]["time_to_first_streamed_token"] = (first_token_time - start_time) * 1000

        total_tokens = {"prompt": 0, "completion": 0, "total": 0}
        if "tokens" in metrics:
            for component_tokens in metrics["tokens"].values():
                if isinstance(component_tokens, dict):
                    total_tokens["prompt"] += component_tokens.get("prompt", 0)
                    total_tokens["completion"] += component_tokens.get("completion", 0)
                    total_tokens["total"] += component_tokens.get("total", 0)
        
        # Add the calculated totals back into the metrics object
        metrics["tokens"]["total"] = total_tokens

        logging.debug(f"EXECUTION METRICS : {metrics}")

        metrics_payload = {"type": "metrics", "data": metrics}
        yield f"{json.dumps(metrics_payload)}\n"
        
        yield f"{json.dumps({'type': 'end', 'data': None})}\n"

        new_history = history + [HumanMessage(content=user_input), AIMessage(content="".join(final_response_content))]
        await self.graph.aupdate_state(config, {"chat_history": new_history}, as_node="supervisor")