import requests
import json
import openai as OpenAI
from pydantic import BaseModel
import streamlit as st
import os  # Import os module to check for file existence



class Answer(BaseModel):
  Step_No: int
  Step_Title: str
  Command_Format: str
  Common_Mistakes: str
  Correct_Input: str
  Hint: str
  Output: str


class Instructional_Document(BaseModel):
  question: str
  answer: list[Answer]

OpenAI.api_key = st.secrets["OpenAI_api_key"]


options = data = {
    1: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "How to reissue a ticket with a penalty"},
    2: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "How to reissue a ticket with no additional collection"},
    3: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "How to reissue a ticket with a residual value EMD"},
    4: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "How to issue a new ticket using a voucher EMD"},
    5: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "How to proceed with an an involuntary reissue"},
    6: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "How to reissue a partially used ticket"},
    7: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "How to exchange a fully ununsed ticket"},
    8: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "What to do if the e-ticket coupon status does not allow reissue"},
    9: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "How to exchange a ticket in a new PNR"},
    10: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "How to add a form of payment for an infant"},
    11: {"bsp_arc": "BSP", "manual_atc": "ATC", "db_available": 1, "clean_question": "How to obtain a credit card approval code"},
    12: {"bsp_arc": "BSP", "manual_atc": "ATC", "db_available": 1, "clean_question": "Itinerary/ Name Change - Verify TST"},
    13: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "Not all remaining coupons available in electronic record"},
    14: {"bsp_arc": "BSP", "manual_atc": "ATC", "db_available": 1, "clean_question": "TSM FOP not first Issue"},
    15: {"bsp_arc": "BSP", "manual_atc": "ATC", "db_available": 1, "clean_question": "TST Fop Not First Issue"},
    16: {"bsp_arc": "BSP", "manual_atc": "ATC", "db_available": 1, "clean_question": "New FOP not required for exchange with refund"},
    17: {"bsp_arc": "BSP", "manual_atc": "ATC", "db_available": 1, "clean_question": "Old Fop Required for Exchange Document"},
    18: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "Exchange doc in FO does not match ETKT record"},
    19: {"bsp_arc": "ARC", "manual_atc": "Manual", "db_available": 1, "clean_question": "Exchange doc in FO does not match ETKT record"},
    20: {"bsp_arc": "BSP", "manual_atc": "Manual", "db_available": 1, "clean_question": "Need NVA For Reissue"},
}





def get_skeleton(payment,product,query):
  url = "http://35.154.13.29:8005/search_outcome_v5"

  payload = json.dumps({
    "product": f"{product}", #Manual/ATC
    "payment": f"{payment}", #BSP/ARC
    "query": f"{query}",
    "stream_type": ""
  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  response_json = json.loads(response.text)
  answer = response_json[0]["answer"]
  question = response_json[0]["question"]
  response_data = {
        "answer": response_json[0]["answer"],
        "question": response_json[0]["question"]
    }
  return(response_data)
#print(response.text)
#print(response_json[0]["question"])
# print(len(response_json[0]["answer"]))

def generate_instructional_doc(skeleton_answer, skeleton_question):

  prompt=(f"""
  You have to create an instructional document which will be used for creating a practice scenario for using  Amadeus Cryptic Platform.
  Can you come up with a real-life practice question where the following process steps will be used. Provide the actual values in the command to be used. 
  Here is a step by step process to answer following question "{skeleton_question}" related to amadeus cryptic platform:
  {skeleton_answer}

  Based on the above information, curate an instructional docuement where there will be a question in fthe form of a scenario with all the details and answer in the form of steps with each step having the command details
  The instructional document should have all the steps and required information availbe for the generated scenario. 

  It will follow the following format
  question: This will be the real-life scenario question with all the relevant information mentioned that are needed to be used in the commands and their relevant fields usually denoted in curly braces in Command from the above answer .
  Do not miss any information. Whatever information is being made up that has to be passed in the command fields for every command should be mentioned in the scenario. Eg if a command is RT{'PNR'}, provide dummy PNR information.
  Example of question 
    Create a PNR for Mr. John Smith. Use the following details:<br>
    Contact number: +12135551234<br>
    Ticketing deadline: 20/03/2025 at 1800 hours<br>
    Flight details:<br>
    Flight Number: BA142<br>
    Class: Y (Economy)<br> 
    Number of Seats: 1<br>
    Date: 25/03/2025<br> 
    Origin: LHR (London Heathrow)<br> 
    Destination: JFK (New York John F. Kennedy)
  
  
  answer: List of steps having following fields:
    Step No : Enter the ordered step number
    Step Title : You will have to come up with a title that will shown as an instruction in the practice scenario. Use the approriate title.
    Correct Input : The correct input with relevant values
    Command Format : The general command format without the values
    Common Mistakes:  Possible mistakes user can do in this command while entering
    Hint: Provide a hint to guide the user to enter this command correctly
    Output: Currently just mention Output
  """

  """
  Here's an example of it
  {
    "answer": {
      "Step No": 1,
      "Step Title": "Check Flight Availability for the Given Date and Route",
      "Correct Input": "AN25MARLHRJFK/ABA",
      "Command Format": "AN<date><origin airport code><destination airport code>/A<airline code>",
      "Common Mistakes": "[Incorrect date format (must be DDMMM, e.g., 01JAN); Invalid airport codes (e.g., LHR or JFK are spelled incorrectly and also they should be three-letter codes according to IATA standards) ]",
      "Hint": "AN checks availability for a given date, origin, and destination.",
      "Output": "Correct step"
          },
    }
  """)
    # Send the prompt to the LLM using the correct method

  #print(prompt)
  response = OpenAI.beta.chat.completions.parse(
      model="gpt-4o-mini",  # Ensure you are using the correct model
      messages=[
            {"role": "system", "content": """You are a practice scenario creator for learning Amadeus Cryptic Commands. You will always provide output in JSON format and You will always n"}"""},
            {"role": "user", "content": prompt }
      ],
      response_format=Instructional_Document
    )
    
  answer = response.choices[0].message.content.strip()
  result = json.loads(answer)

  with open(f'/Users/hussainbhinderwala/RAG_pdf/instructional_documents/{skeleton_question}.json', 'w') as json_file:
        json.dump(result, json_file, indent=4)  # Write the result to a JSON file with indentation for readability
  return(result)



if 'instructional_doc' not in st.session_state:
  st.session_state['instructional_doc']={}

if 'api_answer' not in st.session_state:
  st.session_state['api_answer']={}
  
if 'question' not in st.session_state:
  st.session_state['question']={}

if 'query' not in st.session_state:
  st.session_state['query']={}
  
if 'selected_option' not in st.session_state:
  st.session_state['selected_option'] = {}  # Initialize as an empty dictionary


def streamlit_interface():
  st.title("Create Practice scenario")

  query = st.text_input("Enter here", placeholder="What do you want to practice?")
  
  query = st.pills("Suggestions", [option["clean_question"] for option in options.values()], selection_mode="single") #show all the pills with clean_question
  query_json = {"query": query}
  st.session_state["query"].update(query_json)
  
 
    # Extract the selected option details in one line
  selected_option = next((option for option in options.values() if option["clean_question"] == query), None)
    
    # Ensure selected_option is a dictionary before updating session state
  if selected_option is not None:
      st.session_state['selected_option'].update(selected_option)
        
        # Assign values to bsp_arc and manual_atc only if selected_option is valid
      bsp_arc = st.session_state['selected_option']["bsp_arc"]
      manual_atc = st.session_state['selected_option']["manual_atc"]
        
      with st.status("Fetching Answer") as status:
        api_answer = get_skeleton(bsp_arc, manual_atc, query)
        status.update( label="Answer Fetched!", state="complete", expanded=False)
        st.session_state['api_answer'].update(api_answer)
        st.json(api_answer)

      with st.status("Generating Practice Scenario")as scenario:
              # Check if the instructional document already exists
        file_path = f"/Users/hussainbhinderwala/RAG_pdf/instructional_documents/{api_answer['question']}.json"
        if not os.path.exists(file_path):  # If the file does not exist
            inst_doc = generate_instructional_doc(api_answer["answer"], api_answer["question"])
            print("instructional doc ready!")
        else:
            print("Instructional document already exists. Skipping generation.")
            with open(file_path, 'r') as json_file:  # Open the existing file to read its content
                inst_doc = json.load(json_file)  # Load the JSON content from the file
       
        scenario.update( label="Practice Scenario Created!", state="complete", expanded=False)
        st.session_state['instructional_doc'].update(inst_doc)
        st.markdown(st.session_state['instructional_doc']["question"], unsafe_allow_html=True)
        st.json(st.session_state['instructional_doc']["answer"])

      if(st.session_state['instructional_doc']):
        start_practice = st.button("Start Practice", type="primary")
        if start_practice:
          st.switch_page("pages/practice.py")

streamlit_interface()