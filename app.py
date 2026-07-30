#========LOAD MODULES====================
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import langchain
from langchain.agents import create_agent
from tavily import TavilyClient
import pytesseract as pyt
import streamlit as st
import os
import time
from PIL import Image
import pandas as pd
import numpy as np

# =================== PREMIUM CSS =====================
st.markdown("""
<style>

/* Main App */
.stApp{
    background:#090909;
    color:white;
}

/* Main Container */
.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
    padding-left:3rem;
    padding-right:3rem;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#111111,#1b1b1b);
    border-right:1px solid #2d2d2d;
}

/* Sidebar Title */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label{
    color:white;
}

/* Text */
h1,h2,h3,h4,h5,h6,p,label{
    color:white !important;
}

/* Input Boxes */
.stTextInput input{
    background:#1a1a1a;
    color:white;
    border:1px solid #444;
    border-radius:12px;
}

textarea{
    background:#141414 !important;
    color:white !important;
    border:2px solid #3b82f6 !important;
    border-radius:15px !important;
}

/* Multi Select */
.stMultiSelect{
    color:white;
}

div[data-baseweb="select"]{
    background:#151515;
    border-radius:12px;
}

/* Success Box */
.stSuccess{
    background:#11331b;
    color:#7CFC98;
    border-radius:15px;
}

/* Error Box */
.stError{
    border-radius:15px;
}

/* Info */
.stInfo{
    border-radius:15px;
}

/* Buttons */
.stButton>button{
    width:100%;
    background:linear-gradient(90deg,#2563eb,#7c3aed);
    color:white;
    font-size:18px;
    font-weight:bold;
    border:none;
    border-radius:12px;
    padding:12px;
    transition:0.4s;
}

.stButton>button:hover{
    transform:scale(1.03);
    background:linear-gradient(90deg,#1d4ed8,#6d28d9);
}

/* Cards */
div[data-testid="stVerticalBlock"]>div{
    background:#141414;
    border-radius:18px;
    padding:18px;
}

/* Image */
img{
    border-radius:18px;
}

/* Scroll Bar */
::-webkit-scrollbar{
    width:8px;
}
::-webkit-scrollbar-thumb{
    background:#3b82f6;
    border-radius:10px;
}

/* Tags */
span[data-baseweb="tag"]{
    background:#2563eb !important;
    color:white !important;
    border-radius:20px !important;
}

/* Password Input */
input[type="password"]{
    background:#1a1a1a !important;
    color:white !important;
}

/* Header */
header{
    background:transparent;
}

/* Toolbar */
[data-testid="stToolbar"]{
    right:2rem;
}

/* Footer Hide */
footer{
    visibility:hidden;
}

/* Menu Hide */
#MainMenu{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# to show web app complete page layout
st.set_page_config(layout="wide")

# to give title


st.sidebar.title("fill important detail")


st.markdown("""
<h1 style='text-align:center;
color:white;
font-size:52px;
font-weight:800;'>

🚀 AI Resume Generator
</h1>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image("bg.png", use_container_width=True)

st.write("""this app helps user to build customized professional resume with latest job apply links""")

st.markdown("""
<p style='text-align:center;
font-size:20px;
color:#BDBDBD;'>

Build ATS Friendly Resume • Latest Jobs • AI Powered

</p>
""", unsafe_allow_html=True)





#==============================API KEYS===================

TAVILY_API_KEY = st.sidebar.text_input("Tavily-API",type="password")
GOOGLE_API_KEY =  st.sidebar.text_input("Gemini-API",type="password")
GROQ_API_KEY =  st.sidebar.text_input("Groq-API",type="password")

all_API=[TAVILY_API_KEY,GOOGLE_API_KEY ,GROQ_API_KEY ]
if not all(all_API):
    st.error("Must give API keys")
    st.stop()
elif all(all_API):
    st.success(" API KEYS LOADED SUCESSFULLY")
else:
    st.info("pass all API keys")

#---------------MULTISELECT OPTION--------------------
options= ["delhi","mumbai","pune","banglore","gurugram/gurgaon"]
location= st.sidebar.multiselect("Select Location" , options=options)

profile_op=["data analytics", "full-stack-dev","AI-Engineer","genAi-dev","data scientist"]
profile=st.sidebar.multiselect("select profile", options=profile_op)



#===========MODEL CREATION==============
model = ChatGoogleGenerativeAI(
    model = 'gemini-3.5-flash-lite',
    google_api_key = GOOGLE_API_KEY
)

# response = model.invoke("Hello Buddy!")
# response.content[-1]["text"]


#===========TOOL 1======================
def search_latest_news_jobs(query):
  """This function helps to fetch lastest
  news or jobs related article using
  tavily"""

  client = TavilyClient(
      api_key  = TAVILY_API_KEY)

  response = client.search(query)
  return response


#==========Agent Creation================
agent = create_agent(
    model = model,
    tools = [search_latest_news_jobs]
)
# agent


#==============MAIN AGENT===============
def main_agent(agent, query):
  """This is the main agent, or leader agent
  orchestrate sub agents"""

  # =========Giving prompt to create detailed prompt
  # for code generation=======================
  prompt = """You are AI assistant and
  below given is prompt, your
  task is to give detailed prompt for
  this.
  You are a professional Resume generator
  where user will give their personal info,
  you have to create detailed Resume
  for students or professional one,
  it must be with dynamic UI and UX and,
  with advanced CSS Professional Designing
  Make sure to give output in HTML format only
  no markdowns allowed
  """

  response = agent.invoke({"messages":[{'role':'user',
                                        'content':prompt}]})
  detailed_prompt = response['messages'][-1].content[-1]['text']

  # ============SAVE PROMPT using File Handling==============

  with open("prompt.txt",'w') as f:
    f.write(detailed_prompt)

  user_details = f"""Below Given is a user details
  generate Resume based on that, if not
  given keep: Default Resume: Python Developer
  user details: {query}"""

  final_prompt = prompt + detailed_prompt + user_details

  # ==================CODE GENERATION=========================

  response = agent.invoke({"messages":[{'role':'user',
                                        'content':final_prompt}]})

  code = response['messages'][-1].content[-1]['text']

  return code


#==========CALLING MAIN AGENT===============
# info = """Name: Samir Khan
#         Email: sksamirkhan@gmail.com
#         Education: 12th from jindal public school
#                    BCA from institue of innovation and management
#         Target Role: DATA ANALYST
#         Location: Dabri,Delhi
#         professional summary: according to you
#         work experiance: TCS 0-2 years as junior data analyst and infosys 0-5 as senior data analyst
#         skills: python,java,sql,excel,power bi, word, canva"""
# code = main_agent(agent,info)
# from IPython import display as DISPLAY
# DISPLAY.HTML(code)



#===========Fetch Latest Domain related Jobs using Tavily==========

def get_jobs(agent,Location = "Noida,Delhi",Profile = "ML Engineer"):
  Location = "Noida,Delhi"
  Profile = "Data Analysts, AI Engineer"
  prompt = f"""Based on user given Job profile,
  fetch latest jobs or job apply article
  using Naukri, Linkedin, Indeed, or all popular
  Job applyplatforms, Show Results with
  JOB PROFILE NAME, LOCATION, SALARY, COMPANY NAME,
  SHOW jobs only related to given
  {Location} and {Profile}, output must be in
  Professional HTML Naukri theme cards with Dynamic Design
  Show atleast Top 10-20 results with direct apply"""

  response = agent.invoke({"messages":[{'role':'user',
                                          'content':prompt}]})

  code = response['messages'][-1].content[-1]['text']

  return code


#==========image generation===========

st.markdown("<br>", unsafe_allow_html=True)

col1,col2,col3 = st.columns([1,6,1])

with col2:
    st.image("bg.png", use_container_width=True)


# ===========👇USER INFORMATION + RESUME BUTTON==================

st.markdown("""
<h2 style='color:#4F8CFF'>
👤 User Information
</h2>
""", unsafe_allow_html=True)

user_info = st.text_area(
    "",
    height=220,
    placeholder="""
Name:
Email:
Phone:

Education:

Experience:

Skills:

Projects:

Target Role:

Achievements:

Languages:
"""
)

generate = st.button("🚀 Generate Professional Resume")

if generate:

    with st.spinner("Generating AI Resume..."):

        code = main_agent(agent,user_info)

        st.success("Resume Generated Successfully")

        st.components.v1.html(
            code,
            height=900,
            scrolling=True
        )



#========CALLING GET JOBS====================
# code = get_jobs(agent)
# DISPLAY.HTML(code)

# ------------SHOW LATEST JOBS BUTTON-------------

job = st.button("💼 Show Latest Jobs")

if job:

    with st.spinner("Searching Latest Jobs..."):

        html = get_jobs(agent)

        st.components.v1.html(
            html,
            height=900,
            scrolling=True
        )



        
                
                    

