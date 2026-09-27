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
# Read transactions
# =========================

transactions = pd.read_csv(
    "raw_data/transactions.csv"
)

print(
    "Transaction records loaded:",
    len(transactions)
)

# =========================
# Insert into Neo4j
# =========================

with driver.session(database="neo4j") as session:

    for _, row in transactions.iterrows():

        session.run(
            """
            MERGE (sender:Account {
        number: $sender
    })

    MERGE (receiver:Account {
        number: $receiver
    })

    MERGE (sender)-[:TRANSFERRED {
        date: $date,
        time: $time,
        amount: $amount
    }]->(receiver)
    """,

    sender=str(row["sender_account"]),
    receiver=str(row["receiver_account"]),
    date=str(row["date"]),
    time=str(row["time"]),
    amount=float(row["amount"])
            
        )

print(
    "Transactions successfully imported into Neo4j!"
)

driver.close()