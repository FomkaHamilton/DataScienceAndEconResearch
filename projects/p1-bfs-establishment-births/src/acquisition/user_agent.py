"""
User-Agent header for the data downloads.

Census and BLS ask automated clients to identify themselves with a contact
address. The address is read from the RESEARCH_CONTACT_EMAIL environment
variable, or from a .env file at the repository root (ignored by git), so
it is not stored in the code.
"""

import os

from dotenv import load_dotenv


def user_agent() -> str:
    load_dotenv()
    contact = os.environ.get("RESEARCH_CONTACT_EMAIL", "").strip()
    if not contact:
        raise SystemExit(
            "Set RESEARCH_CONTACT_EMAIL to a contact email address before downloading "
            "(Census and BLS ask automated clients to identify themselves). It can be "
            "set in a .env file at the repository root, which git ignores."
        )
    return f"DataScienceAndEconResearch/0.1 (independent research project; contact: {contact})"
