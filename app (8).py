"""
TemanBelajar - Web Player Musik Pengiring Belajar
Dibuat dengan Streamlit

Fitur:
- Pemutar musik (YouTube embed / upload file / URL audio langsung)
- Playlist tersimpan per kategori
- Timer belajar (Pomodoro) berbasis JS
- Riwayat sesi belajar tersimpan lokal

Cara menjalankan:
    streamlit run app.py
"""

import streamlit as st
import json
import os
import re
from datetime import datetime
import streamlit.components.v1 as components

# =========================================================
# KONFIGURASI & FILE DATA
# =========================================================
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PLAYLIST_FILE = os.path.join(DATA_DIR, "playlist.json")
HISTORY_FILE = os.path.join(DATA_DIR, "study_log.json")

os.makedirs(DATA_DIR, exist_ok=True)

KATEGORI_LIST = ["Lo-fi", "Piano", "Suara Alam", "Instrumental", "Lainnya"]


def load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Playlist contoh awal (link YouTube publik untuk musik instrumental/lo-fi resmi)
DEFAULT_PLAYLIST = [
    {
        "id": 1,
        "judul": "Lo-fi Beats untuk Fokus Belajar",
        "kategori": "Lo-fi",
        "tipe": "youtube",
        "sumber": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
    },
    {
        "id": 2,
        "judul": "Suara Hujan untuk Relaksasi",
        "kategori": "Suara Alam",
        "tipe": "youtube",
        "sumber": "https://www.youtube.com/watch?v=q76bMs-NwRk",
    },
]

DEFAULT_HISTORY = []


def get_youtube_id(url):
    """Ambil video ID dari berbagai format URL YouTube."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
    ]
    for p in patterns:
        match = re.search(p, url)
        if match:
            return match.group(1)
    return None


# =========================================================
# SESSION STATE
# =========================================================
if "playlist" not in st.session_state:
    st.session_state.playlist = load_json(PLAYLIST_FILE, DEFAULT_PLAYLIST)

if "history" not in st.session_state:
    st.session_state.history = load_json(HISTORY_FILE, DEFAULT_HISTORY)

if "now_playing" not in st.session_state:
    st.session_state.now_playing = (
        st.session_state.playlist[0] if st.session_state.playlist else None
    )


# =========================================================
# KOMPONEN: PEMUTAR MUSIK
# =========================================================
def render_player(song):
    if song is None:
        st.info("Belum ada musik. Tambahkan musik dulu di menu 'Tambah Musik'.")
        return

    st.subheader(f"🎵 Sedang diputar: {song['judul']}")
    st.caption(f"Kategori: {song['kategori']}")

    if song["tipe"] == "youtube":
        vid = get_youtube_id(song["sumber"])
        if vid:
            components.iframe(
                f"https://www.youtube.com/embed/{vid}?autoplay=1",
                height=200,
            )
        else:
            st.error("Link YouTube tidak valid.")
    elif song["tipe"] == "url":
        st.audio(song["sumber"])
    elif song["tipe"] == "upload":
        # sumber berisi path file yang sudah disimpan di folder data/uploads
        if os.path.exists(song["sumber"]):
            st.audio(song["sumber"])
        else:
            st.error("File audio tidak ditemukan.")


# =========================================================
# KOMPONEN: TIMER BELAJAR (Pomodoro, berjalan di sisi browser)
# =========================================================
def render_timer():
    st.subheader("⏱️ Timer Belajar")
    menit = st.slider("Durasi belajar (menit)", 5, 90, 25, step=5)

    timer_html = f"""
    <div style="font-family:sans-serif; text-align:center; padding:10px;">
        <div id="display" style="font-size:48px; font-weight:bold; color:#2c3e50;">
            {menit:02d}:00
        </div>
        <button id="startBtn" style="padding:8px 20px; margin:5px; font-size:16px;
            border-radius:8px; border:none; background:#4CAF50; color:white; cursor:pointer;">
            Mulai
        </button>
        <button id="resetBtn" style="padding:8px 20px; margin:5px; font-size:16px;
            border-radius:8px; border:none; background:#e74c3c; color:white; cursor:pointer;">
            Reset
        </button>
        <p id="status" style="color:#555;"></p>
    </div>

    <script>
    let totalSeconds = {menit} * 60;
    let remaining = totalSeconds;
    let timerInterval = null;

    function updateDisplay() {{
        let m = Math.floor(remaining / 60);
        let s = remaining % 60;
        document.getElementById("display").innerText =
            String(m).padStart(2,'0') + ":" + String(s).padStart(2,'0');
    }}

    function playBeep() {{
        // Bunyi alarm sederhana menggunakan Web Audio API (tidak memakai file berhak cipta)
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.connect(g); g.connect(ctx.destination);
        o.frequency.value = 880;
        g.gain.value = 0.2;
        o.start();
        setTimeout(() => o.stop(), 600);
    }}

    document.getElementById("startBtn").onclick = function() {{
        if (timerInterval) return;
        document.getElementById("status").innerText = "Sesi belajar dimulai. Semangat!";
        timerInterval = setInterval(() => {{
            remaining--;
            updateDisplay();
            if (remaining <= 0) {{
                clearInterval(timerInterval);
                timerInterval = null;
                document.getElementById("status").innerText = "Waktu belajar selesai! 🎉";
                playBeep();
            }}
        }}, 1000);
    }};

    document.getElementById("resetBtn").onclick = function() {{
        clearInterval(timerInterval);
        timerInterval = null;
        remaining = totalSeconds;
        updateDisplay();
        document.getElementById("status").innerText = "";
    }};

    updateDisplay();
    </script>
    """
    components.html(timer_html, height=220)

    st.markdown("---")
    st.caption("Setelah selesai belajar, catat sesi ini ke riwayat:")
    catatan = st.text_input("Catatan sesi (opsional)", placeholder="Contoh: Belajar Kimia Analisis Bab Titrimetri")
    if st.button("✅ Simpan Sesi ke Riwayat"):
        entry = {
            "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "durasi_menit": menit,
            "catatan": catatan,
        }
        st.session_state.history.append(entry)
        save_json(HISTORY_FILE, st.session_state.history)
        st.success("Sesi belajar berhasil dicatat!")


# =========================================================
# HALAMAN: BERANDA (Pemutar + Timer berdampingan)
# =========================================================
def page_beranda():
    st.title("🎧 TemanBelajar")
    st.write("Putar musik pengiring sambil belajar, dan gunakan timer untuk menjaga fokus.")

    col1, col2 = st.columns([1, 1])
    with col1:
        judul_list = [s["judul"] for s in st.session_state.playlist]
        if judul_list:
            pilihan = st.selectbox("Pilih musik dari playlist:", judul_list)
            selected_song = next(
                s for s in st.session_state.playlist if s["judul"] == pilihan
            )
            st.session_state.now_playing = selected_song
        render_player(st.session_state.now_playing)

    with col2:
        render_timer()


# =========================================================
# HALAMAN: PLAYLIST SAYA
# =========================================================
def page_playlist():
    st.title("📻 Playlist Saya")
    if not st.session_state.playlist:
        st.info("Playlist masih kosong.")
        return

    for kategori in KATEGORI_LIST:
        lagu_kategori = [s for s in st.session_state.playlist if s["kategori"] == kategori]
        if not lagu_kategori:
            continue
        st.subheader(f"🎼 {kategori}")
        for song in lagu_kategori:
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{song['judul']}**  ·  _{song['tipe']}_")
            if c2.button("▶️ Putar", key=f"play_{song['id']}"):
                st.session_state.now_playing = song
                st.success(f"Memutar: {song['judul']}")
            if c3.button("🗑️ Hapus", key=f"del_{song['id']}"):
                st.session_state.playlist = [
                    s for s in st.session_state.playlist if s["id"] != song["id"]
                ]
                save_json(PLAYLIST_FILE, st.session_state.playlist)
                st.rerun()


# =========================================================
# HALAMAN: TAMBAH MUSIK
# =========================================================
def page_tambah_musik():
    st.title("➕ Tambah Musik ke Playlist")

    tipe = st.radio(
        "Sumber musik:",
        ["Link YouTube", "Upload File Audio", "URL Audio Langsung"],
    )

    judul = st.text_input("Judul / nama musik")
    kategori = st.selectbox("Kategori", KATEGORI_LIST)

    if tipe == "Link YouTube":
        url = st.text_input("Tempel link YouTube di sini")
        if st.button("Tambahkan"):
            if judul and url and get_youtube_id(url):
                new_id = max([s["id"] for s in st.session_state.playlist], default=0) + 1
                st.session_state.playlist.append({
                    "id": new_id, "judul": judul, "kategori": kategori,
                    "tipe": "youtube", "sumber": url,
                })
                save_json(PLAYLIST_FILE, st.session_state.playlist)
                st.success("Musik berhasil ditambahkan!")
            else:
                st.error("Pastikan judul diisi dan link YouTube valid.")

    elif tipe == "Upload File Audio":
        uploaded_file = st.file_uploader("Upload file audio (mp3/wav)", type=["mp3", "wav", "ogg"])
        if st.button("Tambahkan") and uploaded_file and judul:
            upload_dir = os.path.join(DATA_DIR, "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            new_id = max([s["id"] for s in st.session_state.playlist], default=0) + 1
            st.session_state.playlist.append({
                "id": new_id, "judul": judul, "kategori": kategori,
                "tipe": "upload", "sumber": file_path,
            })
            save_json(PLAYLIST_FILE, st.session_state.playlist)
            st.success("File audio berhasil ditambahkan ke playlist!")

    else:  # URL Audio Langsung
        url = st.text_input("Tempel URL file audio (.mp3/.wav) di sini")
        if st.button("Tambahkan"):
            if judul and url:
                new_id = max([s["id"] for s in st.session_state.playlist], default=0) + 1
                st.session_state.playlist.append({
                    "id": new_id, "judul": judul, "kategori": kategori,
                    "tipe": "url", "sumber": url,
                })
                save_json(PLAYLIST_FILE, st.session_state.playlist)
                st.success("Musik berhasil ditambahkan!")
            else:
                st.error("Judul dan URL harus diisi.")


# =========================================================
# HALAMAN: RIWAYAT BELAJAR
# =========================================================
def page_riwayat():
    st.title("📊 Riwayat Belajar")
    if not st.session_state.history:
        st.info("Belum ada riwayat sesi belajar. Selesaikan sesi timer untuk mulai mencatat.")
        return

    total_menit = sum(h["durasi_menit"] for h in st.session_state.history)
    st.metric("Total waktu belajar tercatat", f"{total_menit} menit")

    st.markdown("---")
    for entry in reversed(st.session_state.history):
        st.write(f"🗓️ **{entry['tanggal']}** — {entry['durasi_menit']} menit")
        if entry.get("catatan"):
            st.caption(f"📝 {entry['catatan']}")
        st.markdown("---")

    if st.button("🗑️ Hapus Semua Riwayat"):
        st.session_state.history = []
        save_json(HISTORY_FILE, [])
        st.rerun()


# =========================================================
# NAVIGASI UTAMA
# =========================================================
def main():
    st.set_page_config(page_title="TemanBelajar", page_icon="🎧", layout="wide")

    st.sidebar.title("🎧 TemanBelajar")
    menu = st.sidebar.radio(
        "Menu",
        ["🏠 Beranda", "📻 Playlist Saya", "➕ Tambah Musik", "📊 Riwayat Belajar"],
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Dengarkan musik, atur waktu, dan catat progres belajarmu.")

    if menu == "🏠 Beranda":
        page_beranda()
    elif menu == "📻 Playlist Saya":
        page_playlist()
    elif menu == "➕ Tambah Musik":
        page_tambah_musik()
    elif menu == "📊 Riwayat Belajar":
        page_riwayat()


if __name__ == "__main__":
    main()
