@register_tool()
def call_agent(action_context: ActionContext,
               agent_name: str,
               task: str) -> dict:
    """
    다른 에이전트를 호출하여 특정 작업을 수행하게 한다.

    Args:
        action_context: 사용 가능한 에이전트 레지스트리를 포함
        agent_name: 호출할 에이전트의 이름
        task: 에이전트에게 수행시킬 작업

    Returns:
        호출된 에이전트의 최종 메모리 결과
    """
    # 컨텍스트에서 에이전트 레지스트리를 가져온다
    agent_registry = action_context.get_agent_registry()
    if not agent_registry:
        raise ValueError("컨텍스트에 에이전트 레지스트리가 없습니다")

    # 레지스트리에서 에이전트의 실행 함수를 가져온다
    agent_run = agent_registry.get_agent(agent_name)
    if not agent_run:
        raise ValueError(f"에이전트 '{agent_name}'을 레지스트리에서 찾을 수 없습니다")

    # 호출될 에이전트를 위한 새로운 메모리 인스턴스를 생성한다
    invoked_memory = Memory()

    try:
        # 제공된 작업으로 에이전트를 실행한다
        result_memory = agent_run(
            user_input=task,
            memory=invoked_memory,
            # 필요한 컨텍스트 속성만 전달한다
            action_context_props={
                'auth_token': action_context.get('auth_token'),
                'user_config': action_context.get('user_config'),
                # 무한 재귀 방지를 위해 agent_registry는 전달하지 않는다
            }
        )

        # 마지막 메모리 항목을 결과로 반환한다
        if result_memory.items:
            last_memory = result_memory.items[-1]
            return {
                "success": True,
                "agent": agent_name,
                "result": last_memory.get("content", "결과 내용 없음")
            }
        else:
            return {
                "success": False,
                "error": "에이전트 실행에 실패했습니다."
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }




def call_agent_with_reflection(action_context, agent_name, task):
    # 에이전트 실행
    result_memory = agent_run(user_input=task, memory=invoked_memory)

    # 호출자의 메모리에 에이전트의 사고 과정을 추가
    caller_memory = action_context.get_memory()
    for memory_item in result_memory.items:
        caller_memory.add_memory({
            "type": f"{agent_name}_thought",
            "content": memory_item["content"]
        })