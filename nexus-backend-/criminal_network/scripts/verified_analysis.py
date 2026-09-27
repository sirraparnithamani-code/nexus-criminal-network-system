from neo4j import GraphDatabase
from openai import OpenAI

# ==========================================
# NEO4J CONNECTION
# ==========================================

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "Yaswanth@2006"

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


# ==========================================
# GET VERIFIED CALL STATISTICS
# ==========================================

query = """
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

with driver.session(database="neo4j") as session:

    result = session.run(query)

    findings = [record.data() for record in result]

driver.close()


# ==========================================
# DISPLAY VERIFIED FINDINGS
# ==========================================

print("\nVERIFIED FINDINGS FROM NEO4J")
print("=" * 50)

for finding in findings:
    print(finding)


# ==========================================
# PREPARE DATA FOR QWEN
# ==========================================

prompt = f"""
You are an investigative data analysis assistant.

The following information has been calculated directly
from Neo4j from CDR records.

VERIFIED DATA:
{findings}

Generate an evidence-grounded analytical report.

Include:

1. Communication relationships
2. Total number of calls between each pair
3. Total call duration in seconds
4. First and last communication
5. Important communication patterns
6. Investigator verification points

IMPORTANT RULES:

- Treat phone1 and phone2 as an unordered communication pair.
- The call count is already calculated by Neo4j.
- The total duration is already calculated by Neo4j.
- DO NOT recalculate these numbers.
- Do not invent missing information.
- Do not assume who owns a phone number.
- Do not assume friendship, partnership, criminal association,
  or any other relationship.
- Do not declare anyone guilty.
- Do not make a legal decision.
- Clearly separate factual observations from interpretations.
- The investigator makes the final decision.
"""


# ==========================================
# LM STUDIO
# ==========================================

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)


# ==========================================
# SEND TO QWEN
# ==========================================

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


# ==========================================
# DISPLAY REPORT
# ==========================================

analysis = response.choices[0].message.content

print("\n\nFINAL AI ANALYSIS")
print("=" * 50)
print(analysis)