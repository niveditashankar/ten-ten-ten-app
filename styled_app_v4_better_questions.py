import streamlit as st
import openai

# Initialize OpenAI client using secure secret key from Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page styling
st.set_page_config(page_title="10-10-10 Decision Tool", layout="centered")
st.markdown("""
<style>
    .main {
        background-color: #F9F7F3;
    }
    .stApp {
        max-width: 800px;
        margin: auto;
        padding: 40px;
        background-color: #FFFFFF;
        border-radius: 20px;
        box-shadow: 0px 8px 30px rgba(0, 0, 0, 0.05);
    }
    h1 {
        font-size: 40px;
        font-family: Georgia, serif;
        color: #3C2A1E;
    }
    h2, h3 {
        font-family: Georgia, serif;
        color: #594C3E;
    }
    textarea, input, select {
        font-family: Georgia, serif !important;
        font-size: 16px !important;
        padding: 10px !important;
    }
    .stButton>button {
        background-color: #D19E91;
        color: white;
        font-family: Georgia, serif;
        border-radius: 8px;
        padding: 0.6em 1.6em;
        margin-top: 1em;
    }
    .stButton>button:hover {
        background-color: #c68a7d;
    }
    .small-note {
        font-size: 0.88em;
        color: #6E6259;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Session setup
if "page" not in st.session_state:
    st.session_state["page"] = "decision"

# Step 1: Decision
if st.session_state["page"] == "decision":
    st.title("10-10-10 Decision Tool")
    st.markdown("### 🧡 Step 1: What's the decision you're facing?")
    st.markdown("<p class='small-note'>Think of a real choice you're weighing right now.</p>", unsafe_allow_html=True)
    decision = st.text_input("Your decision", placeholder="e.g., Should I take the job in a new city?")
    if decision:
        st.session_state["decision"] = decision
        if st.button("Next →"):
            st.session_state["page"] = "values"

# Step 2: Values
if st.session_state["page"] == "values":
    st.markdown("### 🌿 Step 2: Know Your Values")
    st.markdown("<p class='small-note'>Pick exactly two for each category.</p>", unsafe_allow_html=True)
    values = [
        "Scope", "Radius", "Familycentrism", "Non Sibi", "Luminance",
        "Agency", "Workcentrism", "Eudaimonia", "Achievement", "Affluence",
        "Voice", "Beholderism", "Belonging", "Place", "Cosmos"
    ]
    must_have = st.multiselect("✅ Values you can't live without", values, max_selections=2)
    dont_care = st.multiselect("❌ Values you don't care about", values, max_selections=2)
    nice_to_have = st.multiselect("🌥️ Values that are nice to have", values, max_selections=2)
    if len(must_have) == 2 and len(dont_care) == 2 and len(nice_to_have) == 2:
        st.session_state["values"] = {
            "must_have": must_have,
            "dont_care": dont_care,
            "nice_to_have": nice_to_have
        }
        if st.button("Next → Reflection"):
            st.session_state["page"] = "reflection"

# Step 3: Reflection
if st.session_state["page"] == "reflection":
    st.markdown("### 🔮 Step 3: Reflect with 10-10-10")
    st.markdown("<p class='small-note'>How might this decision feel in the future? Think deeply. There’s no right or wrong here.</p>", unsafe_allow_html=True)
    ten_min = st.text_area("🕒 If you make this decision, how will it feel 10 minutes from now?")
    ten_months = st.text_area("🗓️ If you make this decision, how might your life look 10 months from now?")
    ten_years = st.text_area("🕰️ If you make this decision, how might it matter 10 years from now?")
    is_complete = all([ten_min.strip(), ten_months.strip(), ten_years.strip()])
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ Generate Insight"):
        if is_complete:
            st.session_state["reflection"] = {
                "10min": ten_min.strip(),
                "10months": ten_months.strip(),
                "10years": ten_years.strip()
            }
            st.session_state["page"] = "summary"
        else:
            st.warning("Please complete all three reflections before generating insight.")

# Step 4: Summary
if st.session_state["page"] == "summary":
    st.markdown("### 💡 Step 4: Insight Summary")
    prompt = f"""
    The user is making this decision: {st.session_state['decision']}
    They can't live without: {', '.join(st.session_state['values']['must_have'])}
    They don't care about: {', '.join(st.session_state['values']['dont_care'])}
    They find these nice to have: {', '.join(st.session_state['values']['nice_to_have'])}

    Reflections:
    - 10 Minutes: {st.session_state['reflection']['10min']}
    - 10 Months: {st.session_state['reflection']['10months']}
    - 10 Years: {st.session_state['reflection']['10years']}

    Provide a warm and motivating summary of how these reflections align with their values, and one concrete action they can take this week.
    """
    with st.spinner("Reflecting and writing your insight..."):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        ai_output = response.choices[0].message.content
        st.success("Here’s what we noticed from your answers:")
        st.markdown(ai_output)
