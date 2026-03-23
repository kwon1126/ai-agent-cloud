import asyncio
import json
import ollama
from typing import Any, Dict, List, Tuple
from fastmcp import Client

MCP_SERVER_PATH = "../create-mcp/main.py"

SYSTEM_PROMPT = """
당신은 코딩 작업을 돕는 코딩 어시스턴트입니다.
당신은 다음과 같은 도구(Tool)들을 실행할 수 있습니다:

{tool_list_repr}

도구를 사용하고자 할 때는 정확히 다음 형식으로 한 줄만 응답하세요: 'tool: TOOL_NAME({{JSON_ARGS}})' 그리고 다른 말은 하지 마세요.
작은따옴표 대신 단일 줄의 간결한 큰따옴표 JSON 형식을 사용하세요. tool_result(...) 메시지를 받은 후에 작업을 계속 진행하세요.
도구가 필요 없는 경우, 평소처럼 응답하세요.
"""


class TextColor:
    LIGHT_BLUE = "\033[94m"
    LIGHT_YELLOW = "\033[93m"
    RESET = "\033[0m"

YOU_COLOR = TextColor.LIGHT_BLUE
ASSISTANT_COLOR = TextColor.LIGHT_YELLOW
RESET_COLOR = TextColor.RESET


def build_tool_list_repr(tools: list) -> str:
    """MCP 서버에서 가져온 도구 목록을 시스템 프롬프트용 문자열로 변환"""
    tool_str = ""
    for tool in tools:
        params = tool.inputSchema.get("properties", {})
        param_list = ", ".join(f"{k}: {v.get('type', 'any')}" for k, v in params.items())
        tool_str += f"""TOOL
===
    이름(Name): {tool.name}
    설명(Description): {tool.description}
    인자(Signature): ({param_list})
{'=' * 15}
"""
    return tool_str


def extract_tool_invocations(text: str) -> List[Tuple[str, Dict[str, Any]]]:
    """'tool: name({...})' 형식의 문자열에서 (도구이름, 인자) 목록을 추출"""
    invocations = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("tool:"):
            continue
        try:
            after = line[len("tool:"):].strip()
            name, rest = after.split("(", 1)
            name = name.strip()
            if not rest.endswith(")"):
                continue
            json_str = rest[:-1].strip()
            args = json.loads(json_str)
            invocations.append((name, args))
        except Exception:
            continue
    return invocations


def execute_llm_call(conversation: List[Dict[str, str]]):
    response = ollama.chat(
        model="qwen2.5-coder:7b",
        messages=conversation
    )
    return response["message"]["content"]


async def run_coding_agent_loop():
    async with Client(MCP_SERVER_PATH) as client:
        # MCP 서버에서 사용 가능한 도구 목록을 가져옴
        tools = await client.list_tools()
        tool_names = {tool.name for tool in tools}

        tool_list_repr = build_tool_list_repr(tools)
        system_prompt = SYSTEM_PROMPT.format(tool_list_repr=tool_list_repr)
        print(system_prompt)

        conversation = [{"role": "system", "content": system_prompt}]

        while True:
            try:
                user_input = input(f"{YOU_COLOR}사용자:{RESET_COLOR} ")
            except (KeyboardInterrupt, EOFError):
                break

            conversation.append({"role": "user", "content": user_input.strip()})

            while True:
                assistant_response = execute_llm_call(conversation)
                tool_invocations = extract_tool_invocations(assistant_response)

                if not tool_invocations:
                    print(f"{ASSISTANT_COLOR}어시스턴트:{RESET_COLOR} {assistant_response}")
                    conversation.append({"role": "assistant", "content": assistant_response})
                    break

                for name, args in tool_invocations:
                    if name not in tool_names:
                        print(f"[{name}] 알 수 없는 도구")
                        continue

                    print(f"[{name}] 도구 실행:", args)
                    # MCP 서버의 도구를 호출
                    result = await client.call_tool(name, args)
                    resp = result[0].text if result else "{}"

                    conversation.append({
                        "role": "user",
                        "content": f"tool_result({resp})"
                    })


if __name__ == "__main__":
    asyncio.run(run_coding_agent_loop())
