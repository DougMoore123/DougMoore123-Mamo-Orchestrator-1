from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Callable, Dict, List

from openai import AzureOpenAI


@dataclass
class Tool:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], str]


@dataclass
class AgentContext:
    client: AzureOpenAI
    chat_model: str
    tools: List[Tool]
    system_prompt: str
    max_steps: int = 6
    trace: List[Dict[str, Any]] | None = None


def _tool_schema(tool: Tool) -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        },
    }


def run_agent(ctx: AgentContext, user_prompt: str) -> str:
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": ctx.system_prompt},
        {
            "role": "user",
            "content": (
                "You are an agent. Use tools to gather evidence, then respond with VALID JSON only.\n"
                f"Question: {user_prompt}"
            ),
        },
    ]

    tools = [_tool_schema(t) for t in ctx.tools]

    for step in range(ctx.max_steps):
        resp = ctx.client.chat.completions.create(
            model=ctx.chat_model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2,
            max_completion_tokens=1200,
        )
        msg = resp.choices[0].message

        if msg.tool_calls:
            messages.append({"role": "assistant", "tool_calls": msg.tool_calls})
            for call in msg.tool_calls:
                tool = next(t for t in ctx.tools if t.name == call.function.name)
                args = json.loads(call.function.arguments or "{}")
                result = tool.handler(args)
                if ctx.trace is not None:
                    ctx.trace.append(
                        {
                            "step": step,
                            "tool": tool.name,
                            "args": args,
                            "result_preview": result[:500],
                        }
                    )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result,
                    }
                )
            continue

        if msg.content:
            return msg.content

    return json.dumps({"error": "Agent exceeded max steps"})
