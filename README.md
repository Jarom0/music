# music
import streamlit as st
import pandas as pd

# Load Data
artists = pd.read_csv("C:/Users/Omar/Desktop/spotify/artists_gp3.dat", sep="\t", comment="", quote="", header=0)
user_artists = pd.read_csv("C:/Users/Omar/Desktop/spotify/user_artists_gp3.dat", sep="\t")

# Function to get top artists
def top_artists(user_id, num_recommendations):
    user_data = user_artists[user_artists['userID'] == user_id]
    artist_interactions = user_data.groupby('artistID')['weight'].sum().reset_index()
    artist_interactions_sorted = artist_interactions.sort_values(by='weight', ascending=False)
    top_artist_ids = artist_interactions_sorted['artistID'].head(num_recommendations).tolist()
    
    # Filter out non-existent artist IDs
    top_artist_ids = [artist_id for artist_id in top_artist_ids if artist_id in artists['id'].values]
    
    top_artist_names = artists.loc[artists['id'].isin(top_artist_ids), 'name'].tolist()
    top_artist_names = [name if pd.notnull(name) else "Unknown Artist" for name in top_artist_names]  # Replace NaN with "Unknown Artist"
    return top_artist_names

# Define UI
st.title("Top Artists For You")
user_id = st.number_input("Enter your User ID:", min_value=int(user_artists['userID'].min()), max_value=int(user_artists['userID'].max()))
submit_button = st.button("Submit")

# Define server logic
if submit_button:
    if user_id in user_artists['userID'].values:
        top_artists_list = top_artists(user_id, 5)
        st.table(pd.DataFrame({"Artist": top_artists_list}))
    else:
        st.write("User ID not found. Please enter a valid user ID.")
