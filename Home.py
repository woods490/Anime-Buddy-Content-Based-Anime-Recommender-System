import  streamlit as st
import pandas as pd 
import requests
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title="Overview",
    page_icon='./app/static/RecommenderIcon.PNG'
)


def recommend_anime(anime_matrix, query_anime_name):
    # Step 1: Query anime based on anime_name
    query_anime = anime_matrix[anime_matrix['anime_name'] == query_anime_name]

    if query_anime.empty:
        print(f"Anime '{query_anime_name}' not found.")
        return

    # Step 2: Get animes in the same cluster
    cluster_id = query_anime['cluster'].values[0]
    cluster_animes = anime_matrix[anime_matrix['cluster'] == cluster_id]

    # Step 3: Compute cosine similarities
    query_vector = query_anime.iloc[:, :305].values 
    cluster_vectors = cluster_animes.iloc[:, :305].values

    similarities = cosine_similarity(query_vector, cluster_vectors)[0]

    # Step 4: Calculate weighted score
    weighted_score = 0.5 * similarities + 0.25 * cluster_animes['score'] + 0.25 * cluster_animes['popularity']
    cluster_animes = cluster_animes.copy()
    cluster_animes.loc[:, 'weighted_score'] = weighted_score

    # Step 5: Exclude the queried anime and sort by weighted score in descending order
    sorted_animes = cluster_animes[cluster_animes['anime_name'] != query_anime_name].sort_values(
        by='weighted_score', ascending=False
    )

    # Step 6: Display recommendation lists information    
    return list(sorted_animes['anime_name']), list(sorted_animes['poster_link'])

def filter_and_sort_anime(anime_matrix, selected_genres):
    # Step 1: Get all animes within the selected genres
    filtered_anime = anime_matrix[anime_matrix['genres'].apply(lambda x: all(genre in x for genre in selected_genres))]

    if filtered_anime.empty:
        print("No anime found with the selected genres.")
        return None

    # Step 2: Calculate weighted score
    filtered_anime['weighted_score'] = 0.5 * filtered_anime['score'] + 0.5 * filtered_anime['popularity']

    # Step 3: Sort anime based on the calculated weighted score
    sorted_anime = filtered_anime.sort_values(by='weighted_score', ascending=False)

    return list(sorted_anime['anime_name']), list(sorted_anime['poster_link'])

def get_unique_genres(anime_matrix):
    all_genres = set()
    for genres_list in anime_matrix['genres']:
        for genre in genres_list:
            # Exclude the string "UNKNOWN" (case-insensitive)
            if 'unknown' not in genre.lower():
                all_genres.add(genre)
    
    return list(all_genres)

anime_matrix = pd.read_pickle('./Model Building Phase/Model Building/Model/model_matrix.pkl')

tab1_text = """
🌟 **:orange[Welcome Anime Lovers!]** 🌟

**:orange[Whether you're a seasoned anime enthusiast or just starting your journey, 
you can get a personalized and refined anime experience.]**

**:orange[You can enter the title of your favorite anime, 
and watch as the recommendation engine unveil a carefully curated selection of similar shows, 
taking into account themes, genres, and many other elements.]**

**:orange[You can also search Animes recommendations by 
filtering according to your selected genres]**
"""

tab1, tab2, tab3 = st.tabs(['**:orange[About]**', '**:orange[Find Similar Animes]**', 
                      '**:orange[Find Anime with Your Filter]**'])

with tab1:
    st.write(tab1_text)    

with tab2:
    def clear():
        st.session_state.session_state = {
            'selected_anime_name': None,
            'names': None,
            'posters': None,
            'current_batch': 0,
        }


    if 'session_state' not in st.session_state:
        st.session_state.session_state = {
            'selected_anime_name': None,
            'names': None,
            'posters': None,
            'current_batch': 0,
        }

    selected_anime_name = st.selectbox(
        label="Type or select an Anime from the dropdown",
        options=anime_matrix['anime_name'].values,
        placeholder="Enter Your Favourite Anime"
    )


    if st.button('Show Recommendations'):
        names, posters = recommend_anime(anime_matrix, selected_anime_name)

        # Update session_state with recommendations
        st.session_state.session_state['names'] = names
        st.session_state.session_state['posters'] = posters
        st.session_state.session_state['current_batch'] = 0

    # Display recommendations using session_state
    if st.session_state.session_state['names']:
        batch_size = 5
        current_batch_size = min(batch_size, len(st.session_state.session_state['names']) - st.session_state.session_state['current_batch'])
        cols = st.columns(current_batch_size)


        for i in range(current_batch_size):
            with cols[i]:
                st.text(st.session_state.session_state['names'][st.session_state.session_state['current_batch'] + i])
                st.image(st.session_state.session_state['posters'][st.session_state.session_state['current_batch'] + i])

        st.session_state.session_state['current_batch'] += current_batch_size
        
        if st.session_state.session_state['current_batch'] < len(st.session_state.session_state['names']):
            if st.button("Load More"):
                pass  

    if st.button("Clear"):
        clear()
    
with tab3:
    def clear_tab3():
        st.session_state.session_state_tab3 = {
            'selected_genres': None,
            'names': None,
            'posters': None,
            'current_batch': 0,
        }

    if 'session_state_tab3' not in st.session_state:
        st.session_state.session_state_tab3 = {
            'selected_genres': None,
            'names': None,
            'posters': None,
            'current_batch': 0,
        }

    selected_genres = st.multiselect(
        label="Select Genres",
        options=get_unique_genres(anime_matrix),
        placeholder="Enter Genres"
    )

    if st.button('Show Recommendations', key='tab3'):
        names, posters = filter_and_sort_anime(anime_matrix, selected_genres[0:])
        # Update session_state with recommendations
        st.session_state.session_state_tab3['names'] = names
        st.session_state.session_state_tab3['posters'] = posters
        st.session_state.session_state_tab3['current_batch'] = 0

    if st.session_state.session_state_tab3['names']:
        batch_size = 5
        current_batch_size = min(batch_size, len(st.session_state.session_state_tab3['names']) - st.session_state.session_state_tab3['current_batch'])
        cols = st.columns(current_batch_size)


        for i in range(current_batch_size):
            with cols[i]:
                st.text(st.session_state.session_state_tab3['names'][st.session_state.session_state_tab3['current_batch'] + i])
                st.image(st.session_state.session_state_tab3['posters'][st.session_state.session_state_tab3['current_batch'] + i])

        st.session_state.session_state_tab3['current_batch'] += current_batch_size
    
        if st.session_state.session_state_tab3['current_batch'] < len(st.session_state.session_state_tab3['names']):
            if st.button("Load More", key='tab3.loadmore'):
                pass  

    if st.button("Clear", key='tab3.clear'):
        clear_tab3()

with open('./app/style/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

