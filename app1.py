import streamlit as st
import pickle
import pandas as pd
import random
import string
import os

# Load registered users from file if it exists
USER_FILE = "registered_users.pkl"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "wb") as f:
        pickle.dump(users, f)

# ✅ Load users at the start
if "registered_users" not in st.session_state:
    st.session_state.registered_users = load_users()


# ✅ Load Movie Data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ✅ Session State Variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "captcha" not in st.session_state:
    st.session_state.captcha = None
if "registered_users" not in st.session_state:
    st.session_state.registered_users = {}
if "history" not in st.session_state:
    st.session_state.history = []
if "current_user" not in st.session_state:
    st.session_state.current_user = None


# ✅ Function to Generate Captcha
def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# ✅ Function to Recommend Movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    return [movies.iloc[i[0]].title for i in movie_list]


# ✅ Function to Get a Random Movie
def surprise_me():
    return random.choice(movies['title'].values)


# ✅ Authentication System



if not st.session_state.authenticated:
    st.title("🎬 Movie Recommender - Sign In / Sign Up")
    menu = st.radio("Select an option:", ["Sign In", "Sign Up"])

    if menu == "Sign Up":
        email = st.text_input("Email ID")
        if email in st.session_state.registered_users:
            st.warning("⚠️ Email already registered. Please Sign In.")
        else:
            full_name = st.text_input("Full Name")
            password = st.text_input("Password", type="password")
            if st.button("Register"):
                # Save user details
                st.session_state.registered_users[email] = {"password": password, "name": full_name, "history": []}
                save_users(st.session_state.registered_users)  # Save to file
                st.success("✅ Registration successful! Please Sign In.")
                st.rerun()


    elif menu == "Sign In":
        email = st.text_input("Email ID")
        password = st.text_input("Password", type="password")

        if st.button("Sign In"):
            if email in st.session_state.registered_users and st.session_state.registered_users[email][
                "password"] == password:
                st.session_state.authenticated = True
                st.session_state.current_user = email
                st.rerun()
            else:
                st.error("❌ Invalid email ID or password. Please try again.")

# ✅ Movie Recommender System UI
if st.session_state.authenticated:
    user_data = st.session_state.registered_users[st.session_state.current_user]

    st.sidebar.subheader("My Profile")
    st.sidebar.text(f"👤 {user_data['name']}")
    st.sidebar.text(f"📧 {st.session_state.current_user}")

    if st.sidebar.button("Reset Password"):
        new_password = st.sidebar.text_input("New Password", type="password")
        if st.sidebar.button("Confirm Reset"):
            user_data["password"] = new_password
            st.success("🔒 Password Reset Successful!")

    st.sidebar.subheader("📜 Recent Searches")
    for movie in user_data['history'][-10:]:
        st.sidebar.text(f"🎬 {movie}")

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.rerun()

    st.title("Movie Recommender System 🎬")
    selected_movie_name = st.selectbox("🎥 Select a Movie:", movies['title'].values)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        recommend_btn = st.button("🎯 Recommend")
    with col2:
        surprise_btn = st.button("🎲 Surprise Me!")
    with col3:
        reset_btn = st.button("🔄 Reset Selection")

    if recommend_btn:
        names = recommend(selected_movie_name)
        user_data['history'].append(selected_movie_name)
        st.subheader("Recommended Movies:")

        for i in range(0, len(names), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(names):
                    with cols[j]:
                        st.markdown(
                            f"""
                            <div class='movie-card'>
                                <p class='movie-title'>{names[i + j]}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

    if surprise_btn:
        random_movie = surprise_me()
        user_data['history'].append(random_movie)
        st.markdown(
            f"""
            <div class='surprise-box'>
                <p class='surprise-text'>🎉 Try watching: {random_movie}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

if st.session_state.authenticated:
    if reset_btn:
        st.session_state["movie_select"] = movies['title'].values[0]  # Reset to the first movie
        st.rerun()


# ✅ Custom Styling
st.markdown("""
    <style>
        .stApp { 
            background-image: url("https://images.unsplash.com/photo-1640127249305-793865c2efe1?q=80&w=2003&auto=format&fit=crop");
            background-size: cover;
            background-position: center;
        }
        .movie-card { 
            background: rgba(180, 180, 180, 0.2); 
            padding: 15px; 
            border-radius: 15px; 
            text-align: center; 
            color: #FFD700; 
            width: 200px;
            height: 180px;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .movie-card:hover { 
            transform: scale(1.1); 
            box-shadow: 0px 0px 20px #FFD700;
        }
        .surprise-box { 
            background: rgba(0, 0, 0, 0.6); 
            color: white; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center; 
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .surprise-box:hover { 
            transform: scale(1.1);
            box-shadow: 0px 0px 20px white;
        }
    </style>
""", unsafe_allow_html=True)
