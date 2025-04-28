class UserService:
    def __init__(self, conn):
        self.conn = conn

    # UC-1: Register a user
    def register_user(self, username, email, password, name="", bio=""):
        username = username.strip().lower()
        check_query = "MATCH (u:User {username: $username}) RETURN u"
        if self.conn.execute_query(check_query, {"username": username}):
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
        return {"success": True}

    # UC-2: Login
    def login_user(self, username, password):
        query = """
        MATCH (u:User {username: $username, password: $password})
        RETURN u
        """
        result = self.conn.execute_query(query, {"username": username, "password": password})
        return bool(result)

    # UC-3: View Profile
    def view_profile(self, username):
        query = "MATCH (u:User {username: $username}) RETURN u"
        result = self.conn.execute_query(query, {"username": username})
        if result:
            user = result[0]["u"]
            return {
                "name": user.get("name", ""),
                "username": user.get("username", ""),
                "email": user.get("email", ""),
                "bio": user.get("bio", "")
            }
        return {"message": "User not found"}

    # UC-4: Edit Profile
    def edit_profile(self, username, new_name, new_bio):
        query = """
        MATCH (u:User {username: $username})
        SET u.name = $name, u.bio = $bio
        """
        self.conn.execute_query(query, {"username": username, "name": new_name, "bio": new_bio})
        return True

    # UC-5: Follow
    def follow_user(self, follower, followee):
        query = """
        MATCH (a:User {username: $follower}), (b:User {username: $followee})
        MERGE (a)-[:FOLLOWS]->(b)
        """
        self.conn.execute_query(query, {"follower": follower, "followee": followee})
        return True

    # UC-6: Unfollow
    def unfollow_user(self, follower, followee):
        query = """
        MATCH (a:User {username: $follower})-[r:FOLLOWS]->(b:User {username: $followee})
        DELETE r
        """
        self.conn.execute_query(query, {"follower": follower, "followee": followee})
        return True

    # UC-7a: View who you follow
    def view_following(self, username):
        query = """
        MATCH (:User {username: $username})-[:FOLLOWS]->(f:User)
        RETURN f.username AS following
        """
        results = self.conn.execute_query(query, {"username": username})
        return [r["following"] for r in results]

    # UC-7b: View your followers
    def view_followers(self, username):
        query = """
        MATCH (f:User)-[:FOLLOWS]->(:User {username: $username})
        RETURN f.username AS follower
        """
        results = self.conn.execute_query(query, {"username": username})
        return [r["follower"] for r in results]

    # UC-8: Mutual connections
    def view_mutual_connections(self, user1, user2):
        query = """
        MATCH (u1:User {username: $user1})-[:FOLLOWS]->(m:User)<-[:FOLLOWS]-(u2:User {username: $user2})
        RETURN m.username AS mutual
        """
        results = self.conn.execute_query(query, {"user1": user1, "user2": user2})
        return [r["mutual"] for r in results]

    # UC-9: Friend recommendations
    def recommend_users_to_follow(self, username):
        query = """
        MATCH (me:User {username: $username})-[:FOLLOWS]->(:User)-[:FOLLOWS]->(rec:User)
        WHERE NOT (me)-[:FOLLOWS]->(rec) AND me <> rec
        RETURN DISTINCT rec.username AS recommended LIMIT 5
        """
        results = self.conn.execute_query(query, {"username": username})
        return [r["recommended"] for r in results]

    # UC-10: Search users
    def search_users(self, keyword):
        query = """
        MATCH (u:User)
        WHERE toLower(u.username) CONTAINS toLower($keyword) OR toLower(u.name) CONTAINS toLower($keyword)
        RETURN u.username AS username, u.name AS name LIMIT 10
        """
        results = self.conn.execute_query(query, {"keyword": keyword})
        return [{"username": r["username"], "name": r["name"]} for r in results]

    # UC-11: Popular users
    def explore_popular_users(self):
        query = """
        MATCH (u:User)<-[:FOLLOWS]-(f:User)
        RETURN u.username AS user, COUNT(f) AS followers
        ORDER BY followers DESC
        LIMIT 5
        """
        results = self.conn.execute_query(query)
        return [{"user": r["user"], "followers": r["followers"]} for r in results]
