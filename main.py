import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
import pytz
from flask import Flask, render_template, jsonify

app = Flask(__name__)

url = 'https://volt.fm/user/g8o6jt8dj9vsnwud'  # Gerçek sayfa URL'sini kullanın
json_file = 'song_data.json'


def load_json_data():
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # JSON dosyası yoksa boş liste başlat


def save_song_data(new_entry):
    json_data = load_json_data()

    if not json_data:
        json_data.append(new_entry)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print(f"Yeni şarkı eklendi: {new_entry}")
        return

    last_song = json_data[-1]
    if (last_song['song_name'] == new_entry['song_name'] and
            last_song['artist_names'] == new_entry['artist_names']):
        print("Şarkı zaten en son eklendiği için tekrar eklenmedi.")
    else:
        json_data.append(new_entry)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print(f"Yeni şarkı eklendi: {new_entry}")


def check_song_info():
    try:
        response = requests.get(url, timeout=10)  # Timeout ile istek
        soup = BeautifulSoup(response.text, 'html.parser')

        album_cover_div = soup.find(
            'div',
            class_='relative w-12 h-12 bg-cover bg-center rounded shadow-md group')
        album_cover_style = album_cover_div['style']
        album_cover_url = album_cover_style.split('url(')[-1].strip(')').strip('"')

        song_name_div = soup.find('div', class_='font-bold external-text')
        song_name = song_name_div.find('a').text.strip()

        artist_name_div = soup.find(
            'div', class_='font-bold text-gray-1000 external-text')
        artist_links = artist_name_div.find_all('a')
        artist_names = [artist.text.strip() for artist in artist_links]

        tz = pytz.timezone('Europe/Istanbul')
        current_timestamp = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

        song_data = {
            'song_name': song_name,
            'artist_names': artist_names,
            'album_cover_url': album_cover_url,
            'added_timestamp': current_timestamp
        }

        save_song_data(song_data)
    except requests.exceptions.RequestException as e:
        print(f"İstek sırasında hata oluştu: {e}")
    except Exception as e:
        print(f"Başka bir hata oluştu: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/songs')
def songs():
    json_data = load_json_data()
    return jsonify(json_data[::-1])


if __name__ == '__main__':
    def run_checking_loop():
        while True:
            try:
                check_song_info()
            except Exception as e:
                print(f"Döngü sırasında hata oluştu: {e}")
            time.sleep(30)  # 30 saniye bekleme süresi

    import threading
    threading.Thread(
        target=run_checking_loop,
        daemon=True).start()

    app.run(debug=True, host="0.0.0.0")
