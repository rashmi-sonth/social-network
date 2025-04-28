import pandas as pd

# Read raw edge list
with open("facebook_combined.txt", "r") as file:
    lines = file.readlines()

edges = []
for line in lines:
    src, dst = map(int, line.strip().split())
    edges.append((src, dst))
    edges.append((dst, src))  # Add reverse for directed Neo4j relationship

# Create follows.csv
follows_df = pd.DataFrame(edges, columns=["source", "target"])
follows_df.to_csv("follows.csv", index=False)

# Create users.csv (unique nodes)
unique_nodes = set(follows_df["source"]).union(set(follows_df["target"]))
users_df = pd.DataFrame(sorted(list(unique_nodes)), columns=["user_id"])
users_df["username"] = users_df["user_id"].apply(lambda x: f"user{x}")
users_df["name"] = users_df["username"].apply(lambda x: x.title())
users_df["bio"] = "Imported from Facebook dataset"
users_df.to_csv("users.csv", index=False)

print("✅ Created users.csv and follows.csv")
