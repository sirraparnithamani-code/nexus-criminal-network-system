import pandas as pd
from neo4j import GraphDatabase

# =========================
# Neo4j connection
# =========================

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "Yaswanth@2006"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

# =========================
# Read CDR CSV
# =========================

cdr = pd.read_csv("raw_data/cdr.csv")

print("CDR records loaded:", len(cdr))

# =========================
# Insert into Neo4j
# =========================

with driver.session() as session:

    for _, row in cdr.iterrows():

        session.run(
            """
            MERGE (caller:Phone {
                number: $caller
            })

            MERGE (receiver:Phone {
                number: $receiver
            })

            CREATE (caller)-[:CALLED {
                date: $date,
                time: $time,
                duration: $duration
            }]->(receiver)
            """,

            caller=str(row["caller"]),
            receiver=str(row["receiver"]),
            date=str(row["date"]),
            time=str(row["time"]),
            duration=int(row["duration"])
        )

print("CDR successfully imported into Neo4j!")

driver.close()