import logging
import unittest
from mysql_client import MysqlClient


class TestMysqlClient(unittest.TestCase):
    def setUp(self):
        self.mc = MysqlClient(db='test_db')
        self.test_course_id = 888
        self.mc.set_course_id(self.test_course_id)

    def test_1_check_table_should_create_table_if_not_exist(self):
        self.mc.set_course_id(666)
        self.mc.course_table.__table__.drop(self.mc.engine)
        self.mc.check_table()
        is_table_exist = self.mc.engine.dialect.has_table(self.mc.engine.connect(), self.mc.course_table_name)
        self.mc.course_table.__table__.drop(self.mc.engine)
        self.mc.set_course_id(self.test_course_id)
        self.assertTrue(is_table_exist)

    def test_2_insert_answer_should_save_answer_to_table(self):
        self.mc.set_course_id(self.test_course_id)
        answers = [
            {
                'question_id': 'a-123',
                'answer': '2'
            },
        ]
        self.mc.insert_answers(answers)
        session = self.mc.DBSession()
        result = session.query(self.mc.course_table).filter_by(question_id='a-123').first().to_dict()
        session.close()
        self.assertEqual(result, answers[0])

    def tearDown(self):
        self.mc.course_table.__table__.drop(self.mc.engine)


if __name__ == '__main__':
    unittest.main()
