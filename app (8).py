import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime
import base64
import random
from PIL import Image, ImageDraw
import io

# Configure Streamlit
st.set_page_config(
    page_title="🎵 Wavo - Web Music Player",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============= STYLING =============
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Card styling */
    .music-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .music-card:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-5px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .player-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.3);
        margin: 20px 0;
    }
    
    .title-text {
        color: white;
        font-size: 32px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .subtitle-text {
        color: rgba(255, 255, 255, 0.9);
        font-size: 16px;
    }
    
    .button-custom {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        cursor: pointer;
        font-weight: bold;
    }
    
    .animation-pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .music-bars {
        display: flex;
        align-items: flex-end;
        gap: 3px;
        height: 40px;
    }
    
    .bar {
        width: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
        animation: bounce 0.8s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# ============= SAMPLE MUSIC DATA =============
SAMPLE_SONGS = [
    {
        "id": 1,
        "title": "Summer Vibes",
        "artist": "The Beats",
        "duration": "3:45",
        "genre": "Electronic",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "color": "#FF6B6B"
    },
    {
        "id": 2,
        "title": "Midnight Dreams",
        "artist": "Luna Echo",
        "duration": "4:12",
        "genre": "Chillhop",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        "color": "#4ECDC4"
    },
    {
        "id": 3,
        "title": "Electric Storm",
        "artist": "Neon Lights",
        "duration": "3:58",
        "genre": "Synthwave",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        "color": "#FFE66D"
    },
    {
        "id": 4,
        "title": "Ocean Waves",
        "artist": "Chill Lofi",
        "duration": "5:30",
        "genre": "Lofi Hip-Hop",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
        "color": "#95E1D3"
    },
    {
        "id": 5,
        "title": "Cosmic Journey",
        "artist": "Space Travelers",
        "duration": "4:45",
        "genre": "Ambient",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
        "color": "#C7CEEA"
    },
    {
        "id": 6,
        "title": "Urban Jungle",
        "artist": "City Sounds",
        "duration": "3:22",
        "genre": "Hip-Hop",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
        "color": "#FFAFCC"
    },
    {
        "id": 7,
        "title": "Jazz Nights",
        "artist": "Jazz Masters",
        "duration": "6:15",
        "genre": "Jazz",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3",
        "color": "#BDB2FF"
    },
    {
        "id": 8,
        "title": "Forest Walk",
        "artist": "Nature Sounds",
        "duration": "4:00",
        "genre": "Nature",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
        "color": "#A0C4FF"
    },
]

# ============= SESSION STATE =============
if "current_song" not in st.session_state:
    st.session_state.current_song = SAMPLE_SONGS[0]

if "is_playing" not in st.session_state:
    st.session_state.is_playing = False

if "playlist" not in st.session_state:
    st.session_state.playlist = SAMPLE_SONGS.copy()

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "selected_genre" not in st.session_state:
    st.session_state.selected_genre = "All"

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# ============= HELPER FUNCTIONS =============
def create_animated_visualizer():
    """Create animated music visualizer"""
    bars = [random.randint(20, 100) for _ in range(10)]
    html = '<div style="display: flex; gap: 8px; justify-content: center; align-items: flex-end; height: 100px;">'
    for i, height in enumerate(bars):
        html += f'<div style="width: 8px; height: {height}px; background: linear-gradient(180deg, #667eea 0%, #764ba2 100%); border-radius: 4px; animation: bounce {0.5 + i*0.1}s ease-in-out infinite;"></div>'
    html += '</div>'
    return html

def get_genres():
    """Get all unique genres"""
    genres = set([song["genre"] for song in SAMPLE_SONGS])
    return ["All"] + sorted(list(genres))

def filter_songs(songs, query, genre):
    """Filter songs by search query and genre"""
    filtered = songs
    
    if genre != "All":
        filtered = [s for s in filtered if s["genre"] == genre]
    
    if query:
        query = query.lower()
        filtered = [s for s in filtered if 
                   query in s["title"].lower() or 
                   query in s["artist"].lower()]
    
    return filtered

def play_song(song):
    """Play selected song"""
    st.session_state.current_song = song
    st.session_state.is_playing = True
    st.session_state.current_index = SAMPLE_SONGS.index(song)

def next_song():
    """Play next song"""
    current_index = st.session_state.current_index
    next_index = (current_index + 1) % len(SAMPLE_SONGS)
    st.session_state.current_song = SAMPLE_SONGS[next_index]
    st.session_state.current_index = next_index

def prev_song():
    """Play previous song"""
    current_index = st.session_state.current_index
    prev_index = (current_index - 1) % len(SAMPLE_SONGS)
    st.session_state.current_song = SAMPLE_SONGS[prev_index]
    st.session_state.current_index = prev_index

def toggle_play():
    """Toggle play/pause"""
    st.session_state.is_playing = not st.session_state.is_playing

# ============= HEADER =============
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown(
        '<div style="text-align: center; padding: 20px;">'
        '<h1 style="color: white; font-size: 48px; text-shadow: 3px 3px 6px rgba(0,0,0,0.3); margin: 0;">🎵 WAVO</h1>'
        '<p style="color: rgba(255,255,255,0.9); font-size: 14px; margin: 5px 0;">Your Personal Web Music Player</p>'
        '</div>',
        unsafe_allow_html=True
    )

# ============= MAIN PLAYER =============
st.markdown('<div class="player-container">', unsafe_allow_html=True)

# Current Song Display
col1, col2 = st.columns([1, 2])

with col1:
    # Create album art with gradient
    img = Image.new('RGB', (200, 200), color=(102, 126, 234))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Draw circles
    for i in range(5):
        draw.ellipse(
            [(40 + i*20, 40 + i*20), (160 - i*20, 160 - i*20)],
            outline=(255, 255, 255, 100 - i*15),
            width=2
        )
    
    # Draw center circle
    draw.ellipse([(80, 80), (120, 120)], fill=(118, 75, 162))
    
    st.image(img, use_column_width=True)

with col2:
    st.markdown(
        f'<div style="padding: 20px;">'
        f'<h2 style="color: white; margin: 0;">{st.session_state.current_song["title"]}</h2>'
        f'<p style="color: rgba(255,255,255,0.8); font-size: 16px; margin: 5px 0;">{st.session_state.current_song["artist"]}</p>'
        f'<p style="color: rgba(255,255,255,0.6); font-size: 14px; margin: 10px 0;">Genre: {st.session_state.current_song["genre"]}</p>'
        f'<p style="color: rgba(255,255,255,0.6); font-size: 14px;">Duration: {st.session_state.current_song["duration"]}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

# Player Controls
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("⏮️ Prev", use_container_width=True):
        prev_song()
        st.rerun()

with col2:
    if st.button("🔀 Shuffle", use_container_width=True):
        random_song = random.choice(SAMPLE_SONGS)
        play_song(random_song)
        st.rerun()

with col3:
    play_text = "⏸️ Pause" if st.session_state.is_playing else "▶️ Play"
    if st.button(play_text, use_container_width=True):
        toggle_play()
        st.rerun()

with col4:
    if st.button("🔁 Repeat", use_container_width=True):
        pass

with col5:
    if st.button("Next ⏭️", use_container_width=True):
        next_song()
        st.rerun()

# Visualizer
if st.session_state.is_playing:
    st.markdown(create_animated_visualizer(), unsafe_allow_html=True)

# Audio Player HTML
st.markdown(
    f'''
    <audio autoplay style="width: 100%;">
        <source src="{st.session_state.current_song['url']}" type="audio/mpeg">
        Your browser does not support the audio element.
    </audio>
    ''',
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)

# ============= SIDEBAR - SEARCH & FILTER =============
with st.sidebar:
    st.markdown("### 🔍 Search & Filter")
    
    search = st.text_input("🎵 Search songs...", placeholder="Title or Artist")
    st.session_state.search_query = search
    
    genre = st.selectbox("Genre", get_genres(), index=get_genres().index(st.session_state.selected_genre))
    st.session_state.selected_genre = genre
    
    st.markdown("---")
    st.markdown("### 📊 Playlist Stats")
    st.metric("Total Songs", len(SAMPLE_SONGS))
    st.metric("Current Song", st.session_state.current_song["title"][:20])

# ============= MUSIC LIBRARY =============
st.markdown("## 🎼 Music Library")

filtered_songs = filter_songs(SAMPLE_SONGS, st.session_state.search_query, st.session_state.selected_genre)

if filtered_songs:
    # Display as grid
    cols = st.columns(4)
    
    for idx, song in enumerate(filtered_songs):
        with cols[idx % 4]:
            st.markdown(
                f'''
                <div class="music-card" style="background: linear-gradient(135deg, {song["color"]}33 0%, {song["color"]}11 100%);">
                    <div style="text-align: center;">
                        <div style="font-size: 40px; margin-bottom: 10px;">♫</div>
                        <h4 style="color: white; margin: 5px 0; font-size: 14px;">{song["title"]}</h4>
                        <p style="color: rgba(255,255,255,0.8); font-size: 12px; margin: 3px 0;">{song["artist"]}</p>
                        <p style="color: rgba(255,255,255,0.6); font-size: 11px; margin: 5px 0;">{song["genre"]} • {song["duration"]}</p>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"▶️ Play", key=f"play_{song['id']}", use_container_width=True):
                    play_song(song)
                    st.rerun()
            
            with col2:
                if st.button(f"❤️", key=f"like_{song['id']}", use_container_width=True):
                    st.toast(f"Added '{song['title']}' to favorites!")
else:
    st.warning("❌ No songs found. Try adjusting your search or filter.")

# ============= FOOTER =============
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: rgba(255,255,255,0.6); padding: 20px;">'
    '<p>🎵 Wavo v1.0 | Built with Streamlit | 2024</p>'
    '<p style="font-size: 12px;">Enjoy your music! 🎧</p>'
    '</div>',
    unsafe_allow_html=True
)
