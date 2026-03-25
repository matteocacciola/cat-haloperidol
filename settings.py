from cat import plugin
from pydantic import BaseModel, Field


class HaloperidolSettings(BaseModel):
    enable_double_check: bool = Field(
        default=False,
        description="If true, the Cat will double check its own reply. Will use more tokens, but reduce hallucinations even more."
    )


@plugin
def settings_schema():
    return HaloperidolSettings.model_json_schema()
