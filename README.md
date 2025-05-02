# 🧠 Social Network App (Python + Neo4j)

This is a basic console-based social networking application built using **Python** for the front end and **Neo4j** as the backend graph database. It supports key social features like user registration, following, mutual connection discovery, and friend recommendations — all powered by real-world data.

---

## 📌 Features (Use Cases Implemented)

### ✅ User Management
- **UC-1**: User Registration
- **UC-2**: User Login
- **UC-3**: View Profile
- **UC-4**: Edit Profile

### 🔗 Social Graph Features
- **UC-5**: Follow another user
- **UC-6**: Unfollow a user
- **UC-7**: View friends/connections
- **UC-8**: Mutual connections
- **UC-9**: Friend recommendations (based on 2nd-degree relationships)

### 🔍 Search & Exploration
- **UC-10**: Search users by name or username
- **UC-11**: Explore popular users (most followers)

---

## 🗃 Dataset Info

- **Dataset**: Ego-Facebook (from SNAP)
- **URL**: [https://snap.stanford.edu/data/egofacebook.html](https://snap.stanford.edu/data/egofacebook.html)
- **Description**: Facebook friendship network collected from survey participants.
- **Files Used**:
  - `facebook_combined.txt` → Converted into `users.csv` and `follows.csv`
  - Processed via `convert_facebook_data.py`

---

## 🛠 Project Structure

```
social_network/
├── main.py                     # Console interface
├── user.py                     # All business logic (UC-1 to UC-11)
├── neo4j_conn.py               # DB connection wrapper
├── convert_facebook_data.py    # Converts txt to users.csv + follows.csv
├── users.csv                   # Node data
├── follows.csv                 # Relationship data
├── README.md
└── requirements.txt
```

---

## 💻 How to Run

### 1. Clone and enter the project:
```bash
git clone <your-repo-url>
cd social_network
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Neo4j (Desktop)
- Open Neo4j Desktop
- Create a new DBMS
  - IMPORTANT: our application HARDCODES connection settings in `neo4j_conn.py`
  ```
  class Neo4jConnection:
    def __init__(self, uri="bolt://localhost:7687"):
        self.driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "password"))
  ```
    - We use the default Neo4j URI port of `bolt://localhost:7687`
    - `auth=basic_auth("neo4j", "password"))` allows us to pass in the database name + the DBMS password
      - `neo4j` is the default database created in a new DBMS; if you want to use a different database name, change that in  `neo4j_conn.py`
      - `password` is the DBMS password that you inputted when creating the DBMS. replace this with your actual DBMS password

- Put `users.csv` and `follows.csv` into your **Neo4j DB's import folder**
  - 1. In Neo4j Desktop, hover over the database you want to use
  - 2. Then, click the three dots on the right
  - 3. Click `Open Folder`, and then click `Import`
  - 4. After importing the files properly, they will appear in the `File` section below the list of databases
    - This means Neo4j has access to these files, such that they can use them in cypher commands

- Finally, run the following Cypher commands in Neo4j Browser:
```cypher
LOAD CSV WITH HEADERS FROM 'file:///users.csv' AS row
MERGE (u:User {id: toInteger(row.user_id)})
SET u.username = row.username, u.name = row.name, u.bio = row.bio;

LOAD CSV WITH HEADERS FROM 'file:///follows.csv' AS row
MATCH (a:User {id: toInteger(row.source)})
MATCH (b:User {id: toInteger(row.target)})
MERGE (a)-[:FOLLOWS]->(b);
```

### 4. Run the application
```bash
python main.py
```
