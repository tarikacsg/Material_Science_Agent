import json

from tools import TOOLS
from state import STATE

from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("TRITON_API_KEY"),
    base_url="https://tritonai-api.ucsd.edu/v1"
)


SYSTEM_PROMPT = """
You are a materials-science planning agent.

Your job:
1. Understand the user request.
2. Choose tools when needed.
3. Build a structure workflow step by step.
4. Stop when the task is complete.

Rules:
- Use fetch_structure before make_supercell if no structure is loaded.
- Use make_supercell when the user asks for a supercell.
- Use save_poscar and/or save_cif if the user asks to export files.
- Use describe_structure near the end if the user wants a summary.
- Be concise and action-oriented.
"""


TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "fetch_structure",
        "description": "Fetch a crystal structure for a material formula from Materials Project and store it in memory.",
        "parameters": {
            "type": "object",
            "properties": {
                "material": {
                    "type": "string",
                    "description": "Material formula, e.g. CH3NH3PbI3 or Si",
                }
            },
            "required": ["material"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "make_supercell",
        "description": "Create a supercell from the currently loaded structure.",
        "parameters": {
            "type": "object",
            "properties": {
                "scaling": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 3,
                    "maxItems": 3,
                    "description": "Supercell scaling, e.g. [2, 2, 2]",
                }
            },
            "required": ["scaling"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "save_poscar",
        "description": "Save the current structure as a VASP POSCAR file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Output filename, e.g. POSCAR or MAPbI3_POSCAR",
                }
            },
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "save_cif",
        "description": "Save the current structure as a CIF file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Output CIF filename",
                }
            },
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "describe_structure",
        "description": "Describe the currently loaded structure.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
]

CHAT_TOOL_SCHEMAS = [
    {"type": "function", "function": {k: v for k, v in schema.items() if k != "type"}}
    for schema in TOOL_SCHEMAS
]


def run_agent(user_request: str, model: str = "api-gpt-oss-120b", max_steps: int = 8) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_request},
    ]

    for _ in range(max_steps):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=CHAT_TOOL_SCHEMAS,
            tool_choice="auto",
        )

        assistant_msg = response.choices[0].message
        tool_calls = assistant_msg.tool_calls or []

        if not tool_calls:
            return assistant_msg.content or ""

        messages.append(assistant_msg.model_dump(exclude_none=True))
        for call in tool_calls:
            tool_name = call.function.name
            tool_args = json.loads(call.function.arguments or "{}")

            if tool_name not in TOOLS:
                tool_result = {"ok": False, "error": f"Unknown tool: {tool_name}"}
            else:
                try:
                    tool_result = TOOLS[tool_name](**tool_args)
                except Exception as e:
                    tool_result = {"ok": False, "error": str(e)}

            STATE["history"].append(
                {
                    "tool": tool_name,
                    "args": tool_args,
                    "result": tool_result,
                }
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(tool_result),
                }
            )

    return "Stopped after reaching max_steps without a final response."
