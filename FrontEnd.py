import streamlit as st
import requests
from PIL import Image
import io

# Set page config
st.set_page_config(page_title="Fashion Visual Search & Styling Assistant", layout="wide")
st.title("Fashion Visual Search & Intelligent Styling Assistant")
st.markdown("Upload an image to find similar fashion items and get outfit recommendations.")

# Ngrok URL (update if it changes)
API_URL = "https://5744-34-106-160-160.ngrok-free.app" # Make sure this matches your current ngrok URL

# File uploader
uploaded_file = st.file_uploader("Choose a fashion image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", width=300)

    st.header("Similar Items")
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

    try:
        response = requests.post(f"{API_URL}/search/visual?top_k=5", files=files, timeout=10)
        response.raise_for_status()

        # --- REMOVED: raw_data display ---
        # raw_data = response.text  # Debugging raw response
        # st.write("**Raw API Response:**", raw_data)

        data = response.json()
        similar_items = data.get("results", [])

        if similar_items:
            cols = st.columns(len(similar_items))
            for idx, item in enumerate(similar_items):
                with cols[idx]:
                    image_url = item.get("image_url")
                    if image_url and image_url.startswith("/images/"):
                        image_url = f"{API_URL}{image_url}"  # Ensure absolute URL

                    # --- REMOVED: Debugging image URL display ---
                    # st.write(f"**Debug Image URL:** {image_url}")  # Debugging info

                    try:
                        st.image(
                            image_url if image_url else "https://via.placeholder.com/150?text=No+Image",
                            caption=f"{item['name']} (Category: {item['category']}) - Similarity: {item['similarity_score']:.2f}",
                            width=150
                        )
                    except Exception as e:
                        st.image("https://via.placeholder.com/150?text=Image+Error", width=150)
                        st.write(f"Image load error: {e}")

                    if st.button(f"Get Outfit ({item['name']})", key=f"outfit_{item['product_id']}"):
                        try:
                            outfit_response = requests.post(
                                f"{API_URL}/search/outfit",
                                json={"product_id": item["product_id"], "max_items_per_category": 3},
                                timeout=10
                            )
                            outfit_response.raise_for_status()
                            outfit_data = outfit_response.json()
                            recommendations = outfit_data.get("recommendations", {})

                            st.subheader(f"Outfit Recommendations for {item['name']}")
                            for category, items in recommendations.items():
                                if items:
                                    st.write(f"**{category.capitalize()}**")
                                    rec_cols = st.columns(min(len(items), 3))
                                    for i, rec_item in enumerate(items):
                                        with rec_cols[i]:
                                            rec_image_url = rec_item.get("image_url")
                                            if rec_image_url and rec_image_url.startswith("/images/"):
                                                rec_image_url = f"{API_URL}{rec_image_url}"

                                            # --- REMOVED: Debugging outfit URL display ---
                                            # st.write(f"**Debug Outfit URL:** {rec_image_url}")  # Debugging info

                                            try:
                                                st.image(
                                                    rec_image_url if rec_image_url else "https://via.placeholder.com/150?text=No+Image",
                                                    caption=f"{rec_item['product_name']} ({rec_item['brand']}) - ₹{rec_item['price']:.2f}",
                                                    width=100
                                                )
                                            except Exception as e:
                                                st.image("https://via.placeholder.com/100?text=Image+Error", width=100)
                                                st.write(f"Image load error: {e}")

                        except requests.exceptions.RequestException as e:
                            st.error(f"Outfit recommendation error: {e}")

        else:
            st.warning("No similar items found.")

    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Connection Error: Ensure the FastAPI server is running and ngrok is active.")
    except requests.exceptions.Timeout:
        st.error("Timeout Error: The backend took too long to respond.")
    except requests.exceptions.RequestException as e:
        st.error(f"API Request Error: {e}")