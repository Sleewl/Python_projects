import requests
import pandas as pd
import matplotlib.pyplot as plt
import getpass
from vkaudiotoken import get_kate_token
import time
from datetime import datetime

genre_map = {
    1: 'Rock',
    2: 'Pop',
    3: 'Rap & Hip-Hop',
    4: 'Easy Listening',
    5: 'House & Dance',
    6: 'Instrumental',
    7: 'Metal',
    8: 'Dubstep',
    10: 'Drum & Bass',
    11: 'Trance',
    12: 'Chanson',
    13: 'Ethnic',
    14: 'Acoustic & Vocal',
    15: 'Reggae',
    16: 'Classical',
    17: 'Indie Pop',
    18: 'Other',
    19: 'Speech',
    21: 'Alternative',
    22: 'Electropop & Disco',
    1001: 'Jazz & Blues'
}


def fetch_tracks(token, user_agent):
    url = "https://api.vk.com/method/audio.get"
    params = {
        "access_token": token,
        "v": "5.95",
        "count": 1000,
        "offset": 0
    }
    headers = {"User-Agent": user_agent}
    tracks = []
    while True:
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            if 'response' not in data or 'items' not in data['response']:
                print("Ошибка получения данных:", data.get('error', 'Неизвестная ошибка'))
                break
            items = data['response']['items']
            tracks.extend(items)
            print(f"Получено {len(items)} треков, всего: {len(tracks)}")
            if len(items) < 1000:
                break
            params['offset'] += 1000
            time.sleep(0.5)
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            break
    return tracks


def analyze_tracks(tracks):
    if not tracks:
        print("Нет треков для анализа.")
        return

    df = pd.DataFrame(tracks)

    required_columns = ['artist', 'title', 'duration', 'genre_id', 'date']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Отсутствуют столбцы: {missing_columns}")
        return

    df['genre_name'] = df['genre_id'].map(genre_map).fillna('Unknown')
    df['date'] = pd.to_datetime(df['date'], unit='s')

    total_tracks = len(df)
    total_duration = df['duration'].sum()
    avg_duration = df['duration'].mean()
    unique_artists = df['artist'].nunique()
    most_frequent_artist = df['artist'].mode()[0] if not df['artist'].empty else 'N/A'
    longest_track = df.loc[df['duration'].idxmax()] if not df.empty else None
    shortest_track = df.loc[df['duration'].idxmin()] if not df.empty else None

    print("\n Основные метрики:")
    print(f"Всего треков: {total_tracks}")
    print(f"Общая длительность: {total_duration // 3600} ч, {(total_duration % 3600) // 60} мин")
    print(f"Средняя длительность: {avg_duration:.2f} сек")
    print(f"Уникальных исполнителей: {unique_artists}")
    print(f"Самый частый исполнитель: {most_frequent_artist}")
    if longest_track is not None:
        print(
            f"Самый длинный трек: {longest_track['artist']} - {longest_track['title']} ({longest_track['duration']} сек)")
    if shortest_track is not None:
        print(
            f"Самый короткий трек: {shortest_track['artist']} - {shortest_track['title']} ({shortest_track['duration']} сек)")

    plt.style.use('seaborn')

    top_artists = df['artist'].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    top_artists.plot(kind='bar')
    plt.title('Топ-10 исполнителей по количеству треков')
    plt.xlabel('Исполнитель')
    plt.ylabel('Количество треков')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('top_artists.png')
    plt.close()

    plt.figure(figsize=(10, 6))
    df['duration'].plot(kind='hist', bins=30, edgecolor='black')
    plt.title('Распределение длительности треков')
    plt.xlabel('Длительность (секунды)')
    plt.ylabel('Частота')
    plt.tight_layout()
    plt.savefig('duration_distribution.png')
    plt.close()

    genre_counts = df['genre_name'].value_counts()
    plt.figure(figsize=(10, 8))
    genre_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140)
    plt.title('Распределение жанров')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig('genre_distribution.png')
    plt.close()

    monthly_counts = df['date'].dt.to_period('M').value_counts().sort_index()
    plt.figure(figsize=(12, 6))
    monthly_counts.plot(kind='line', marker='o')
    plt.title('Динамика добавления треков по месяцам')
    plt.xlabel('Месяц')
    plt.ylabel('Количество треков')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('tracks_over_time.png')
    plt.close()

    df.to_csv('vk_music_data.csv', index=False)
    print("\n Данные сохранены в 'vk_music_data.csv'")
    print(" Визуализации сохранены как PNG-файлы")


def main():
    print("🚀 Запуск анализатора музыки ВКонтакте")

    login = input("Введите логин ВКонтакте (телефон или email): ")
    password = getpass.getpass("Введите пароль ВКонтакте: ")

    try:
        token, user_agent = get_kate_token(login, password)
        print(" Токен успешно получен")
    except Exception as e:
        print(f" Ошибка получения токена: {e}")
        return

    tracks = fetch_tracks(token, user_agent)

    analyze_tracks(tracks)


if __name__ == "__main__":
    main()