import os
import datetime
import concurrent.futures
from googleapiclient.discovery import build
from flask import jsonify

# Configuración de la API de YouTube
api_key = os.getenv('GOOGLE_API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)

def get_video_details(video_id):
    """Obtiene detalles de un video (paralelizable)."""
    try:
        response = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()

        details = response['items'][0]
        stats = details.get('statistics', {})

        return {
            'title': details['snippet'].get('title', 'Sin título'),
            'description': details['snippet'].get('description', 'Sin descripción'),
            'thumbnails': details['snippet'].get('thumbnails', {}).get('medium', {}).get('url', ''),
            'keywords': details['snippet'].get('tags', []),
            'views': int(stats.get('viewCount', 0)),
            'likes': int(stats.get('likeCount', 0)),
            'comments': int(stats.get('commentCount', 0)),
            'video_url': f"https://www.youtube.com/watch?v={video_id}"
        }
    except Exception as e:
        print(f"[ERROR] No se pudo obtener detalles del video {video_id}: {str(e)}")
        return None

def get_youtube_videos(query):
    """Obtiene los 10 videos más populares en las últimas 24 horas en paralelo."""
    last_24_hours = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat("T") + "Z"

    print(f"[INFO] Buscando videos de las últimas 24 horas desde {last_24_hours}")

    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=10,
        order='viewCount',
        publishedAfter=last_24_hours,
        type='video'
    ).execute()

    video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]

    print(f"[INFO] Se encontraron {len(video_ids)} videos. Obteniendo detalles en paralelo...")

    video_data = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(get_video_details, video_ids)

    for result in results:
        if result:
            video_data.append(result)

    print(f"[INFO] Se procesaron {len(video_data)} videos correctamente.")
    return video_data
