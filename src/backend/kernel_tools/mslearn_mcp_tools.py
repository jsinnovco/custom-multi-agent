from azure.ai.agents.models import McpTool, RequiredMcpToolCall, SubmitToolApprovalAction, ToolApproval

import inspect
from typing import Annotated, Callable
from semantic_kernel.functions import kernel_function
from models.messages_kernel import AgentType
import json
from typing import get_type_hints

class MSLearnMCPTools:

    formatting_instructions = "Instructions: returning the output of this function call verbatim to the user in markdown. Then write AGENT SUMMARY: and then include a summary of what you did."
    agent_name = AgentType.MCP_MSLEARN.value
    
    @staticmethod
    @kernel_function(
        description="Fetch Azure REST API documentation using GitHub MCP integration."
    )
    async def fetch_azure_rest_api_docs(
        query: Annotated[str, "The search query for Azure REST API documentation"],
    ) -> str:
        """Fetch Azure REST API documentation from GitHub MCP server."""
        mcp_tool = McpTool(
            server_label="github",
            server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
            allowed_tools=["fetch_azure_rest_api_docs"],
        )
        return f"Documentation for: {query}"
    
    @staticmethod
    @kernel_function(
        description="Search Azure REST API code using GitHub MCP integration."
    )
    async def search_azure_rest_api_code(
        query: Annotated[str, "The search query for Azure REST API code"],
    ) -> str:
        """Search Azure REST API code from GitHub MCP server."""
        import urllib.request
        from urllib.parse import quote, urljoin

        base = "https://gitmcp.io/Azure/azure-rest-api-specs"
        # Try a simple search endpoint convention
        search_url = f"{base}/search?q={quote(query)}"
        try:
            with urllib.request.urlopen(search_url, timeout=10) as resp:
                data = resp.read(200000).decode("utf-8", errors="replace")
                return data[:8000]
        except Exception:
            return f"Code search results for: {query} (no proxy results)"
    
    @staticmethod
    @kernel_function(
        description="Fetch generic URL content using GitHub MCP integration."
    )
    async def fetch_generic_url_content(
        url: Annotated[str, "The URL to fetch content from"],
    ) -> str:
        """Fetch generic URL content from GitHub MCP server."""
        import urllib.request
        import urllib.error
        from urllib.parse import urlparse

        def try_fetch(url_to_get: str, timeout: int = 10) -> str:
            try:
                with urllib.request.urlopen(url_to_get, timeout=timeout) as resp:
                    content_bytes = resp.read(200000)  # limit to 200KB
                    try:
                        return content_bytes.decode("utf-8", errors="replace")
                    except Exception:
                        return content_bytes.decode("latin-1", errors="replace")
            except Exception as e:
                return f"[error fetching {url_to_get}: {e}]"

        parsed = urlparse(url)

        # If GitHub repo URL, try to fetch README from raw.githubusercontent
        if parsed.netloc.lower() == "github.com":
            parts = [p for p in parsed.path.split("/") if p]
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
                # Try common README locations/branches
                raw_urls = [
                    f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.MD",
                ]
                for raw_url in raw_urls:
                    content = try_fetch(raw_url)
                    if content and not content.startswith("[error fetching"):
                        snippet = content[:8000]
                        return f"Fetched README from {owner}/{repo}:\n\n{snippet}"

        # Otherwise attempt to fetch the original URL
        content = try_fetch(url)
        if content.startswith("[error fetching"):
            # As a last resort, attempt querying known MCP base host if present
            mcp_base = "https://gitmcp.io/Azure/azure-rest-api-specs"
            try_url = f"{mcp_base}?q={urllib.request.quote(url)}"
            fallback = try_fetch(try_url)
            if not fallback.startswith("[error fetching"):
                return f"Fetched via MCP proxy: {fallback[:8000]}"
            return content

        # Return a reasonable-length snippet
        snippet = content[:8000]
        return snippet
    
    @staticmethod
    @kernel_function(
        description="Search Azure REST API documentation using GitHub MCP integration."
    )
    async def search_azure_rest_api_docs(
        query: Annotated[str, "The search query for Azure REST API documentation"],
    ) -> str:
        """Search Azure REST API documentation from GitHub MCP server."""
        import urllib.request
        from urllib.parse import quote

        base = "https://gitmcp.io/Azure/azure-rest-api-specs"
        search_url = f"{base}/search?q={quote(query)}"
        try:
            with urllib.request.urlopen(search_url, timeout=10) as resp:
                data = resp.read(200000).decode("utf-8", errors="replace")
                return data[:8000]
        except Exception:
            return f"Documentation search results for: {query} (no proxy results)"
    
    @classmethod
    def generate_tools_json_doc(cls) -> str:
        """
        Generate a JSON document containing information about all methods in the class.

        Returns:
            str: JSON string containing the methods' information
        """

        tools_list = []

        # Get all methods from the class that have the kernel_function annotation
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            # Skip this method itself and any private methods
            if name.startswith("_") or name == "generate_tools_json_doc":
                continue

            # Check if the method has the kernel_function annotation
            if hasattr(method, "__kernel_function__"):
                # Get method description from docstring or kernel_function description
                description = ""
                if hasattr(method, "__doc__") and method.__doc__:
                    description = method.__doc__.strip()

                # Get kernel_function description if available
                if hasattr(method, "__kernel_function__") and getattr(
                    method.__kernel_function__, "description", None
                ):
                    description = method.__kernel_function__.description

                # Get argument information by introspection
                sig = inspect.signature(method)
                args_dict = {}

                # Get type hints if available
                type_hints = get_type_hints(method)

                # Process parameters
                for param_name, param in sig.parameters.items():
                    # Skip first parameter 'cls' for class methods (though we're using staticmethod now)
                    if param_name in ["cls", "self"]:
                        continue

                    # Get parameter type
                    param_type = "string"  # Default type
                    if param_name in type_hints:
                        type_obj = type_hints[param_name]
                        # Convert type to string representation
                        if hasattr(type_obj, "__name__"):
                            param_type = type_obj.__name__.lower()
                        else:
                            # Handle complex types like List, Dict, etc.
                            param_type = str(type_obj).lower()
                            if "int" in param_type:
                                param_type = "int"
                            elif "float" in param_type:
                                param_type = "float"
                            elif "bool" in param_type:
                                param_type = "boolean"
                            else:
                                param_type = "string"

                    # Create parameter description
                    # param_desc = param_name.replace("_", " ")
                    args_dict[param_name] = {
                        "description": param_name,
                        "title": param_name.replace("_", " ").title(),
                        "type": param_type,
                    }

                # Add the tool information to the list
                tool_entry = {
                    "agent": cls.agent_name,  # Use agent type
                    "function": name,
                    "description": description,
                    "arguments": json.dumps(args_dict).replace('"', "'"),
                }

                tools_list.append(tool_entry)

        # Return the JSON string representation
        return json.dumps(tools_list, ensure_ascii=False, indent=2)

    # This function does NOT have the kernel_function annotation
    # because it's meant for introspection rather than being exposed as a tool
    @classmethod
    def get_all_kernel_functions(cls) -> dict[str, Callable]:
        """
        Returns a dictionary of all methods in this class that have the @kernel_function annotation.
        This function itself is not annotated with @kernel_function.

        Returns:
            Dict[str, Callable]: Dictionary with function names as keys and function objects as values
        """
        kernel_functions = {}

        # Get all class methods
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            # Skip this method itself and any private/special methods
            if name.startswith("_") or name == "get_all_kernel_functions":
                continue

            # Check if the method has the kernel_function annotation
            # by looking at its __annotations__ attribute
            method_attrs = getattr(method, "__annotations__", {})
            if hasattr(method, "__kernel_function__") or "kernel_function" in str(
                method_attrs
            ):
                kernel_functions[name] = method

        return kernel_functions
