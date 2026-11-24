"""When would Deep Agents summarize the conversation for this model? Read from the installed library, not run.

    python -m tools.summarization_facts
"""
from deepagents.middleware.summarization import compute_summarization_defaults

from app.common import make_model

model = make_model()
print(f"model {model.model_name}: profile = {getattr(model, 'profile', None)!r}")
for key, value in compute_summarization_defaults(model).items():
    print(f"  {key}: {value!r}")
