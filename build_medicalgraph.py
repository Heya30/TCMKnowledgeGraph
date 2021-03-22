import os
import json
import re
from Util import get_acronym, reserve_chinese, getHash
from py2neo import Graph, Node

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
                self.addNode(record_prescription, '方剂')

                if '中医诊断' in record:
                    record_diagnose = record['中医诊断']
                    self.addNode(record_diagnose, '疾病')
                    self.relations.append([record_prescription, record_diagnose, '治疗'])
                if '组成' in record:
                    for herb in record['组成'].split(","):
                        if bool(re.search(r'\d', herb)):
                            herb = re.search(r'([^\r\n]*?)[0-9]', herb).group(1)
                        herb = re.sub('[\\r\\n]', '', herb)
                        self.addNode(herb, '草药')
                        self.relations.append([record_prescription, herb, '组成'])
        return self.relations, self.nodes

    def addNode(self, entityName, type):
        node = [getHash(entityName), entityName, type]
        if node not in self.nodes:
            self.nodes.append(node)


class MedicalGraph:
    def __init__(self):
        self.g = Graph(
            host='127.0.0.1',
            http_port=7474,
            user='neo4j',
            password='123456')

    def generate_nodes(self, nodes):
        for node in nodes:
            neo4j_node = Node(node[2], name=node[1], id=node[0])
            self.g.create(neo4j_node)

    def generate_relation(self, relations):
        for relation in relations:
            startName = relation[0]
            endName = relation[1]
            relType = relation[2]
            query = "match(p),(q) where p.name='%s'and q.name='%s' create (p)-[rel:%s]->(q)" % (startName, endName, relType)
            try:
                self.g.run(query)
            except Exception as e:
                print(e)


def outTriple(relation):
    f = open(os.path.join(cur_dir, 'dict/triple.txt'), 'w', encoding='utf-8')
    for line in relation:
        f.write(line[0] + ' ' + line[1] + ' ' + line[2] + '\n')
    f.close()


def outNodes(entities):
    f = open(os.path.join(cur_dir, 'dict/node.txt'), 'w', encoding='utf-8')
    f.write("node:ID|name|:LABEL\n")
    for line in entities:
        f.write(line[0] + '|' + line[1] + '|' + line[2] + '\n')
    f.close()


def outEdges(relations):
    f = open(os.path.join(cur_dir, 'dict/edge.txt'), 'w', encoding='utf-8')
    f.write(":START_ID|:END_ID|:TYPE\n")
    for line in relations:
        f.write(getHash(line[0]) + '|' + getHash(line[1]) + '|' + line[2] + '\n')
    f.close()


if __name__ == '__main__':
    handler = NameEntityRecognition()
    relations, nodes = handler.read_nodes()

    generateGraph = MedicalGraph()
    generateGraph.generate_nodes(nodes)
    generateGraph.generate_relation(relations)
