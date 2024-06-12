from django.db import models


# explaintion about foreign key 'questions' in the buttom
class Test(models.Model):
    id = models.AutoField(primary_key=True)  # Field to store the test ID
    title = models.CharField(max_length=100)
    skill = models.CharField(max_length=100)  # Field to store skill
    subject = models.CharField(max_length=100)  # Field to store subject
    # sub_topic = models.CharField(max_length=100)  # Field to store sub-topic
    #creation_date = models.DateField(auto_now_add=True)  # Automatically set the creation date to the current date when the object is created
    teacher = models.ForeignKey('Teacher', related_name='tests', on_delete=models.CASCADE)  # Field to store the teacher
    # link = models.URLField(max_length=200, blank=True, null=True)  # Field to store the URL link for the test
    grade = models.CharField(max_length=100)

    # class Meta:
    #      unique_together = ('title', 'teacher')  # Ensure unique combination of title and teacher

    def __str__(self):
        return f"Test: {self.skill}, {self.subject}, {self.sub_topic}"


class Question(models.Model):
    id = models.AutoField(primary_key=True)  # Field to store the question ID
    test = models.ForeignKey('Test', related_name='questions', on_delete=models.CASCADE)
    number = models.IntegerField()  # Number of the question
    text = models.TextField()  # Text of the question

    def __str__(self):
        return f"Question {self.number}: {self.text}"


class Answer(models.Model):
    student_identifier = models.CharField(max_length=100)  # Field to store student identifier
    # question_id = models.IntegerField()  # Assuming question IDs are integers
    question = models.ForeignKey('Question', related_name='answers',
                                 on_delete=models.CASCADE)  # Field to store the question
    answer_text = models.TextField()
    origin_eval = models.TextField(default="Not yet evaluated")
    approved_eval = models.TextField(default="Not yet approved")
    is_approved = models.BooleanField(default=False)
    testbox = models.BooleanField(default=False)

    def __str__(self):
        return f'Submission for question {self.answer_text}'


class Student(models.Model):
    student_id = models.EmailField(primary_key=True)  # Field to store email address as id
    first_name = models.CharField(max_length=100)  # Field to store first name
    last_name = models.CharField(max_length=100)  # Field to store last name
    tests = models.ManyToManyField('Test', related_name='students')  # Field to store tests

    def __str__(self):
        return f"{self.first_name}"


class Teacher(models.Model):
    email = models.EmailField()  # identifier

    # first_name = models.CharField(max_length=100)  # Field to store first name
    # last_name = models.CharField(max_length=100)  # Field to store last name

    def __str__(self):
        return f"{self.first_name}"

# No, you don't need to have a questions attribute field in the Test model because Django automatically generates a reverse relation for ForeignKey fields.
# In your Question model, you have defined a ForeignKey field named test that establishes a relationship between Question and Test. This ForeignKey field creates a relationship where each Question instance is associated with a single Test instance.
# When you define a ForeignKey in Django, it automatically creates a reverse relation on the related model (in this case, Test). This reverse relation allows you to access related objects from the other side of the relationship. In your case, since you've specified related_name='questions' in the ForeignKey definition, you can access the related Question objects from a Test instance using the questions attribute.
# For example, if you have a Test instance named my_test, you can access its related Question objects like this:
# my_questions = my_test.questions.all()
