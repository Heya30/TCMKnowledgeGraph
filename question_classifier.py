import os
import ahocorasick


class QuestionClassifier:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        #　特征词路径
        self.node_path = os.path.join(cur_dir, 'dict/node.txt')

        self.herb_wds = []
        self.prescription_wds = []
        self.disease_wds = []

        for node in open(self.node_path):
            s = node.strip().split("|")
            name = s[1]
            type = s[2]
            if type == "草药":
                self.herb_wds.append(name)
            elif type == "方剂":
                self.prescription_wds.append(name)
            elif type == '疾病':
                self.disease_wds.append(name)

        self.region_words = set(self.herb_wds + self.prescription_wds + self.disease_wds)

        # 构造领域actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()
        # 问句疑问词

        self.cureway_qwds = ['怎么治疗', '如何医治', '怎么医治', '怎么治', '怎么医', '如何治', '医治方式', '疗法', '咋治', '怎么办', '咋办', '咋治', '开什么方', '什么方能治']
        self.cure_qwds = ['治疗什么', '治啥', '治疗啥', '医治啥', '治愈啥', '主治啥', '主治什么', '有什么用', '有何用', '用处', '用途',
                          '有什么好处', '有什么益处', '有何益处', '用来', '用来做啥', '用来作甚', '需要', '要', '治什么']
        self.contain_qwds = ['包含', '有哪些', '组成']

        print('model init finished ......')

        return

    '''分类主函数'''
    def classify(self, question):
        data = {}
        medical_dict = self.check_medical(question)
        if not medical_dict:
            return {}
        data['args'] = medical_dict
        # 收集问句当中所涉及到的实体类型
        types = []
        for type_ in medical_dict.values():
            types += type_

        question_types = []

        # 开方
        if self.check_words(self.cureway_qwds, question) and ('disease' in types):
            question_type = 'disease_prescription'
            question_types.append(question_type)

        # 药方组成
        if self.check_words(self.contain_qwds, question) and ('prescription' in types):
            question_type = 'prescription_contains'
            question_types.append(question_type)

        # 症状
        if self.check_words(self.cure_qwds, question) and ('herb' in types):
            question_type = 'herb_disease'
            question_types.append(question_type)


        # 若没有查到相关的外部查询信息，那么则将该疾病的描述信息返回
        if question_types == [] and 'disease' in types:
            question_types = ['disease_prescription']


        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types

        return data

    '''构造词对应的类型'''
    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.disease_wds:
                wd_dict[wd].append('disease')
            if wd in self.herb_wds:
                wd_dict[wd].append('herb')
            if wd in self.prescription_wds:
                wd_dict[wd].append('prescription')
        return wd_dict

    '''构造actree，加速过滤'''
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''问句过滤'''
    def check_medical(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)

        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i:self.wdtype_dict.get(i) for i in final_wds}

        return final_dict

    '''基于特征词进行分类'''
    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False


if __name__ == '__main__':
    handler = QuestionClassifier()

    data = handler.classify("丹参可以用来治什么病，痛经可以吃什么")
    print(data)