from neo4j import GraphDatabase
import time

class Neo4jCRUD:
    def __init__(self, uri, user, password):
        # Neo4jの起動を待つため、最大30秒まで接続を試みる
        start_time = time.time()
        while True:
            try:
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
                # 接続テスト
                with self.driver.session() as session:
                    session.run("MATCH () RETURN 1 LIMIT 1")
                break
            except Exception as e:
                if time.time() - start_time > 30:
                    raise Exception("Neo4jへの接続がタイムアウトしました")
                print("Neo4jの起動を待っています...")
                time.sleep(2)

    def close(self):
        self.driver.close()

    # Create操作: ユーザーノードを作成
    def create_user(self, name, age):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_user, name, age
            )
            return result

    @staticmethod
    def _create_user(tx, name, age):
        query = (
            "CREATE (u:User {name: $name, age: $age}) "
            "RETURN u.name, u.age"
        )
        result = tx.run(query, name=name, age=age)
        return result.single()

    # Read操作: 全ユーザーを取得
    def get_all_users(self):
        with self.driver.session() as session:
            return session.read_transaction(self._get_all_users)

    @staticmethod
    def _get_all_users(tx):
        query = "MATCH (u:User) RETURN u.name, u.age"
        result = tx.run(query)
        return [{"name": record["u.name"], "age": record["u.age"]} 
                for record in result]

    # Update操作: ユーザーの年齢を更新
    def update_user_age(self, name, new_age):
        with self.driver.session() as session:
            return session.write_transaction(
                self._update_user_age, name, new_age
            )

    @staticmethod
    def _update_user_age(tx, name, new_age):
        query = (
            "MATCH (u:User {name: $name}) "
            "SET u.age = $new_age "
            "RETURN u.name, u.age"
        )
        result = tx.run(query, name=name, new_age=new_age)
        return result.single()

    # Delete操作: ユーザーを削除
    def delete_user(self, name):
        with self.driver.session() as session:
            return session.write_transaction(self._delete_user, name)

    @staticmethod
    def _delete_user(tx, name):
        query = "MATCH (u:User {name: $name}) DELETE u"
        return tx.run(query, name=name)

def main():
    # Neo4jデータベースに接続
    crud = Neo4jCRUD("bolt://my_neo4j:7687", "neo4j", "docker")
    
    try:
        # 1. ユーザーの作成
        print("\n=== ユーザーの作成 ===")
        crud.create_user("田中", 25)
        crud.create_user("鈴木", 30)
        
        # 2. 全ユーザーの取得
        print("\n=== 全ユーザーの取得 ===")
        users = crud.get_all_users()
        for user in users:
            print(f"名前: {user['name']}, 年齢: {user['age']}")
        
        # 3. ユーザーの更新
        print("\n=== ユーザーの更新 ===")
        crud.update_user_age("田中", 26)
        users = crud.get_all_users()
        for user in users:
            print(f"名前: {user['name']}, 年齢: {user['age']}")
        
        # 4. ユーザーの削除
        print("\n=== ユーザーの削除 ===")
        crud.delete_user("鈴木")
        users = crud.get_all_users()
        for user in users:
            print(f"名前: {user['name']}, 年齢: {user['age']}")

    finally:
        crud.close()

if __name__ == "__main__":
    main()
