import streamlit as st
import pandas as pd

# Load data
artists = pd.read_csv('artists_gp3.dat', delimiter='\t', names=['id', 'name', 'url', 'pictureURL'])
user_artists = pd.read_csv('user_artists_gp3.dat', delimiter='\t', names=['userID', 'artistID', 'weight'])

import streamlit as st
import pandas as pd

# Load data
artists_df = pd.read_csv('artists_gp3.dat', delimiter='\t', names=['id', 'name', 'url', 'pictureURL'])
user_artists_df = pd.read_csv('user_artists_gp3.dat', delimiter='\t', names=['userID', 'artistID', 'weight'])

# Function to get top artists
def get_top_artists(user_id):
    try:
        # Filter user data for the given user ID
        user_data = user_artists_df[user_artists_df['userID'] == user_id]
        
        # Aggregate artist interactions by summing the weights
        artist_interactions = user_data.groupby('artistID')['weight'].sum()
        
        # Sort artist interactions by total weight in descending order
        artist_interactions_sorted = artist_interactions.sort_values(ascending=False)
        
        # Get top artist IDs
        top_artist_ids = artist_interactions_sorted.head(5).index.tolist()
        
        # Get top artist names
        top_artists = artists_df[artists_df['id'].isin(top_artist_ids)]['name'].tolist()
        
        return top_artists
    except Exception as e:
        print("Error:", e)
        return None

# Streamlit app
def main():
    st.title('Top Artists for User')
    user_id = st.text_input('Enter User ID:')
    
    if st.button('Submit'):
        try:
            user_id = int(user_id)
            top_artists = get_top_artists(user_id)
            if top_artists:
                st.write(f"Top artists for User ID {user_id}:")
                for i, artist_name in enumerate(top_artists, start=0):
                    st.write(f"{i}. {artist_name}")
            else:
                st.write("Invalid User ID or User not found.")
        except ValueError:
            st.write("Error: Please enter a valid User ID (integer).")

if __name__ == "__main__":
    main()

