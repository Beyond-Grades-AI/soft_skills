# web/views.py
from .models import Student  # Import the Question model
from django.urls import reverse
from .models import Question  # Import the Question model
from .models import Answer
from django.http import HttpResponseServerError
from django.utils import timezone
from language_model.LM import create_questions as create_questions_LM
from django.shortcuts import render, redirect
from .models import Test, Teacher



def login_screen(request):
    if request.method == 'POST':
        email = request.POST.get('input_email', '')

        try:
            # Check if the email exists in the database
            teacher = Teacher.objects.get(email=email)
            # If the teacher exists, log them in
            request.session['teacher'] = teacher.email
            # Redirect to the main screen upon successful login
            return redirect('main_screen')
        except Teacher.DoesNotExist:
            # If teacher does not exist, create a new teacher
            teacher = Teacher.objects.create(email=email)
            # Save the new teacher's email in session and redirect to main screen
            request.session['teacher'] = teacher.email
            # Redirect to the main screen upon successful registration/login
            return redirect('main_screen')

    # Render login screen if request method is GET
    return render(request, 'login_screen.html')


# View for rendering the main screen
def main_screen(request):
    return render(request, 'main_screen.html')

# Function to process input text and generate questions using the language model
def process_input(input_text: str, soft_skill: str, num_q) -> str:
    # Call the create_questions_LM function to generate questions
    questions = create_questions_LM(input_text, soft_skill,True, 5)
    return questions

# View for handling question creation
def create_questions(request):
    print('create_questions!!')
    print('request method: ')
    print(request.method)

    generated_questions = ""  # Initialize generated questions text

    if request.method == 'POST':
        # Get form inputs
        input_text = request.POST.get('input_text', '')
        skill = request.POST.get('skill', '')
        subject = request.POST.get('subject', '')
        grade = request.POST.get('grade', '')
        test_title = request.POST.get('title','')

        print(f"skill: {skill} subject: {subject}, grade: {grade}, test_title: {test_title}")

        # Validate form inputs
        if not (skill and subject): #<--and sub_topic
            return HttpResponseServerError("Please fill in all required fields")

        # Process input text
        if input_text:
            generated_questions = process_input(input_text, skill, 5)
            print( f"num of questions: {len(generated_questions)}")

        # Validate form inputs
        if not (skill and subject and generated_questions): #<--and sub_topic
            return HttpResponseServerError("Please fill in all required fields and provide input text or upload a file.")

        creation_date = timezone.now()
        print('*************')
        current_date_str = creation_date.strftime('%d-%m-%Y')
        print(current_date_str)
        print('*************')
        test_id = int(creation_date.timestamp())  # Generate a unique test ID using the creation date

        # Render the teacher screen with generated questions
        return render(request, 'generated_test.html', {
            'generated_questions': generated_questions,
            'skill': skill,
            'subject': subject,
            'grade': grade,
            'test_title': test_title,
            'test_id': test_id,
            })

    # Render the teacher screen without generated questions if GET request
    return render(request, 'teacher_screen.html')


#view for editing the test
def edit_test(request):
    return

# View for generating a test link
def generate_link(request):

    print('generate_link view!!')
    if request.method == 'POST':
        # Get form data
        test_id = request.POST.get('test_id')
        subject = request.POST.get('subject')
        skill = request.POST.get('skill')
        grade = request.POST.get('grade')
        test_title = request.POST.get('test_title')
        current_time = timezone.now()
        current_time_str = current_time.strftime('%d-%m-%Y')
        print(f"(post request) skill: {skill} subject: {subject}, grade: {grade}, test_title: {test_title}")

        if not (subject and skill):
            return HttpResponseServerError("Please select a subject and a skill.")

        try:
            teacher = Teacher.objects.get(email=request.session.get('teacher'))

            # Create a Test object only if it doesn't already exist
            teacher = Teacher.objects.get(email=request.session.get('teacher'))
            test, created = Test.objects.get_or_create(
                id=test_id,
                defaults={
                    'teacher': teacher,
                    'title': test_title,
                    'subject': subject,
                    'skill': skill,
                    'grade': grade
                }
            )

            if created:
                # Get generated questions from the form
                questions = request.POST.getlist('questions[]')
                print('questions: ')
                print(questions)

                # Iterate over the questions and create Question objects
                for index, question in enumerate(questions, start=1):
                    Question.objects.create(
                        id=f"{test.id}{index}",
                        test=test,
                        number=index,
                        text=question
                        )

        except Exception as e:
            print(e)
            return HttpResponseServerError("An error occurred while saving the test and questions.")

        # Generate the URL for the test page with the test ID appended
        test_page_url = reverse('test_page', args=[test.id])
        # Assign the URL to the link attribute of the test object
        test.link = test_page_url
        test.save()
        return render(request, 'test_link.html', {'test_page_url': test_page_url,
                                                  'grade': grade,
                                                  'skill': skill,
                                                  'subject': subject,
                                                  'test_title': test_title})
    print("get request")
    return render(request, 'generated_test.html')

# def display_link(request):
#     print("display link view")
#     return render(request, 'test_link.html')

def display_link(request, test_page_url, grade, skill, subject, test_title):
    return render(request, 'test_link.html', {
        'test_page_url': test_page_url,
        'grade': grade,
        'skill': skill,
        'subject': subject,
        'test_title': test_title
    })

# View for displaying the test page
def test_page(request, test_id):
    try:
        # Retrieve the test object
        test = Test.objects.get(id=test_id)
        # Retrieve associated questions
        questions = test.questions.all()  # Assuming a related_name of 'questions' in Test model

        if questions:
            return render(request, 'test_page.html', {'questions': questions, 'test': test, 'grade': test.grade, 'skill': test.skill})
        else:
            return render(request, 'test_page.html', {'error_message': 'No questions found for this test.'})
    except Test.DoesNotExist:
        # Handle case where the Test object does not exist
        return render(request, 'test_page.html', {'error_message': 'Test not found.'})

def submit_answers(request):
    print('submit_answers view!!')
    if request.method == 'POST':
        # Retrieve test ID from the hidden input field
        test_id = request.POST.get('test_id')

        test = Test.objects.get(id=test_id)
        questions = test.questions.all()

        # Retrieve student's full name from the form
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        test_box = request.POST.get('test') == 'on'

        # Validate the full name (two words)
        if not full_name or len(full_name.split()) < 2:
            # If full name is not provided or doesn't contain at least two words
            return render(request, 'test_page.html', {'test': test, 'questions': questions, 'error_message': 'Please provide your full name with two words.'})

        ##new##
        # Check if the student has already submitted answers for this test
        existing_answers = Answer.objects.filter(student_identifier=email, question__in=questions)
        if existing_answers.exists():
            return render(request, 'test_page.html', {'test': test, 'questions': questions, 'error_message': 'You have already submitted this test.'})
        ##new##


        # Retrieve questions and create Answer objects
        for key, value in request.POST.items():
            if key.startswith('answer_'): # this 'answer_' prefix comes from the test_page template
                # Extract question ID from the key
                question_id = key.split('_')[1]

                # Retrieve the corresponding Question object
                question = Question.objects.get(id=question_id)

                # Create Answer object
                Answer.objects.create(
                    student_identifier=email,
                    question=question,
                    answer_text=value,
                    testbox =test_box
                )

        # if it is the first student's submission, Create a Student object and associate it with the test
        student, created = Student.objects.get_or_create(
            student_id = email,
            defaults={'first_name': full_name.split()[0], 'last_name': full_name.split()[1]}
            )

        student.tests.add(test)

        # Redirect to a success page
        return render(request, 'submitted.html')

    # If the request method is not POST, redirect to the test page
    return render(request, 'test_page.html')


def submitted(request):
    return render(request, 'submitted.html')



# View for displaying tests for the logged-in teacher and reviewing test submissions
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

    # POST request handling (teacher choosed a test to display his submissions)
    else:
        print('POST request')
        test_id = request.POST.get('test_id')
        test = Test.objects.get(id=test_id)
        student_submitted = test.students.all()
        return render(request, 'tests_screen.html', {'test_id': test_id, 'students': student_submitted, 'test': test, 'tests': teacher_tests})

def test_feedback(request):
    print('START OF TEST FEEDBACK IN VIEWS')
    if request.method == 'POST':
        test_id = request.POST.get('test_id')
        print("Test ID:", test_id)  # Debug print statement
        test = Test.objects.get(id=test_id)
        student_submitted = test.students.all()
        students_submitted_count = test.students.count()
        print('Count: ', students_submitted_count)
        return render(request, 'test_feedback.html', {'students' : student_submitted, 'count' : students_submitted_count, 'test' : test})
    print('THE END OF TEST FEEDBACK IN VIEWS')

# View for reviewing a test and handling evaluations
def review_test(request, test_id, student_id ):
    print('review_test view!!')
    if request.method == 'GET':
        print('GET request')
        # Retrieve the test object
        test = Test.objects.get(id=test_id)
        student = Student.objects.get(student_id=student_id)

        student_name = f"{student.first_name} {student.last_name}"
        question = test.questions.all()

        # Create a dictionary to store questions and answers for the student
        question_answers_dict = {}

        for q in question:
            print(q.text)
            answer = q.answers.all().filter(student_identifier=student_id).first() ####assuming there is only one result
            #answer = Answer.objects.get(question=question, student=student).first()
            print('ANSWER: ', answer)
            print('******************************************')
            question_answers_dict[q] = answer

        return render(request, 'review_test.html', {'test': test, 'student_name': student_name ,'student': student, 'question_answers_dict': question_answers_dict})
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
                answer = Answer.objects.get(question_id=question_id, student_identifier = student_id)
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