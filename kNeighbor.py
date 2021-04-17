from neo4j import GraphDatabase
import faiss
import numpy
from sklearn.neighbors import NearestNeighbors
driver = GraphDatabase.driver("bolt://localhost", auth=("neo4j", "123456"))

dict = dict()
embedding = []
with driver.session(database="test01.db") as session:
    result = session.run("""
    MATCH (n)
    RETURN n.name AS name, n.embeddingNode2vec AS embedding
    """)
    for record in result:
        embedding.append([record["name"],  record["embedding"]])

print(embedding[0])

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

def sklearn():
    nbrs = NearestNeighbors(n_neighbors=10, algorithm='ball_tree').fit(vec)
    distances, indices = nbrs.kneighbors(vec[:1])
    print(distances)
    print(indices)
