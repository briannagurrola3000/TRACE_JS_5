from neo4j import GraphDatabase

class DBEnumerator:
    def __init__(self, uri="neo4j+s://941e739f.databases.neo4j.io", user="neo4j", password="Team_Blue"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.tableNames = []  # Node labels (e.g., Project, User, File)
        self.columnNames = []  # All property keys across nodes
        self.table = {}  # Map of label -> node data
        self.enumerate_database()

    def enumerate_database(self):
        with self.driver.session() as session:
            # Enumerate node labels (SRS 3.2.2.8.6)
            result = session.run("CALL db.labels()")
            self.tableNames = [record["label"] for record in result]

            # Enumerate property keys (SRS 3.2.2.8.7)
            result = session.run("CALL db.propertyKeys()")
            self.columnNames = [record["propertyKey"] for record in result]

            # Enumerate nodes and properties (SRS 3.2.2.8.5)
            for label in self.tableNames:
                result = session.run(f"MATCH (n:{label}) RETURN n")
                self.table[label] = [dict(record["n"]) for record in result]

    def process_responses(self, machine_data):
        # Placeholder: Could process external data into Neo4j (SRS 3.2.2.8.8)
        pass

    def save_results(self):
        # Already in Neo4j; could export if needed (SRS 3.2.2.8.9)
        pass

    def reset(self):
        # Clear in-memory data and re-enumerate (SRS 3.2.2.8.10)
        self.tableNames = []
        self.columnNames = []
        self.table = {}
        self.enumerate_database()

    def display_results(self):
        # Display results (SRS 3.2.2.8.11)
        print("Node Labels (Tables):", self.tableNames)
        print("Property Keys (Columns):", self.columnNames)
        print("Node Data (Table):", self.table)

# Example usage
if __name__ == "__main__":
    db_enum = DBEnumerator()
    db_enum.display_results()