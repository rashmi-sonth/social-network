from neo4j_conn import Neo4jConnection
from user import UserService

def main():
    conn = Neo4jConnection()
    user_service = UserService(conn)

    print("=== 🧠 Social Network App ===")

    while True:
        print("\n📋 Main Menu:")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            username = input("Username: ")
            email = input("Email: ")
            password = input("Password: ")
            name = input("Full Name (optional): ")
            bio = input("Bio (optional): ")
            user_service.register_user(username, email, password, name, bio)

        elif choice == "2":
            username = input("Username: ")
            password = input("Password: ")

            if user_service.login_user(username, password):
                while True:
                    print(f"\n👋 Welcome, {username}!")
                    print("1. View Profile")
                    print("2. Edit Profile")
                    print("3. Follow a user")
                    print("4. Unfollow a user")
                    print("5. View who you follow")
                    print("6. View your followers")
                    print("7. View mutual connections")
                    print("8. Friend recommendations")
                    print("9. Search users")
                    print("10. Explore popular users")
                    print("11. Logout")

                    action = input("Choose an action: ").strip()
                    print()

                    if action == "1":
                        user_service.view_profile(username)
                    elif action == "2":
                        new_name = input("Enter new name: ")
                        new_bio = input("Enter new bio: ")
                        user_service.edit_profile(username, new_name, new_bio)
                    elif action == "3":
                        target = input("Enter username to follow: ")
                        user_service.follow_user(username, target)
                    elif action == "4":
                        target = input("Enter username to unfollow: ")
                        user_service.unfollow_user(username, target)
                    elif action == "5":
                        user_service.view_following(username)
                    elif action == "6":
                        user_service.view_followers(username)
                    elif action == "7":
                        other = input("Enter another username: ")
                        user_service.view_mutual_connections(username, other)
                    elif action == "8":
                        user_service.recommend_users_to_follow(username)
                    elif action == "9":
                        keyword = input("Search keyword: ")
                        user_service.search_users(keyword)
                    elif action == "10":
                        user_service.explore_popular_users()
                    elif action == "11":
                        print("🚪 Logged out.")
                        break
                    else:
                        print("❌ Invalid choice. Try again.")
            else:
                print("❌ Login failed.")

        elif choice == "3":
            print("👋 Exiting the app.")
            break

        else:
            print("❌ Invalid choice. Try again.")

    conn.close()

if __name__ == "__main__":
    main()
