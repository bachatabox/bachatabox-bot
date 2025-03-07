import telebot
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Configurar claves de API
TELEGRAM_BOT_TOKEN = "tu_telegram_bot_token"
SPOTIPY_CLIENT_ID = "tu_spotify_client_id"
SPOTIPY_CLIENT_SECRET = "tu_spotify_client_secret"
SPOTIPY_REDIRECT_URI = "http://localhost:8080/callback"

# Inicializar bot de Telegram
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Configurar autenticación de Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-modify-playback-state,user-read-playback-state"
))

# Lista de canciones preseleccionadas
song_options = {
    "1": "Blinding Lights - The Weeknd",
    "2": "Levitating - Dua Lipa",
    "3": "Taki Taki - DJ Snake",
    "4": "Bachata - Manuel Turizo"
}

# Diccionario para almacenar votos
votes = {}

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "¡Bienvenido a Bachatabox! 🎶 Vota por la próxima canción escribiendo el número:\n"
    for key, song in song_options.items():
        welcome_text += f"{key}. {song}\n"
    bot.send_message(message.chat.id, welcome_text)

# Manejar votos
@bot.message_handler(func=lambda message: message.text in song_options.keys())
def vote_song(message):
    user_id = message.from_user.id
    votes[user_id] = message.text  # Guardar la elección del usuario
    bot.send_message(message.chat.id, f"✅ Voto registrado: {song_options[message.text]}")

# Comando /play para reproducir la canción más votada
@bot.message_handler(commands=['play'])
def play_most_voted_song(message):
    if not votes:
        bot.send_message(message.chat.id, "❌ No hay votos aún. ¡Vota con un número!")
        return

    # Contar votos y seleccionar la canción más votada
    song_counts = {}
    for vote in votes.values():
        song_counts[vote] = song_counts.get(vote, 0) + 1

    most_voted = max(song_counts, key=song_counts.get)
    selected_song = song_options[most_voted]

    # Buscar canción en Spotify y reproducirla
    results = sp.search(q=selected_song, limit=1, type='track')
    if results["tracks"]["items"]:
        track_uri = results["tracks"]["items"][0]["uri"]
        sp.start_playback(uris=[track_uri])
        bot.send_message(message.chat.id, f"▶️ Reproduciendo ahora: {selected_song}")
    else:
        bot.send_message(message.chat.id, "❌ No se encontró la canción en Spotify.")

# Iniciar el bot
bot.polling()
