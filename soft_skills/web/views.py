# web/views.py
from pyexpat.errors import messages
from django.shortcuts import render
from .models import Answer, Question, Student, Teacher, Test  # Import the Question model
from django.shortcuts import render
from django.urls import reverse
from .models import Question  # Import the Question model
from .models import Answer
from django.http import HttpResponseServerError
from django.utils import timezone



from django.shortcuts import render, redirect
from .models import Test, Teacher

#first screen
def login_screen(request):
    if request.method == 'POST':
        email = request.POST.get('input_email', '')

        try:
            # Check if the email exists in the database
            teacher = Teacher.objects.get(email=email)
            # If the teacher exists, log them in
            request.session['teacher'] = teacher.email
            return redirect('main_screen')  # Redirect to the main screen upon successful login
        except Teacher.DoesNotExist:
            # If the teacher does not exist, create a new one
            teacher = Teacher.objects.create(email=email)
            # Log in the newly registered teacher
            request.session['teacher'] = teacher.email
            return redirect('main_screen')  # Redirect to the main screen upon successful registration/login
    return render(request, 'login_screen.html')


def main_screen(request):
    return render(request, 'main_screen.html')

#update later to cordinate with LM Component
def process_input(input_text: str) -> str:
    """
    Process the input text or file content and split it into numbered questions.
    Args:
        input_text (str): Input text or file content.

    Returns:
        str: numbered questions seperated with new line
    """
    # Split the input text by newline characters
    lines = input_text.split('\n')


    # Create a list of numbered questions
    questions = '\n'.join(lines)

    return questions

def teacher_screen(request):
    print('teacher view!!')
    print('request method: ')
    print(request.method)
    generated_questions = ""  # Initialize generated questions text
    if request.method == 'POST':
        # Get form inputs
        input_text = request.POST.get('input_text', '')
        skill = request.POST.get('skill', '')
        subject = request.POST.get('subject', '')
        sub_topic = request.POST.get('sub_topic', '')
        print(skill)
        print(subject)

        # Check if the file is uploaded
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            try:
                # Parse the content of the uploaded file
                file_content = uploaded_file.read().decode('utf-8')  # Adjust encoding as necessary
                # Process the file content
                generated_questions = process_input(file_content)
            except Exception as e:
                return HttpResponseServerError("An error occurred while parsing the file content.")

        # Process input text
        if input_text:
            generated_questions = process_input(input_text)

        # Validate form inputs
        if not (skill and subject and generated_questions): #<--and sub_topic 
            return HttpResponseServerError("Please fill in all required fields and provide input text or upload a file.")
        print('saving dict')
        return render(request, 'teacher_screen.html', {'generated_questions': generated_questions, 'skill': skill, 'subject': subject})
    
    return render(request, 'teacher_screen.html', {'generated_questions': generated_questions})


def generate_link(request):
    print('generate_link view!!')
    if request.method == 'POST':
        # Get form data
        subject = 'subject' #request.POST.get('subject') #############################################################################################
        skill = 'skill' #request.POST.get('skill')      ###################################################################################################

        if not (subject and skill):
            return HttpResponseServerError("Please select a subject and a skill.")
        # Assuming creation date should be set to the current date and time
        creation_date = timezone.now()
        test_id = int(creation_date.timestamp())  # Generate a unique test ID using the creation date

        try:
            # Create a Test object
            teacher = Teacher.objects.get(email=request.session.get('teacher'))
            test = Test.objects.create(id = test_id, teacher=teacher)  #<--skill=skill, subject=subject, sub_topic=sub_topic, creation_date=creation_date,
            # Get generated questions from the form
            questions_text = request.POST.get('generated_questions', '')
            print('questions_text: ')
            print(questions_text)
            # Split the questions by newline
            questions_list = questions_text.split('\n')
            print(len(questions_list))
            # Iterate over the questions and create Question objects
            for i, question_text in enumerate(questions_list, start=1):
                 Question.objects.create(id=str(test.id) + str(i), test=test, number=i, text=question_text, )
        except Exception as e:
            print(e)
            return HttpResponseServerError("An error occurred while saving the test and questions.")

        # Generate the URL for the test page with the test ID appended
        test_page_url = reverse('test_page', args=[test.id])
        return render(request, 'teacher_screen.html', {'test_page_url': test_page_url})  

    return render(request, 'teacher_screen.html')

def test_page(request, test_id):
    try:
        # Retrieve the test object
        test = Test.objects.get(id=test_id)
        # Retrieve questions associated with the test
        questions = test.questions.all()  # Assuming a related_name of 'questions' in Test model
        if questions:
            return render(request, 'test_page.html', {'questions': questions, 'test': test})
        else:
            # Handle case where no questions are found for the test
            return render(request, 'test_page.html', {'error_message': 'No questions found for this test.'})
    except Test.DoesNotExist:
        # Handle case where the Test object does not exist
        return render(request, 'test_page.html', {'error_message': 'Test not found.'})

def submit_answers(request):
    print('submit_answers view!!')
    if request.method == 'POST':
        # Retrieve test ID from the hidden input field
        test_id = request.POST.get('test_id')
        print('test_id: ')  
        print(test_id)
        test = Test.objects.get(id=test_id)
        questions = test.questions.all()
        
        # Retrieve student's full name from the form
        full_name = request.POST.get('full_name')
        
        # Validate the full name (two words)
        if not full_name or len(full_name.split()) < 2:
            # If full name is not provided or doesn't contain at least two words
            return render(request, 'test_page.html', {'test': test, 'questions': questions, 'error_message': 'Please provide your full name with two words.'})
        
        # Retrieve questions and create Answer objects
        for key, value in request.POST.items():
            if key.startswith('answer_'):
                # Extract question ID from the key
                question_id = key.split('_')[1]
                
                # Retrieve the corresponding Question object
                question = Question.objects.get(id=question_id)
                
                # Create Answer object
                Answer.objects.create(
                    student_identifier=full_name,
                    question=question,
                    answer_text=value
                )
        
        student = Student.objects.create(first_name=full_name)  # Create a Student object and associate it with the test
        student.tests.add(test)
        
        # Redirect to a success page
        return render(request, 'submitted.html')

    # If the request method is not POST, redirect to the test page
    return render(request, 'test_page.html')

def submitted(request):
    return render(request, 'submitted.html')

#GET request - displaying tests of the logged in teacher
#POST request - teacher choosed a test to display his submissions
def tests_screen(request):
    print('tests_screen view!!')

    # Retrieve the logged-in teacher's email from the session
    teacher_email = request.session.get('teacher')
    if teacher_email:
        # Retrieve the logged-in teacher's tests
        try:
            teacher = Teacher.objects.get(email=teacher_email)
            teacher_tests = teacher.tests.all()
        except Teacher.DoesNotExist:
            # Handle case where teacher does not exist
            pass
    else:
        # Handle case where teacher is not logged in
        return redirect('login_screen')
    
    if request.method == 'GET':
        print('GET request')
        return render(request, 'tests_screen.html', {'tests': teacher_tests})

    #teacher choosed a test to display his submissions
    #request.method == 'POST'
    else:
        print('POST request')
        test_id = request.POST.get('test_id')
        test = Test.objects.get(id=test_id)
        student_submitted = test.students.all()
        return render(request, 'tests_screen.html', {'test_id': test_id, 'students': student_submitted, 'test': test, 'tests': teacher_tests})

# def display_tests(request):
#     # Retrieve the logged-in teacher's email from the session
#     teacher_email = request.session.get('teacher')
#     if teacher_email:
#         # Retrieve the logged-in teacher's tests
#         try:
#             teacher = Teacher.objects.get(email=teacher_email)
#             teacher_tests = teacher.tests.all()
#         except Teacher.DoesNotExist:
#             # Handle case where teacher does not exist
#             pass
#     else:
#         # Handle case where teacher is not logged in
#         return redirect('login_screen')

#     return render(request, 'tests_screen.html', {'tests': teacher_tests})

def review_test(request, test_id, first_name):
    print('review_test view!!')
    if request.method == 'GET':
        print('GET request')
        # Retrieve the test object
        test = Test.objects.get(id=test_id)
        student = Student.objects.get(first_name=first_name)
        question = test.questions.all()

        # Create a dictionary to store questions and answers for the student
        question_answers_dict = {}

        for q in question:
            print(q.text)
            answer = q.answers.all().filter(student_identifier=first_name).first() ####assuming there is only one result
            #answer = Answer.objects.get(question=question, student=student).first()

            question_answers_dict[q] = answer

        return render(request, 'review_test.html', {'test': test, 'student': student, 'question_answers_dict': question_answers_dict})
    else:
        print('POST request')
        # Retrieve the test object
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return redirect('failure_url')  # Redirect to an appropriate URL if the test is not found

        # Retrieve the submitted evaluations from the form data
        submitted_evaluations = {}
        for key, value in request.POST.items():
            if key.startswith('evaluation_'):
                question_id = key.split('_')[1]
                submitted_evaluations[question_id] = value

        # Update the evaluations for each question's answer
        for question_id, evaluation in submitted_evaluations.items():
            try:
                answer = Answer.objects.get(question_id=question_id, student_identifier = first_name)
                answer.approved_eval = evaluation
                answer.is_approved = True
                answer.save()
            except Answer.DoesNotExist:
                # Handle case where the answer is not found
                pass

        ######################################################################
        # Retrieve the logged-in teacher's email from the session
        teacher_email = request.session.get('teacher')
        if teacher_email:
            # Retrieve the logged-in teacher's tests
            try:
                teacher = Teacher.objects.get(email=teacher_email)
                teacher_tests = teacher.tests.all()
            except Teacher.DoesNotExist:
                # Handle case where teacher does not exist
                pass
        else:
            # Handle case where teacher is not logged in
            return redirect('login_screen')
        ######################################################################
        return render(request, 'tests_screen.html', {'tests': teacher_tests})

def failure_url(request):
    return render(request, 'failure_url.html')