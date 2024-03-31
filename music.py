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

def add_new_user_favorites(unique_id, favorite_artists):
    artist_ids = artists_df[artists_df['name'].isin(favorite_artists)]['id'].tolist()
    new_rows = pd.DataFrame([{'userID': unique_id, 'artistID': artist_id, 'weight': 1} for artist_id in artist_ids])
    global user_artists_df
    user_artists_df = pd.concat([user_artists_df, new_rows], ignore_index=True)

def display_artists_and_tracks(section_title, artists_tracks):
    st.subheader(section_title)
    if artists_tracks:
        for artist_track in artists_tracks:
            artist_name = artist_track['Artist Name']
            track_title = artist_track['Top Track']
            track_link = artist_track['Track Link']
            track_picture_url = artist_track['Track Picture URL']
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(track_picture_url, caption=track_title, width=150)
            with col2:
                st.write(f"**Artist:** {artist_name}")
                st.write(f"**Track:** {track_title}")
                st.markdown(f"[Play Track]({track_link})")
            st.write("---")
    else:
        st.write("No information available.")

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

    # New user functionality
    new_user = st.checkbox('I am a new user')
    if new_user:
        favorite_artists = st.multiselect('Select your three favorite artists:', artists_df['name'].tolist())
        if len(favorite_artists) == 3:
            unique_id = np.random.randint(1000, 10000)
            add_new_user_favorites(unique_id, favorite_artists)
            st.write(f"Your unique user ID: {unique_id}")
            recommendations = get_music_recommendations(unique_id)
            display_artists_and_tracks("**Recommended Artists and Tracks for New User:**", recommendations)
        else:
            st.warning('Please select exactly three artists.')

    user_id = st.text_input('Enter User ID:', '')

    if st.button('Submit') and user_id:
        user_id = int(user_id)
        top_artists = get_top_artists(user_id)
        
        left, right = st.columns(2)
        
        with left:
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
                st.write("No top artists found.")
                
        with right:
            st.subheader("**Recommended Artists and Tracks:**")
            recommendations = get_music_recommendations(user_id)
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
                st.write("No recommendations available.")

if __name__ == "__main__":
    main()
 