"""
AI content generation endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, validator, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.services.ai_service import (
    generate_platform_content, 
    refine_content, 
    regenerate_platform_content,
    regenerate_image
)

router = APIRouter(prefix="/api", tags=["ai"])
limiter = Limiter(key_func=get_remote_address)


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500, description="Topic for content generation")
    tone: str = "casual"
    image_style: str = "realistic"
    generate_image: bool = True
    use_prompt_enhancer: bool = True
    image_provider: str = "dalle"  # "dalle" or "nano-banana"
    
    @validator('topic')
    def validate_topic(cls, v):
        if not v or not v.strip():
            raise ValueError('Topic cannot be empty')
        # Remove excessive whitespace
        v = ' '.join(v.split())
        if len(v) > 500:
            raise ValueError('Topic too long (maximum 500 characters)')
        return v
    
    @validator('tone')
    def validate_tone(cls, v):
        valid_tones = ['casual', 'professional', 'corporate', 'funny', 'inspirational', 'educational', 'storytelling', 'promotional']
        if v not in valid_tones:
            raise ValueError(f'Invalid tone. Must be one of: {", ".join(valid_tones)}')
        return v
    
    @validator('image_style')
    def validate_image_style(cls, v):
        valid_styles = ['realistic', 'minimal', 'anime', '2d', 'comics', 'sketch', 'vintage', 'disney']
        if v not in valid_styles:
            raise ValueError(f'Invalid image style. Must be one of: {", ".join(valid_styles)}')
        return v
    
    @validator('image_provider')
    def validate_image_provider(cls, v):
        valid_providers = ['dalle', 'nano-banana']
        if v not in valid_providers:
            raise ValueError(f'Invalid image provider. Must be one of: {", ".join(valid_providers)}')
        return v


class RegenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    platform: str
    tone: str = "casual"
    previous_content: str = ""
    
    @validator('topic')
    def validate_topic(cls, v):
        if not v or not v.strip():
            raise ValueError('Topic cannot be empty')
        return ' '.join(v.split())
    
    @validator('platform')
    def validate_platform(cls, v):
        valid_platforms = ['facebook', 'instagram', 'twitter', 'reddit']
        if v not in valid_platforms:
            raise ValueError(f'Invalid platform. Must be one of: {", ".join(valid_platforms)}')
        return v


class RegenerateImageRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    tone: str = "casual"
    image_style: str = "realistic"
    image_provider: str = "dalle"  # "dalle" or "nano-banana"
    
    @validator('topic')
    def validate_topic(cls, v):
        if not v or not v.strip():
            raise ValueError('Topic cannot be empty')
        return ' '.join(v.split())


class RefineRequest(BaseModel):
    original_content: str = Field(..., min_length=1, max_length=5000)
    platform: str
    instructions: str = Field(..., min_length=1, max_length=500)
    
    @validator('platform')
    def validate_platform(cls, v):
        valid_platforms = ['facebook', 'instagram', 'twitter', 'reddit']
        if v not in valid_platforms:
            raise ValueError(f'Invalid platform. Must be one of: {", ".join(valid_platforms)}')
        return v


@router.post("/generate-content")
@limiter.limit("10/minute")  # Max 10 AI generations per minute
async def generate_content(request: GenerateRequest, http_request: Request):
    """
    Generate platform-specific content for all social media platforms with optional image
    Automatically enhances user prompts for better results
    Rate limited: 10 requests per minute
    """
    try:
        result = await generate_platform_content(
            topic=request.topic,
            tone=request.tone,
            image_style=request.image_style,
            generate_image=request.generate_image,
            use_prompt_enhancer=request.use_prompt_enhancer,
            image_provider=request.image_provider
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate content: {str(e)}"
        )


@router.post("/regenerate-content")
@limiter.limit("20/minute")  # More lenient for regeneration
async def regenerate_content(request: RegenerateRequest, http_request: Request):
    """
    Regenerate content for a specific platform
    Rate limited: 20 requests per minute
    """
    try:
        result = await regenerate_platform_content(
            topic=request.topic,
            platform=request.platform,
            tone=request.tone,
            previous_content=request.previous_content
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate content: {str(e)}"
        )


@router.post("/regenerate-image")
@limiter.limit("15/minute")  # Image regeneration limit
async def regenerate_image_endpoint(request: RegenerateImageRequest, http_request: Request):
    """
    Regenerate a new image with selected provider (DALL-E 3 or Nano Banana)
    Rate limited: 15 requests per minute
    """
    try:
        result = await regenerate_image(
            topic=request.topic,
            tone=request.tone,
            image_style=request.image_style,
            image_provider=request.image_provider
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate image: {str(e)}"
        )


@router.post("/refine-content")
@limiter.limit("30/minute")  # More lenient for content refinement
async def refine_post_content(request: RefineRequest, http_request: Request):
    """
    Refine existing content based on user instructions
    Rate limited: 30 requests per minute
    """
    try:
        result = await refine_content(
            original_content=request.original_content,
            platform=request.platform,
            instructions=request.instructions
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refine content: {str(e)}"
        )

