import streamlit as st
import pandas as pd
from textblob import TextBlob
from datetime import datetime
import os
import random
import csv
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import time
import sys
import hashlib



st.set_page_config(page_title="Login", layout="centered")  

# Set session flags
if "intro_shown" not in st.session_state:
    st.session_state.intro_shown = False

# 1. 🌟 INTRO ANIMATION SCREEN
if not st.session_state.intro_shown:
    st.markdown("""
    <style>
    .intro-container {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(135deg, #fce3ff, #e0f7ff);
        display: flex; justify-content: center; align-items: center;
        z-index: 9999;
        animation: fadeIn 3s ease-in-out;
    }
    .intro-text {
        font-size: 3rem;
        font-weight: bold;
        color: #5b007b;
        text-align: center;
        animation: glow 1s infinite alternate;
    }
    @keyframes glow {
        from { text-shadow: 0 0 10px #ff00ff; }
        to { text-shadow: 0 0 30px #00ffff; }
    }
    </style>

    <div class="intro-container">
        <div class="intro-text">
            ✨ Welcome to Mood Diary ✨<br>
            <span style='font-size: 1.3rem;'>Sit back... just feel your heart 💜</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    time.sleep(3)
    st.session_state.intro_shown = True
    st.rerun()
    st.stop()

st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #fce3ff, #e0f7ff);
    }
    </style>
""", unsafe_allow_html=True)

# ---- THEME STYLING (auto applies on start) ----
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #fafcff, #eef1f6);
    }
    .stApp {
        font-family: 'Segoe UI', sans-serif;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border: 2px solid #d0d0d0;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
        font-weight: 500;
        color: #1a1a1a;
    }
    .stTextInput > div > div > input:focus {
        border: 2px solid #a084e8;
        outline: none;
    }
    .stButton button {
        background-color: #a084e8;
        color: white;
        font-weight: bold;
        padding: 8px 20px;
        border-radius: 8px;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #7f5af0;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)



# ---------- LOGIN SYSTEM ----------
LOGIN_LOG_FILE = "login_attempts.csv"
USERS_FILE = "users.csv"

# Function to log login attempts
def log_login_attempt(username, success):
    attempt = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": username,
        "status": "Success" if success else "Failed"
    }

    file_exists = os.path.exists(LOGIN_LOG_FILE)
    with open(LOGIN_LOG_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "username", "status"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(attempt)

# -------- Load Users --------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        return {row['username']: row['password'] for row in reader}

# -------- Save New User --------
def save_new_user(username, password):
    file_exists = os.path.exists(USERS_FILE)
    with open(USERS_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["username", "password"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({"username": username, "password": password})

# -------- Sign Up --------
def sign_up():
    st.subheader("📝 Sign Up")
    new_user = st.text_input("Choose a username", key="new_user")
    new_pass = st.text_input("Choose a password", type="password", key="new_pass")
    if st.button("Create Account"):
        users = load_users()
        if new_user in users:
            st.error("🚫 Username already exists.")
        else:
            save_new_user(new_user, new_pass)
            st.success("✅ Account created! Please log in.")
            st.session_state.show_login = True

# -------- Password Reset --------
def reset_password():
    st.subheader("🔑 Forgot Password?")
    question = "Who's your comfort person?"
    answer = st.text_input(question, key="security_answer")

    if answer:
        if answer.strip().lower() == "chatgpt":
            new_password = st.text_input("Enter your new password", type="password")
            if st.button("Reset Password"):
                st.success("✅ Password reset! (But not updated here)")
                st.stop()
        else:
            st.error("❌ Incorrect answer.")

# -------- Check Login --------
def check_password():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "login_attempts" not in st.session_state:
        st.session_state["login_attempts"] = 0

    users = load_users()

    def password_entered():
        username = st.session_state["username"]
        password = st.session_state["password"]

        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["login_attempts"] = 0
            log_login_attempt(username, True)
            del st.session_state["password"]
        else:
            st.session_state["logged_in"] = False
            st.session_state["login_attempts"] += 1
            log_login_attempt(username, False)
            st.warning(f"❌ Incorrect username or password. Attempts: {st.session_state['login_attempts']}")

    if not st.session_state["logged_in"]:
        st.subheader("🔐 Login")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password", on_change=password_entered)

        if st.session_state["login_attempts"] >= 3:
            reset_password()

        st.markdown("Don't have an account?")
        if st.button("Sign Up"):
            st.session_state.show_login = False
        return False
    else:
        return True

# -------- Handle Login or Signup View --------
if "show_login" not in st.session_state:
    st.session_state.show_login = True

if st.session_state.show_login:
    if not check_password():
        st.stop()
else:
    sign_up()
    st.stop()


# Initialize session state variables
if "current_mood" not in st.session_state:
    st.session_state.current_mood = "Neutral"
if "playlist_index" not in st.session_state:
    st.session_state.playlist_index = 0
if "theme_applied" not in st.session_state:
    st.session_state.theme_applied = False

if "journal_entries" not in st.session_state:
    st.session_state.journal_entries = []

if "saved_hashes" not in st.session_state:
    st.session_state.saved_hashes = set()

if "current_mood" not in st.session_state:
    st.session_state.current_mood = "Neutral"


# Mood-based playlist dictionary
playlist_dict = {
    "Positive": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX3rxVfibe1L0",  # Happy Vibes
        "https://open.spotify.com/embed/playlist/37i9dQZF1DXdPec7aLTmlC",  # Mood Booster
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX1BzILRveYHb",  # All Out 2010s
    ],
    "Negative": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX3YSRoSdA634",  # Sad Vibes
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX7qK8ma5wgG1",  # Life Sucks
        "https://open.spotify.com/embed/playlist/37i9dQZF1DWXRqgorJj26U",  # Deep Focus
    ],
    "Neutral": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DWVV27DiNWxkR",  # Lofi Beats
        "https://open.spotify.com/embed/playlist/37i9dQZF1DWU4xkXxbaU3V",  # Chill Vibes
        "https://open.spotify.com/embed/playlist/37i9dQZF1DXcCnTAt8CfNe",  # Beats to think to
    ]
}

# File to save journal entries
JOURNAL_FILE = "journal_db.csv"

# Ensure journal file exists
def ensure_journal_file():
    if not os.path.exists(JOURNAL_FILE):
        df = pd.DataFrame(columns=["date", "entry", "sentiment", "keywords"])
        df.to_csv(JOURNAL_FILE, index=False)

# Overthinking keyword list
overthinking_keywords = [
    "always", "never", "can't","not", "should have", "why", "again", "mess", "ruined",
    "everything", "nothing", "failed", "hate", "hopeless", "worthless","sad","what if",
    "maybe i should have","i can't stop thinking about", "why did i","what will they think",
    "i always mess things up","what is it goes wrong?", "did i say something wrong?","i need to be sure",
    "past","future","every time","doubt","anxious","nervous","insecure","guilt","fear","regret"
    "embarrassed","shame","panic","die","depressed","depression","low","without","alone","weak","confusion","confuse",
    "remember","i wonder","left","alone","defeat","destroy","disappointed" "disappoinment","end","loser"
]

positive_prompts = [
    "What are three things that went okay today?",
    "What would I tell a friend feeling this way?",
    "What's something I'm proud of this week?",
    "What if everything works out better than I imagined?",
    "What’s one small thing I can do to feel more in control?",
    "What if I trusted myself a little more today?",
    "What is this moment trying to teach me?",
    "How can I let go of what I can’t control and focus on what I can?",
    "What’s the best possible outcome I can imagine from this situation?",
    "What am I grateful for right now that’s going well?",
    "Is this thought helpful or just a habit?",
    "What’s one thing I’ve handled well recently?",
    "Who do I want to be in this moment—calm, patient, or confident?",
    "How can I simplify this situation in my mind?",
    "What’s one reason I believe in myself in this situation?",
    
]

supportive_messages = [
    "You're doing better than you think. 🌱",
    "It’s okay to feel this way — be gentle with yourself.🤗🫂",
    "Progress isn’t always visible, but it’s still progress.😮‍💨",
    "You don’t have to figure it all out right now.😌",
    "Breathe. Let it go—just for now.😮‍💨",
    "One step at a time is enough.👍🏻",
    "Your thoughts are not always the truth.✌🏻",
    "You’ve handled hard things before—you can do it again.💪🏻",
    "Progress, not perfection.🧑🏻‍🦯",
    "It’s okay to pause. It’s okay to rest.🌷🍃",
    "You are safe right now. The rest can wait.🍂",
    "Trust yourself—you’ve got this.😌✌🏻",
    "Overthinking is the art of creating problems that weren’t even there.🙂‍↕️🙂‍↔️",
    "Don’t believe everything you think.💫",
    "Worrying means you suffer twice.✨",
    "Let go or be dragged.🙂",
    "You can’t control everything. Sometimes you just need to relax and have faith.😇",
    "Feelings are visitors. Let them come and go.😉",
    "Overthinking ruins moods. Breathe and let it be.😮‍💨😌"
]


# Detect overthinking keywords
def detect_overthinking(text):
    return [kw for kw in overthinking_keywords if kw in text.lower()]

# Analyze entry: sentiment + keyword detection
def analyze_entry(entry):
    blob = TextBlob(entry)
    sentiment = blob.sentiment.polarity
    keywords = detect_overthinking(entry)
    return sentiment,keywords


#Convert regular link into embed link
def to_embed_url(link):
    if "spotify.com" not in link:
        return ""  # not a valid Spotify link
    if "embed" in link:
        return link  # already embed format
    try:
        # Extract the type and ID from the URL
        parts = link.split("spotify.com/")[1].split("?")[0].split("/")
        if len(parts) == 2:
            content_type, content_id = parts
            return f"https://open.spotify.com/embed/{content_type}/{content_id}"
    except Exception as e:
        return ""
    return ""



# Save journal entry
def save_entry(entry, sentiment, keywords):
    entry_data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "entry": entry,
        "sentiment": sentiment,
        "keywords": ", ".join(keywords)
    }
    df = pd.DataFrame([entry_data])
    df.to_csv(JOURNAL_FILE, mode='a', header=not os.path.exists(JOURNAL_FILE), index=False)

# Load past entries
def load_entries():
    if os.path.exists(JOURNAL_FILE):
        return pd.read_csv(JOURNAL_FILE)
    return pd.DataFrame(columns=["date", "entry", "sentiment", "keywords"])


# Apply theme based on mood
def apply_mood_theme(mood):
    if mood == "Positive":
        bg_color = "#fff9c4"
        text_color = "#333"
    elif mood == "Negative":
        bg_color = "#e3f2fd"
        text_color = "#333"
    else:
        bg_color = "#f3e5f5"
        text_color = "#333"
    st.markdown(f"""
        <style>
            .stApp {{ background-color: {bg_color}; color: {text_color}; }}
            .stTextArea textarea {{ background-color: white; color: black; }}
        </style>
    """, unsafe_allow_html=True)

def get_music_embed_link(mood):
    playlists = playlist_dict.get(mood, [])
    if not playlists:
        return ""
    index = st.session_state.playlist_index % len(playlists)
    return playlists[index]


# ------- Setup ------- #
st.title("🧠 Overthinker Journal Assistant")

st.markdown("""
Write your thoughts and let the assistant gently reflect back what it sees.
This is your safe space to process and breathe. 💬🫧
""")

ensure_journal_file()

# Optional Spotify playlist customization
st.subheader("🎵 Custom Playlist for Your Mood")
user_playlist = st.text_input("Paste your Spotify Playlist Link")
if user_playlist:
    embed_link = to_embed_url(user_playlist)
    if embed_link:
        st.markdown(
            f'<iframe src="{embed_link}" width="100%" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>',
            unsafe_allow_html=True
        )
    else:
        st.warning("⚠️ Please enter a valid Spotify playlist link.")


entry = st.text_area("✍️ Journal Entry:", height=200)

# Live theme change while typing
if entry.strip():
    live_sentiment, _ = analyze_entry(entry)
    if live_sentiment > 0.3:
        st.session_state.current_mood = "Positive"
    elif live_sentiment < -0.3:
        st.session_state.current_mood = "Negative"
    else:
        st.session_state.current_mood = "Neutral"

apply_mood_theme(st.session_state.current_mood)

# Get Spotify music link based on mood and cycling index
def get_music_embed_link(mood):
    playlists = playlist_dict.get(mood, [])
    if not playlists:
        return ""  # fallback
    index = st.session_state.playlist_index % len(playlists)
    return playlists[index]


def get_entry_hash(entry_text):
    return hashlib.md5(entry_text.strip().encode()).hexdigest()

# Helper function for mood label
def get_mood_label(sentiment):
    if sentiment > 0.3:
        return "☺️"
    elif sentiment < -0.3 or overthinking_keywords:
        return "😞"
    else:
        return "🙂"

# 💾 Save Entry in session state
def save_entry(entry, sentiment, keywords):
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = []

    entry_hash = get_entry_hash(entry)
    existing_hashes = [get_entry_hash(e['entry']) for e in st.session_state.journal_entries]

    if entry_hash not in existing_hashes:
        st.session_state.journal_entries.append({
            "entry": entry,
            "sentiment": sentiment,
            "keywords": keywords,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

# 🗑️ Delete entry by index
def delete_entry(index):
    if 'journal_entries' in st.session_state and 0 <= index < len(st.session_state.journal_entries):
        del st.session_state.journal_entries[index]


# Analyze & Save button
if st.button("📊 Analyze & Save"):
    if entry.strip() == "":
        st.warning("Please enter something before analyzing.")
    else:
        sentiment, keywords = analyze_entry(entry)

        apply_mood_theme(sentiment)
        save_entry(entry, sentiment, keywords)

        # 🧠 Show Analysis
        st.subheader("🔍 Analysis Result")
        if sentiment < -0.3 or keywords:
            st.markdown("**💡 Gentle Insight:** It seems you're reflecting on something heavy or overthinking.")
            if keywords:
                st.markdown(f"**🧠 Keywords:** `{', '.join(keywords)}`")
            st.markdown(f"**💬 Support:** _{random.choice(supportive_messages)}_")
            st.markdown(f"**🪶 Prompt:** _{random.choice(positive_prompts)}_")
        elif sentiment > 0.3:
            st.success("🌟 You're in a good space! Keep that momentum!")
        else:
            st.info("🌀 Neutral tone detected. Every feeling is valid.")

        st.markdown("---")
        st.subheader("📚 Your Saved Journals")
for i, journal in enumerate(st.session_state.journal_entries[::-1]):  # show newest first
            with st.expander(f"📝 {journal['timestamp']}"):
                st.write(journal["entry"])
                st.markdown(f"**Mood:** {get_mood_label(journal['sentiment'])}")
                if journal["keywords"]:
                    st.markdown(f"**🧠 Keywords:** `{', '.join(journal['keywords'])}`")
                if st.button("🗑️ Delete Entry", key=f"delete_{i}"):
                    delete_entry(len(st.session_state.journal_entries) - 1 - i)
                    st.rerun()



sentiment, keywords = analyze_entry(entry)
save_entry(entry, sentiment, keywords)
# Determine mood from sentiment
mood = "Positive" if sentiment > 0.1 else "Negative" if sentiment < -0.1 else "Neutral"

# Define playlists for each mood
playlist_dict = {
    "Positive": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX3rxVfibe1L0",
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX0UrRvztWcAU"
    ],
    "Negative": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX3YSRoSdA634",
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX4WYpdgoIcn6"
    ],
    "Neutral": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DWVV27DiNWxkR",
        "https://open.spotify.com/embed/playlist/37i9dQZF1DWY4xHQp97fN6"
    ]
}


# Get list of playlists for the mood
playlist_list = playlist_dict.get(mood, [])
if playlist_list:
    current_index = st.session_state.playlist_index % len(playlist_list)
    music_link = playlist_list[current_index]

    st.markdown(f"### 🎶 Here's a playlist for your {mood.lower()} mood:")
    import streamlit.components.v1 as components
    components.html(
        f"""
        <iframe style="border-radius:12px" src="{music_link}" width="100%" height="380"
        frameBorder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
        loading="lazy"></iframe>
        """,
        height=400,
    )

    if st.button("🔁 Next Playlist"):
        st.session_state.playlist_index += 1
        st.rerun()


MOOD_LOG_FILE = "mood_log.csv"
# Mood mapping
MOOD_SCORE_MAP = {
    "positive": 1,
    "neutral": 0,
    "negative": -1
}

# Mood-based quotes dictionary
mood_quotes = {
    "positive": [
        "You're doing amazing, sweetie! 💪🌟",
        "Smiles are contagious—pass one on! ✨😊💛",
        "Happiness is homemade.🏡🌸🍪",
        "Today is a good day for a good day.🌞🌼🎈",
        "Sunshine mixed with a little bit of magic.☀️🧚‍♀️🍃",
        "Joy is not in things; it is in us. 💖🌷🌈",
        "Your smile can light up a whole galaxy! ✨💖",
        "Keep going, you're on fire! 🔥🚀"
    ],
    "neutral": [
        "Take a deep breath, you're exactly where you need to be. 🌿",
        "Not every moment needs a meaning. Just be. 🌙",
        "Life is in the little pauses. ☕📖",
        "One step at a time.🐾🕰️🌿",
        "This too shall pass. ⏳🍂🌤️",
        "Not every day needs fireworks.🕊️📖🕯️",
        "Breathe. Just be. 🌬️🪷🧘‍♀️",
        "Stillness speaks volumes.🌌🌙📦"
    ],
    "negative": [
        "Even the moon goes through phases. You'll shine again. 🌑🌕",
        "It's okay to cry. You're still strong. 🤍🌧️",
        "You matter more than you know. 💌",
        "It's okay to not be okay. 🌧️🫂💙",
        "Tears are words the heart can't say. 💧🖤📖",
        "Even the moon goes through phases. 🌙🌘🌑",
        "Healing is messy, but it’s worth it. 🩹🌱🕊️",
        "You grow through what you go through. 🌾🛤️🌧️"
    ]
}

# Suggestions based on mood
mood_suggestions = {
    "positive": [
        "Celebrate your wins, even the small ones! 🎉",
        "Share your joy with someone you love. 🥰",
        "Use this energy to start something new! ✨",
        "Dance like nobody's watching 💃🎶",
        "Capture the moment with photos 📸🌸",
        "Call or hug someone you love 🤗📞",
        "Bake something sweet 🍪🧁",
        "Make a gratitude list ✨📝",
        "Spread kindness—compliment a stranger or do a good deed 💌🌼",
        "Create art, journal, or start a DIY project 🎨✂️"

    ],
    "neutral": [
        "Go for a mindful walk and just observe 🍃",
        "Journal what you’re feeling—it might surprise you 🖋️",
        "Listen to soft music and just be 🎧",
        "Declutter a small space around you 🧹📦",
        "Make a cup of tea or coffee ☕🍵",
        "Do a simple meditation or breathing exercise 🧘‍♀️🌬️",
        "Try out a new playlist or podcast 🎙️🎶",
        "Go on a casual stroll—no destination needed 🚶‍♀️🌆",
        "Sketch, doodle, or write freely 🎨✍️",
        "Just sit and be—no pressure, no expectations 🌌🕯️"

    ],
    "negative": [
        "Talk to someone you trust 🤝",
        "Do one small thing you enjoy—just one 🌸",
        "Wrap yourself in a cozy blanket and rest. You deserve it 🫂",
        "Listen to calm music or your favorite comforting playlist 🎧🫂",
        "Journal your thoughts—let it all out 🖊️📖",
        "Cry if you need to, it’s healing 💧",
        "Take a walk in nature, even just a short one 🌿🍃",
        "Watch a feel-good movie or series 🍿💫",
        "Talk to a friend or write them a message ☎️💬"
    ]
}

# Save mood
def save_mood(sentiment):
    today = pd.Timestamp.today().strftime('%Y-%m-%d')
    new_entry = pd.DataFrame({"date": [today], "sentiment": [sentiment]})
    
    if os.path.exists(MOOD_LOG_FILE):
        old = pd.read_csv(MOOD_LOG_FILE)
        updated = pd.concat([old, new_entry], ignore_index=True)
    else:
        updated = new_entry

    updated.to_csv(MOOD_LOG_FILE, index=False)

# Load mood entries
def load_entries():
    if os.path.exists(MOOD_LOG_FILE):
        return pd.read_csv(MOOD_LOG_FILE)
    else:
        return pd.DataFrame(columns=["date", "sentiment"])

# Sentiment analyzer
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return round(analysis.sentiment.polarity, 2)

# --- Placeholder logic if you still want score detection ---
def get_mood_category(score):
    if score > 0.4:
        return "positive"
    elif score < -0.3 or keywords:
        return "negative"
    else:
        return "neutral"

def get_mood_suggestions(score):
    mood = get_mood_category(score)
    return random.sample(mood_suggestions[mood], k=2), mood

# --- UI Starts Here ---
st.header("📝 How Are You Feeling Today?")

# Manual mood selection using radio
selected_mood = st.radio("Choose your mood:", ["😊 Positive", "😐 Neutral", "😔 Negative"])
mood_map = {
    "😊 Positive": "positive",
    "😐 Neutral": "neutral",
    "😔 Negative": "negative"
}

# Display quote and suggestions
if st.button("Show me something 💡"):
    mood_key = mood_map[selected_mood]
    quote = random.choice(mood_quotes[mood_key])
    suggestions = random.sample(mood_suggestions[mood_key], k=2)

    st.markdown(f"### 💬 Mood Quote:")
    st.info(f"**{quote}**")

    st.markdown("### 🌱 Things You Can Do:")
    for tip in suggestions:
        st.success(f"• {tip}")


# Function to save mood entry based on radio mood
def save_mood_entry(text, mood):
    score = MOOD_SCORE_MAP[mood]
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": text,
        "sentiment": score
    }
    if os.path.exists(MOOD_LOG_FILE):
        existing = pd.read_csv(MOOD_LOG_FILE)
        updated = pd.concat([existing, pd.DataFrame([entry])], ignore_index=True)
    else:
        updated = pd.DataFrame([entry])
    updated.to_csv(MOOD_LOG_FILE, index=False)

# Function to load entries for graph
def load_entries():
    if os.path.exists(MOOD_LOG_FILE):
        return pd.read_csv(MOOD_LOG_FILE)
    else:
        return pd.DataFrame(columns=["date", "text", "sentiment"])

# === Auto Log Mood from Radio Button ===
st.markdown("---")
st.subheader("📊 Your Mood Trend")

# Save mood automatically when selected
if selected_mood:
    mood_key = mood_map[selected_mood]
    save_mood_entry(text="(Radio selection)", mood=mood_key)
    st.success(f"Auto-logged: {mood_key} mood at {datetime.now().strftime('%H:%M:%S')}")


# Reset mood history
if st.button("🔁 Reset Mood History"):
    if os.path.exists(MOOD_LOG_FILE):
        os.remove(MOOD_LOG_FILE)
        st.success("Mood history cleared! Refresh to start again.")
        st.stop()

# Show graph
history = load_entries()
if not history.empty:
    history["date"] = pd.to_datetime(history["date"])
    history = history.sort_values("date")
    st.line_chart(history.set_index("date")["sentiment"])
else:
    st.info("No mood entries yet. Select a mood to start tracking!")



st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<center><sub>Made with ❤️ for your beautiful moods 💫</sub></center>",
    unsafe_allow_html=True,
)
