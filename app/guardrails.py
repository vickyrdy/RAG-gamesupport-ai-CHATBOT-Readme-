import re

INJECTION_PATTERNS = [
    r"\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b",
    r"\b(reveal|show|print)\s+(your\s+|the\s+)?system\s+prompt\b",
]

SECRET_PATTERNS = [
    r"\bgsk_[A-Za-z0-9_-]{20,}\b",
    r"\bAIza[A-Za-z0-9_-]{20,}\b",
    r"\bsk-[A-Za-z0-9_-]{20,}\b",
]


def check_input(text: str) -> str | None:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return "I cannot follow requests to override my instructions."

    for pattern in SECRET_PATTERNS:
        if re.search(pattern, text):
            return "Please remove API keys or secrets before continuing."

    return None


def redact_output(text: str) -> str:
    for pattern in SECRET_PATTERNS:
        text = re.sub(pattern, "[REDACTED]", text)
    return text