from dataclasses import dataclass, field, asdict


@dataclass
class QuizDTO:
    title: str
    description: str
    quiz_type: str = 'practice_quiz'


@dataclass
class Answer:  # pylint: disable=too-few-public-methods
    """canvas answer see for complete list of (valid) fields
    https://canvas.instructure.com/doc/api/quiz_questions.html#:~:text=An%20Answer-,object,-looks%20like%3A
    """
    answer_html: str
    answer_weight: int


AnswerOptions = dict[str, int]  # answer_text, answer_weigth


# complete list of params : https://canvas.instructure.com/doc/api/quiz_questions.html


@dataclass
class QuestionDTO:
    answers: list[AnswerOptions]
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


@dataclass
class Stats:
    quiz_ids: list[int] = field(default_factory=list)
    question_ids: list[int] = field(default_factory=list)