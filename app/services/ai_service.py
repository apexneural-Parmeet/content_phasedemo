"""
AI content generation service using OpenAI
"""
import httpx
import os
import uuid
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import settings

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

# Directory for AI-generated images
AI_IMAGES_DIR = Path("uploads/ai_generated")
AI_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


async def enhance_user_prompt(user_prompt: str, tone: str, image_style: str) -> dict:
    """
    Enhance user's basic prompt into optimized prompts for content and image generation
    
    Args:
        user_prompt: The user's basic topic/idea
        tone: Selected tone (casual, professional, corporate, etc.)
        image_style: Selected image style (realistic, anime, minimal, etc.)
        
    Returns:
        dict: Enhanced prompts for content and image generation
    """
    if not client:
        # If no OpenAI key, return original prompt
        return {
            "content_prompt": user_prompt,
            "image_prompt": user_prompt,
            "original_prompt": user_prompt,
            "enhanced": False
        }
    
    # Detailed tone guidelines for content
    tone_guidelines = {
        "casual": "friendly, conversational, relatable language with warmth and approachability. Use everyday language, personal anecdotes, and create connection.",
        "professional": "formal, authoritative, business-appropriate language with expertise and credibility. Use industry terminology, data-driven insights, and professional tone.",
        "corporate": "ULTRA-MINIMAL text - only 1-2 sentences maximum. Think Apple/Tesla minimalism. Clean, simple, impactful language with NO fluff, NO hashtags, NO emojis. Pure sophistication.",
        "funny": "hilarious, witty, entertaining language with humor and comedic timing. Use jokes, puns, pop culture references, and make people laugh out loud.",
        "inspirational": "motivational, uplifting, empowering language with emotional depth. Use powerful quotes, success stories, and drive action through inspiration.",
        "educational": "informative, teaching-focused, clear explanations with valuable insights. Use step-by-step guidance, facts, and help audience learn.",
        "storytelling": "narrative-driven, emotional, engaging story structure with character and plot. Use story arcs, emotional hooks, and compelling narratives.",
        "promotional": "persuasive, sales-focused, action-oriented language with urgency. Use strong CTAs, benefits-focused messaging, and create FOMO."
    }
    
    # Detailed image style guidelines for DALL-E
    image_style_guidelines = {
        "realistic": "PHOTOREALISTIC style: Professional photography quality with real-world textures, natural lighting, authentic details, high-resolution clarity, lifelike colors, and camera-shot composition. Like a professional photographer's work.",
        "minimal": "ULTRA-MINIMALIST style: Clean white/neutral backgrounds, single focal subject, MAXIMUM negative space, Apple-style simplicity, geometric precision, NO text overlays, NO clutter. Think Apple product ads - pure, clean, sophisticated.",
        "anime": "JAPANESE ANIME style: Vibrant cel-shaded colors, manga-inspired character designs, dynamic action poses, expressive large eyes, clean outlined illustration, colorful backgrounds, Japanese animation aesthetic. Think Studio Ghibli or popular anime series.",
        "2d": "FLAT 2D ILLUSTRATION style: Modern vector graphics, geometric shapes, flat colors without gradients, clean lines, contemporary graphic design, minimalist illustration approach. Think modern app design or infographics.",
        "comics": "COMIC BOOK ART style: Bold black outlines, dynamic action panels, speech bubble aesthetic (no actual text), vibrant primary colors, dramatic shading, graphic novel atmosphere, superhero comic aesthetic.",
        "sketch": "HAND-DRAWN SKETCH style: Pencil or charcoal sketch appearance, artistic linework, sketchy textures, visible pencil strokes, artistic imperfection, raw creative energy, hand-crafted feel.",
        "vintage": "VINTAGE RETRO style: 1950s-1980s aesthetic, aged paper texture, retro color palette (muted oranges, browns, creams), classic poster design, nostalgic feel, old-school typography style, weathered look.",
        "disney": "DISNEY PIXAR style: 3D animated cartoon aesthetic, whimsical character design, bright cheerful colors, rounded friendly shapes, Pixar-quality 3D rendering, family-friendly warm atmosphere."
    }
    
    try:
        # Create enhanced, detailed prompt
        enhancement_prompt = f"""You are a MASTER prompt engineer specializing in viral social media content and stunning AI image generation. You transform basic ideas into professional, highly-detailed prompts.

USER'S BASIC IDEA: "{user_prompt}"

SELECTED TONE: {tone}
TONE REQUIREMENTS: {tone_guidelines.get(tone, 'engaging and authentic')}

SELECTED IMAGE STYLE: {image_style}
IMAGE STYLE REQUIREMENTS: {image_style_guidelines.get(image_style, 'professional quality')}

YOUR MISSION:
Create TWO highly-detailed, professional prompts that will generate EXCEPTIONAL results:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CONTENT PROMPT (for social media text generation):
Transform the basic idea into a RICH, DETAILED prompt that captures:
   - Main message and key themes
   - Specific emotions to evoke
   - Target audience considerations
   - Platform-specific best practices (Facebook: conversational; Instagram: visual focus; Twitter: concise; Reddit: authentic)
   - Tone-specific requirements (see TONE REQUIREMENTS above)
   - Engagement hooks and call-to-action approach
   - Content structure and flow
   
Make it SPECIFIC and ACTIONABLE - not just "create a post about X" but "create a {tone} post that [specific detailed instructions]"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. IMAGE PROMPT (for DALL-E 3 generation):
Transform the basic idea into an EXTREMELY DETAILED visual description:
   - Exact subject/scene description
   - Precise composition and framing (rule of thirds, centered, asymmetric, etc.)
   - Specific colors and color palette
   - Detailed lighting description (natural light, studio lighting, golden hour, dramatic shadows, etc.)
   - Exact mood and atmosphere
   - Background and environmental details
   - Style-specific elements (see IMAGE STYLE REQUIREMENTS above)
   - Camera angle and perspective
   - Textures and materials
   - Any additional visual elements that enhance impact
   
Be HYPER-SPECIFIC about visual details. Instead of "a product", say "a sleek silver smartphone at 45-degree angle on white marble surface with soft shadows"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXAMPLES OF QUALITY:

BAD Content Prompt: "Create a post about coffee"
GOOD Content Prompt: "Create a warm, inspirational post about the ritual of morning coffee that evokes comfort and motivation. Focus on the sensory experience - rich aroma, warming first sip, peaceful morning moment. Target busy professionals who rely on coffee to start their day. Include themes of self-care, daily rituals, and small pleasures. Encourage audience to share their own coffee moments."

BAD Image Prompt: "Coffee cup"
GOOD Image Prompt: "Close-up of a pristine white ceramic coffee cup filled with freshly brewed dark coffee, steam rising gracefully, placed on rustic wooden table with natural morning sunlight streaming from left creating soft highlights and long shadows, scattered coffee beans artistically arranged, blurred green plant in background, warm earth-tone color palette with cream and brown accents, shallow depth of field, professional food photography style, cozy intimate atmosphere"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return ONLY valid JSON in this exact format:
{{
  "content_prompt": "your enhanced detailed content prompt here",
  "image_prompt": "your enhanced detailed image prompt here"
}}

NO other text, NO explanations, ONLY the JSON."""

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a MASTER prompt engineer with 10+ years of experience in viral social media marketing and AI art generation. 

Your expertise includes:
- Creating prompts that generate 10x more engagement
- Deep understanding of platform algorithms and audience psychology
- Expert knowledge of DALL-E 3's capabilities and optimal prompt structure
- Ability to transform vague ideas into crystal-clear, actionable instructions
- Mastery of visual composition, lighting, color theory, and artistic styles

Your prompts consistently produce professional-grade results that look like they were created by expert marketers and professional photographers/artists.

You ALWAYS provide extremely detailed, specific prompts - never vague or generic."""
                },
                {
                    "role": "user",
                    "content": enhancement_prompt
                }
            ],
            temperature=0.8,  # Slightly higher for more creative enhancements
            max_tokens=800  # More tokens for detailed prompts
        )
        
        # Parse the JSON response
        import json
        enhanced_data = json.loads(response.choices[0].message.content.strip())
        
        return {
            "content_prompt": enhanced_data.get("content_prompt", user_prompt),
            "image_prompt": enhanced_data.get("image_prompt", user_prompt),
            "original_prompt": user_prompt,
            "enhanced": True
        }
        
    except Exception as e:
        print(f"Prompt enhancement error: {e}")
        # Fallback to original prompt if enhancement fails
        return {
            "content_prompt": user_prompt,
            "image_prompt": user_prompt,
            "original_prompt": user_prompt,
            "enhanced": False,
            "error": str(e)
        }


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, Exception)),
    reraise=True
)
async def generate_image_with_dalle(prompt_style: str, topic: str, enhanced_image_prompt: str = None, content_context: str = None) -> dict:
    """
    Generate a high-quality social media image using DALL-E 3
    
    Args:
        prompt_style: Style additions based on tone
        topic: Original topic for context
        enhanced_image_prompt: Enhanced prompt from prompt enhancer (optional)
        content_context: Summary of generated content to ensure image matches (optional)
        
    Returns:
        dict: Image URL and local path
    """
    if not client:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    
    try:
        # Create a coordinated DALL-E prompt that matches the content
        if enhanced_image_prompt and content_context:
            # Best case: Use enhanced prompt + content context for maximum coordination
            image_prompt = f"{enhanced_image_prompt}. This should visually represent content that says: {content_context[:150]}. Style: {prompt_style}. Professional quality, suitable for social media."
        elif enhanced_image_prompt:
            # Use enhanced prompt
            image_prompt = f"{enhanced_image_prompt}. Style: {prompt_style}. Professional quality, suitable for social media."
        elif content_context:
            # Use content context to create a matching image
            image_prompt = f"Create a professional social media image that visually represents: {content_context[:200]}. About: {topic}. {prompt_style}. High quality, visually appealing."
        else:
            # Fallback: Simple, direct prompt
            image_prompt = f"Create a professional social media image about {topic}. {prompt_style}. High quality, visually appealing, suitable for social platforms."

        # Generate image with DALL-E 3
        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt[:4000],  # DALL-E has prompt limit
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        
        # Download and save the image locally
        async with httpx.AsyncClient() as http_client:
            img_response = await http_client.get(image_url)
            img_response.raise_for_status()
            
            # Save with unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_generated_{timestamp}_{uuid.uuid4().hex[:8]}.png"
            file_path = AI_IMAGES_DIR / filename
            
            with open(file_path, "wb") as f:
                f.write(img_response.content)
        
        return {
            "success": True,
            "image_url": image_url,
            "local_path": str(file_path),
            "filename": filename,
            "web_path": f"/uploads/ai_generated/{filename}"
        }
        
    except Exception as e:
        print(f"DALL-E generation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "image_url": None,
            "local_path": None
        }


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, Exception)),
    reraise=True
)
async def generate_image_with_fal(prompt_style: str, topic: str, enhanced_image_prompt: str = None, content_context: str = None) -> dict:
    """
    Generate image using Fal.ai Nano Banana - Ultra-fast, lightweight model
    
    Args:
        prompt_style: Style additions based on tone
        topic: Original topic
        enhanced_image_prompt: Enhanced prompt (optional)
        content_context: Content summary for coordination (optional)
        
    Returns:
        dict: Image URL and local path
    """
    if not settings.FAL_KEY:
        raise HTTPException(
            status_code=500,
            detail="Fal.ai API key not configured. Add FAL_KEY to .env file"
        )
    
    try:
        import fal_client
        import os as os_module
        
        # Set API key
        os_module.environ["FAL_KEY"] = settings.FAL_KEY
        
        # Create modern, clean prompt that avoids text generation issues
        # Nano Banana works best with clear, focused prompts without text requests
        
        base_quality = "high quality, modern, clean composition, professional photography, trending on social media, vibrant colors, well-lit, sharp focus, 4K resolution"
        no_text = "NO TEXT, NO WORDS, NO LETTERS, NO TYPOGRAPHY, visual only"
        
        if enhanced_image_prompt and content_context:
            # Extract key visual concepts from content
            visual_concept = content_context[:100].replace('"', '').replace("'", "")
            image_prompt = f"{enhanced_image_prompt}. Visual concept: {visual_concept}. {prompt_style}. {base_quality}. {no_text}"
        elif enhanced_image_prompt:
            image_prompt = f"{enhanced_image_prompt}. {prompt_style}. {base_quality}. {no_text}"
        elif content_context:
            # Focus on visual representation only
            visual_concept = content_context[:150].replace('"', '').replace("'", "")
            image_prompt = f"Modern social media visual about {topic}: {visual_concept}. {prompt_style}. {base_quality}. {no_text}"
        else:
            image_prompt = f"Modern, eye-catching social media visual about {topic}. {prompt_style}. {base_quality}. Contemporary aesthetic, minimalist when appropriate. {no_text}"
        
        print(f"🍌 Generating image with Nano Banana (Fal.ai)...")
        
        # Generate with Nano Banana
        result = fal_client.subscribe(
            "fal-ai/nano-banana",
            arguments={
                "prompt": image_prompt[:2000],
                "image_size": "square_hd",
                "num_inference_steps": 4,
                "num_images": 1
            }
        )
        
        # Get image URL
        image_url = result["images"][0]["url"]
        
        print(f"✅ Nano Banana image generated: {image_url}")
        
        # Download and save locally
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            img_response = await http_client.get(image_url)
            img_response.raise_for_status()
            
            # Save with unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            filename = f"ai_generated_{timestamp}_{unique_id}.png"
            filepath = AI_IMAGES_DIR / filename
            
            with open(filepath, "wb") as f:
                f.write(img_response.content)
        
        print(f"💾 Image saved: {filepath}")
        
        return {
            "success": True,
            "image_url": image_url,
            "local_path": str(filepath),
            "filename": filename,
            "web_path": f"/uploads/ai_generated/{filename}",
            "provider": "fal-ai",
            "model": "nano-banana"
        }
        
    except Exception as e:
        print(f"❌ Nano Banana error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Nano Banana image generation failed: {str(e)}"
        )


async def generate_platform_content(topic: str, tone: str = "casual", image_style: str = "realistic", generate_image: bool = True, use_prompt_enhancer: bool = True, image_provider: str = "dalle") -> dict:
    """
    Generate platform-specific content for all social media platforms
    
    Args:
        topic: What the post is about
        tone: Writing tone (casual, professional, funny, inspirational, educational, storytelling, promotional)
        image_style: Visual style for DALL-E (realistic, anime, 2d, comics, sketch, vintage, disney, 3d)
        generate_image: Whether to generate an image
        use_prompt_enhancer: Whether to enhance the user's prompt first (default: True)
        
    Returns:
        dict: Generated content for each platform
    """
    if not client:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI API key not configured"
        )
    
    # Step 1: Enhance the user's prompt if enabled
    enhanced_prompts = None
    if use_prompt_enhancer:
        enhanced_prompts = await enhance_user_prompt(topic, tone, image_style)
        content_topic = enhanced_prompts["content_prompt"]
        image_topic = enhanced_prompts["image_prompt"]
    else:
        content_topic = topic
        image_topic = topic
    
    # Platform-specific prompts
    platforms_info = {
        "facebook": {
            "max_length": 500 if tone != "corporate" else 150,
            "style": "conversational and friendly, can be longer" if tone != "corporate" else "ultra-brief, minimal, clean",
            "hashtags": "optional, 2-3 max" if tone != "corporate" else "NO hashtags"
        },
        "instagram": {
            "max_length": 400 if tone != "corporate" else 100,
            "style": "visual and engaging with emojis" if tone != "corporate" else "minimal caption, let image speak",
            "hashtags": "5-10 relevant hashtags" if tone != "corporate" else "1-2 minimal hashtags max"
        },
        "twitter": {
            "max_length": 260 if tone != "corporate" else 100,
            "style": "concise and punchy" if tone != "corporate" else "extremely brief and impactful",
            "hashtags": "1-3 hashtags" if tone != "corporate" else "NO hashtags"
        },
        "reddit": {
            "max_length": 300 if tone != "corporate" else 150,
            "style": "authentic and community-focused, no spam" if tone != "corporate" else "simple, direct, no fluff",
            "hashtags": "avoid hashtags, focus on genuine content"
        }
    }
    
    results = {}
    
    # STEP 1: Generate content FIRST for all platforms
    # Enhanced tone descriptions for content
    tone_instructions = {
        "casual": "Be conversational, friendly, and approachable like talking to a friend",
        "professional": "Be formal, polished, and business-appropriate with expertise",
        "corporate": "Be EXTREMELY brief and minimal. Use only 1-2 short sentences MAX. Clean, simple language. Think Apple or Tesla - minimal text, maximum impact. NO hashtags. NO emojis unless absolutely essential. Pure corporate minimalism.",
        "funny": "Be hilarious, witty, and entertaining with humor that makes people laugh out loud",
        "inspirational": "Be deeply motivational, uplifting, and empowering with powerful impact",
        "educational": "Be informative, clear, and teaching-focused with valuable insights",
        "storytelling": "Be narrative-driven, engaging, and emotionally compelling like a great story",
        "promotional": "Be persuasive, sales-focused, and action-oriented with strong call-to-action"
    }
    
    tone_instruction = tone_instructions.get(tone, "Be engaging and authentic")
    
    for platform, info in platforms_info.items():
        prompt = f"""Create a {tone} social media post about: {content_topic}

Platform: {platform.upper()}
Style: {info['style']}
Max length: {info['max_length']} characters
Hashtags: {info['hashtags']}

TONE INSTRUCTION: {tone_instruction}

Requirements:
- Make it HIGHLY engaging and scroll-stopping
- Optimize for {platform}'s specific audience
- Include appropriate emojis that enhance the message
- Return ONLY the post text, nothing else

Post:"""

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional social media content creator specializing in {platform}. Create engaging, authentic posts optimized for {platform}'s unique audience and format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            results[platform] = {
                "content": generated_text,
                "success": True,
                "character_count": len(generated_text)
            }
            
        except Exception as e:
            results[platform] = {
                "content": "",
                "success": False,
                "error": str(e)
            }
    
    # STEP 2: Generate image BASED ON the actual generated content
    # This ensures the image matches what the content is actually talking about
    image_data = None
    if generate_image:
        # Extract key themes from generated content to create a better image prompt
        content_summary = ""
        if results.get("facebook", {}).get("success"):
            # Use Facebook content as base since it's usually the most detailed
            content_summary = results["facebook"]["content"][:300]
        
        # Enhanced tone descriptions for image
        tone_styles = {
            "casual": "friendly and approachable, warm and inviting atmosphere",
            "professional": "sleek, corporate, and polished with sophisticated elegance",
            "corporate": "ultra-clean, minimalist corporate aesthetic, extreme simplicity with maximum impact",
            "funny": "hilarious, playful, vibrant and whimsical with comedic flair",
            "inspirational": "motivational, uplifting, dramatic and empowering with cinematic quality",
            "educational": "clear, informative, well-structured with visual learning elements",
            "storytelling": "narrative-driven, emotional, engaging with story-like composition",
            "promotional": "eye-catching, sales-focused, bold and attention-grabbing"
        }
        
        # Image style mappings for DALL-E
        style_prompts = {
            "realistic": "professional photography style, high quality, well-lit, sharp focus, beautiful composition, commercial photography aesthetic",
            "minimal": "ultra-minimalist design, clean white space, single focal point, Apple-style simplicity, corporate clean aesthetic, NO text overlays, pure visual impact, negative space emphasis",
            "anime": "Japanese anime art style, vibrant colors, cel-shaded illustration, manga-inspired",
            "2d": "flat 2D vector illustration, modern graphic design, clean shapes",
            "comics": "comic book art style, bold outlines, dynamic panels, graphic novel aesthetic",
            "sketch": "hand-drawn pencil sketch, artistic linework, sketchy texture",
            "vintage": "retro vintage style, nostalgic feel, classic poster design, aged aesthetic",
            "disney": "Disney Pixar animation style, 3D cartoon, whimsical character design"
        }
        
        tone_desc = tone_styles.get(tone, "clean and modern")
        style_desc = style_prompts.get(image_style, "photorealistic")
        combined_prompt = f"{style_desc}, {tone_desc}"
        
        # Create a coordinated image prompt that matches the content
        # If we have enhanced prompts, use them; otherwise use the topic + content summary
        coordinated_image_prompt = None
        if enhanced_prompts and enhanced_prompts.get("image_prompt"):
            coordinated_image_prompt = enhanced_prompts["image_prompt"]
        elif content_summary:
            # Create an image prompt that matches the actual content
            coordinated_image_prompt = f"Visual representation of: {topic}. Related to this content: {content_summary[:200]}"
        
        # Generate image that matches the content
        # Choose provider based on user selection with fallback
        image_data = None
        primary_provider = image_provider
        fallback_provider = "dalle" if image_provider == "nano-banana" else "nano-banana"
        
        try:
            if image_provider == "nano-banana":
                print("🍌 Using Nano Banana (Fal.ai) for ultra-fast image generation...")
                image_data = await generate_image_with_fal(
                    combined_prompt, 
                    topic,
                    enhanced_image_prompt=coordinated_image_prompt,
                    content_context=content_summary
                )
            else:
                print("🎨 Using DALL-E 3 for image generation...")
                image_data = await generate_image_with_dalle(
                    combined_prompt, 
                    topic,
                    enhanced_image_prompt=coordinated_image_prompt,
                    content_context=content_summary
                )
        except Exception as primary_error:
            # Fallback to alternative provider
            print(f"⚠️ {primary_provider} failed: {primary_error}. Trying fallback provider...")
            
            try:
                if fallback_provider == "nano-banana":
                    print("🍌 Fallback: Using Nano Banana...")
                    image_data = await generate_image_with_fal(
                        combined_prompt, 
                        topic,
                        enhanced_image_prompt=coordinated_image_prompt,
                        content_context=content_summary
                    )
                else:
                    print("🎨 Fallback: Using DALL-E 3...")
                    image_data = await generate_image_with_dalle(
                        combined_prompt, 
                        topic,
                        enhanced_image_prompt=coordinated_image_prompt,
                        content_context=content_summary
                    )
                print(f"✅ Successfully generated with fallback provider: {fallback_provider}")
            except Exception as fallback_error:
                print(f"❌ Both providers failed. Primary: {primary_error}, Fallback: {fallback_error}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Image generation failed with both providers. Primary ({primary_provider}): {str(primary_error)}, Fallback ({fallback_provider}): {str(fallback_error)}"
                )
    
    return {
        "success": True,
        "platforms": results,
        "image": image_data,
        "topic": topic,
        "tone": tone,
        "enhanced_prompts": enhanced_prompts if use_prompt_enhancer else None
    }


async def regenerate_image(topic: str, tone: str = "casual", image_style: str = "realistic", image_provider: str = "dalle") -> dict:
    """
    Regenerate a new image for the same topic with selected provider
    
    Args:
        topic: Original topic
        tone: Tone for styling
        image_style: Visual style (realistic, anime, 2d, comics, sketch, vintage, disney, 3d)
        image_provider: "dalle" or "nano-banana"
        
    Returns:
        dict: New image data
    """
    # Enhanced tone descriptions
    tone_styles = {
        "casual": "friendly and approachable, warm and inviting atmosphere",
        "professional": "sleek, corporate, and polished with sophisticated elegance",
        "corporate": "ultra-clean, minimalist corporate aesthetic, extreme simplicity with maximum impact",
        "funny": "hilarious, playful, vibrant and whimsical with comedic flair",
        "inspirational": "motivational, uplifting, dramatic and empowering with cinematic quality",
        "educational": "clear, informative, well-structured with visual learning elements",
        "storytelling": "narrative-driven, emotional, engaging with story-like composition",
        "promotional": "eye-catching, sales-focused, bold and attention-grabbing"
    }
    
    # Image style mappings for DALL-E
    style_prompts = {
        "realistic": "professional photography style, high quality, well-lit, sharp focus, beautiful composition, commercial photography aesthetic",
        "minimal": "ultra-minimalist design, clean white space, single focal point, Apple-style simplicity, corporate clean aesthetic, NO text overlays, pure visual impact, negative space emphasis",
        "anime": "Japanese anime art style, vibrant colors, cel-shaded illustration, manga-inspired",
        "2d": "flat 2D vector illustration, modern graphic design, clean shapes",
        "comics": "comic book art style, bold outlines, dynamic panels, graphic novel aesthetic",
        "sketch": "hand-drawn pencil sketch, artistic linework, sketchy texture",
        "vintage": "retro vintage style, nostalgic feel, classic poster design, aged aesthetic",
        "disney": "Disney Pixar animation style, 3D cartoon, whimsical character design"
    }
    
    tone_desc = tone_styles.get(tone, "clean and modern")
    style_desc = style_prompts.get(image_style, "photorealistic")
    combined_prompt = f"{style_desc}, {tone_desc}"
    
    # Choose provider based on user selection with fallback
    primary_provider = image_provider
    fallback_provider = "dalle" if image_provider == "nano-banana" else "nano-banana"
    
    try:
        if image_provider == "nano-banana":
            print(f"🍌 Regenerating image with Nano Banana...")
            return await generate_image_with_fal(combined_prompt, topic)
        else:
            print(f"🎨 Regenerating image with DALL-E 3...")
            return await generate_image_with_dalle(combined_prompt, topic)
    except Exception as primary_error:
        # Fallback to alternative provider
        print(f"⚠️ {primary_provider} failed during regeneration. Trying {fallback_provider}...")
        
        try:
            if fallback_provider == "nano-banana":
                print(f"🍌 Fallback: Regenerating with Nano Banana...")
                return await generate_image_with_fal(combined_prompt, topic)
            else:
                print(f"🎨 Fallback: Regenerating with DALL-E 3...")
                return await generate_image_with_dalle(combined_prompt, topic)
        except Exception as fallback_error:
            raise HTTPException(
                status_code=500,
                detail=f"Image regeneration failed with both providers. Primary ({primary_provider}): {str(primary_error)}, Fallback ({fallback_provider}): {str(fallback_error)}"
            )


async def regenerate_platform_content(topic: str, platform: str, tone: str = "casual", previous_content: str = "") -> dict:
    """
    Regenerate content for a single platform
    
    Args:
        topic: Original topic
        platform: Specific platform to regenerate
        tone: Writing tone
        previous_content: Previous content to avoid duplication
        
    Returns:
        dict: New generated content for the platform
    """
    if not client:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    
    platforms_info = {
        "facebook": {"max_length": 500, "style": "conversational and friendly", "hashtags": "2-3 max"},
        "instagram": {"max_length": 400, "style": "visual with emojis", "hashtags": "5-10 hashtags"},
        "twitter": {"max_length": 260, "style": "concise and punchy", "hashtags": "1-3 hashtags"},
        "reddit": {"max_length": 300, "style": "authentic, no spam", "hashtags": "avoid hashtags"}
    }
    
    info = platforms_info.get(platform, platforms_info["facebook"])
    
    prompt = f"""Create a {tone} social media post about: {topic}

Platform: {platform.upper()}
Style: {info['style']}
Max length: {info['max_length']} characters
Hashtags: {info['hashtags']}

IMPORTANT: Create a DIFFERENT version from this previous attempt:
{previous_content if previous_content else "N/A"}

Make it engaging and authentic. Return ONLY the post text:"""

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional social media content creator for {platform}. Create fresh, engaging alternatives."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.9,  # Higher for more variety
            max_tokens=300
        )
        
        generated_text = response.choices[0].message.content.strip()
        
        return {
            "success": True,
            "content": generated_text,
            "character_count": len(generated_text),
            "platform": platform
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate {platform} content: {str(e)}"
        )


async def refine_content(original_content: str, platform: str, instructions: str) -> dict:
    """
    Refine existing content based on user instructions
    
    Args:
        original_content: The current content
        platform: Target platform
        instructions: What to change
        
    Returns:
        dict: Refined content
    """
    if not client:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    
    prompt = f"""Original post for {platform}:
{original_content}

User wants: {instructions}

Rewrite the post incorporating the user's feedback. Keep it optimized for {platform}.
Return only the revised post text:"""

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful social media content editor. Refine posts based on user feedback while keeping them optimized for {platform}."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return {
            "success": True,
            "content": response.choices[0].message.content.strip()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refine content: {str(e)}"
        )

