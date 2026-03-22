import inspect
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from typing import Any, Dict, List, Tuple

# .env 파일 로드
load_dotenv()

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

# OpenAI 클라이언트 초기화
# 실행 전 환경변수 OPENAI_API_KEY가 설정되어 있어야 합니다.
client = OpenAI()


def resolve_abs_path(path_str: str) -> Path:
    """
    상대 경로를 절대 경로로 변환합니다. file.py -> /Users/home/.../file.py
    """
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def read_file_tool(filename: str) -> Dict[str, Any]:
    """
    사용자가 지정한 파일의 전체 내용을 읽어옵니다.
    :param filename: 읽어올 파일의 이름.
    :return: 파일의 전체 내용.
    """
    full_path = resolve_abs_path(filename)
    print(full_path)
    with open(str(full_path), "r", encoding="utf-8") as f:
        content = f.read()
    return {
        "file_path": str(full_path),
        "content": content
    }


def list_files_tool(path: str) -> Dict[str, Any]:
    """
    사용자가 지정한 디렉토리의 파일 목록을 반환합니다.
    :param path: 파일 목록을 조회할 디렉토리 경로.
    :return: 디렉토리 내 파일 목록.
    """
    full_path = resolve_abs_path(path)
    all_files = []
    for item in full_path.iterdir():
        all_files.append({
            "filename": item.name,
            "type": "file" if item.is_file() else "dir"
        })
    return {
        "path": str(full_path),
        "files": all_files
    }


def edit_file_tool(path: str, old_str: str, new_str: str) -> Dict[str, Any]:
    """
    파일에서 old_str이 처음 등장하는 부분을 new_str로 교체합니다. old_str이 비어있으면,
    new_str 내용으로 파일을 생성하거나 덮어씁니다.
    :param path: 수정할 파일 경로.
    :param old_str: 교체할 기존 문자열.
    :param new_str: 교체될 새 문자열.
    :return: 처리된 파일 경로와 작업 결과.
    """
    full_path = resolve_abs_path(path)
    if old_str == "":
        full_path.write_text(new_str, encoding="utf-8")
        return {
            "path": str(full_path),
            "action": "파일이 생성되었습니다"
        }
    original = full_path.read_text(encoding="utf-8")
    if original.find(old_str) == -1:
        return {
            "path": str(full_path),
            "action": "old_str을 찾을 수 없습니다"
        }
    edited = original.replace(old_str, new_str, 1)
    full_path.write_text(edited, encoding="utf-8")
    return {
        "path": str(full_path),
        "action": "수정 완료"
    }


TOOL_REGISTRY = {
    "read_file": read_file_tool,
    "list_files": list_files_tool,
    "edit_file": edit_file_tool 
}


def get_tool_str_representation(tool_name: str) -> str:
    tool = TOOL_REGISTRY[tool_name]
    return f"""
    이름(Name): {tool_name}
    설명(Description): {tool.__doc__}
    인자(Signature): {inspect.signature(tool)}
    """


def get_full_system_prompt():
    tool_str_repr = ""
    for tool_name in TOOL_REGISTRY:
        tool_str_repr += "TOOL\n===" + get_tool_str_representation(tool_name)
        tool_str_repr += f"\n{'='*15}\n"
    return SYSTEM_PROMPT.format(tool_list_repr=tool_str_repr)


def extract_tool_invocations(text: str) -> List[Tuple[str, Dict[str, Any]]]:
    """
    'tool: name({...})' 형식의 문자열에서 (도구이름, 인자) 목록을 추출하여 반환합니다.
    단일 줄의 간결한 JSON 형식을 괄호 안에 예상합니다.
    """
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
    response = client.chat.completions.create(
        model="gpt-4o", # gpt-4o, gpt-4o-mini 등으로 변경 가능
        messages=conversation
    )
    return response.choices[0].message.content


def run_coding_agent_loop():
    # OpenAI API Key 확인
    if not os.environ.get("OPENAI_API_KEY"):
        print(f"{TextColor.LIGHT_YELLOW}경고: OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.{TextColor.RESET}")
        print("프로젝트 폴더의 '.env' 파일에 'OPENAI_API_KEY=sk-...' 를 등록해주세요.")
        return

    print(get_full_system_prompt())
    conversation = [{
        "role": "system",
        "content": get_full_system_prompt()
    }]
    while True:
        try:
            user_input = input(f"{YOU_COLOR}사용자:{RESET_COLOR} ")
        except (KeyboardInterrupt, EOFError):
            break
        conversation.append({
            "role": "user",
            "content": user_input.strip()
        })
        while True:
            assistant_response = execute_llm_call(conversation)
            if assistant_response is None:
                assistant_response = ""
            
            tool_invocations = extract_tool_invocations(assistant_response)
            if not tool_invocations:
                print(f"{ASSISTANT_COLOR}어시스턴트:{RESET_COLOR} {assistant_response}")
                conversation.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                break
            for name, args in tool_invocations:
                tool = TOOL_REGISTRY.get(name)
                resp = ""
                print(f"[{name}] 도구 실행:", args)
                if tool is None:
                    resp = f"Error: 도구 {name}가 존재하지 않습니다."
                else:
                    try:
                        if name == "read_file":
                            resp = tool(args.get("filename", "."))
                        elif name == "list_files":
                            resp = tool(args.get("path", "."))
                        elif name == "edit_file":
                            resp = tool(args.get("path", "."), 
                                        args.get("old_str", ""), 
                                        args.get("new_str", ""))
                    except Exception as e:
                        resp = f"Error: 도구 실행 중 오류 발생 {str(e)}"
                
                conversation.append({
                    "role": "user",
                    "content": f"tool_result({json.dumps(resp, ensure_ascii=False)})"
                })
                

if __name__ == "__main__":
    run_coding_agent_loop()
