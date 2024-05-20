# from django.http import HttpResponse

# def homepage(request):
#   return HttpResponse("Hello World! This is teh home page")

# def about(request):
#   return HttpResponse("My About Page")


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
from crewai import Crew, Agent, Task, Process
from textwrap import dedent
from crewai_tools import TXTSearchTool
import os



os.environ["OPENAI_API_KEY"] = "sk-proj-1j0rI4ujwFua7rWGytDlT3BlbkFJwHncuWCnnYZADHHSAkrw"
os.environ["SERPER_API_KEY"] = "d1b04924fa8092b742ea783991626a950f1a0c1a"
os.environ['OPENAI_MODEL_NAME'] =  "gpt-4-0125-preview"

def homepage(request):
  return render(request,'home.html')

def about(request):
  return render(request,'about.html')

def candidate_notes(request):
  return render(request,"notes.html")

def faq_agent(request):
  return render(request,"faq.html")

def onboarding(request):
  return render(request,"email.html")


@csrf_exempt
def summarize_notes(request):
    if request.method == 'POST':
        candidate_name = request.POST['candidateName']
        notes_file = request.FILES['notesFile']
        file_path = default_storage.save('tmp/' + notes_file.name, notes_file)

        txt_search = TXTSearchTool(file_path)

        notes_agent = Agent(
            role="Candidate Notes Summarizer",
            goal='Summarizes the notes on a candidate',
            backstory=dedent("""\
                As a Notes Summarizer, your mission is to read through the entire file
                and summarize the information in a concise yet informative manner into bullet points."""),
            tools=[txt_search],
            verbose=True
        )

        def candidate_notes_task(name):
            return Task(
                description=dedent(f"""\
                    Summarize the document into a few detailed bullet points
                    Candidate Name: {name}"""),
                expected_output=dedent("""\
                    Ensure each bullet point isn't longer than 80 characters
                    Have a list of 5-6 bullet points on notes given about the candidate
                    Use this format for your output:
                    Candidate Name : [Candidate Name]
                    - Candidate notes"""),
                agent=notes_agent,
            )

        candidate_task = candidate_notes_task(candidate_name)

        crew = Crew(agents=[notes_agent], tasks=[candidate_task])
        result = crew.kickoff()
        print(result)

        # Clean up the temporary file
        os.remove(file_path)

        return JsonResponse({'summary': result})

    return JsonResponse({'error': 'Invalid request'}, status=400)
