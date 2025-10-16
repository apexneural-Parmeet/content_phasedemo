"""
Instagram posting service
"""
import httpx
import asyncio
import cloudinary.uploader
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings


async def get_instagram_account_info() -> tuple:
    """
    Get Instagram account information
    
    Returns:
        tuple: (instagram_account_id, username)
    """
    # Lazy import to avoid circular dependency
    from app.services.credentials_service import get_platform_credentials
    
    # Get credentials from storage first, fallback to env
    credentials = get_platform_credentials("instagram")
    account_id = credentials.get("account_id") if credentials else settings.INSTAGRAM_ACCOUNT_ID
    access_token = credentials.get("access_token") if credentials else settings.INSTAGRAM_ACCESS_TOKEN
    
    if not account_id:
        raise HTTPException(status_code=500, detail="Instagram Account ID not configured")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.INSTAGRAM_GRAPH_URL}/{account_id}",
                params={
                    "fields": "username",
                    "access_token": access_token
                }
            )
            response.raise_for_status()
            data = response.json()
            return account_id, data.get("username", "Instagram")
        except Exception as e:
            print(f"Error fetching Instagram info: {e}")
            return account_id, "Instagram"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def post_photo_to_instagram(image_path: str, caption: str) -> dict:
    """
    Post a photo with caption to Instagram using Cloudinary for hosting
    
    Args:
        image_path: Path to the image file
        caption: Caption text for the post
        
    Returns:
        dict: Response from Instagram API with post ID
    """
    try:
        # Lazy import to avoid circular dependency
        from app.services.credentials_service import get_platform_credentials
        
        # Get credentials from storage first, fallback to env
        credentials = get_platform_credentials("instagram")
        ig_account_id = credentials.get("account_id") if credentials else settings.INSTAGRAM_ACCOUNT_ID
        access_token = credentials.get("access_token") if credentials else settings.INSTAGRAM_ACCESS_TOKEN
        
        if not ig_account_id:
            raise Exception("Instagram Account ID not configured")
        if not access_token:
            raise Exception("Instagram Access Token not configured")

        # Upload to Cloudinary to get a permanent HTTPS URL
        if not all([settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET]):
            raise Exception("Cloudinary is not configured. Please set CLOUDINARY_* env vars.")

        upload_result = cloudinary.uploader.upload(
            image_path,
            folder=settings.CLOUDINARY_FOLDER,
            overwrite=True,
            resource_type="image"
        )
        public_image_url = upload_result.get("secure_url")
        if not public_image_url:
            raise Exception("Failed to obtain secure_url from Cloudinary upload")

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Create media container with image_url
            container_response = await client.post(
                f"{settings.INSTAGRAM_GRAPH_URL}/{ig_account_id}/media",
                data={
                    "image_url": public_image_url,
                    "caption": caption,
                    "access_token": access_token
                }
            )

            if container_response.status_code != 200:
                error_data = container_response.json() if container_response.text else {}
                print(f"Instagram container creation failed: {error_data}")
                raise Exception(f"Failed to create media container: {error_data}")

            container_data = container_response.json()
            container_id = container_data.get("id")
            if not container_id:
                raise Exception("No container ID returned from Instagram")

            # Poll container status until FINISHED (or fail after timeout)
            for _ in range(20):  # ~20 seconds max wait
                status_resp = await client.get(
                    f"{settings.INSTAGRAM_GRAPH_URL}/{container_id}",
                    params={
                        "fields": "status_code",
                        "access_token": access_token
                    }
                )
                status_resp.raise_for_status()
                status = status_resp.json().get("status_code")
                if status == "FINISHED":
                    break
                elif status in ("ERROR", "FAILED"):
                    raise Exception(f"Instagram media processing failed: {status}")
                await asyncio.sleep(1)

            # Publish the container
            publish_response = await client.post(
                f"{settings.INSTAGRAM_GRAPH_URL}/{ig_account_id}/media_publish",
                data={
                    "creation_id": container_id,
                    "access_token": access_token
                }
            )

            if publish_response.status_code != 200:
                error_data = publish_response.json() if publish_response.text else {}
                print(f"Instagram publish failed: {error_data}")
                raise Exception(f"Failed to publish media: {error_data}")

            result = publish_response.json()
            
            # Add media ID info (Instagram doesn't provide direct post URL easily)
            media_id = result.get("id")
            if media_id:
                result["media_id"] = media_id
                result["info"] = f"Media ID: {media_id}"
            
            return result

    except Exception as e:
        error_msg = str(e)
        print(f"Instagram posting error: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Instagram posting failed: {error_msg}")

