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
        top_artists = get_top_artists(user_id)
        if top_artists:
            st.write(f"Top artists for User ID {user_id}:")
            for i, artist_name in enumerate(top_artists, start=1):
                st.write(f"{i}. {artist_name}")
                # Get the picture URL for the current artist
                artist_row = artists_df.loc[artists_df['name'] == artist_name]
                picture_url = artist_row['pictureURL'].iloc[0] if not artist_row.empty else None
                if picture_url:
                    try:
                        st.image(picture_url, caption=artist_name, use_column_width=True)
                    except Exception as e:
                        st.write(f"Error displaying image for {artist_name}: {e}")
                else:
                    st.write(f"No picture available for {artist_name}")
                
                # Create a hyperlink to the artist's page
                artist_url = artist_row['url'].iloc[0] if not artist_row.empty else None
                if artist_url:
                    st.markdown(f"[Click here to see the artist]({artist_url})")
                else:
                    st.write("No artist page available")
        else:
            st.write("Invalid User ID or User not found: Please enter a valid User ID (integer).")
            st.markdown('<span style="color:red">Wait for the next update if you are a new user</span>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()