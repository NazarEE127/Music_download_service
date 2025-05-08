from flask_restful import Api, Resource
from flask import Flask, jsonify
from config import YANDEX_MUSIC_TOKEN
from yandex_music import Client
import os
import requests

app = Flask(__name__)
api = Api(app)
client = Client(YANDEX_MUSIC_TOKEN).init()


def format_duration(ms):
    total_seconds = int(ms / 1000)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


class MusicResourse(Resource):
    def get(self, user_track):
        search_result = client.search(user_track, type_='track', nocorrect=True)
        tracks = search_result.tracks.results
        track = tracks[0]
        filename = f"temp\{track.artists[0].name}-{track.title}.mp3"
        if os.path.exists(filename):
            os.remove(filename)
        track.download(filename)
        return jsonify({
            "response": "OK", 
            "filename": filename,
            "duration": format_duration(track.duration_ms)
        })


class MusicAlbumResourse(Resource):
    def get(self, user_album):
        search_result = client.search(user_album, type_='album', nocorrect=True)
        albums = search_result.albums.results
        album = albums[0]
        
        album_info = {
            "title": album.title,
            "artists": [artist.name for artist in album.artists],
            "year": album.year,
            "genre": album.genre,
            "cover": album.cover_uri.replace('%%', '300x300'),
            "tracks": []
        }
        
        tracks = client.albums_with_tracks(album.id)
        if tracks and hasattr(tracks, 'volumes'):
            for volume in tracks.volumes:
                for track in volume:
                    track_info = {
                        "title": track.title,
                        "artists": [artist.name for artist in track.artists],
                        "duration": format_duration(track.duration_ms),
                        "id": track.id
                    }
                    album_info["tracks"].append(track_info)
        
        return jsonify({
            "response": "OK",
            "album_info": album_info
        })


class SimilarTracksResource(Resource):
    def get(self, track):
        search_result = client.search(track, type_='track', nocorrect=True)
        if not search_result.tracks or not search_result.tracks.results:
            return jsonify({"error": "Трек не найден"}), 404
            
        original_track = search_result.tracks.results[0]
        original_artist = original_track.artists[0]
        
        similar_tracks = []

        artist_tracks = client.artists_tracks(original_artist.id, page=0, page_size=5)
        if artist_tracks and artist_tracks.tracks:
            for track in artist_tracks.tracks:
                if track.id != original_track.id:
                    similar_tracks.append({
                        "title": track.title,
                        "artists": [artist.name for artist in track.artists],
                        "duration": format_duration(track.duration_ms),
                        "id": track.id,
                        "cover": f"https://{track.cover_uri.replace('%%', '300x300')}" if hasattr(track, 'cover_uri') else None,
                        "link": f"https://music.yandex.ru/track/{track.id}"
                    })
                    break

        title_tracks = client.search(text=original_track.title, type_='track', nocorrect=True)
        if title_tracks and title_tracks.tracks:
            for track in title_tracks.tracks.results:
                if track.id != original_track.id and track.artists[0].id != original_artist.id:
                    if not any(t['id'] == track.id for t in similar_tracks):
                        similar_tracks.append({
                            "title": track.title,
                            "artists": [artist.name for artist in track.artists],
                            "duration": format_duration(track.duration_ms),
                            "id": track.id,
                            "cover": f"https://{track.cover_uri.replace('%%', '300x300')}" if hasattr(track, 'cover_uri') else None,
                            "link": f"https://music.yandex.ru/track/{track.id}"
                        })
                        if len(similar_tracks) >= 5:
                            break
        
        return jsonify({
            "response": "OK",
            "original_track": {
                "title": original_track.title,
                "artists": [artist.name for artist in original_track.artists],
                "duration": format_duration(original_track.duration_ms),
                "id": original_track.id,
                "cover": f"https://{original_track.cover_uri.replace('%%', '300x300')}" if hasattr(original_track, 'cover_uri') else None,
                "link": f"https://music.yandex.ru/track/{original_track.id}"
            },
            "similar_tracks": similar_tracks[:5]
        })


class AIChoiceTracksResourse(Resource):
    def get(self, tracks):
        prompt = {
            "modelUri": "gpt://b1gv60cikrkjbv24gd2e/yandexgpt",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": "2000"
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты — музыкальный эксперт, который специализируется на поиске реально существующих треков в Яндекс.Музыке. "
                            "Твоя задача — найти похожие треки, которые точно существуют в каталоге Яндекс.Музыки. "
                            "Важные правила:"
                            "1. Рекомендуй только реально существующие треки, которые можно найти в Яндекс.Музыке"
                            "2. Используй только актуальных исполнителей и их реальные треки"
                            "3. Формат ответа: каждая строка должна быть в формате 'Номер. Исполнитель - Название трека'"
                            "4. Не придумывай несуществующие треки"
                            "5. Если не уверен в существовании трека, не включай его в рекомендации"
                            "6. Рекомендуй треки того же жанра и стиля"
                            "7. Учитывай популярность и актуальность треков"
                },
                {
                    "role": "user",
                    "text": f"Найди 10 похожих треков для следующих треков: {tracks}. "
                            f"Убедись, что все рекомендованные треки реально существуют в Яндекс.Музыке. "
                            f"Выдай ответ строго в формате:"
                            f"1. Исполнитель - Название трека"
                            f"2. Исполнитель - Название трека"
                            f"и так далее..."
                }
            ]
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key AQVN2XcYp7xb_DnkSPEp7VG_1vJPYY6Ju5f5IvZh"
        }

        response = requests.post(url, headers=headers, json=prompt)
        result = response.json()["result"]["alternatives"][0]["message"]['text']
        if not result:
            return {"error": "ничего не нашлось"}
            
        ai_recommendations = []
        for res in result.split("\n"):
            if ". " in res:
                track_info = res.split(". ")[1]
                ai_recommendations.append(track_info)
        
        verified_tracks = []
        for track in ai_recommendations:
            try:
                search_result = client.search(track, type_='track', nocorrect=True)
                if search_result.tracks and search_result.tracks.results:
                    track_info = search_result.tracks.results[0]
                    verified_tracks.append({
                        "title": track_info.title,
                        "artists": [artist.name for artist in track_info.artists],
                        "duration": format_duration(track_info.duration_ms),
                        "id": track_info.id,
                        "cover": f"https://{track_info.cover_uri.replace('%%', '300x300')}" if hasattr(track_info, 'cover_uri') else None,
                        "link": f"https://music.yandex.ru/track/{track_info.id}"
                    })
            except Exception as e:
                print(f"Ошибка при поиске трека {track}: {str(e)}")
                continue
                
        return jsonify({
            "response": "OK",
            "recommendations": verified_tracks[:5]
        })


api.add_resource(MusicResourse, '/api/v1/track/<string:user_track>')
api.add_resource(MusicAlbumResourse, '/api/v1/album/<string:user_album>')
api.add_resource(SimilarTracksResource, '/api/v1/similar/<string:track>')
api.add_resource(AIChoiceTracksResourse, '/api/v1/AI_tracks/<string:tracks>')


if __name__ == '__main__':
    app.run(debug=True)
