from attrs import define

@define
class QuizDTO:
    title: str
    description: str
    quiz_type: str = 'practice_quiz'


@define
class Answer:  # pylint: disable=too-few-public-methods
    """canvas answer see for complete list of (valid) fields
    https://canvas.instructure.com/doc/api/quiz_questions.html#:~:text=An%20Answer-,object,-looks%20like%3A
    """
    answer_html: str
    answer_weight: int
# complete list of params : https://canvas.instructure.com/doc/api/quiz_questions.html


@define
class QuestionDTO:
    answers: list[Answer]
    question_name: str = ""
    question_type: str = 'multiple_choice_question'  # other option is essay question
    question_text: str = ''
    points_possible: str = '1.0'
    correct_comments: str = ''
    incorrect_comments: str = ''
    neutral_comments: str = ''
    correct_comments_html: str = ''
    incorrect_comments_html: str = ''
    neutral_comments_html: str = ''


@define
class Stats:
    quiz_ids: list[int] = []
    question_ids: list[int] = []

