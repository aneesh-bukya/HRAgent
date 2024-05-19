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




