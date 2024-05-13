import os
import smtplib
import ssl
from email.message import EmailMessage
import csv
from textwrap import dedent
from dotenv import load_dotenv
from crewai import Crew, Agent, Task, Process
from tasks import MeetingPrepTasks
from agents import MeetingPrepAgents
from datetime import datetime, timedelta
from crewai_tools import DOCXSearchTool, CSVSearchTool, TXTSearchTool, tool, SerperDevTool

os.environ["OPENAI_API_KEY"] = "sk-proj-iMq8aB6ABRhHHgQod4p4T3BlbkFJvI2j87hwAF6wlmb8EKi3"
os.environ["SERPER_API_KEY"] = "d1b04924fa8092b742ea783991626a950f1a0c1a" # serper.dev API key
os.environ['OPENAI_MODEL_NAME'] =  "gpt-4-0125-preview"   
doc_search = DOCXSearchTool("docs/Employee-Code-of-Conduct.docx")
csv_search = CSVSearchTool('interview_data.csv')
google_search = SerperDevTool()
# ##########################This is for the FAQ Section ######################################################
print("Welcome to FAQ Section of Company XYZ! I'm here to clarify any questions regarding our company's policies. ")
print("----------------------------------------------------------------------------------------------------")
asked_question = input("Ask your question: ")

faq_agent = Agent(
			role='Human Resource Employee',
			goal='Find the section of the document which contains relevant information and summarzie them. ',
			tools=[doc_search],
			backstory=dedent("""\
					As a HR Employee, your mission is to find which sections of the document contains the
                    relevant information and summarize those in a few sentences. If you can't find any keywords then just say 
                    I couldn't find anything in our company's policy regarding this topic . Kindly 
                    contact HR for information on this topic."""),
			verbose=True
		)
def summary_task(question):
		return Task(
			description=dedent(f"""\
				Find all the relevant areas of the document where the words from the question appear and
                summarize them in a few sentences.
				Question: {question}"""),
			expected_output=dedent("""\
				A few sentences summarizing the relevant infomration in the document which 
                conatins the keyword asked in the question. Starts each answer with Our company
                policy states that."""),
			agent=faq_agent
		)


summarize_task = summary_task(asked_question)

crew = Crew(agents=[faq_agent], tasks=[summarize_task])
# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)
##################################################################################################################################

##########################This is for the onboarding section ######################################################
print("")
print("This is the onboarding use case")
name = input("Name: ")
role = input("Role: ")
receiver_email = input("Email: ")

researcher_agent = Agent(
        role="Research Specialist",
        goal='Research the role to find the best practices for the job role and provide links on how to be successful ',
        tools=[google_search],
        backstory=dedent("""\
          As a Research Specialist, your job is to search the web and come up with the best practices and methods
          to be successful at a specific job role and also provide useful links which talk about how to be successful
          in the partciular job role."""),
        verbose=True
      )

def research_task(role):
        return Task(
            description=dedent(f"""\
				generate the best practices and ways a person can successful at the given job role
                Job Role: {role}"""),
            expected_output=dedent("""\
				The best practices and things to do to be successful at the job role along with useful links for reference"""),
            agent=researcher_agent,
        )
set_research_task = research_task(role)

greet_agent = Agent(
        role="Personalized Message Sender",
        goal='Write a personalized message to person and welcome them into the company ',
        backstory=dedent("""\
          Your job is to write a personalized message to the new employee joining the company and talk about company culture and wish
          the employee success in the company"""),
        verbose=True
      )
def onboard_task(name,link):
        return Task(
            description=dedent(f"""\
				onboard the people by wishing good luck and ask them to review the code of conduct
                Employee Code of Conduct Link: {link},
                Name: {name}"""),
            expected_output=dedent("""\
				Output should be formatted like this:
                - Greeting and well wishes 
                - Ask to review Employee Code of Conduct with link 
                - Best Practices to be successful along with links
                - end it with
                Best Regards,
                John McEnroe,
                HR of Company XYZ"""),
            agent=greet_agent,
            context = [set_research_task]
        )
set_onboard_task = onboard_task(name,"https://resources.workable.com/employee-code-of-conduct-company-policy")

crew = Crew(agents=[researcher_agent,greet_agent], tasks=[set_research_task,set_onboard_task])
# Get your crew to work!
result = crew.kickoff()
print("######################")
print(result)



# Define email sender and receiver
email_sender = 'aneeshbsri@gmail.com'
email_password = "rsds xytr dtgz xrme"
email_receiver = receiver_email

# Set the subject and body of the email
subject = 'Welcome to Company XYZ!!!'
body = result

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_receiver
em['Subject'] = subject
em.set_content(body)

# Add SSL (layer of security)
context = ssl.create_default_context()

# Log in and send the email
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_receiver, em.as_string())

print("Email has been sent to",name,"Email:",receiver_email)


###############################################################################################################################################################




###############################################################################################################################################################
# Candidate notes
print("")
print("This is the candidate notes use case")
candidate_name = input("Name: ")
candidate_notes_doc = input("Please enter the link to this candidate's notes:  ")
txt_search = TXTSearchTool(candidate_notes_doc)

notes_agent = Agent(
        role="Candidate Notes Summarizer",
        goal='Summarizes the notes on a candidate ',
        backstory=dedent("""\
          As a Notes Summarizer, your mission is to read through the enitre file
         and summarize them the information in a concise yet informative manner into bullet points. """),
        tools=[txt_search],
        verbose=True
      )

def candidate_notes_task(name):
        return Task(
            description=dedent(f"""\
				Summarize the document into a few detailed bullet points
				Candidate Name: {name}"""),
            expected_output=dedent("""\
                Ensure each bullet point isn't longer than 80 charcters
                Have a list of 5-6 bullet points on notes given about the candidate 
                Use this format for your output:
                Candidate Name : [Candidate Name] 
                - Candidate notes
				"""),
            agent=notes_agent,
        )
candidate_task = candidate_notes_task(candidate_name)

crew = Crew(agents=[notes_agent], tasks=[candidate_task])
# Get your crew to work!
result = crew.kickoff()
print(result)
with open("candidate_bullet.txt", mode='a', newline='') as file:
    file.write(result)
    file.write("\n")
print(candidate_name+"'s notes have been summarized and stored!")
print("####################################")
###############################################################################################################################################################










# class InterviewTools():
#     @tool("checks if the interview is available")
#     def check_interview_availability(requested_date: str, requested_time: str, file_path: str):
#         """
#         Check if the requested interview date and time are available.

#         Parameters:
#         - requested_date (str): The requested date in 'MM-DD' format.
#         - requested_time (str): The requested time in 'HH:MM AM/PM' format.
#         - file_path (str): The path to the CSV file containing interview schedules.
        
#         Returns:
#         - bool: True if the interview is available, False otherwise.
#         """
#         with open(file_path, 'r') as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 interview_date = datetime.strptime(row['Date'], '%m-%d')
#                 interview_time = datetime.strptime(row['Time'], '%I:%M %p').time()
#                 interview_datetime = datetime.combine(interview_date.date(), interview_time)

#                 # Check if the requested date matches an existing date
#                 if interview_date.strftime('%m-%d') == requested_date:
#                     requested_datetime = datetime.combine(interview_date.date(), datetime.strptime(requested_time, '%I:%M %p').time())
#                     # Check if the requested time matches an existing time
#                     if interview_datetime.time() == requested_datetime.time():
#                         return False
#                     # Check if the requested time is within one hour of an existing time
#                     elif abs(requested_datetime - interview_datetime) <= timedelta(hours=1):
#                         return False
#         return True
