"""
Unit tests for AI content and image generation
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, Mock
import json


class TestAIContentGeneration:
    """Test AI content generation functionality"""
    
    @pytest.mark.asyncio
    async def test_generate_platform_content_success(self, mock_openai_response, mock_dalle_response):
        """Test successful content generation"""
        from app.services.ai_service import generate_platform_content
        
        with patch('app.services.ai_service.client') as mock_client, \
             patch('app.services.ai_service.httpx.AsyncClient') as mock_httpx:
            
            # Mock OpenAI response
            mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
            mock_client.images.generate = AsyncMock(return_value=mock_dalle_response)
            
            # Mock image download
            mock_httpx_instance = AsyncMock()
            mock_httpx_instance.__aenter__.return_value.get = AsyncMock(
                return_value=Mock(content=b'fake_image_data')
            )
            mock_httpx.return_value = mock_httpx_instance
            
            result = await generate_platform_content(
                topic="Test topic",
                tone="casual",
                image_style="minimal",
                image_provider="dalle"
            )
            
            assert "facebook" in result
            assert "instagram" in result
            assert "twitter" in result
            assert "reddit" in result
            assert "image_path" in result
            assert result["facebook"] == "Test Facebook post content"
    
    @pytest.mark.asyncio
    async def test_generate_with_nano_banana(self, mock_fal_response):
        """Test image generation with Nano Banana"""
        from app.services.ai_service import generate_platform_content
        
        with patch('app.services.ai_service.client') as mock_client, \
             patch('app.services.ai_service.fal_client') as mock_fal, \
             patch('app.services.ai_service.httpx.AsyncClient') as mock_httpx:
            
            # Mock content generation
            mock_client.chat.completions.create = AsyncMock(
                return_value=MagicMock(
                    choices=[MagicMock(
                        message=MagicMock(
                            content=json.dumps({
                                "facebook": "FB content",
                                "instagram": "IG content",
                                "twitter": "Tweet",
                                "reddit": "Reddit post"
                            })
                        )
                    )]
                )
            )
            
            # Mock Fal.ai response
            mock_fal.subscribe = MagicMock(return_value=mock_fal_response)
            
            # Mock image download
            mock_httpx_instance = AsyncMock()
            mock_httpx_instance.__aenter__.return_value.get = AsyncMock(
                return_value=Mock(content=b'fake_image_data')
            )
            mock_httpx.return_value = mock_httpx_instance
            
            result = await generate_platform_content(
                topic="Test",
                tone="casual",
                image_style="minimal",
                image_provider="nano-banana"
            )
            
            assert "image_path" in result
            assert all(platform in result for platform in ["facebook", "instagram", "twitter", "reddit"])
    
    @pytest.mark.asyncio
    async def test_generate_all_tones(self, mock_openai_response, mock_dalle_response):
        """Test generation with all available tones"""
        from app.services.ai_service import generate_platform_content
        
        tones = ["casual", "professional", "corporate", "funny", 
                 "inspirational", "educational", "storytelling", "promotional"]
        
        for tone in tones:
            with patch('app.services.ai_service.client') as mock_client, \
                 patch('app.services.ai_service.httpx.AsyncClient') as mock_httpx:
                
                mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
                mock_client.images.generate = AsyncMock(return_value=mock_dalle_response)
                
                mock_httpx_instance = AsyncMock()
                mock_httpx_instance.__aenter__.return_value.get = AsyncMock(
                    return_value=Mock(content=b'fake_image_data')
                )
                mock_httpx.return_value = mock_httpx_instance
                
                result = await generate_platform_content(
                    topic="Test",
                    tone=tone,
                    image_style="minimal",
                    image_provider="dalle"
                )
                
                assert "facebook" in result
    
    @pytest.mark.asyncio
    async def test_generate_all_image_styles(self, mock_openai_response, mock_dalle_response):
        """Test generation with all available image styles"""
        from app.services.ai_service import generate_platform_content
        
        styles = ["realistic", "minimal", "anime", "2d", 
                  "comics", "sketch", "vintage", "disney"]
        
        for style in styles:
            with patch('app.services.ai_service.client') as mock_client, \
                 patch('app.services.ai_service.httpx.AsyncClient') as mock_httpx:
                
                mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
                mock_client.images.generate = AsyncMock(return_value=mock_dalle_response)
                
                mock_httpx_instance = AsyncMock()
                mock_httpx_instance.__aenter__.return_value.get = AsyncMock(
                    return_value=Mock(content=b'fake_image_data')
                )
                mock_httpx.return_value = mock_httpx_instance
                
                result = await generate_platform_content(
                    topic="Test",
                    tone="casual",
                    image_style=style,
                    image_provider="dalle"
                )
                
                assert "image_path" in result
    
    @pytest.mark.asyncio
    async def test_regenerate_image(self, mock_dalle_response):
        """Test image regeneration"""
        from app.services.ai_service import regenerate_image
        
        with patch('app.services.ai_service.client') as mock_client, \
             patch('app.services.ai_service.httpx.AsyncClient') as mock_httpx:
            
            mock_client.images.generate = AsyncMock(return_value=mock_dalle_response)
            
            mock_httpx_instance = AsyncMock()
            mock_httpx_instance.__aenter__.return_value.get = AsyncMock(
                return_value=Mock(content=b'fake_image_data')
            )
            mock_httpx.return_value = mock_httpx_instance
            
            result = await regenerate_image(
                image_prompt="Test prompt",
                image_style="minimal",
                image_provider="dalle"
            )
            
            assert result.startswith("uploads/ai_generated/")
            assert result.endswith(".png")


class TestStyleConfiguration:
    """Test style configuration utilities"""
    
    def test_get_tone_guidelines(self):
        """Test tone guidelines retrieval"""
        from app.services.ai.style_config import get_tone_guidelines
        
        guidelines = get_tone_guidelines()
        
        assert isinstance(guidelines, dict)
        assert "casual" in guidelines
        assert "professional" in guidelines
        assert "corporate" in guidelines
        assert len(guidelines) == 8
    
    def test_get_style_prompts(self):
        """Test style prompts retrieval"""
        from app.services.ai.style_config import get_style_prompts
        
        prompts = get_style_prompts()
        
        assert isinstance(prompts, dict)
        assert "realistic" in prompts
        assert "minimal" in prompts
        assert "anime" in prompts
        assert len(prompts) == 8
    
    def test_get_platform_configs(self):
        """Test platform configuration retrieval"""
        from app.services.ai.style_config import get_platform_configs
        
        configs = get_platform_configs()
        
        assert "facebook" in configs
        assert "instagram" in configs
        assert "twitter" in configs
        assert "reddit" in configs
        
        # Check Instagram has hashtag limit
        assert configs["instagram"]["hashtag_limit"] == 30
        
        # Check Twitter has character limit
        assert configs["twitter"]["max_length"] == 280


class TestPromptEnhancement:
    """Test prompt enhancement functionality"""
    
    @pytest.mark.asyncio
    async def test_enhance_prompt(self, mock_openai_response):
        """Test prompt enhancement"""
        from app.services.ai_service import enhance_user_prompt
        
        with patch('app.services.ai_service.client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(
                message=MagicMock(
                    content="CONTENT PROMPT: Enhanced content prompt\n\nIMAGE PROMPT: Enhanced image prompt"
                )
            )]
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            
            result = await enhance_user_prompt(
                user_prompt="Test topic",
                tone="casual",
                image_style="minimal"
            )
            
            assert "enhanced_content_prompt" in result
            assert "enhanced_image_prompt" in result

