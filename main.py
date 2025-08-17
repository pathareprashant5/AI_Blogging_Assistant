import streamlit as st
from apikey import google_gemini_api_key, openai_api_key


from openai import OpenAI
client1 = OpenAI(api_key=openai_api_key)
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# Streamlit Carousel for displaying images
from streamlit_carousel import carousel

single_image= dict(    
    title="",
    text="",
    interval=None,
    img=""
    )

    


# Set Streamlit app layout
st.set_page_config(layout="wide")

# Title and Subheader
st.title("✍️ Crafting Blog: AI 🤖 Blogging Assistant 📝")
st.subheader("Create Engaging Blogs with AI Assistance")

# Sidebar Inputs
with st.sidebar:
    st.header("Input your blog details")
    blog_title = st.text_input("Blog Title", placeholder="Enter your blog title here")
    keywords = st.text_area("Keywords (comma-separated)", placeholder="Enter keywords related to your blog")
    num_words = st.slider("Number of Words", min_value=250, max_value=1000, value=500, step=250)
    num_images = st.number_input("Number of Images", min_value=1, max_value=5, value=3, step=1)
    submit_button = st.button("Generate Blog")

# Generate blog using Gemini
def generate_blog(title, keywords, word_count):
    client = genai.Client(api_key=google_gemini_api_key)
    model = "gemini-2.0-flash"

    prompt = (
        f"""Generate a comprehensive, engaging blog post relevant to the given title "{title}" and keywords "{keywords}". 
        Make sure to incorporate these keywords naturally in the blog. 
        The blog should be approximately {word_count} words in length, suitable for an online audience. 
        Ensure the content is original, informative, and maintains a consistent tone throughout."""
    )

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]

    config = types.GenerateContentConfig(
        tools=[
            types.Tool(googleSearch=types.GoogleSearch())
        ],
    )

    full_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=config,
    ):
        if chunk.text:
            full_text += chunk.text

    return full_text

# Run generation when button is clicked
if submit_button:

    images=[]
    images_gallery=[]

    for i in range(num_images):
        
        # Generate image using OpenAI's DALL-E
        response = client1.images.generate(
        model="dall-e-3",   # correct model for image generation
        prompt=f"Generate a Blog Post Image on the title: {blog_title}",
        size="1024x1024",
        quality="hd",
        n=1
        )
        new_image=single_image.copy()
        new_image["title"]=f"Image {i+1}"
        new_image["text"]=f"{blog_title}"
        new_image["img"]=response.data[0].url
        images_gallery.append(new_image)

        #images.append(response.data[0].url) 

    st.title("Generated Images for Your Blog")
    carousel(items=images_gallery, width=1)

    
    #st.image(image_url, caption="Generated Image")
    st.title("Your Blog Post is Ready!")
    if blog_title and keywords:
        with st.spinner("Generating your blog..."):
            output = generate_blog(blog_title, keywords, num_words)
            st.success("✅ Blog Generated Successfully!")
            st.markdown("---")
            st.markdown("### 📝 Your AI-Generated Blog")
            st.markdown(output)
    else:
        st.warning("Please provide both a blog title and keywords.")
