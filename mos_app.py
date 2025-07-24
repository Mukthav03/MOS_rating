import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Constants
AUDIO_FOLDER = "audios_kyutai"
RATINGS_FILE = "ratings.csv"

# Page config
st.set_page_config(page_title="MOS Audio Rating", layout="centered")

# Title and instruction
st.title("🔊 TTS Audio Rating")
st.markdown("""
Please rate each audio on a scale of **1 to 5**, based on the **overall quality** of the speech.  
Consider:
- **Clarity**: Is the speech easy to understand?
- **Naturalness**: Does it sound like a real human?
- **Comfort**: Would you be comfortable listening to this voice for a long time?

**Default rating is 0**, which means *not rated*. Only rated audios will be saved.
""")

# Check folder exists
if not os.path.exists(AUDIO_FOLDER):
    st.warning(f"Folder '{AUDIO_FOLDER}' not found. Please create it and add your `.wav` files.")
    st.stop()

audio_files = sorted([f for f in os.listdir(AUDIO_FOLDER) if f.endswith(".wav")])

if not audio_files:
    st.warning("No audio files found in the folder. Please add some `.wav` files.")
    st.stop()

# Form to rate audio files
with st.form("rating_form"):
    st.subheader("🎧 Rate the Audio Samples")
    ratings = []

    for audio_file in audio_files:
        st.markdown(f"**🎵 {audio_file}**")
        st.audio(os.path.join(AUDIO_FOLDER, audio_file))
        rating = st.selectbox(f"Rating for {audio_file}", [0, 1, 2, 3, 4, 5], index=0, key=audio_file)
        ratings.append({"audio": audio_file, "rating": rating})

    name = st.text_input("🧑 Your Name or ID (optional)")
    submitted = st.form_submit_button("✅ Submit Ratings")

# Save ratings
if submitted:
    # Filter out unrated (rating = 0)
    rated = [r for r in ratings if r["rating"] > 0]
    if not rated:
        st.error("⚠️ No ratings submitted. Please rate at least one audio.")
    else:
        df = pd.DataFrame(rated)
        df["timestamp"] = datetime.now()
        df["user"] = name if name else "anonymous"

        # Append to file
        if os.path.exists(RATINGS_FILE):
            df_existing = pd.read_csv(RATINGS_FILE)
            df = pd.concat([df_existing, df], ignore_index=True)

        df.to_csv(RATINGS_FILE, index=False)
        st.success("✅ Thank you! Your ratings have been saved.")

# Show previous ratings
if os.path.exists(RATINGS_FILE):
    st.markdown("---")
    st.subheader("📊 All Ratings So Far")
    ratings_df = pd.read_csv(RATINGS_FILE)
    st.dataframe(ratings_df)

    avg_scores = ratings_df.groupby("audio")["rating"].mean().reset_index()
    avg_scores.columns = ["Audio", "Average Rating"]
    st.write("### 📈 Average Ratings per Audio")
    st.dataframe(avg_scores)
