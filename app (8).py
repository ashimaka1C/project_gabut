import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
import base64
import requests
from github import Github

# GitHub configuration
GITHUB_TOKEN = st.secrets.get("github_token", os.environ.get("GITHUB_TOKEN"))
REPO_NAME = "music-streaming-repo"
GITHUB_USER = "ashimaka1C"

# Initialize GitHub
g = Github(GITHUB_TOKEN)
user = g.get_user()

# Create repo if it doesn't exist
try:
    repo = user.get_repo(REPO_NAME)
except:
    repo = user.create_repo(
        name=REPO_NAME,
        description="Music Streaming Website",
        private=False,
        auto_init=True
    )

st.set_page_config(
    page_title="🎵 MusicFlow - GitHub Edition",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    h1, h2, h3 {
        color: white !important;
    }
    .song-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "songs" not in st.session_state:
    st.session_state.songs = []
if "playlists" not in st.session_state:
    st.session_state.playlists = {}
if "current_song" not in st.session_state:
    st.session_state.current_song = None
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# Helper functions
def load_from_github():
    """Load songs and playlists from GitHub"""
    try:
        # Load songs
        try:
            songs_file = repo.get_contents("data/songs.json")
            st.session_state.songs = json.loads(songs_file.decoded_content)
        except:
            st.session_state.songs = []
        
        # Load playlists
        try:
            playlists_file = repo.get_contents("data/playlists.json")
            st.session_state.playlists = json.loads(playlists_file.decoded_content)
        except:
            st.session_state.playlists = {}
        
        # Load favorites
        try:
            favorites_file = repo.get_contents("data/favorites.json")
            st.session_state.favorites = json.loads(favorites_file.decoded_content)
        except:
            st.session_state.favorites = []
    except Exception as e:
        st.error(f"Error loading from GitHub: {e}")

def save_to_github(data, filepath, message):
    """Save data to GitHub"""
    try:
        content = json.dumps(data, indent=2)
        
        try:
            file = repo.get_contents(filepath)
            repo.update_file(
                filepath,
                message,
                content,
                file.sha
            )
        except:
            repo.create_file(
                filepath,
                message,
                content
            )
        st.success(f"✅ Saved to GitHub!")
    except Exception as e:
        st.error(f"Error saving to GitHub: {e}")

def add_song(title, artist, album, url, cover_url):
    """Add a new song"""
    song = {
        "id": len(st.session_state.songs) + 1,
        "title": title,
        "artist": artist,
        "album": album,
        "url": url,
        "cover_url": cover_url,
        "plays": 0,
        "added_at": datetime.now().isoformat()
    }
    st.session_state.songs.append(song)
    save_to_github(st.session_state.songs, "data/songs.json", "Add new song")
    return song

def play_song(song):
    """Play a song"""
    st.session_state.current_song = song
    song["plays"] = song.get("plays", 0) + 1
    save_to_github(st.session_state.songs, "data/songs.json", f"Increment plays for {song['title']}")

def add_to_favorites(song):
    """Add song to favorites"""
    if song["id"] not in st.session_state.favorites:
        st.session_state.favorites.append(song["id"])
        save_to_github(st.session_state.favorites, "data/favorites.json", "Update favorites")

def create_playlist(name):
    """Create a new playlist"""
    if name not in st.session_state.playlists:
        st.session_state.playlists[name] = []
        save_to_github(st.session_state.playlists, "data/playlists.json", f"Create playlist: {name}")

def add_to_playlist(playlist_name, song_id):
    """Add song to playlist"""
    if playlist_name in st.session_state.playlists:
        if song_id not in st.session_state.playlists[playlist_name]:
            st.session_state.playlists[playlist_name].append(song_id)
            save_to_github(st.session_state.playlists, "data/playlists.json", f"Add song to {playlist_name}")

def search_songs(query):
    """Search songs"""
    return [s for s in st.session_state.songs if 
            query.lower() in s["title"].lower() or 
            query.lower() in s["artist"].lower() or
            query.lower() in s["album"].lower()]

# Main interface
col1, col2, col3 = st.columns([2, 3, 1])
with col1:
    st.title("🎵 MusicFlow")
with col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        load_from_github()
        st.rerun()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "🎵 Browse", "➕ Upload", "📋 Playlists", "❤️ Favorites"])

# Load data on first run
load_from_github()

# HOME PAGE
if page == "🏠 Home":
    st.header("Welcome to MusicFlow")
    st.write("Your music library powered by GitHub and Streamlit")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Songs", len(st.session_state.songs))
    with col2:
        st.metric("Total Plays", sum(s.get("plays", 0) for s in st.session_state.songs))
    with col3:
        st.metric("Playlists", len(st.session_state.playlists))
    
    st.subheader("🎶 Recently Added")
    if st.session_state.songs:
        recent_songs = sorted(st.session_state.songs, 
                            key=lambda x: x.get("added_at", ""), 
                            reverse=True)[:5]
        for song in recent_songs:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.image(song.get("cover_url", "https://via.placeholder.com/50"), width=50)
                with col2:
                    st.write(f"**{song['title']}**")
                    st.caption(f"{song['artist']} • {song['album']}")
                with col3:
                    if st.button("▶️ Play", key=f"play_{song['id']}"):
                        play_song(song)
                        st.success(f"Now Playing: {song['title']}")
    else:
        st.info("No songs yet. Upload some music to get started!")

# BROWSE PAGE
elif page == "🎵 Browse":
    st.header("Browse Songs")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Search songs, artists, albums...")
    with col2:
        sort_by = st.selectbox("Sort by", ["Recent", "Most Played", "Title", "Artist"])
    
    # Filter songs
    if search_query:
        songs_to_display = search_songs(search_query)
    else:
        songs_to_display = st.session_state.songs.copy()
    
    # Sort songs
    if sort_by == "Most Played":
        songs_to_display.sort(key=lambda x: x.get("plays", 0), reverse=True)
    elif sort_by == "Title":
        songs_to_display.sort(key=lambda x: x["title"])
    elif sort_by == "Artist":
        songs_to_display.sort(key=lambda x: x["artist"])
    else:
        songs_to_display.sort(key=lambda x: x.get("added_at", ""), reverse=True)
    
    if songs_to_display:
        cols = st.columns(3)
        for idx, song in enumerate(songs_to_display):
            with cols[idx % 3]:
                with st.container():
                    st.image(song.get("cover_url", "https://via.placeholder.com/150"), use_column_width=True)
                    st.write(f"**{song['title']}**")
                    st.caption(f"{song['artist']}")
                    st.caption(f"Album: {song['album']}")
                    st.caption(f"▶️ {song.get('plays', 0)} plays")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("▶️", key=f"play_btn_{song['id']}"):
                            play_song(song)
                            st.rerun()
                    with col2:
                        if st.button("❤️", key=f"fav_btn_{song['id']}"):
                            add_to_favorites(song)
                            st.rerun()
                    with col3:
                        if st.button("➕", key=f"add_btn_{song['id']}"):
                            st.session_state.add_to_playlist_id = song['id']
    else:
        st.info("No songs found. Try a different search.")

# UPLOAD PAGE
elif page == "➕ Upload":
    st.header("Upload Music")
    
    with st.form("upload_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Song Title")
            artist = st.text_input("Artist Name")
        with col2:
            album = st.text_input("Album Name")
            cover_url = st.text_input("Cover Image URL (optional)")
        
        url = st.text_input("Audio File URL (or Spotify link)")
        submitted = st.form_submit_button("📤 Upload Song", use_container_width=True)
        
        if submitted:
            if title and artist and url:
                add_song(title, artist, album, url, 
                        cover_url or "https://via.placeholder.com/150")
                st.success("✅ Song uploaded successfully!")
                st.balloons()
            else:
                st.error("Please fill in all required fields")

# PLAYLISTS PAGE
elif page == "📋 Playlists":
    st.header("My Playlists")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        playlist_name = st.text_input("Create new playlist")
    with col2:
        if st.button("Create", use_container_width=True):
            if playlist_name:
                create_playlist(playlist_name)
                st.rerun()
    
    if st.session_state.playlists:
        for playlist_name, song_ids in st.session_state.playlists.items():
            with st.expander(f"📋 {playlist_name} ({len(song_ids)} songs)"):
                for song_id in song_ids:
                    song = next((s for s in st.session_state.songs if s["id"] == song_id), None)
                    if song:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"**{song['title']}** - {song['artist']}")
                        with col2:
                            if st.button("▶️", key=f"play_pl_{song_id}"):
                                play_song(song)
    else:
        st.info("No playlists yet. Create one to get started!")

# FAVORITES PAGE
elif page == "❤️ Favorites":
    st.header("Favorite Songs")
    
    favorite_songs = [s for s in st.session_state.songs if s["id"] in st.session_state.favorites]
    
    if favorite_songs:
        cols = st.columns(3)
        for idx, song in enumerate(favorite_songs):
            with cols[idx % 3]:
                with st.container():
                    st.image(song.get("cover_url", "https://via.placeholder.com/150"), use_column_width=True)
                    st.write(f"**{song['title']}**")
                    st.caption(f"{song['artist']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("▶️ Play", key=f"fav_play_{song['id']}"):
                            play_song(song)
                            st.rerun()
                    with col2:
                        if st.button("❌ Remove", key=f"fav_remove_{song['id']}"):
                            st.session_state.favorites.remove(song["id"])
                            save_to_github(st.session_state.favorites, "data/favorites.json", "Remove from favorites")
                            st.rerun()
    else:
        st.info("No favorites yet. Like songs to add them here!")

# Player at bottom
st.divider()
if st.session_state.current_song:
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.write(f"🎵 **Now Playing:** {st.session_state.current_song['title']}")
        st.caption(f"by {st.session_state.current_song['artist']}")
    with col2:
        st.audio(st.session_state.current_song["url"])
    with col3:
        if st.button("✖️ Stop"):
            st.session_state.current_song = None
            st.rerun()
else:
    st.info("Select a song to play")
