import streamlit as st
import pandas as pd

# Load data files
artists_df = pd.read_csv('artists_gp3.dat', sep='\t', header=None, names=['artist_id', 'artist_name'])
user_artists_df = pd.read_csv('user_artists_gp3.dat', sep='\t', header=None, names=['user_id', 'artist_id', 'weight'])

# Function to get top 5 artists for a given user ID
def get_top_artists(user_id):
    user_data = user_artists_df[user_artists_df['user_id'] == user_id]
    if user_data.empty:
        return None
    user_top_artists = user_data.groupby('artist_id')['weight'].sum().nlargest(5).reset_index()
    user_top_artists = user_top_artists.merge(artists_df, on='artist_id')
    return user_top_artists[['artist_name', 'weight']]

# Streamlit app
def main():
    st.title('Top Artists for User')
    st.write('Enter your User ID to see your top 5 artists.')

    # User input
    user_id = st.text_input('User ID:')
    if user_id.strip() == '':
        st.warning('Please enter a User ID.')
        return

    try:
        user_id = int(user_id)
    except ValueError:
        st.warning('Invalid User ID. Please enter a valid User ID.')
        return

    if user_id not in user_artists_df['user_id'].unique():
        st.warning('User ID not found in the dataset. Please enter a valid User ID.')
        return

    # Get top artists
    top_artists = get_top_artists(user_id)
    if top_artists is None:
        st.warning('No interaction data found for this User ID.')
    else:
        st.subheader('Top 5 Artists:')
        st.dataframe(top_artists)

if __name__ == "__main__":
    main()
