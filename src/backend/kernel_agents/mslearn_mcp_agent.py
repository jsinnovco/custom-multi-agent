import logging
from typing import Dict, List, Optional

from context.cosmos_memory_kernel import CosmosMemoryContext
from kernel_agents.agent_base import BaseAgent
from kernel_tools.mslearn_mcp_tools import MSLearnMCPTools
from models.messages_kernel import AgentType
from semantic_kernel.functions import KernelFunction
from azure.ai.agents.models import McpTool, RequiredMcpToolCall, SubmitToolApprovalAction, ToolApproval


class MCPMSLearnAgent(BaseAgent):
    """MS Learn MCP agent implementation using Semantic Kernel and MCP.

       This is an MS Learn MCP agent."""

    def __init__(
        self,
        session_id: str,
        user_id: str,
        memory_store: CosmosMemoryContext,
        tools: Optional[List[KernelFunction]] = None,
        system_message: Optional[str] = None,
        agent_name: str = AgentType.MCP_MSLEARN.value,
        client=None,
        definition=None,
    ) -> None:
        """Initialize the MS Learn MCP Agent.

        Args:
            kernel: The semantic kernel instance
            session_id: The current session identifier
            user_id: The user identifier
            memory_store: The Cosmos memory context
            tools: List of tools available to this agent (optional)
            system_message: Optional system message for the agent
            agent_name: Optional name for the agent (defaults to "Learning Agent")
            client: Optional client instance
            definition: Optional definition instance
        """
        # Load configuration if tools not provided
        if not tools:
            # Get tools directly from MSLearnMCPTools class
            tools_dict = MSLearnMCPTools.get_all_kernel_functions()
            tools = [KernelFunction.from_method(func) for func in tools_dict.values()]
            # Use system message from config if not explicitly provided
        if not system_message:
            system_message = self.default_system_message(agent_name)

        # Use agent name from config if available
        agent_name = AgentType.MCP_MSLEARN.value

        super().__init__(
            agent_name=agent_name,
            session_id=session_id,
            user_id=user_id,
            memory_store=memory_store,
            tools=tools,
            system_message=system_message,
            client=client,
            definition=definition,
        )

    @classmethod
    async def create(
        cls,
        **kwargs: Dict[str, str],
    ) -> None:
        """Asynchronously create the LearningAgent.

        Creates the Azure AI Agent for looking up Github repositories and fetching relevant data or codebases from it.

        Returns:
            None
        """

        session_id = kwargs.get("session_id")
        user_id = kwargs.get("user_id")
        memory_store = kwargs.get("memory_store")
        tools = kwargs.get("tools", None)
        system_message = kwargs.get("system_message", None)
        agent_name = kwargs.get("agent_name")
        client = kwargs.get("client")

        print("Creating LearningAgent with the following parameters:")
        print(f"Session ID: {session_id}")
        print(f"User ID: {user_id}")
        print(f"Memory Store: {memory_store}")
        print(f"Tools: {tools}")
        print(f"System Message: {system_message}")
        print(f"Agent Name: {agent_name}")
        print(f"Client: {client}")

        try:
            logging.info("Initializing LearningAgent from async init azure AI Agent")

            # Create the Azure AI Agent using AppConfig with string instructions
            agent_definition = await cls._create_azure_ai_agent_definition(
                agent_name=agent_name,
                instructions=system_message,  # Pass the formatted string, not an object
                temperature=0.0,
                response_format=None,
                tools=tools,

            )
            print(f"Created agent, ID: {agent_definition}")
            # print(f"MCP Server: {agent_definition.server_label} at {mcp_tool.server_url}")

            return cls(
                session_id=session_id,
                user_id=user_id,
                memory_store=memory_store,
                tools=tools,
                system_message=system_message,
                agent_name=agent_name,
                client=client,
                definition=agent_definition,
            )

        except Exception as e:
            logging.error(f"Failed to create Azure AI Agent for LearningAgent: {e}")
            raise

    @staticmethod
    def default_system_message(agent_name=None) -> str:
        """Get the default system message for the agent.
        Args:
            agent_name: The name of the agent (optional)
        Returns:
            The default system message for the agent
        """
        # return "You are a helpful agent that can use MCP tools to assist users. Ground answers in official Microsoft documentation via the Microsoft Learn MCP tools."
        return "You are a helpful agent that can use MCP tools to assist users using the GitHub MCP integration to answer questions and perform tasks. You can do things like fetching GitHub repository links, summarize README documents, fetch and search Azure REST API code and documentation."

    # @property
    # def plugins(self):
    #     """Get the plugins for the event learning agent."""
    #     return MSLearnMCPTools.get_all_kernel_functions()
