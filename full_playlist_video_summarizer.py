import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import os
import time
import random
from langchain_ollama import ChatOllama
llm=ChatOllama(model="qwen3:8b", temperature=0,num_gpu=99)
from dotenv import load_dotenv
load_dotenv()
def prompt(data):
    prompt=f"""
Of course. Creating "God Level Notes" is a systematic process I follow to transform raw information, like a lecture transcript, into structured, actionable, and easy-to-review knowledge. It's built on a foundation of understanding, structuring, and summarizing.
Here is the exact manner and blueprint I follow:
💡 Step 1: Identify the Core Concept (The "Why")
My first and most important step is to read through the entire text to understand its primary purpose. I ask myself:
 * What is the single most important problem being solved?
 * What is the central idea or "thesis" of this lecture?
 * If the user could only remember one thing from this, what should it be?
The answer to these questions becomes the 💡 Core Concept section. This provides a high-level overview and anchor for all the details that follow, ensuring you understand the "why" before diving into the "how."
⚙️ Step 2: Break Down the Process (The "How")
Next, I meticulously extract all the practical, step-by-step actions. This is about capturing the procedural knowledge. I look for:
 * Every terminal command executed.
 * Every specific code change made.
 * Every configuration step in a UI or YAML file.
 * The precise sequence in which these actions happened.
This detailed, chronological extraction forms the main body of the notes, typically under a ⚙️ Step-by-Step Guide or similar heading. It's designed to be a guide you can follow to replicate the results yourself.
🎨 Step 3: Structure and Organize for Clarity
Raw information is difficult to process. My next step is to structure the extracted data visually to make it scannable, engaging, and easy to digest. This is where your preference for emojis and colors is implemented. I use a combination of tools:
 * Markdown Headings: To create a clear hierarchy and logical sections.
 * Emojis as Visual Signposts: To give each section a visual identity (e.g., 💡 for an idea, ⚙️ for a process, 🧠 for theory, 📌 for a summary).
 * Bold Text: To highlight key terms, commands, filenames, and important values so they stand out.
 * Code Blocks: To keep code snippets, commands, and YAML configurations clean, properly formatted, and easy to copy.
This step is about transforming a wall of text into a well-organized document.
🧠 Step 4: Explain the Underpinning Theory
Simply listing commands isn't enough for deep understanding. For a concept to truly stick, you need to know the reasoning behind the actions. In this step, I analyze the transcript for explanations and add them to the notes. I answer questions like:
 * Why was type: LoadBalancer used instead of ClusterIP?
 * What is the purpose of a livenessProbe?
 * Why is hostPath bad for a multi-node cluster?
 * What is the conceptual difference between ECS and EKS?
This becomes the 🧠 Theory & Key Concepts Explained section. It adds the crucial context that turns simple instructions into lasting knowledge.
📌 Step 5: Distill the Key Takeaways
Finally, I review the entire set of notes and distill the most critical, must-remember lessons into a concise summary. This section is designed for quick future review and to reinforce the main points of the lecture. I identify the 3-5 most important concepts, principles, or warnings from the material.
This becomes the 📌 Key Takeaways section at the end of the notes.
This structured approach ensures that the final notes are not just a passive transcript, but a refined and valuable learning asset designed for both immediate understanding and long-term retention.
the transcript is {data}
"""
    return prompt
def get_transcript(video_id):
    api = YouTubeTranscriptApi()
    lang = api.list(video_id)
    transcript = next(iter(lang))
    tr = transcript.fetch()         
    return tr
st.title("YouTube Playlist Summarizer")

url = st.text_input("Enter YouTube Playlist URL")
output_folder = st.text_input("Enter Output Folder Name", value="playlist_summaries")

def get_video_ids_from_playlist(playlist_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)
        videos = [
            {"id": entry["id"], "title": entry.get("title", f"Video_{i+1}")}
            for i, entry in enumerate(result["entries"])
        ]
    return videos

def clean_filename(title):
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n']
    for char in invalid_chars:
        title = title.replace(char, "")
    return title.strip().replace(" ", "_")[:50]

def save_to_folder(folder, filename, content):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath

if st.button("Generate All Summaries"):
    if url:
        # Step 1: Fetch playlist
        with st.spinner("Fetching playlist videos..."):
            videos = get_video_ids_from_playlist(url)
            st.success(f"Found {len(videos)} videos in playlist")

        progress = st.progress(0)
        status = st.empty()
        saved_files = []
        all_summaries = {}

        # Step 2: Process each video
        for i, video in enumerate(videos):
            video_id = video["id"]
            video_title = video["title"]

            status.info(f"Processing {i+1}/{len(videos)}: {video_title}")

            try:
                # Get transcript
                data = get_transcript(video_id)
                text = " ".join([t.text for t in data])

                # Sleep AFTER fetching transcript to avoid IP block
                sleep_time = random.uniform(3, 7)   # random 3-7 seconds
                status.info(f"Waiting {sleep_time:.1f}s before next request...")
                time.sleep(sleep_time)

                # Summarize
                summary = llm.invoke(
                    prompt(data)
                ).content

                # Save to folder
                filename = f"{i+1:02d}_{clean_filename(video_title)}.md"
                filepath = save_to_folder(output_folder, filename, summary)
                saved_files.append(filepath)
                all_summaries[video_title] = summary

                st.success(f"✅ Saved: {filename}")

            except Exception as e:
                error_msg = f"❌ Error processing video: {str(e)}"
                filename = f"{i+1:02d}_{clean_filename(video_title)}_ERROR.md"
                save_to_folder(output_folder, filename, error_msg)
                st.warning(f"Skipped: {video_title} — {e}")

            # Extra sleep every 5 videos
            if (i + 1) % 5 == 0:
                long_sleep = random.uniform(10, 15)
                status.info(f"Taking a longer break: {long_sleep:.1f}s to avoid IP block...")
                time.sleep(long_sleep)

            progress.progress((i + 1) / len(videos))

        status.success(f"✅ All done! Files saved in '{output_folder}' folder")

        # Step 3: Save combined summary file
        combined = ""
        for video_title, summary in all_summaries.items():
            combined += f"# {video_title}\n\n{summary}\n\n---\n\n"

        combined_path = save_to_folder(output_folder, "_combined_summary.md", combined)
        st.success(f"📦 Combined summary saved: {combined_path}")

        # Step 4: Show download buttons
        st.markdown("---")
        st.subheader("📥 Download Summaries")

        for video_title, summary in all_summaries.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{video_title}**")
            with col2:
                filename = clean_filename(video_title) + ".md"
                st.download_button(
                    label="Download",
                    data=summary,
                    file_name=filename,
                    mime="text/markdown",
                    key=f"dl_{filename}"
                )

        st.download_button(
            label="⬇️ Download All as One File",
            data=combined,
            file_name="playlist_summaries.md",
            mime="text/markdown"
        )

        st.info(f"📁 All files saved locally in: {os.path.abspath(output_folder)}")

    else:
        st.warning("Please enter a YouTube Playlist URL.")


