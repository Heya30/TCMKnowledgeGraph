from neo4j import GraphDatabase
import faiss
import numpy
driver = GraphDatabase.driver("bolt://localhost", auth=("neo4j", "123456"))

dict = dict()
embedding = []
with driver.session(database="test01.db") as session:
    result = session.run("""
    MATCH (n)
    RETURN n.name AS name, n.embeddingNode2vec AS embedding
    """)
    for record in result:
        # dict[record["name"]] = record["embedding"]
        embedding.append([record["name"],  record["embedding"]])

print(embedding[0])

d=10
index = faiss.IndexFlatL2(d)   # build the index
# index.add(xb)    # add vectors to the index

vec = []
for record in embedding:
    print(record[0])
    vec.append(record[1])
vec = numpy.array(vec).astype("float32")
print(vec.dtype)
index.add(numpy.array(vec))
print(index.ntotal)

print(vec[:1])
k = 10                         # we want to see 4 nearest neighbors
D, I = index.search(vec[15:16], k) # sanity check

for i in I[0]:
    print(embedding[i])