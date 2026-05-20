from question_model import Question
from data import question_data

question_list = []

for one_question in question_data:
    question_t = one_question["text"]
    question_a = one_question["answer"]
    new_question = Question(question_t, question_a)
    question_list.append(new_question)
    
print(question_list)