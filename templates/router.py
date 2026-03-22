"""
Adaptive Router (rc5)

Routes between direct and checklist execution based on active rule count.
Threshold of 5 was determined empirically through cross-model validation.
"""


def count_active_rules(config: str, user_query: str) -> int:
    """
    Count how many rules/constraints are likely activated by the user query.

    In production, this could be:
    - A simple keyword/condition matcher against rule conditions
    - An LLM pre-pass that extracts relevant rule IDs
    - A static analysis of the config structure

    For now, this is a placeholder that should be implemented
    based on your specific config structure.
    """
    # TODO: Implement rule activation detection
    # Example heuristic: count rules with matching conditions
    raise NotImplementedError("Implement based on your config structure")


def select_strategy(active_rules: int, threshold: int = 5) -> str:
    """
    Select execution strategy based on active rule count.

    Args:
        active_rules: Number of simultaneously active rules/constraints
        threshold: Complexity phase transition point (default: 5)

    Returns:
        "direct" or "checklist"
    """
    if active_rules >= threshold:
        return "checklist"
    return "direct"


def build_prompt(config: str, strategy: str) -> str:
    """
    Build the system prompt for the selected strategy.

    Args:
        config: The XML-semantic v2 configuration content
        strategy: "direct" or "checklist"

    Returns:
        Complete system prompt string
    """
    import os

    template_dir = os.path.dirname(os.path.abspath(__file__))

    if strategy == "checklist":
        template_file = os.path.join(template_dir, "prompt_checklist.txt")
    else:
        template_file = os.path.join(template_dir, "prompt_direct.txt")

    with open(template_file) as f:
        template = f.read()

    return template.replace("{config}", config)


# Example usage:
#
#   config = open("my_agent_config.xml").read()
#   active = count_active_rules(config, user_query)
#   strategy = select_strategy(active)
#   prompt = build_prompt(config, strategy)
#   response = call_llm(system=prompt, user=user_query)
