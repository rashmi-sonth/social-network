import streamlit as st
from neo4j_conn import Neo4jConnection
from user import UserService

# ─── Setup ─────────────────────────────────────────────────────────
conn = Neo4jConnection()
user_service = UserService(conn)

st.set_page_config(page_title="Social Network", layout="wide")
st.title("🧐 Social Network App")

# Initialize login state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ─── Sidebar Menu ──────────────────────────────────────────────────
menu = ["Register", "Login"]
choice = st.sidebar.selectbox("Choose an action", menu, key="main_menu")

# ─── UC-1: Register ─────────────────────────────────────────────────
if choice == "Register":
    st.subheader("👤 Register a New User")
    u = st.text_input("Username", key="register_username")
    e = st.text_input("Email", key="register_email")
    p = st.text_input("Password", type="password", key="register_password")
    n = st.text_input("Full Name (optional)", key="register_name")
    b = st.text_area("Bio (optional)", key="register_bio")

    if st.button("Register", key="register_btn"):
        res = user_service.register_user(u, e, p, n, b)
        if isinstance(res, dict) and "error" in res:
            st.error(f"❌ {res['error']}")
        else:
            st.success("✅ Registered successfully!")
            st.session_state.username = u
            st.session_state.logged_in = True

# ─── UC-2: Login ────────────────────────────────────────────────────
elif choice == "Login":
    if not st.session_state.logged_in:
        st.subheader("🔐 Login")
        lu = st.text_input("Username", key="login_username")
        lp = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_btn"):
            if user_service.login_user(lu, lp):
                st.session_state.logged_in = True
                st.session_state.username = lu
                st.success(f"✅ Welcome, {lu}!")
            else:
                st.error("❌ Login failed. Try again.")

    if st.session_state.logged_in:
        username = st.session_state.username
        st.success(f"✅ Welcome, {username}!")

        tabs = st.tabs([
            "👤 View Profile", "🗘 Edit Profile", "👥 Follow", "🚫 Unfollow",
            "📍 Following", "👥 Followers", "🔄 Mutual Connections",
            "💡 Recommendations", "🔍 Search Users", "🔥 Popular Users"
        ])

        # ─── UC-3: View Profile ──────────────────────────────────────
        with tabs[0]:
            st.subheader("👤 Your Profile")

            if st.session_state.get("profile_updated", False):
                st.info("🔄 Fetching updated profile…")
                st.session_state.profile_updated = False

            profile = user_service.view_profile(username) or {}
            if profile.get("username"):
                st.markdown(f"""
                <div style="background:#1e1e1e;padding:20px;border-radius:10px;">
                  <h4 style="color:#f1f1f1;">👤 <b>{profile['name'] or profile['username']}</b></h4>
                  <p style="color:#aaa;">📧 <code>{profile['email']}</code></p>
                  <p style="color:#aaa;">🆔 <code>{profile['username']}</code></p>
                  <p style="color:#aaa;">📝 {profile['bio'] or "No bio added yet."}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ Profile not found.")

        # ─── UC-4: Edit Profile ──────────────────────────────────────
        with tabs[1]:
            st.subheader("🗘 Edit Profile")

            # preload once
            if "edit_loaded" not in st.session_state:
                prof = user_service.view_profile(username) or {}
                st.session_state.new_name = prof.get("name", "")
                st.session_state.new_bio  = prof.get("bio", "")
                st.session_state.edit_loaded = True

            name_in = st.text_input(
                "New Name",
                value=st.session_state.new_name,
                key="edit_name",
            )
            bio_in = st.text_area(
                "New Bio",
                value=st.session_state.new_bio,
                key="edit_bio",
            )

            if st.button("Update Profile", key="edit_btn"):
                n = name_in.strip()
                b = bio_in.strip()
                if not n and not b:
                    st.warning("⚠️ Enter name or bio to update.")
                else:
                    # fall back on existing if blank
                    prof = user_service.view_profile(username) or {}
                    final_name = n if n else prof.get("name", "")
                    final_bio  = b if b else prof.get("bio", "")
                    user_service.edit_profile(username, final_name, final_bio)
                    st.session_state.new_name = final_name
                    st.session_state.new_bio  = final_bio
                    st.session_state.profile_updated = True
                    st.success("✅ Profile updated.")

        # ─── UC-5: Follow ─────────────────────────────────────────────
        with tabs[2]:
            st.subheader("👥 Follow Someone")
            to_follow = st.text_input("Username to follow", key="follow_input")
            if st.button("Follow", key="follow_btn"):
                user_service.follow_user(username, to_follow)
                st.success(f"✅ Now following **{to_follow}**")

        # ─── UC-6: Unfollow ───────────────────────────────────────────
        with tabs[3]:
            st.subheader("🚫 Unfollow Someone")
            to_unfollow = st.text_input("Username to unfollow", key="unfollow_input")
            if st.button("Unfollow", key="unfollow_btn"):
                user_service.unfollow_user(username, to_unfollow)
                st.success(f"✅ Unfollowed **{to_unfollow}**")

        # ─── UC-7a: Following ────────────────────────────────────────
        with tabs[4]:
            st.subheader("📍 Following")
            following = user_service.view_following(username) or []
            for u in following:
                st.markdown(f"🔗 **{u}**")

        # ─── UC-7b: Followers ────────────────────────────────────────
        with tabs[5]:
            st.subheader("👥 Followers")
            followers = user_service.view_followers(username) or []
            for u in followers:
                st.markdown(f"👤 **{u}**")

        # ─── UC-8: Mutual Connections ────────────────────────────────
        with tabs[6]:
            st.subheader("🔄 Mutual Connections")
            other = st.text_input("Compare with username", key="mutual_input")
            if st.button("Find Mutual", key="mutual_btn"):
                mutuals = user_service.view_mutual_connections(username, other) or []
                for u in mutuals:
                    st.markdown(f"🧩 **{u}**")

        # ─── UC-9: Recommendations ───────────────────────────────────
        with tabs[7]:
            st.subheader("💡 Friend Recommendations")
            recs = user_service.recommend_users_to_follow(username) or []
            for u in recs:
                st.markdown(f"🌟 **{u}**")

        # ─── UC-10: Search Users ─────────────────────────────────────
        with tabs[8]:
            st.subheader("🔍 Search Users")
            kw = st.text_input("Search keyword", key="search_input")
            if st.button("Search", key="search_btn"):
                results = user_service.search_users(kw) or []
                for r in results:
                    st.markdown(f"🔎 **{r['username']}** — {r.get('name','')}")

        # ─── UC-11: Popular Users ────────────────────────────────────
        with tabs[9]:
            st.subheader("🔥 Most Followed Users")
            popular = user_service.explore_popular_users() or []
            for p in popular:
                st.markdown(f"👑 **{p['user']}** — {p['followers']} followers")

# ─── Tear-down ────────────────────────────────────────────────────
conn.close()
