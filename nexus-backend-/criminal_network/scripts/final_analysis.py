from neo4j import GraphDatabase
from openai import OpenAI

# ==================================================
# 1. NEO4J CONNECTION
# ==================================================

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "Yaswanth@2006"

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


# ==================================================
# 2. GET COMMUNICATION DATA
# ==================================================

call_query = """
MATCH (a:Phone)-[r:CALLED]->(b:Phone)

WITH
    CASE
        WHEN a.number < b.number THEN a.number
        ELSE b.number
    END AS phone1,

    CASE
        WHEN a.number < b.number THEN b.number
        ELSE a.number
    END AS phone2,

    r

RETURN
    phone1,
    phone2,
    count(r) AS call_count,
    sum(r.duration) AS total_duration,
    min(r.date + " " + r.time) AS first_call,
    max(r.date + " " + r.time) AS last_call

ORDER BY call_count DESC
"""


# ==================================================
# 3. GET FINANCIAL DATA
# ==================================================

transaction_query = """
MATCH (a:Account)-[r:TRANSFERRED]->(b:Account)

RETURN
    a.number AS sender,
    b.number AS receiver,
    count(r) AS transaction_count,
    sum(r.amount) AS total_amount,
    min(r.date + " " + r.time) AS first_transaction,
    max(r.date + " " + r.time) AS last_transaction

ORDER BY total_amount DESC
"""


# ==================================================
# 4. GET PERSON-LINKED INFORMATION
# ==================================================

person_query = """
MATCH (p:Person)-[r]->(entity)

RETURN
    p.name AS person,
    type(r) AS relationship,
    labels(entity) AS entity_type,
    coalesce(entity.number, entity.name) AS entity

ORDER BY person
"""


# ==================================================
# 5. RUN QUERIES
# ==================================================

with driver.session(database="neo4j") as session:

    calls = [
        record.data()
        for record in session.run(call_query)
    ]

    transactions = [
        record.data()
        for record in session.run(transaction_query)
    ]

    people = [
        record.data()
        for record in session.run(person_query)
    ]

driver.close()


# ==================================================
# 6. DISPLAY VERIFIED DATA
# ==================================================

print("\n========================================")
print("VERIFIED COMMUNICATION DATA")
print("========================================")

for item in calls:
    print(item)


print("\n========================================")
print("VERIFIED FINANCIAL DATA")
print("========================================")

for item in transactions:
    print(item)


print("\n========================================")
print("ENTITY LINKS")
print("========================================")

for item in people:
    print(item)


# ==================================================
# 7. PREPARE DATA FOR QWEN
# ==================================================

prompt = f"""
You are an evidence analysis assistant.

Analyze ONLY the verified information below.

COMMUNICATION DATA:
{calls}

FINANCIAL TRANSACTION DATA:
{transactions}

PERSON-ENTITY LINKS:
{people}

Create a structured, evidence-based investigation report.

Include:

1. Case overview
2. Identified entities
3. Communication relationships
4. Financial relationships
5. Cross-domain connections
6. Timeline
7. Important factual patterns
8. Evidence requiring verification
9. Limitations
10. Conclusion

STRICT RULES:

- Use ONLY the supplied data.
- Do not invent facts.
- Do not change phone numbers, account numbers,
  dates, times, call counts, durations, or amounts.
- Do not assume two people share a phone number unless
  the supplied data explicitly shows the same phone number
  linked to both people.
- Do not create relationships that are not present in the data.
- A Person USES a phone only when explicitly shown in
  PERSON-ENTITY LINKS.
- A Person OWNS an account only when explicitly shown in
  PERSON-ENTITY LINKS.
- Do not assume that communication means friendship,
  partnership, collaboration, or criminal association.
- Do not assume that a financial transaction is suspicious.
- Do not infer guilt.
- Do not make legal decisions.
- Do not describe transaction amounts as suspicious or
  significant unless the supplied data explicitly establishes this.
- Currency is INR (Indian Rupees).
- Call duration is in seconds.
- Preserve the exact transaction direction.
- Clearly separate FACTS from INTERPRETATION.
- If something cannot be established from the data,
  say "Not established by the available data."
- The investigator must verify all findings against
  the original evidence.

For cross-domain connections, explicitly follow the
person-to-phone and person-to-account mappings.

For example, if:

Person A -> USES -> Phone A
Person A -> OWNS -> Account A

then this does NOT mean Person A shares Phone A
with another person.

Only report relationships that actually exist.
"""


# ==================================================
# 8. CONNECT TO LM STUDIO
# ==================================================

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)


# ==================================================
# 9. SEND EVERYTHING TO QWEN
# ==================================================

response = client.chat.completions.create(
    model="qwen2.5-7b-instruct",

    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],

    temperature=0.1
)


# ==================================================
# 10. GET REPORT
# ==================================================

report = response.choices[0].message.content


print("\n\n========================================")
print("FINAL INVESTIGATION ANALYSIS")
print("========================================\n")

print(report)


# ==================================================
# 11. SAVE REPORT
# ==================================================

with open(
    "output/final_report.txt",
    "w",
    encoding="utf-8"
) as file:

    file.write(report)


print("\n\nReport saved to:")
print("output/final_report.txt")