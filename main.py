import os
import json
import re
from Util import get_acronym, reserve_chinese, getHash

cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])


class NameEntityRecognition:
    def __init__(self):
        self.data_path = os.path.join(cur_dir, 'data/data_example1.txt')
        self.nodes = []
        self.relations = []

    def read_nodes(self):
        with open(self.data_path, 'r', encoding='utf-8-sig') as f:
            data = f.read()
        data_json = json.loads(data)
        for key, value in data_json.items():
            id = get_acronym(reserve_chinese(key))
            if '医案' in value:
                record = value['医案']
                record_prescription = "方剂" + '_' + id
                if '方名' in record:
                    record_prescription = record['方名'] + '_' + id
                if record_prescription in [node[1] for node in self.nodes]:
                    record_prescription += ''.join(re.findall(r'\d', record['就诊时间']))
                    print(record_prescription)
                self.addNode(record_prescription, '方剂')

                if '中医诊断' in record:
                    record_diagnose = record['中医诊断']
                    self.addNode(record_diagnose, '疾病')
                    self.relations.append([record_prescription, record_diagnose, '治疗'])
                if '组成' in record:
                    for herb in record['组成'].split(","):
                        if bool(re.search(r'\d', herb)):
                            herb = re.search(r'([^\r\n]*?)[0-9]', herb).group(1)
                        self.addNode(re.sub('[\\r\\n]', '', herb), '草药')
                        self.relations.append([record_prescription, herb, '组成'])
        return self.relations, self.nodes

    def addNode(self, entityName, type):
        node = [getHash(entityName), entityName, type]
        if node not in self.nodes:
            self.nodes.append(node)


def outTriple(relation):
    f = open(os.path.join(cur_dir, 'result/triple.txt'), 'w', encoding='utf-8')
    for line in relation:
        f.write(line[0] + ' ' + line[1] + ' ' + line[2] + '\n')
    f.close()


def outNodes(entities):
    f = open(os.path.join(cur_dir, 'result/node.txt'), 'w', encoding='utf-8')
    f.write("node:ID,name,:LABEL\n")
    for line in entities:
        f.write(line[0] + ',' + line[1] + ',' + line[2] + '\n')
    f.close()


def outEdges(relations):
    f = open(os.path.join(cur_dir, 'result/edge.txt'), 'w', encoding='utf-8')
    f.write(":START_ID,:END_ID,:TYPE\n")
    for line in relations:
        f.write(getHash(line[0]) + ',' + getHash(line[1]) + ',' + line[2] + '\n')
    f.close()


if __name__ == '__main__':
    handler = NameEntityRecognition()
    relations, nodes = handler.read_nodes()
    print(len(relations))
    # outNodes(nodes)
    # outEdges(relations)
    print(nodes)
