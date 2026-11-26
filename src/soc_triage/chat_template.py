"""Configure the chat template used by JSON-only SOC rounds."""

NON_THINKING_PREFIX = "{%- set enable_thinking = false -%}"


def disable_chat_thinking(tokenizer) -> None:
    """Set the mode in the template because MLX ChatDataset passes no mode option."""
    template = tokenizer.chat_template
    if not isinstance(template, str) or "enable_thinking" not in template:
        raise ValueError("O tokenizer não oferece enable_thinking no chat template.")
    if not template.startswith(NON_THINKING_PREFIX):
        tokenizer.chat_template = NON_THINKING_PREFIX + template
