- 命令行直接导入neo4j命令
bin/neo4j-admin import --database=test01.db --delimiter "|"  --id-type STRING  --nodes ./import/node.txt --relationships ./import/edge.txt
