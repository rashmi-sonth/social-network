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
                        print("Leave any field blank to keep its current value.")

                        current_profile = user_service.view_profile(username)  # reuse view_profile method
                        print(f"Current Name: {current_profile.get('name', 'N/A')}")
                        print(f"Current Email: {current_profile.get('email', 'N/A')}")
                        print(f"Current Bio: {current_profile.get('bio', 'N/A')}")

                        new_name_input = input("Enter new name (or press Enter to skip): ").strip()
                        new_email_input = input("Enter new email (or press Enter to skip): ").strip()
                        new_bio_input = input("Enter new bio (or press Enter to skip): ").strip()
                        new_password_input = input("Enter new password (or press Enter to skip): ")

                        name_to_update = new_name_input if new_name_input else None
                        email_to_update = new_email_input if new_email_input else None
                        bio_to_update = new_bio_input if new_bio_input else None
                        password_to_update = new_password_input if new_password_input else None

                        if (name_to_update is None and
                            email_to_update is None and
                            bio_to_update is None and
                            password_to_update is None):
                            print("No changes entered.")
                        else:
                            user_service.edit_profile(
                                username,
                                new_name=name_to_update,
                                new_bio=bio_to_update,
                                new_email=email_to_update,
                                new_password=password_to_update
                            )
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
