import streamlit as st
import pandas as pd
import numpy as np

# Set the page configuration to use a wide layout
st.set_page_config(page_title="Recommending Songs For You", layout="wide")

# Load data
artists_df = pd.read_csv('artists_gp3.dat', delimiter='\t', names=['id', 'name', 'url', 'pictureURL'], skiprows=1)
user_artists_df = pd.read_csv('user_artists_gp3.dat', delimiter='\t', names=['userID', 'artistID', 'weight'], skiprows=1)
scraped_data_df = pd.read_csv('scraped_data_df.csv', delimiter=';', names=['Artist Name', 'Top Track', 'Track Picture URL', 'Track Link', 'Artist Picture URL'], header=None)

# Placeholder image URL for missing or invalid track pictures
placeholder_image_url = 'https://via.placeholder.com/150'

# Function to get top artists based on user ID
def get_top_artists(user_id):
    try:
        user_data = user_artists_df[user_artists_df['userID'] == user_id]
        artist_interactions = user_data.groupby('artistID')['weight'].sum()
        artist_interactions_sorted = artist_interactions.sort_values(ascending=False)
        top_artist_ids = artist_interactions_sorted.head(5).index.tolist()
        top_artists = artists_df[artists_df['id'].isin(top_artist_ids)]['name'].tolist()
        return top_artists
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# Function to get music recommendations for a user
def get_music_recommendations(user_id):
    top_artists = get_top_artists(user_id)[:5]
    top_artist_ids = artists_df[artists_df['name'].isin(top_artists)]['id'].tolist()

    similar_users = user_artists_df[(user_artists_df['artistID'].isin(top_artist_ids)) & (user_artists_df['userID'] != user_id)]
    similar_users = similar_users.groupby('userID').filter(lambda x: len(x) <= 3)

    initial_recommendations = user_artists_df[
        user_artists_df['userID'].isin(similar_users['userID']) & 
        (~user_artists_df['artistID'].isin(top_artist_ids))
    ].groupby('artistID')['weight'].sum().sort_values(ascending=False)

    recommended_artist_ids = initial_recommendations.index.tolist()

    # Supplement recommendations if fewer than 5 are found
    if len(recommended_artist_ids) < 5:
        all_artist_ids = user_artists_df.groupby('artistID')['weight'].sum().sort_values(ascending=False).index.tolist()
        # Exclude already chosen or user's top artists
        supplemental_artist_ids = [id for id in all_artist_ids if id not in recommended_artist_ids and id not in top_artist_ids][:5 - len(recommended_artist_ids)]
        recommended_artist_ids.extend(supplemental_artist_ids)

    recommendations = []
    for artist_id in recommended_artist_ids[:5]:  # Ensure up to 5 recommendations
        artist_info = artists_df[artists_df['id'] == artist_id]
        artist_name = artist_info['name'].iloc[0] if not artist_info.empty else "Unknown Artist"
        track_info = scraped_data_df[scraped_data_df['Artist Name'].str.lower() == artist_name.lower()].head(1)
        
        if not track_info.empty:
            track = track_info.iloc[0]
            image_url = track['Track Picture URL'] if track['Track Picture URL'] and track['Track Picture URL'] != "Not Found" else placeholder_image_url
            recommendations.append({
                'Artist Name': artist_name,
                'Top Track': track['Top Track'],
                'Track Link': track['Track Link'],
                'Track Picture URL': image_url
            })
        else:
            # Fallback if no specific track info is available
            recommendations.append({
                'Artist Name': artist_name,
                'Top Track': "Track information not available",
                'Track Link': "",
                'Track Picture URL': placeholder_image_url
            })

    return recommendations[:5]  # Ensure only 5 recommendations are returned

# Function to add a new user's favorite artists to the DataFrame
def add_new_user_favorites(unique_id, favorite_artists):
    # Map artist names to IDs
    artist_ids = artists_df[artists_df['name'].isin(favorite_artists)]['id']
    # Create new user rows for user_artists_df
    new_rows = [{'userID': unique_id, 'artistID': artist_id, 'weight': 1} for artist_id in artist_ids]
    # Append new user data
    global user_artists_df
    user_artists_df = user_artists_df.append(new_rows, ignore_index=True)

def main():
    # Custom CSS to inject into the Streamlit app for changing background color
    background_color = "#FFFFFF"
    text_color = "#000000"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {background_color};
            color: {text_color};
        }}
        #MainMenu, footer {{
            visibility: hidden;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title('**Top Artists and Tracks for User**')
    
    new_user = st.checkbox('I am a new user')
    if new_user:
        favorite_artists = st.multiselect('Select your three favorite artists:', artists_df['name'].tolist())
        if len(favorite_artists) == 3 and st.button("Get Recommendations"):
            unique_id = np.random.randint(1000, 10000)
            # Save new user's favorite artists
            add_new_user_favorites(unique_id, favorite_artists)
            st.write(f"Your unique user ID: {unique_id}")
            recommendations = get_music_recommendations(unique_id)
            for rec in recommendations:
                st.write(f"**Artist:** {rec['Artist Name']}, **Track:** {rec['Top Track']}")
                st.image(rec['Track Picture URL'], caption=rec['Top Track'], width=150)
                st.markdown(f"[Play Track]({rec['Track Link']})")
        else:
            st.warning('Please select exactly three artists.')

    user_id_input = st.text_input('Or enter your User ID:', '')
    if user_id_input:
        user_id = int(user_id_input)
        top_artists = get_top_artists(user_id)
        recommendations = get_music_recommendations(user_id)
        
        # Display the top artists for the existing user
        st.subheader("**Your Top Artists:**")
        if top_artists:
            for artist_name in top_artists:
                top_track_info = scraped_data_df[scraped_data_df['Artist Name'].str.lower() == artist_name.lower()].head(1)
                for _, track in top_track_info.iterrows():
                    image_url = track['Track Picture URL'] if track['Track Picture URL'] and track['Track Picture URL'] != "Not Found" else placeholder_image_url
                    st.write(f"**Artist:** {artist_name}, **Top Track:** {track['Top Track']}")
                    st.image(image_url, caption=track['Top Track'], width=150)
                    st.markdown(f"[Play Track]({track['Track Link']})")
                    st.write("---")
        else:
            st.write("No top artists found for this user ID.")
        
        # Fetch and display recommendations for the existing user
        recommendations = get_music_recommendations(user_id)
        st.subheader("**Recommended Artists and Tracks:**")
        if recommendations:
            for rec in recommendations:
                artist_name = rec['Artist Name']
                track_title = rec['Top Track']
                track_link = rec['Track Link']
                track_picture_url = rec['Track Picture URL']
                
                st.write(f"**Artist:** {artist_name}, **Track:** {track_title}")
                st.image(track_picture_url, caption=track_title, width=150)
                st.markdown(f"[Play Track]({track_link})")
                st.write("---")
        else:
            st.write("No recommendations available for this user ID.")

if __name__ == "__main__":
    main()
