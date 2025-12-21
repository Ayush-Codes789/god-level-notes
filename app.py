import streamlit as st
import google.generativeai as genai

# Page configuration
st.set_page_config(page_title="God Level Notes", page_icon="⚡", layout="wide")

# App Header
st.title("⚡ God Level Note Generator")
st.subheader("Powered by Gemini 1.5 Flash")

# Sidebar for API Configuration
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    model_name = st.selectbox("Choose Model", ["gemini-2.5-flash", "gemini-2.5-pro"])
    st.info("Get your key at [Google AI Studio](https://aistudio.google.com/)")

# The Prompt Template
SYSTEM_PROMPT = """
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
I'm ready for the next lecture whenever you are.
"""

# UI Layout
transcript = st.text_area("Paste the Video Transcript here:", height=300, placeholder="Wait... then he says 'npm install'...")

if st.button("Generate God Level Notes"):
    if not api_key:
        st.error("Please provide an API Key in the sidebar.")
    elif not transcript:
        st.warning("Please paste a transcript first.")
    else:
        try:
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            
            with st.spinner("Processing transcript into God Level Notes..."):
                # Combining prompt with user input
                full_prompt = f"{SYSTEM_PROMPT}\n\nTRANSCRIPT:\n{transcript}"
                
                response = model.generate_content(full_prompt)
                
                # Display Results
                st.markdown("---")
                st.markdown(response.text)
                
                # Add a download button for the generated markdown
                st.download_button(
                    label="Download as Markdown",
                    data=response.text,
                    file_name="god_level_notes.md",
                    mime="text/markdown"
                )
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.caption("Crafted for high-efficiency learning.")