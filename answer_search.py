from py2neo import Graph
from Util import reserve_chinese


class AnswerSearcher:
    def __init__(self):
        self.g = Graph(
            host="127.0.0.1",
            http_port=7474,
            user="neo4j",
            password="123456")
        self.num_limit = 20

    '''执行cypher查询，并返回相应结果'''
    def search_main(self, sqls):
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                ress = self.g.run(query).data()
                answers += ress
            final_answer = self.answer_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answer

    '''根据对应的qustion_type，调用相应的回复模板'''
    def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''
        if question_type == 'disease_prescription':
            desc = [reserve_chinese(i['n.name']) for i in answers]
            desc = set(desc)
            if "方剂" in desc:
                desc.remove("方剂")
            subject = answers[0]['m.name']
            final_answer = '治疗{0}可以用的方子有：{1}'.format(subject, '；'.join(list(desc)))

        elif question_type == 'prescription_contains':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '药方{0}包含的药材有：{1}'.format(subject, '；'.join(list(set(desc))))

        elif question_type == 'herb_disease':
            desc = [i['disease.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}可以用来治疗的疾病有：{1}'.format(subject, '；'.join(list(set(desc))))
        return final_answer


if __name__ == '__main__':
    searcher = AnswerSearcher()
    s = searcher.search_main([{'question_type': 'prescription_contains', 'sql': ["MATCH (m:`方剂`)-[:组成]->(n:`草药`) where m.name = '自拟方_crkxqhxqfbygsfzlbbf' return distinct m.name,n.name"]}])
    print(s)