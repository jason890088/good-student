import requests
from bs4 import BeautifulSoup
from mysql_client import MysqlClient
import logging


class Examinee:
    def __init__(self, cookie, course_id):
        self.cookie = cookie
        self.course_id = course_id
        self.mc = MysqlClient()
        self.set_course_id(self.course_id)
        self.headers = {
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Cookie': self.cookie
        }

    def set_course_id(self, course_id):
        self.course_id = course_id
        self.mc.set_course_id(course_id)

    def full_process(self):

        questions, answers = self.get_questions()
        exam_result = self.do_exam(questions, answers)
        self.save_exam_result(exam_result)

    def get_questions(self):
        url = f'https://iedu.foxconn.com/public/play/examUI?courseId={self.course_id}'
        headers = self.headers

        response = requests.request('GET', url, headers=headers)
        questions = BeautifulSoup(response.text, 'html.parser')
        logging.info(f'{self.course_id} start')
        return questions, self.mc.get_answers()

    def do_exam(self, questions, answers):
        url = f'https://iedu.foxconn.com/public/play/submitExam'
        headers = self.headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        exam_id = questions.find('input', {'name': 'examId'}).get('value')
        exam_token = questions.find('input', {'name': 'examToken'}).get('value')
        start_date = questions.find('input', {'name': 'startDate'}).get('value')
        user_name = questions.find('input', {'name': 'userName'}).get('value')

        payload = f'examId={exam_id}&examToken={exam_token}&startDate={start_date}&userName={user_name}'
        for question_id in self.get_questions_id(questions):
            answer = answers.get(question_id)
            if answer and len(answer) == 1:
                # 單選題
                payload += f'&{question_id}={answer}'
            elif answer:
                # 多選題
                for option in answer:
                    payload += f'&{question_id}={option}'
            else:
                # the answer not in database yet
                pass

        response = requests.request('POST', url, headers=headers, data=payload)
        exam_result = BeautifulSoup(response.text, 'html.parser')
        scores = exam_result.select_one('div', {'class': 'exam_result'}).findNext('strong').getText()
        print(f'成績:{scores}')
        return exam_result

    @staticmethod
    def get_questions_id(questions):
        return [question.select_one('input').get('name') for question in
                questions.find_all('div', {'class': 'question_warp'})]

    def save_exam_result(self, exam_result):
        answers = []
        for question in exam_result.find_all('div', {'class': 'question_warp'}):
            # print(question)
            answer = question.select_one('p', {'class': 'answer'}).findNext('strong')
            answers.append({
                'question_id': question.select_one('input', {'disabled': ''}).get('name'),
                'answer': self.answer_transform(answer.getText())
            })
        self.mc.insert_answers(answers)

    @staticmethod
    def answer_transform(answer):
        if answer == '正确':
            return '1'
        elif answer == '错误':
            return '0'
        else:
            return str(answer)


def main():
    cookie = 'deviceid=Wb05a8345fbc84530a38f9d3ff1857436; zh_choose=t; fxbdLocal=zh_CH; JSESSIONID=3876EE3EB9C6F6FE2A5B9E0DDACEB775'
    course_id = 17680
    examinee = Examinee(cookie=cookie, course_id=course_id)
    examinee.full_process()


if __name__ == '__main__':
    main()
