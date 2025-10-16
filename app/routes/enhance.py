"""
Prompt enhancement endpoint
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_service import enhance_user_prompt

router = APIRouter(prefix="/api", tags=["enhance"])


class EnhancePromptRequest(BaseModel):
    prompt: str
    tone: str = "casual"
    image_style: str = "realistic"


@router.post("/enhance-prompt")
async def enhance_prompt(request: EnhancePromptRequest):
    """
    Enhance user's prompt before content generation
    """
    try:
        result = await enhance_user_prompt(
            user_prompt=request.prompt,
            tone=request.tone,
            image_style=request.image_style
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enhance prompt: {str(e)}"
        )

