from neo4j import GraphDatabase
from openai import OpenAI

# ==========================================
# 1. NEO4J CONNECTION
# ==========================================

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "Yaswanth@2006"

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


# ==========================================
# 2. GET CDR DATA FROM NEO4J
# ==========================================

query = """
MATCH (caller:Phone)-[r:CALLED]->(receiver:Phone)

RETURN
    caller.number AS caller,
    receiver.number AS receiver,
    r.date AS date,
    r.time AS time,
    r.duration AS duration

ORDER BY r.date, r.time
"""

with driver.session(database="neo4j") as session:

    result = session.run(query)

    findings = [record.data() for record in result]

driver.close()


# ==========================================
# 3. DISPLAY DATA RETRIEVED FROM NEO4J
# ==========================================

print("\nDATA RETRIEVED FROM NEO4J")
print("============================")

for finding in findings:
    print(finding)


# ==========================================
# 4. CONNECT TO LM STUDIO
# ==========================================

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)


# ==========================================
# 5. CREATE PROMPT FOR QWEN
# ==========================================

prompt = f"""
You are an investigative data analysis assistant.

Analyze the following Call Detail Record (CDR)
relationships retrieved from a Neo4j graph database.

CDR DATA:
{findings}

Provide an analytical report containing:

1. Important communication relationships
2. Frequently communicating phone numbers
3. Timeline observations
4. Significant patterns
5. Possible connections between entities
6. Points requiring investigator verification

IMPORTANT RULES:

- Use ONLY the information provided.
- Do not invent information.
- Do not claim that anyone is guilty.
- Do not make a legal decision.
- Clearly distinguish observations from assumptions.
- The final decision must be made by the investigator.
"""


# ==========================================
# 6. SEND DATA TO QWEN THROUGH LM STUDIO
# ==========================================

response = client.chat.completions.create(
    model="Qwen2.5 7B Instruct",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.2
)


# ==========================================
# 7. DISPLAY QWEN ANALYSIS
# ==========================================

analysis = response.choices[0].message.content

print("\n\nQWEN ANALYSIS")
print("============================")
print(analysis)