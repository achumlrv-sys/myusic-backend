from fastapi import FastAPI, HTTPException
from ytmusicapi import YTMusic
import yt_dlp

app = FastAPI()
yt = YTMusic()

@app.get("/api/search")
def search_yt(query: str):
    try:
        # Search specifically for songs to keep the data clean
        results = yt.search(query, filter="songs", limit=15)
        formatted = []
        
        for item in results:
            if 'videoId' in item:
                # Map it to match your Flutter Song model exactly
                formatted.append({
                    "id": item['videoId'],
                    "title": item['title'],
                    "artist": ", ".join([a['name'] for a in item.get('artists', [])]),
                    "album": item.get('album', {}).get('name', 'YouTube') if item.get('album') else 'YouTube',
                    "imageUrl": item['thumbnails'][-1]['url'] if item.get('thumbnails') else '',
                    "audioUrl": "" # Fetched later on tap
                })
        return {"success": True, "data": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stream")
def get_stream(video_id: str):
    try:
        # Force the extractor to only look for m4a/aac audio to prevent Android crashes
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'quiet': True,
            'simulate': True,
            'noplaylist': True,
            'cachedir': False,
            # THE BYPASS: Disguise the request as an official mobile app to dodge the bot block
            'extractor_args': {
                'youtube': ['client=IOS,ANDROID']
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return {"success": True, "url": info['url']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
