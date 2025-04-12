from neo4j import GraphDatabase
import ssl

URI = "neo4j://941e739f.databases.neo4j.io"
USER = "neo4j"
PASSWORD = "Team_Blue"

# Crear un contexto SSL que no verifique certificados
context = ssl._create_unverified_context()

# Pasar el contexto SSL al driver
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD), encrypted=True, ssl_context=context)

with driver.session() as session:
    result = session.run("MATCH (n) RETURN count(n) AS node_count")
    print("Connected successfully! Nodes:", result.single()["node_count"])

driver.close()