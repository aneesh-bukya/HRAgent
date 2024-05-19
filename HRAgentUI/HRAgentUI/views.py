# from django.http import HttpResponse

# def homepage(request):
#   return HttpResponse("Hello World! This is teh home page")

# def about(request):
#   return HttpResponse("My About Page")


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import subprocess


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
    if request.method == 'POST' and request.FILES['notesFile']:
        notes_file = request.FILES['notesFile']
        fs = FileSystemStorage()
        filename = fs.save(notes_file.name, notes_file)
        file_path = fs.path(filename)

        # Run the notes.py script and capture the output
        try:
            result = subprocess.run(['python3', 'notes.py', file_path], capture_output=True, text=True)
            summary = result.stdout
        except Exception as e:
            summary = str(e)

        return JsonResponse({'summary': summary})

    return JsonResponse({'error': 'Invalid request'}, status=400)