class UserService:
    def __init__(self, conn):
        self.conn = conn

    # UC-1: Register a user
    def register_user(self, username, email, password, name="", bio=""):
        username = username.strip().lower()
        check_query = "MATCH (u:User {username: $username}) RETURN u"
        if self.conn.execute_query(check_query, {"username": username}):
            print(f"🚫 Error: Username '{username}' already exists.")
            return {"error": "Username already exists."}

        create_query = """
        CREATE (u:User {
            username: $username,
            email: $email,
            password: $password,
            name: $name,
            bio: $bio
        })
        """
        self.conn.execute_query(create_query, {
            "username": username,
            "email": email,
            "password": password,
            "name": name,
            "bio": bio
        })
        print(f"✅ User '{username}' registered successfully.")
        return {"success": True}

    # UC-2: Login
    def login_user(self, username, password):
        query = """
        MATCH (u:User {username: $username, password: $password})
        RETURN u
        """
        result = self.conn.execute_query(query, {"username": username, "password": password})
        if result:
            print(f"✅ User '{username}' logged in successfully.")
        else:
            print(f"🚫 Login failed for user '{username}'. Incorrect username or password.")
        return bool(result)

    # UC-3: View Profile
    def view_profile(self, username):
        query = "MATCH (u:User {username: $username}) RETURN u"
        result = self.conn.execute_query(query, {"username": username})
        if result:
            user = result[0]["u"]
            print("\n--- 📄 User Profile ---")
            print("👤 Name:", user.get("name", "N/A"))
            print("🆔 Username:", user.get("username", "N/A"))
            print("📧 Email:", user.get("email", "N/A"))
            print("📝 Bio:", user.get("bio", "N/A"))
            print("-----------------------")
            return {
                "name": user.get("name", ""),
                "username": user.get("username", ""),
                "email": user.get("email", ""),
                "bio": user.get("bio", "")
            }
        print(f"User '{username}' not found.")
        return {"message": "User not found"}

    # UC-4: Edit Profile
    def edit_profile(self, username, new_name=None, new_bio=None, new_email=None, new_password=None):
        set_clauses = []
        params = {"username": username}

        # in all cases, we allow users to pass an empty string to clear the field
        if new_name is not None:
            set_clauses.append("u.name = $name")
            params["name"] = new_name
        if new_bio is not None:
            set_clauses.append("u.bio = $bio")
            params["bio"] = new_bio
        if new_email is not None:
            if "@" in new_email or new_email == "":
                 set_clauses.append("u.email = $email")
                 params["email"] = new_email
            else:
                 print(f"Warning: Invalid email format '{new_email}' provided. Email not updated.")
                 pass
        if new_password is not None and new_password != "": # only update if non-empty password provided
            set_clauses.append("u.password = $password")
            params["password"] = new_password # passwords are stored plainly

        # check if we actually make changes
        if not set_clauses:
            print(f"No valid fields provided to update for user '{username}'.")
            return True

        # if there are updates, construct the query + run it
        query = f"""
        MATCH (u:User {{username: $username}})
        SET {', '.join(set_clauses)}
        RETURN u
        """
        try:
            result = self.conn.execute_query(query, params)
            if result:
                print(f"Profile for user '{username}' updated successfully.")
                return True
            else:
                print(f"Failed to update profile for user '{username}'.")
                return False
        except Exception as e:
            print(f"Database error during profile update for {username}: {e}")
            return False

    # UC-5: Follow
    def follow_user(self, follower, followee):
        # check if both the follower and followee exist
        check_users_query = """
        MATCH (a:User {username: $follower}), (b:User {username: $followee})
        RETURN a, b
        """
        users = self.conn.execute_query(check_users_query, {"follower": follower, "followee": followee})

        if not users:
            check_followee_query = "MATCH (b:User {username: $followee}) RETURN b"
            followee_exists = self.conn.execute_query(check_followee_query, {"followee": followee})

            # case for if user is trying to follow a non-existent user
            if not followee_exists:
                print(f"Error: User '{followee}' does not exist. Cannot follow.")
                return False

            # case for if current user doens't exist... this should never hit
            print(f"Error: User '{follower}' does not exist. Cannot initiate follow.")
            return False


        # check if relationship already exists (follower -> followee)
        check_follows_query = """
        MATCH (:User {username: $follower})-[r:FOLLOWS]->(:User {username: $followee})
        RETURN r
        """
        already_follows = self.conn.execute_query(check_follows_query, {"follower": follower, "followee": followee})
        if already_follows:
            print(f"User '{follower}' is already following '{followee}'.")
            return False

        # if both users exist + relationship doesn't yet exist, create the following relationship
        query = """
        MATCH (a:User {username: $follower}), (b:User {username: $followee})
        MERGE (a)-[:FOLLOWS]->(b)
        """
        self.conn.execute_query(query, {"follower": follower, "followee": followee})
        print(f"👤 {follower} is now following 👤 {followee}")
        return True

    # UC-6: Unfollow
    def unfollow_user(self, follower, followee):
        # check if the relationship (follower -> followee) exists
        check_follows_query = """
        MATCH (a:User {username: $follower})-[r:FOLLOWS]->(b:User {username: $followee})
        RETURN r
        """
        relationship_exists = self.conn.execute_query(check_follows_query, {"follower": follower, "followee": followee})

        # case for if the user is trying to unfollow a non-existent user
        if not relationship_exists:
            print(f"User '{follower}' is not following '{followee}'. Cannot unfollow.")
            return False

        # if so, delete it
        query = """
        MATCH (a:User {username: $follower})-[r:FOLLOWS]->(b:User {username: $followee})
        DELETE r
        """
        self.conn.execute_query(query, {"follower": follower, "followee": followee})
        print(f"👤 {follower} has unfollowed 👤 {followee}")
        return True

    # UC-7a: View who you follow
    def view_following(self, username):
        query = """
        MATCH (:User {username: $username})-[:FOLLOWS]->(f:User)
        RETURN f.username AS following
        """
        results = self.conn.execute_query(query, {"username": username})
        following_list = [r["following"] for r in results]
        print(f"\n--- 📍 Users followed by '{username}' ---")
        if following_list:
            for followed_user in following_list:
                print(f"👤 {followed_user}")
        else:
            print(f"'{username}' is not following anyone.")
        print("--------------------------------------")
        return following_list

    # UC-7b: View your followers
    def view_followers(self, username):
        query = """
        MATCH (f:User)-[:FOLLOWS]->(:User {username: $username})
        RETURN f.username AS follower
        """
        results = self.conn.execute_query(query, {"username": username})
        follower_list = [r["follower"] for r in results]
        print(f"\n--- 👥 Followers of '{username}' ---")
        if follower_list:
            for follower_user in follower_list:
                print(f"👤 {follower_user}")
        else:
            print(f"'{username}' has no followers.")
        print("---------------------------------")
        return follower_list

    # UC-8: Mutual connections
    def view_mutual_connections(self, user1, user2):
        query = """
        MATCH (u1:User {username: $user1})-[:FOLLOWS]->(m:User)<-[:FOLLOWS]-(u2:User {username: $user2})
        RETURN m.username AS mutual
        """
        results = self.conn.execute_query(query, {"user1": user1, "user2": user2})
        mutual_list = [r["mutual"] for r in results]
        print(f"\n--- 🤝 Mutual Connections: '{user1}' & '{user2}' ---")
        if mutual_list:
            for mutual_user in mutual_list:
                print(f"👥 {mutual_user}")
        else:
            print(f"No mutual connections found between '{user1}' and '{user2}'.")
        print("----------------------------------------------------------")
        return mutual_list

    # UC-9: Friend recommendations
    def recommend_users_to_follow(self, username):
        query = """
        MATCH (me:User {username: $username})-[:FOLLOWS]->(:User)-[:FOLLOWS]->(rec:User)
        WHERE NOT (me)-[:FOLLOWS]->(rec) AND me <> rec
        RETURN DISTINCT rec.username AS recommended LIMIT 5
        """
        results = self.conn.execute_query(query, {"username": username})
        recommendations = [r["recommended"] for r in results]
        print(f"\n--- 💡 Friends recommendations for '{username}' ---")
        if recommendations:
            for recommended_user in recommendations:
                print(f"👤 {recommended_user}")
        else:
            print(f"No recommendations found for '{username}' at this time.")
        print("------------------------------------------------")
        return recommendations

    # UC-10: Search users
    def search_users(self, keyword):
        query = """
        MATCH (u:User)
        WHERE toLower(u.username) CONTAINS toLower($keyword) OR toLower(u.name) CONTAINS toLower($keyword)
        RETURN u.username AS username, u.name AS name LIMIT 10
        """
        results = self.conn.execute_query(query, {"keyword": keyword})
        search_results = [{"username": r["username"], "name": r["name"]} for r in results]
        print(f"\n--- 🔎 Search results for '{keyword}' ---")
        if search_results:
            for user_info in search_results:
                print(f"👤 Username: {user_info['username']:10} | Name: {user_info['name']}")
        else:
            print(f"No users found matching '{keyword}'.")
        print("--------------------------------------")
        return search_results

    # UC-11: Popular users
    def explore_popular_users(self):
        query = """
        MATCH (u:User)<-[:FOLLOWS]-(f:User)
        RETURN u.username AS user, COUNT(f) AS followers
        ORDER BY followers DESC
        LIMIT 5
        """
        results = self.conn.execute_query(query)
        popular_users = [{"user": r["user"], "followers": r["followers"]} for r in results]
        print("\n--- 🔥 Popular Users ---")
        if popular_users:
            for user_info in popular_users:
                print(f"👤 {user_info['user']:<10} - Followers: {user_info['followers']}")
        else:
            print("No popular users found yet.")
        print("------------------------")
        return popular_users
