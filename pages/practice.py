import json
import openai as OpenAI
import streamlit as st
import time

from pydantic import BaseModel

class Feedback(BaseModel):
    is_correct: bool
    feedback: str
    is_hint: bool
 
def load_practice_data(file_path):
    """
    Loads the practice session data from a JSON file.
    Expects a top-level key "document" with "question" and "answer" fields.
    """
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def evaluate_command(step, user_input, question):
    """
    Uses an LLM (via OpenAI's API) to evaluate the user's input for a given step.
    Returns a dict with keys:
      - 'is_correct': boolean flag indicating if the user's input is correct.
      - 'feedback': feedback string.
    
    If the user requests a hint (by entering 'hint'), the function returns the hint.
    """
    # Check if the user asked for a hint
    # if user_input.strip().lower() == "hint":
    #     return {"is_correct": False, "feedback": f"Hint: {step['Hint']}"}
    
    # Build a prompt that includes the step details and the user's input
    prompt = (

         "Step Details:\n"
        f"Question: {question}\n"
        f"Step No: {step['Step_No']}\n"
        f"Step Title: {step['Step_Title']}\n"
        f"Command Format: {step['Command_Format']}\n"
        f"Common Mistakes: {step['Common_Mistakes']}\n"
        f"Correct Input: {step['Correct_Input']}\n\n"
        f"Hint: {step['Hint']}\n\n"
        f"User Input: {user_input}\n\n"
        
        f"""You are an evaluator for cryptic command practice. You are given the following context format
                a. Question: It has the main question with details for which multiple steps are the answer.
                b. Step No: Showing the order of the steps followed. This order should be strictly followed.
                c. Step Title: Having the step title of the command. Display it as an instruction to the user
                d. Correct Input: It has the correct answer to the command which should be checked with the user input.
                e. Common Mistakes: It has the common mistakes related to the current step command a user can make. 
                f. Command Format: It has the relevant command format for the correct input with optional fields. 
                g. Hint: It has the relevant hint for the command.
        
        User will enter the command in the terminal and you will evaluate the command. If input is 'hint', you will provide a hint.
        Evaluate the following user input: {user_input} against the Correct Input: {step['Correct_Input']} and do the following:

        If user_input matches with the "Correct Input" : the user's input is correct, set 'is_correct' to true and provide a small congratulatory feedback message. 
        
        If the user_input entered is 'hint', set 'is_correct' to false, set 'is_hint' to try  and use the information in "Hint" and "Command Format" to provide hint as a feedback. Proivde the command format but dont reveal the correct input. Don't mistake hint for an incorrect command.
        
        If user_input is not matching the "Correct Input"(ignoring the optional fields), it is incorrect. Do the following: 
        -> Set 'is_correct' to false and analyze the mistakes in the user input. First compare with the "Correct Input", then compare with the "Command Format" and identify the syntax errors(eg wrong format, missing fields(ignore optional fields), etc).
        -> Use the "Common Mistakes" and "Command Format" information to to provide targetted feedback to the user. Don't be strict on optional fields, its not mandatory to enter them.
        -> Share the type of mistake the user have made but DONT REVEAL the "Correct Input" or "Command Format" in this step. 
        
        Provide neat and clean output for feedback. Use double new line for new sentences. While displaying Command Format, use new line always.
        Wherever there is Command format or anything related to it is in the feedback. Pass those values in this html markdown format ":green-background[`command_syntax`]" where `` should always be inside [].
        Always strictly follow the JSON format, do not add any other text or comments or characters"""
        """Return the result in valid JSON format with exactly two keys: following the format {"is_correct": "boolean", "feedback": "string", "is_hint":"boolean"}.
        """
    )

    # Send the prompt to the LLM using the correct method
    response = OpenAI.beta.chat.completions.parse(
        model="gpt-4o-mini",  # Ensure you are using the correct model
        messages=[
            {"role": "system", "content": """You are a strict evaluator for cryptic command practice. You will always provide output in JSON format and You will always strictly follow this JSON format {"is_correct": boolean, "feedback": "string","is_hint":"boolean"}"""},
            {"role": "user", "content": prompt}
        ],
        response_format=Feedback
    )
    answer = response.choices[0].message.content.strip()
    print(answer)
    # Check if the answer is empty or not valid JSON
    if not answer:
        print("Error: Received an empty response from the API.")
        return {"is_correct": False, "feedback": "No response from the evaluator."}
    
    try:
        # Parse the JSON output from the LLM and return it.
        result = json.loads(answer)
    except json.JSONDecodeError:
        print("Error: Received invalid JSON from the API.")
        return {"is_correct": False, "feedback": "Invalid response format from the evaluator."}
    
    return result

def run_practice_session(data):
    """
    Runs the step-by-step practice session.
    """
    steps = data["answer"]  # List of step dictionaries
    total_steps = len(steps)
    current_step_index = 0
    print("Question:")
    print(data["question"])

    while current_step_index < total_steps:
        step = steps[current_step_index]
        print("\n---------------------------------------------")
        print(f"Step {step['Step_No']}: {step['Step_Title']}")
        print("> Enter your command (or type 'hint' for a hint):")
        
        user_input = input("> ").strip()
        result = evaluate_command(step, user_input, data["question"])
        
        # Provide feedback
        print("\nFeedback:")
        print(result["feedback"])
        # Only move to the next step if the evaluator marks the answer correct
        if result["is_correct"]:
            current_step_index += 1
        else:
            print("Let's try again for this step.")
    
    print("\nCongratulations! You have completed all steps successfully.")



def main():
    if 'instructional_doc' not in st.session_state:
        st.session_state['instructional_doc']={}
    
    if 'api_answer' not in st.session_state:
        st.session_state['api_answer']={}
    
    if 'query' not in st.session_state:
        st.session_state['query']={}
  
    if 'selected_option' not in st.session_state:
        st.session_state['selected_option']={}

    
    
    #print(st.session_state['instructional_doc'])
    OpenAI.api_key = st.secrets["OpenAI_api_key"]
    data = st.session_state['instructional_doc']
    #run_practice_session(data)



    st.set_page_config(layout="wide", page_title="PNR Practice", page_icon="✈️")
    
    # Add CSS for fade-in effect
    st.markdown("""
    <style>
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize current_step_index only if it doesn't exist
    if "current_step_index" not in st.session_state:
        st.session_state["current_step_index"] = 0

    # current_step_index = st.session_state["current_step_index"]
    steps = data["answer"]  # List of step dictionaries
    total_steps = len(steps)
    html_question = f"<body>{data["question"]}</body>"
    
    back_home = st.button('Back')
    if back_home:
          st.switch_page("streamlit.py")

    with st.expander("Question",expanded=True):
        st.write(html_question, unsafe_allow_html=True)
    
    with st.expander("Instructional Document"):
        st.json(st.session_state['instructional_doc'])
    
    col1, col2 = st.columns([1, 2])
    
    # Question Panel


    left_container = col1.container(border=True, height=700)
    left_container.header(":material/electric_bolt: Super Tutor")
    with left_container:
        super_tutor = left_container.chat_message("assistant", avatar=":material/electric_bolt:")
        ai_container = left_container.container(border=False,height=500)
        
    #left_container.button("Ask Hint", key="hint")
    # Terminal Panel
    terminal = col2.container(border=False, key='terminal')
    terminal.header("Terminal")
    container_input=terminal.container(border=False)
    container_output=terminal.container(border=False)
    

    if st.session_state["current_step_index"] < total_steps:
        super_tutor.write(steps[st.session_state['current_step_index']]['Step_Title'])
        # Get user input
        command = container_input.chat_input(placeholder="> Enter your command (or type 'hint' for a hint):")
        print("Command:", command)
        
        if command:
            container_output.code("> " + command)
            with ai_container, st.spinner("Evaluating..."):
                # Call evaluate_command with the current step based on the current_step_index
                print("Current step index:", st.session_state["current_step_index"])
                response = evaluate_command(steps[st.session_state["current_step_index"]], command, data["question"])
                if response:
                    st.session_state["response"] = response
                    if response["is_hint"]:
                        super_tutor.info(st.session_state["response"]["feedback"],icon="💡")

                    elif response["is_correct"]:
                        
                        super_tutor.success(st.session_state["response"]["feedback"], icon="✅")
                    
                    elif response["is_correct"] is not 'True':
                        
                        super_tutor.warning(st.session_state["response"]["feedback"], icon="🔶")
                        

                    if response["is_correct"]:
                        container_output.code(steps[st.session_state["current_step_index"]]["Output"]) 
                        st.session_state["current_step_index"] += 1
                        if st.session_state["current_step_index"] < total_steps:
                            print("Current step index after increment:", st.session_state["current_step_index"])
                            text="Next Step: " +  steps[st.session_state['current_step_index']]['Step_Title'] # Move to the next step
                            super_tutor.write(f"**{text}**")  # Show next step title
                        #st.rerun()
                    else:
                        container_output.code("Please try again")

    if st.session_state["current_step_index"] >= total_steps:
        ai_container.balloons()
        super_tutor.write("\nYou have completed all steps successfully.")

main()


