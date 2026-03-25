from cat import hook, CatMessage, AgenticWorkflowOutput, AgenticWorkflowTask


@hook
def before_cat_sends_message(message: CatMessage, agent_output: AgenticWorkflowOutput, cat) -> CatMessage:
    settings = cat.mad_hatter.get_plugin().load_settings()
    if not settings.get("enable_double_check"):
        return message

    context_memories = ""
    if not cat.working_memory.context_memories:
        context_memories += "(empty context)"
    else:
        for m in cat.working_memory.context_memories:
            context_memories += " --- " + m.document.page_content + " ---\n"

    context_history = ""
    if not cat.working_memory.history:
        context_history += "(empty history)"
    else:
        for h in cat.working_memory.history:
            context_history += " --- " + h.text + " ---\n"
    
    system_prompt = f"""Fact check and review the final response of a conversation, leaving only the information that can
be inferred from the contents of the tag <facts> and <history>. If all the information is contained in the <facts> or <history>,
repeat the response. Otherwise, recreate the response with only the information that is contained in <facts>.
If <facts> is empty, ask for document uploads to be able to answer the question.

<facts>
{context_memories}
</facts>

<history>
{context_history}
</history>
"""

    prompt=f"""
Response to be fact checked (may contain information not present in the <facts> or <history> tags):
- {message.text}

Fact checked response:
- """

    agent_input = AgenticWorkflowTask(system_prompt=system_prompt, user_prompt=prompt)

    message.text = cat.agentic_workflow.run(
        task=agent_input,
        llm=cat.large_language_model,
        callbacks=cat.plugin_manager.execute_hook("llm_callbacks", [], caller=cat),
    )
    return message
