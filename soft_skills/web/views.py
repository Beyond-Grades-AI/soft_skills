# web/views.py
from io import BytesIO
from xml.dom.minidom import Document

from .models import Student  # Import the Question model
from django.urls import reverse
from .models import Question  # Import the Question model
from .models import Answer
from django.http import HttpResponseServerError, HttpResponseRedirect, HttpResponse
from django.utils import timezone
from language_model.LM import create_questions as create_questions_LM
from django.shortcuts import render, redirect
from .models import Test, Teacher
from django.core.files.storage import FileSystemStorage
import pdfplumber
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import fonts
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os



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
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    reversed_text = []
    for para in doc.paragraphs:
        reversed_words = []
        for word in para.text.split():
            reversed_word = word[::-1]  # Reverse word letter-by-letter
            reversed_words.append(reversed_word)
        reversed_paragraph = ' '.join(reversed_words)
        reversed_text.append(reversed_paragraph)
    return '\n\n'.join(reversed_text)

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error reading PDF file: {e}")
    return text

def create_questions(request):
    print('create_questions!!')
    print('request method: ')
    print(request.method)
    generated_questions = ""  # Initialize generated questions text
    input_text = ""
    if request.method == 'POST':
        skill = request.POST.get('skill', '')
        subject = request.POST.get('subject', '')
        grade = request.POST.get('grade', '')
        test_title = request.POST.get('title', '')
        try:
            if request.FILES['file']:
                uploaded_file = request.FILES['file']
                fs = FileSystemStorage()
                filename = fs.save(uploaded_file.name, uploaded_file)
                print(f'file name is: {filename}')
                file_path = fs.path(filename)
                print(f'file path is: {file_path}')
                if uploaded_file.name.endswith('.docx'):
                    input_text = extract_text_from_docx(file_path)
                elif uploaded_file.name.endswith('.pdf'):
                    input_text = extract_text_from_pdf(file_path)
                else:
                    input_text = 'Unsupported file type'
        except Exception as e:
            print(f"Error reading PDF file: {e}")
        # Get form inputs
        if input_text == "":
            input_text = request.POST.get('input_text', '')
            print(f"skill: {skill} subject: {subject}, grade: {grade}, test_title: {test_title}")

        # Validate form inputs
        if not (skill and subject): #<--and sub_topic
            return HttpResponseServerError("Please fill in all required fields")

        # Process input text
        print('ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ')
        print(f'input text : {input_text}')
        print('ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ')
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
        # test_box = request.POST.get('test') == 'on'

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
                    testbox =0
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
        print('*******************POST request*******************')
        searched_title = request.POST.get('testNameSearched')
        print('******************* SEARCHED TITLE *******************')
        print('ENTERED: ', searched_title)
        searched_tests = []
        for test in teacher_tests:
            if searched_title in test.title:
                searched_tests.append(test)
        return render(request, 'tests_screen.html', {'tests': searched_tests})


def test_feedback(request):
    print('START OF TEST FEEDBACK IN VIEWS')
    if request.method == 'POST':
        test_id = request.POST.get('test_id')
        print("Test ID:", test_id)  # Debug print statement
        test = Test.objects.get(id=test_id)
        students_submitted = test.students.all()
        students_submitted_count = test.students.count()
        questions = test.questions.all()
        first_question = questions[0]       #WE NEED ANY QUESTION TO CHECK IF EXAM IS REVIEWED - WE WILL GET FIRST QUESTION
        students_with_approved_eval = []
        for student in students_submitted:
            student_id = student.student_id
            answer = first_question.answers.all().filter(student_identifier=student_id).first()
            if answer.is_approved:
                students_with_approved_eval.append(student_id)

        print('Count: ', students_submitted_count)
        return render(request, 'test_feedback.html', {'students' : students_submitted, 'count' : students_submitted_count, 'test' : test, 'students_with_approved_eval' : students_with_approved_eval})
    print('THE END OF TEST FEEDBACK IN VIEWS')

# View for reviewing a test and handling evaluations
def review_test(request, test_id, student_id ):
    print('review_test view!!')
    # Retrieve the test object
    clickable = True
    test = Test.objects.get(id=test_id)
    student = Student.objects.get(student_id=student_id)

    student_name = f"{student.first_name} {student.last_name}"
    question = test.questions.all()

    # Create a dictionary to store questions and answers for the student
    question_answers_dict = {}

    for q in question:
        print(q.text)
        answer = q.answers.all().filter(student_identifier=student_id).first()  ####assuming there is only one result
        # answer = Answer.objects.get(question=question, student=student).first()
        print('ANSWER: ', answer)
        print('******************************************')
        question_answers_dict[q] = answer
        if answer.is_approved:
            clickable = False


    if request.method == 'GET':
        print('GET request')
        return render(request, 'review_test.html', {'test': test, 'student_name': student_name ,'student': student, 'question_answers_dict': question_answers_dict, 'clickable': clickable})
    else:
        print('POST request')
        # Retrieve the test object
        try:
            print('***********************INSIDE POST REVIEW TEST*****************************')
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return redirect('failure_url')  # Redirect to an appropriate URL if the test is not found

        # Retrieve the submitted evaluations from the form data
        index = 1
        for question, answer in question_answers_dict.items():
            submitted_evaluation = request.POST.get(f'exampleFormControlTextarea{index}')
            print('submitted = ', submitted_evaluation)
            answer.approved_eval = submitted_evaluation
            print(f'answer{index}: answer approved eval: {answer.approved_eval}')
            answer.is_approved = True
            answer.save()
            index = index + 1

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
        test = Test.objects.get(id=test_id)
        students_submitted = test.students.all()
        questions = test.questions.all()
        first_question = questions[0]  # WE NEED ANY QUESTION TO CHECK IF EXAM IS REVIEWED - WE WILL GET FIRST QUESTION
        students_with_approved_eval = []
        for student in students_submitted:
            student_id = student.student_id
            answer = first_question.answers.all().filter(student_identifier=student_id).first()
            if answer.is_approved:
                students_with_approved_eval.append(student_id)
        students_submitted_count = test.students.count()
        return render(request, 'test_feedback.html', {'students' : students_submitted, 'count' : students_submitted_count, 'test' : test, 'students_with_approved_eval' : students_with_approved_eval})


def reverse_hebrew_text(text):
    """Reverse Hebrew text to render correctly in PDF."""
    return text[::-1]


def draw_hebrew_text(p, text, x, y, max_width, font_size=12, line_height=20):
    """Draw Hebrew text with manual wrapping and right-to-left alignment."""
    p.setFont("Hebrew", font_size)

    lines = []
    current_line = ""

    # Split text into words and handle line wrapping
    for word in text.split():
        # Check if adding the word exceeds max_width
        if p.stringWidth(reverse_hebrew_text(current_line + word), "Hebrew", font_size) <= max_width:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "

    # Append the last line
    if current_line.strip():
        lines.append(current_line.strip())

    # Draw each line of text right-to-left
    for line in lines:
        # Calculate the starting x position for right-to-left text
        text_width = p.stringWidth(reverse_hebrew_text(line), "Hebrew", font_size)
        x_start = x + max_width - text_width

        # Check if y position is within page boundaries
        if y < 50:  # Adjust as necessary to leave margin at the bottom
            p.showPage()  # Start a new page if space is insufficient
            p.setFont("Hebrew", font_size)  # Reset font after new page
            y = A4[1] - 50  # Adjust starting Y position for new page

        p.drawString(x_start, y, reverse_hebrew_text(line))
        y -= line_height  # Adjust Y position for the next line

    return y

def download_test(request, test_id, student_id):
    font_path2 = os.path.join(os.path.dirname(__file__), 'fonts', 'bold.ttf')
    pdfmetrics.registerFont(TTFont('Bold', font_path2))

    font_path1 = os.path.join(os.path.dirname(__file__), 'fonts', 'mriam.ttf')
    pdfmetrics.registerFont(TTFont('Hebrew', font_path1))

    student = Student.objects.get(student_id=student_id)
    test = Test.objects.get(id=test_id)
    test_questions = test.questions.all()
    tmp = '----------------------------------------------------------------------------------------------------------------'

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)

    y = 800  # Starting Y position

    # Use Hebrew font
    p.setFont("Bold", 16)

    title = 'מבחן בנושא: ' + test.title
    draw_hebrew_text(p, title, 50, y, 450)

    grade = 'כיתה ' + test.grade
    draw_hebrew_text(p, grade, -250, y, 450)

    skill = 'מיומנות: ' + test.skill
    draw_hebrew_text(p, skill, -300, y, 450)
    y -= 30

    student_name = 'שם התלמיד: ' + student.first_name + ' ' + student.last_name
    draw_hebrew_text(p, student_name, 50, y, 450)
    y -= 60

    # Reset font size for content
    index = 1

    for question in test_questions:
        questionFormat = 'שאלה ' + str(index) + ': '
        answer = question.answers.all().filter(student_identifier=student_id).first()
        anwer_eval = answer.approved_eval

        y = draw_hebrew_text(p, questionFormat, 50, y, 450)
        y -= 10

        p.setFont("Hebrew", 12)
        y = draw_hebrew_text(p, question.text, 50, y, 450)
        y -= 10

        p.setFont("Bold", 16)
        answerFormat = 'תשובת התלמיד: '
        y = draw_hebrew_text(p, answerFormat, 50, y, 450)
        y -= 10

        p.setFont("Hebrew", 12)
        y = draw_hebrew_text(p, answer.answer_text, 50, y, 450)
        y -= 10

        p.setFont("Bold", 16)
        reviewFormat = 'משוב על התשובה : '
        y = draw_hebrew_text(p, reviewFormat, 50, y, 450)
        y -= 10

        p.setFont("Hebrew", 12)
        y = draw_hebrew_text(p, anwer_eval, 50, y, 450)
        y -= 10

        y = draw_hebrew_text(p, tmp, 50, y, 450)
        y -= 40

        index = index + 1

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def failure_url(request):
    return render(request, 'failure_url.html')