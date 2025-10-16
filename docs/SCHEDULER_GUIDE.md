# 📅 Post Scheduler Feature

## Overview
The scheduler feature allows you to schedule social media posts for a specific date and time. Posts will be automatically published to your selected platforms at the scheduled time.

## Features

### ✨ Key Capabilities
- **Schedule Posts**: Set a specific date and time for your posts
- **View Scheduled Posts**: See all your upcoming scheduled posts in one place
- **Delete Scheduled Posts**: Cancel any scheduled post before it goes live
- **Multi-Platform Support**: Schedule posts for Facebook, Instagram, Twitter, and Reddit
- **Persistent Storage**: Scheduled posts survive server restarts
- **Auto-Cleanup**: Expired scheduled posts are automatically cleaned up

## How to Use

### 1. Schedule a Post

1. Fill in your post caption and upload an image
2. Select the platforms you want to post to
3. Toggle the **"Schedule Post"** switch
4. Select the **date** and **time** for your post
5. Click **"📅 Schedule Post"** button

### 2. View Scheduled Posts

All your scheduled posts appear in the **"📅 Scheduled Posts"** section below the main form. Each scheduled post shows:
- 📆 Scheduled date and time
- 📝 Post caption (truncated if long)
- 🌐 Selected platforms
- 🗑️ Delete button

### 3. Delete a Scheduled Post

Click the **🗑️** trash icon on any scheduled post to cancel and remove it.

## Technical Details

### Backend (Python/FastAPI)
- **Scheduler**: Uses APScheduler for background job scheduling
- **Storage**: Scheduled posts stored in `scheduled_posts.json`
- **Persistence**: Jobs restored on server restart
- **API Endpoints**:
  - `POST /api/post` - Create immediate or scheduled post
  - `GET /api/scheduled-posts` - List all scheduled posts
  - `DELETE /api/scheduled-posts/{post_id}` - Delete a scheduled post

### Frontend (React)
- **Date/Time Picker**: Native HTML5 date and time inputs
- **Toggle Switch**: Smooth animated toggle for scheduling mode
- **Real-time Updates**: Auto-refresh scheduled posts list
- **Responsive Design**: Works on desktop and mobile

## Installation

The scheduler feature requires APScheduler. Install dependencies:

```bash
pip install -r requirements.txt
```

## Important Notes

1. **Server Uptime**: The server must be running at the scheduled time for posts to be published
2. **Timezone**: Scheduled times are in your server's local timezone
3. **Minimum Time**: You can only schedule posts for future times (not past)
4. **Image Storage**: Uploaded images are stored until the post is published or deleted

## Example Usage

### Schedule a Post for Tomorrow at 9 AM
1. Write your caption: "Good morning! Here's today's update 🌅"
2. Upload your image
3. Enable "Schedule Post" toggle
4. Select tomorrow's date
5. Set time to 09:00
6. Click "Schedule Post"

Your post will automatically be published to all selected platforms at 9 AM tomorrow!

## Troubleshooting

**Post didn't publish at scheduled time**
- Ensure the server is running
- Check server logs for any errors
- Verify platform credentials are valid

**Can't schedule a post**
- Make sure the date/time is in the future
- Verify both date and time fields are filled
- Check that an image is uploaded

**Scheduled post disappeared**
- If scheduled time has passed, the post has been published or expired
- Check if it was manually deleted

## Future Enhancements (Potential)
- Recurring/repeating posts
- Timezone selection
- Email notifications when posts are published
- Draft posts (save without scheduling)
- Bulk scheduling from CSV
- Calendar view of scheduled posts

