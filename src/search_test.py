# Neo4jドライバーをインポート
from neo4j import GraphDatabase

# Neo4jデータベースへの接続を確立
driver = GraphDatabase.driver('bolt://my_neo4j:7687', auth=('neo4j', 'docker'))
# セッションを開始
session = driver.session()
# データベース内のすべてのノードを25件まで取得して表示
for i in session.run('MATCH (n) RETURN n LIMIT 25'):
    print(i['n'])
# セッションを閉じる
session.close()
