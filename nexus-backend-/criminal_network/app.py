import streamlit as st
from neo4j import GraphDatabase
from pyvis.network import Network
import streamlit.components.v1 as components
import os
import base64

st.set_page_config(
    page_title="Criminal Network Analysis",
    page_icon="🔍",
    layout="wide"
)


# =====================================================
# NEO4J CONNECTION
# =====================================================

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USERNAME = "neo4j"

# IMPORTANT:
# Put your current Neo4j password here.
NEO4J_PASSWORD = "Yaswanth@2006"


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


# =====================================================
# GET DATA FROM NEO4J
# =====================================================

def get_graph_data():

    query = """
    MATCH (n)-[r]->(m)
    RETURN
        elementId(n) AS source_id,
        labels(n) AS source_labels,
        properties(n) AS source_props,
        type(r) AS relationship,
        properties(r) AS relationship_props,
        elementId(m) AS target_id,
        labels(m) AS target_labels,
        properties(m) AS target_props
    """

    with driver.session(database="neo4j") as session:

        result = session.run(query)

        return [
            record.data()
            for record in result
        ]


# =====================================================
# CREATE INTERACTIVE GRAPH
# =====================================================

def create_graph(data):

    network = Network(
        height="800px",
        width="100%",
        bgcolor="#111111",
        font_color="white",
        directed=True
    )

    added_nodes = set()

    # -------------------------------------------------
    # FIXED POSITIONS
    #
    # Person  -> left
    # Phone   -> center
    # Account -> right
    # -------------------------------------------------

    positions = {

        "Person": [
            (-350, -180),
            (-350, 0),
            (-350, 180)
        ],

        "Phone": [
            (0, -180),
            (0, 0),
            (0, 180)
        ],

        "Account": [
            (350, -180),
            (350, 0),
            (350, 180)
        ]
    }

    counters = {
        "Person": 0,
        "Phone": 0,
        "Account": 0
    }


    # =================================================
    # ADD NODES AND RELATIONSHIPS
    # =================================================

    for row in data:

        source_id = row["source_id"]
        target_id = row["target_id"]

        source_props = row["source_props"]
        target_props = row["target_props"]

        source_labels = row["source_labels"]
        target_labels = row["target_labels"]


        # -------------------------------------------------
        # GET NODE TYPES
        # -------------------------------------------------

        source_type = (
            source_labels[0]
            if source_labels
            else "Unknown"
        )

        target_type = (
            target_labels[0]
            if target_labels
            else "Unknown"
        )


        # -------------------------------------------------
        # GET NODE NAMES
        # -------------------------------------------------

        source_name = (
            source_props.get("name")
            or source_props.get("number")
            or source_id
        )

        target_name = (
            target_props.get("name")
            or target_props.get("number")
            or target_id
        )


        # =================================================
        # SOURCE NODE
        # =================================================

        if source_id not in added_nodes:

            if source_type in positions:

                index = counters[source_type]

                x, y = positions[source_type][
                    index % len(positions[source_type])
                ]

                counters[source_type] += 1

            else:

                x, y = 0, 0


            network.add_node(

                source_id,

                label=str(source_name),

                title=(
                    f"Type: {source_type}<br>"
                    f"Name: {source_name}"
                ),

                x=x,
                y=y,

                physics=False,

                shape="dot",

                size=25,

                # -------------------------------------------------
                # NORMAL TEXT
                # -------------------------------------------------

                font={
                    "size": 16,
                    "face": "Arial",
                    "color": "#FFFFFF",
                    "strokeWidth": 0
                }
            )

            added_nodes.add(source_id)


        # =================================================
        # TARGET NODE
        # =================================================

        if target_id not in added_nodes:

            if target_type in positions:

                index = counters[target_type]

                x, y = positions[target_type][
                    index % len(positions[target_type])
                ]

                counters[target_type] += 1

            else:

                x, y = 0, 0


            network.add_node(

                target_id,

                label=str(target_name),

                title=(
                    f"Type: {target_type}<br>"
                    f"Name: {target_name}"
                ),

                x=x,
                y=y,

                physics=False,

                shape="dot",

                size=25,

                # -------------------------------------------------
                # NORMAL TEXT
                # -------------------------------------------------

                font={
                    "size": 16,
                    "face": "Arial",
                    "color": "#FFFFFF",
                    "strokeWidth": 0
                }
            )

            added_nodes.add(target_id)


        # =================================================
        # RELATIONSHIP
        # =================================================

        relationship = row["relationship"]

        relationship_props = row["relationship_props"]


        network.add_edge(

            source_id,
            target_id,

            label=str(relationship),

            title=str(relationship_props),

            arrows="to",

            # -------------------------------------------------
            # NORMAL RELATIONSHIP TEXT
            # -------------------------------------------------

            font={
                "size": 11,
                "face": "Arial",
                "color": "#FFFFFF",
                "strokeWidth": 0
            },

            smooth={
                "enabled": True,
                "type": "curvedCW"
            }
        )


    # =================================================
    # GRAPH SETTINGS
    # =================================================

    network.set_options("""
    {
        "physics": {
            "enabled": false
        },

        "interaction": {

            "dragNodes": true,

            "dragView": true,

            "zoomView": true,

            "navigationButtons": true,

            "keyboard": true,

            "hover": true
        },

        "layout": {

            "improvedLayout": true
        },

        "edges": {

            "arrows": {

                "to": {

                    "enabled": true,

                    "scaleFactor": 0.8
                }
            },

            "font": {

                "size": 11,

                "face": "Arial",

                "color": "#FFFFFF",

                "strokeWidth": 0
            },

            "smooth": {

                "enabled": true,

                "type": "curvedCW"
            }
        },

        "nodes": {

            "font": {

                "size": 16,

                "face": "Arial",

                "color": "#FFFFFF",

                "strokeWidth": 0
            },

            "borderWidth": 2
        }
    }
    """)


    return network


# =====================================================
# READ FINAL AI REPORT
# =====================================================

def get_report():

    report_path = "output/final_report.txt"


    if not os.path.exists(report_path):

        return (
            "No final report found.\n\n"
            "Run final_analysis.py first."
        )


    with open(
        report_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# =====================================================
# FRONTEND HEADER
# =====================================================

st.title(
    "🔍 Criminal Network Analysis System"
)


st.write(
    "Evidence-based analysis of communication "
    "and financial relationships."
)


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title(
    "Case Information"
)


st.sidebar.write(
    "Case ID: SIH-DEMO-001"
)


st.sidebar.write(
    "Status: Analysis Complete"
)


st.sidebar.divider()


st.sidebar.info(
    "AI-generated findings require investigator verification."
)


# =====================================================
# DASHBOARD
# =====================================================

graph_column, report_column = st.columns(
    [1, 1]
)


# =====================================================
# GRAPH
# =====================================================

with graph_column:

    st.subheader(
        "📊 Network Graph"
    )


    try:

        graph_data = get_graph_data()


        if len(graph_data) == 0:

            st.warning(
                "No relationships found in Neo4j."
            )


        else:

            # ---------------------------------------------
            # CREATE GRAPH
            # ---------------------------------------------

            network = create_graph(
                graph_data
            )


            graph_file = (
                "output/network.html"
            )


            network.save_graph(
                graph_file
            )


            # ---------------------------------------------
            # READ GRAPH HTML
            # ---------------------------------------------

            with open(
                graph_file,
                "r",
                encoding="utf-8"
            ) as file:

                graph_html = file.read()


            # =================================================
            # FULLSCREEN GRAPH BUTTON
            # =================================================

            graph_b64 = base64.b64encode(
                graph_html.encode("utf-8")
            ).decode("utf-8")


            fullscreen_button = f"""

            <style>

            .fullscreen-container {{

                display: flex;

                justify-content: flex-end;

                margin-bottom: 8px;
            }}


            #openFullscreen {{

                padding: 9px 15px;

                background: white;

                color: #111111;

                border: none;

                border-radius: 6px;

                cursor: pointer;

                font-size: 14px;

                font-weight: 500;
            }}


            #openFullscreen:hover {{

                background: #dddddd;
            }}

            </style>


            <div class="fullscreen-container">

                <button id="openFullscreen">

                    ⛶ Open Fullscreen Graph

                </button>

            </div>


            <script>

            const graphData =
                "{graph_b64}";


            document.getElementById(
                "openFullscreen"
            ).onclick = function() {{

                try {{

                    const binary =
                        atob(graphData);


                    const bytes =
                        new Uint8Array(
                            binary.length
                        );


                    for (
                        let i = 0;
                        i < binary.length;
                        i++
                    ) {{

                        bytes[i] =
                            binary.charCodeAt(i);

                    }}


                    const html =
                        new TextDecoder(
                            "utf-8"
                        ).decode(bytes);


                    const blob =
                        new Blob(
                            [html],
                            {{
                                type:
                                "text/html"
                            }}
                        );


                    const url =
                        URL.createObjectURL(
                            blob
                        );


                    window.open(
                        url,
                        "_blank"
                    );

                }}

                catch (error) {{

                    console.error(
                        "Could not open graph:",
                        error
                    );

                }}

            }};

            </script>

            """


            # ---------------------------------------------
            # BUTTON
            # ---------------------------------------------

            components.html(

                fullscreen_button,

                height=55,

                scrolling=False
            )


            # ---------------------------------------------
            # GRAPH
            # ---------------------------------------------

            components.html(

                graph_html,

                height=800,

                scrolling=False
            )


    except Exception as error:

        st.error(
            f"Neo4j connection error: {error}"
        )


# =====================================================
# AI REPORT
# =====================================================

with report_column:

    st.subheader(
        "🤖 AI Investigation Report"
    )


    report = get_report()


    st.text_area(

        "Final Report",

        report,

        height=750
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()


st.caption(

    "The system analyzes evidence and generates "
    "analytical findings. Final decisions remain "
    "with the investigator."

)