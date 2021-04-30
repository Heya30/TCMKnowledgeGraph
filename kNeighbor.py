from neo4j import GraphDatabase
import faiss
import numpy
from sklearn.neighbors import NearestNeighbors
import os

cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
driver = GraphDatabase.driver("bolt://localhost", auth=("neo4j", "123456"))

dict = dict()
embedding = []
disease = []
with driver.session(database="test01.db") as session:
    result = session.run("""
    MATCH (n:`疾病`)
    RETURN n.name AS name, n.embeddingNode2vec AS embedding
    """)
    for record in result:
        embedding.append([record["name"],  record["embedding"]])
        # print(record["embedding"])
        # dict[record["embedding"]] = record["name"]


vec = []
for record in embedding:
    vec.append(record[1])
vec = numpy.array(vec).astype("float32")


# faiss
def faissNeighbor():
    d=10
    index = faiss.IndexFlatL2(d)   # build the index
    index.add(numpy.array(vec))

    k = 10                         # we want to see 4 nearest neighbors
    D, I = index.search(vec[:1], k) # sanity check

    print(D)
    print(I)
    for i in I[0]:
        print(embedding[i])

def sklearn(disease):
    nbrs = NearestNeighbors(n_neighbors=11, algorithm='ball_tree').fit(vec)
    var = vec[disease].reshape(1, -1)
    distances, indices = nbrs.kneighbors(var)
    print("distance:")
    print(distances)
    print(indices)
    for i in indices[0]:
        print(embedding[i][0])

def out():
    f = open(os.path.join(cur_dir, 'dict/diseaseEmbedding.txt'), 'w', encoding='utf-8')
    for index in range(0, len(embedding)):
        f.write(str(index) + ' ' + embedding[index][0] +'\n')
    f.close()

sklearn(64)
out()