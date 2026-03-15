import sys
import os

# Add project root to sys.path so the ai/ module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.services.llm_service import generate_response

print(generate_response("Hello, are you there?"))
