from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def generate_course_table(table_name):
    class Course(Base):
        __tablename__ = table_name
        question_id = Column(String(45), primary_key=True, nullable=False, unique=True)
        answer = Column(String(45), nullable=False)

    return Course


class MysqlClient:
    def __init__(self):
        self.username = 'user'
        self.password = 'password'
        self.engine = create_engine(f'mysql+mysqlconnector://{self.username}:{self.password}@192.168.1.135:3306/db')
        self.DBSession = sessionmaker(bind=self.engine)
        self.course_id = None
        self.course_table = None
        self.course_table_name = None

    def set_course_table_name(self):
        self.course_table_name = f'course_id_{self.course_id}'

    def set_course_id(self, course_id):
        self.course_id = course_id
        self.set_course_table_name()
        self.course_table = generate_course_table(self.course_table_name)
        self.check_table()

    def check_table(self):
        self.course_table.__table__.create(bind=self.engine, checkfirst=True)

    def get_answers(self):
        session = self.DBSession()
        answers = {}
        for question in session.query(self.course_table).all():
            answers[question.question_id] = question.answer
        session.close()
        return answers

    def insert_answers(self, answers):
        session = self.DBSession()
        for answer in answers:
            try:
                if session.query(self.course_table).filter_by(question_id=answer.get('question_id')).one_or_none():
                    pass
                else:
                    question = self.course_table()
                    question.question_id = answer.get('question_id')
                    question.answer = answer.get('answer')
                    session.add(question)
                session.commit()
            except Exception as e:
                print(e)
                session.close()


def main():
    mq = MysqlClient()
    mq.set_course_id(17680)
    mq.get_answers()
    answers = [
        {
            'question_id': 'a-123',
            'answer': '2'
        },
        {
            'question_id': 'm-123',
            'answer': '2'
        },
        {
            'question_id': 'u-123',
            'answer': 'ABC'
        }
    ]
    mq.insert_answers(answers)
    mq.get_answers()


if __name__ == '__main__':
    main()
