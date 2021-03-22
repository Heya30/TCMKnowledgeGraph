class QuestionPaser:

    '''构建实体节点'''
    def build_entitydict(self, args):
        entity_dict = {}
        for name, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [name]
                else:
                    entity_dict[type].append(name)

        return entity_dict

    '''解析主函数'''
    def parser_main(self, res_classify):
        args = res_classify['args']
        # ['args'] = medical_dict
        entity_dict = self.build_entitydict(args)
        # ['question_types'] = question_types
        question_types = res_classify['question_types']
        sqls = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []
            # 查询治疗某疾病的方子
            if question_type == 'disease_prescription':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            # 查询药方包含的药材
            elif question_type == 'prescription_contains':
                sql = self.sql_transfer(question_type, entity_dict.get('prescription'))

            # 查询药材可以治疗的疾病
            elif question_type == 'herb_disease':
                sql = self.sql_transfer(question_type, entity_dict.get('herb'))

            if sql:
                sql_['sql'] = sql
                sqls.append(sql_)

        return sqls

    '''针对不同的问题，分开进行处理'''
    def sql_transfer(self, question_type, entities):
        if not entities:
            return []
        # 查询语句
        sql = []
        # 查询治疗某疾病的方子
        if question_type == 'disease_prescription':
            sql = ["MATCH (m:`疾病`)<- [:治疗]-(n:`方剂`) where m.name = '{0}' return distinct m.name, n.name".format(i) for i in entities]

        # 查询药方包含的药材
        elif question_type == 'prescription_contains':
            sql = ["MATCH (m:`方剂`)-[:组成]->(n:`草药`) where m.name = '{0}' return distinct m.name,n.name".format(i) for i in entities]

        # 查询药材可以治疗的疾病
        elif question_type == 'herb_disease':
            sql = ["match (m:`草药`) <-[:组成]-(n:`方剂`), (n)-[:`治疗`]->(disease:`疾病`) where m.name = '{0}' return distinct " \
                   "m.name, disease.name".format(i) for i in entities]

        return sql


if __name__ == '__main__':
    handler = QuestionPaser()
    sql = handler.parser_main({'args': {'自拟方_crkxqhxqfbygsfzlbbf': ['prescription']}, 'question_types': ['prescription_contains']})
    print(sql)