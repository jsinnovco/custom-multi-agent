import inspect
from typing import Annotated, Callable

from semantic_kernel.functions import kernel_function
from models.messages_kernel import AgentType
import json
from typing import get_type_hints


class EventPlannerTools:

    formatting_instructions = "Instructions: returning the output of this function call verbatim to the user in markdown. Then write AGENT SUMMARY: and then include a summary of what you did."
    agent_name = AgentType.EVENT_PLANNER.value

    # Define Event Planner tools (functions)
    @staticmethod
    @kernel_function(description="Initial planning and consultation for an event.")
    async def planning() -> str:
        return (
            f"##### Met with stakeholders to define event goals, audience, budget, and scope.\n"
            f"{EventPlannerTools.formatting_instructions}"
        )

    @staticmethod
    @kernel_function(description="Budget & Resource Management.")
    async def budgeting() -> str:
        return (
            f"##### Track costs using tools like the “Cost Tracker” and manage GBO budgets.\n"
            f"Coordinate swag orders, catering, and venue logistics with internal teams like Eventions.\n"
            f"{EventPlannerTools.formatting_instructions}"
        )

    @staticmethod
    @kernel_function(description="Venue & Vendor Coordination.")
    async def venue_coordination() -> str:
        return (
            f"##### Select and book venues, negotiate contracts, and manage logistics such as seating, AV setup, and accessibility.\n"
            f"Liaise with external suppliers for food, entertainment, and decor.\n"
            f"{EventPlannerTools.formatting_instructions}"
        )

    @staticmethod
    @kernel_function(description="Marketing & Communications.")
    async def marketing() -> str:
        return (
            f"##### Create and send invites, manage RSVP tracking, and coordinate pre- and post-event communications.\n"
            f"**Share wrap-up emails and upload content to internal libraries for future reference.**\n\n"
            f"{EventPlannerTools.formatting_instructions}"
        )

    @staticmethod
    @kernel_function(description="Track the status of caterering.")
    async def track_order(order_number: str) -> str:
        return (
            f"##### Order Tracking\n"
            f"**Order Number:** {order_number}\n"
            f"**Status:** In Transit\n\n"
            f"Order {order_number} is currently in transit.\n"
            f"{EventPlannerTools.formatting_instructions}"
        )
    @staticmethod
    @kernel_function(description="Execution & Onsite Management.")
    async def execution() -> str:
        return (
            f"##### Oversee event flow, troubleshoot issues, and ensure compliance with safety and inclusion policies.\n"
            f"**Monitor attendance and engagement, often using tools like RAPID templates and registration dashboards.**\n"
            f"{EventPlannerTools.formatting_instructions}"
        )
        
    @staticmethod
    @kernel_function(description="Post-Event Reporting.")
    async def post_event() -> str:
        return (
            f"#####Analyze attendee data, no-show rates, and feedback to assess impact.\n"
            f"**Share results with marketing and leadership teams to inform future planning..**\n"
            f"{EventPlannerTools.formatting_instructions}"
        )
    @staticmethod
    @kernel_function(
        description="Get event planning information, such as policies, procedures, and guidelines."
    )
    async def get_event_planning_information(
        query: Annotated[str, "The query for the event planner knowledgebase"],
    ) -> str:
        information = (
            f"##### Event Planner Information\n\n"
            f"**Document Name:** Contoso's Event Planning Policies and Procedures\n"
            f"**Domain:** Event Planning Policy\n"
            f"**Description:** Guidelines outlining the event planning processes for Contoso, including venue selection, equipment hires, service or catering orders, and attendee list management.\n\n"
            f"**Key points:**\n"
            f"- All event logistics (permits, safety, accessibility), catering, seating, venue bookings or purchases must be approved by the procurement department.\n"
            f"- All equipment purchases for video conferencing must also be approved by Tech Support Agent.\n"
            f"- Register early for labs and workshops—ideally 30 days in advance—to secure a spot.\n"
            f"- Daily 90-minute networking lunches encourage peer connection.\n"
            f"- Regular inventory checks should be conducted to maintain optimal stock levels.\n"
            f"- All sessions to be recorded and made available to attendees later. \n"
            f"- Dedicated project managers are assigned to drive individual streams like attendee lists, sending invites, ordering catering etc.\n"
            f"- All event-related purchases must be documented and tracked for budget management.\n"
            f"- Event planners should liaise with vendors to ensure timely delivery of services and equipment.\n"
            f"- Hotel reservations must be canceled at least 72 hours before check-in to avoid charges.\n"
            f"{EventPlannerTools.formatting_instructions}"
        )
        return information

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
                    "agent": cls.agent_name,  # Use HR agent type
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
