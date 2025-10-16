"""
AI Content and Image Style Configuration
Tone guidelines and image style prompts for AI generation
"""

def get_tone_guidelines():
    """Get tone-specific content guidelines"""
    return {
        "casual": "friendly, conversational, relatable language with warmth and approachability. Use everyday language, personal anecdotes, and create connection.",
        "professional": "formal, authoritative, business-appropriate language with expertise and credibility. Use industry terminology, data-driven insights, and professional tone.",
        "corporate": "ULTRA-MINIMAL text - only 1-2 sentences maximum. Think Apple/Tesla minimalism. Clean, simple, impactful language with NO fluff, NO hashtags, NO emojis. Pure sophistication.",
        "funny": "hilarious, witty, entertaining language with humor and comedic timing. Use jokes, puns, pop culture references, and make people laugh out loud.",
        "inspirational": "motivational, uplifting, empowering language with emotional depth. Use powerful quotes, success stories, and drive action through inspiration.",
        "educational": "informative, teaching-focused, clear explanations with valuable insights. Use step-by-step guidance, facts, and help audience learn.",
        "storytelling": "narrative-driven, emotional, engaging story structure with character and plot. Use story arcs, emotional hooks, and compelling narratives.",
        "promotional": "persuasive, sales-focused, action-oriented language with urgency. Use strong CTAs, benefits-focused messaging, and create FOMO."
    }


def get_image_style_guidelines():
    """Get detailed image style descriptions for prompt enhancement"""
    return {
        "realistic": "PHOTOREALISTIC style: Professional photography quality with real-world textures, natural lighting, authentic details, high-resolution clarity, lifelike colors, and camera-shot composition. Like a professional photographer's work.",
        "minimal": "ULTRA-MINIMALIST style: Clean white/neutral backgrounds, single focal subject, MAXIMUM negative space, Apple-style simplicity, geometric precision, NO text overlays, NO clutter. Think Apple product ads - pure, clean, sophisticated.",
        "anime": "JAPANESE ANIME style: Vibrant cel-shaded colors, manga-inspired character designs, dynamic action poses, expressive large eyes, clean outlined illustration, colorful backgrounds, Japanese animation aesthetic. Think Studio Ghibli or popular anime series.",
        "2d": "FLAT 2D ILLUSTRATION style: Modern vector graphics, geometric shapes, flat colors without gradients, clean lines, contemporary graphic design, minimalist illustration approach. Think modern app design or infographics.",
        "comics": "COMIC BOOK ART style: Bold black outlines, dynamic action panels, speech bubble aesthetic (no actual text), vibrant primary colors, dramatic shading, graphic novel atmosphere, superhero comic aesthetic.",
        "sketch": "HAND-DRAWN SKETCH style: Pencil or charcoal sketch appearance, artistic linework, sketchy textures, visible pencil strokes, artistic imperfection, raw creative energy, hand-crafted feel.",
        "vintage": "VINTAGE RETRO style: 1950s-1980s aesthetic, aged paper texture, retro color palette (muted oranges, browns, creams), classic poster design, nostalgic feel, old-school typography style, weathered look.",
        "disney": "DISNEY PIXAR style: 3D animated cartoon aesthetic, whimsical character design, bright cheerful colors, rounded friendly shapes, Pixar-quality 3D rendering, family-friendly warm atmosphere."
    }


def get_style_prompts():
    """Get DALL-E specific style prompts"""
    return {
        "realistic": "professional photography style, high quality, well-lit, sharp focus, beautiful composition, commercial photography aesthetic",
        "minimal": "minimalist design, clean white background, single subject, maximum negative space, Apple product photography style, ultra-clean composition",
        "anime": "anime art style, manga illustration, vibrant colors, Japanese animation style, Studio Ghibli quality",
        "2d": "flat 2D illustration, modern vector art, clean geometric shapes, contemporary graphic design",
        "comics": "comic book art, graphic novel style, bold outlines, dynamic composition, superhero aesthetic",
        "sketch": "pencil sketch, hand-drawn illustration, artistic linework, sketchy texture",
        "vintage": "vintage 1970s aesthetic, retro colors, aged paper texture, nostalgic feel",
        "disney": "Disney Pixar 3D animation style, whimsical cartoon, bright colorful, family-friendly"
    }


def get_platform_configs():
    """Get platform-specific configuration"""
    return {
        "facebook": {
            "max_length": 63206,
            "supports_hashtags": True,
            "supports_mentions": True,
            "emoji_friendly": True
        },
        "instagram": {
            "max_length": 2200,
            "supports_hashtags": True,
            "supports_mentions": True,
            "emoji_friendly": True,
            "hashtag_limit": 30
        },
        "twitter": {
            "max_length": 280,
            "supports_hashtags": True,
            "supports_mentions": True,
            "emoji_friendly": True
        },
        "reddit": {
            "max_length": 40000,
            "supports_hashtags": False,
            "supports_mentions": True,
            "emoji_friendly": True
        }
    }

