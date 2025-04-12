from neo4j import GraphDatabase
from json_builder import json
from datetime import datetime
import ssl
import json

URI="neo4j://941e739f.databases.neo4j.io"
User="neo4j"
Password="Team_Blue"
class Neo4jInteractive:
    def __init__(self, uri, user, password):
        context = ssl._create_unverified_context()
        # ENCRYPTED and SSL_CONTEXT don't move, they are neccessary for Macs (Mayra in this case at least)
        self.driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=True, ssl_context=context)
            
    # Allows to create a Lead Analyst
    # @params Name: Name of the Analyst, ID: Id of the Analyst
    # @returns JSON with format of all analysts or status error JSON
    def create_Analyst(self, Name, role, initials):
        # if we don't have all the parameters necessary to create an analyst we return a json with error status and erorr Message
        if not all([Name, role, initials]):
            return {"status": "failure", "error":"One or more parameters missing"}
        # initial query to create user
        query="CREATE (u: Analyst {name: $name, initials: $initials}) RETURN elementId(u)"
        
        query_find_role = """
        MERGE (r:Role {role: $role})
        RETURN r
        """
        with self.driver.session() as session:
            # run query with params in safe way using $
            result=session.run(query, name=str(Name), initials=str(initials).upper())
            session.run(query_find_role, role=str(role).capitalize())
            # Depending if is Lead or regular Analyst the permissinons are set
            query_create_relation = """MATCH (u:Analyst {initials: $initials}), (r:Role {role: $role}) MERGE (u)-[:HAS_ROLE]->(r)
                                    SET r.can_lock_unlock= CASE r.role WHEN 'Lead' THEN true ELSE false END, 
                                    r.can_delete = CASE r.role WHEN 'Lead' THEN true ELSE false END,
                                    r.can_create = CASE r.role WHEN 'Lead' THEN true else false END
                                    """
            session.run(query_create_relation, initials=str(initials).upper(), role=str(role).capitalize())
            return {"status": "success"}
    
    # Allows to delete an alayst specifying it's initials
    # @params: initials: Initials of the analyst we are going to delete
    # @returns: JSON format with success or error messages
    def delete_Analyst(self, initials):
        query = """
        MATCH (a:Analyst {initials: $initials})
        DETACH DELETE a
        RETURN COUNT(a) AS deleted_count
        """
        with self.driver.session() as session:
            result = session.run(query, initials=str(initials).upper())
            deleted_count = result.single()["deleted_count"]
        
            if deleted_count > 0:
                return {"status": "success"}
            else:
                return {"status": "failure", "error": "No analyst found"}

    
    
    #Allows to create project with name, id and locked status
    #@params: Project_Name: Name of the project, Lockedstatus: boolean value for locked status
    #         description: Some text to describe the project, MachineIP: the ip associated to that project
    #         status: current status of the project, list_files: list of all the files that the project have
    #@returns: JSON format of with success or error messages
    def create_project(self, Project_Name, lockedstatus, description, MachineIP, status, list_files):
        locked_bool = lockedstatus if isinstance(lockedstatus, bool) else lockedstatus.lower() == "true"
        if not is_ip_valid(MachineIP):
            return {"status": "failure", "error":"Invalid IP"}
        todayDate=datetime.now()
        formatDate = todayDate.strftime("%Y-%m-%dT%H:%M:%S")
        query= """CREATE (p: Project {name: $name, locked:$locked_status, 
                Stamp_Date: datetime($Stamp_Date), description: $description, MachineIP: $MachineIP, Status: $Status, files: $files, last_edit_date: datetime($last_edit)})"""
        with self.driver.session() as session:
            session.run(query, name=str(Project_Name), locked_status=locked_bool, Stamp_Date=formatDate, description=str(description), MachineIP=str(MachineIP), Status=str(status), files=[]if list_files=="" else list(list_files), last_edit=formatDate)
            return {"status": "success"}
        
    def relationship_results(self, project_name, id):
        if not all([project_name, id]):
            return {"status": "failure", "error":"One or more parameters missing"}
        query= """MATCH (p:Project {name: $name}), (r:Result {id:$id}) MERGE (p)-[:HAS_RESULT]->(r)"""
        with self.driver.session() as session:
            session.run(query, name=str(project_name), id=int(id))
            return {"status": "success"}


     # Allows to delete a specific project from the DB
    # @params: Project_ID: unique id of project to delete
    # @returns: JSON format of all projects updated
    def delete_project(self, project_name):
        with self.driver.session() as session:
            query = "MATCH (p:Project {name: $project_name}) DETACH DELETE p"
            session.run(query, project_name=project_name)
            return {"status": "success"}


    # Allows the Database to receive a JSON and put all the information inside a node called Results
    # @params: json_data: json object, result_type: indicator for which type of result is
    # @returns: json with success or failure status 
    def process_Response(self, json_data, result_type):
        #verify the multiple ways we can have our json
        if isinstance(json_data, str):
            try:
                results= json.loads(json_data)
            except json.JSONDecodeError:
                return {"status":"failure","error":"Unsupported type of JSON"}
        elif isinstance(json_data, list):
            results=json_data
        elif isinstance(json_data, dict):
            results=[json_data]
        else:
            return {"status":"failure", "error":"Unsupported type of JSON"}
        # Ensures our response contains all the required values
        required_fields = {"id", "response", "lines", "words", "chars", "payload", "length", "error"}
        for i, result in enumerate(results):
            if not required_fields.issubset(result.keys()):
                return {"status": "failure", "error": "Incomplete JSON, missing fields"}
        query = """
            CREATE (r:Result {
            id: $id,
            response: $response,
            lines: $lines,
            words: $words,
            chars: $chars,
            payload: $payload,
            length: $length,
            error: $error,
            type: $type
            })
            """
        with self.driver.session() as session:
            for result in results:
                session.execute_write(lambda tx: tx.run(query, **result, type=result_type))
        return {"status": "success"}
            
    #Allows to join to an existing project
    #@params: project_name: Name of the project to join, analystInitials: Initials of the analyst that will join the project
    #@returns: JSON format with success or error messages
    def join_project(self, project_name, analystInitials):
        query = """
        MATCH (a:Analyst {initials: $initials}), (p:Project {name: $name})
        MERGE (a)-[:inProject]->(p)
        RETURN COUNT(a) AS analysts_joined
        """
        with self.driver.session() as session:
            result = session.run(query, initials=str(analystInitials).upper(), name=str(project_name))
            analysts_joined = result.single()["analysts_joined"]

            if analysts_joined > 0:
                return {"status": "success"}
            else:
                return {"status": "failure", "error": "No analysts or project not found"}
    # Allows to create a folder(node) to store projects
    # @params: path: string with the path or name for the folder
    # @returns: JSON with success or failure status        
    def create_folder(self, path):
        if not path:
            return {"status":"failure", "error": "No name received"}
        query="""CREATE (:Folder {path:$path})"""
        with self.driver.session() as session:
            session.run(query, path=str(path))
            return {"status": "success"}
    
    def add_project_to_folder(self, project_name, folder_path):
        if not all([project_name, folder_path]):
            return {"status": "failure", "error": "No project or folder received"}
        query= """MATCH (u:Project {name: $name}), (f:Folder{path:$folder_path}) 
                MERGE (u)-[:IS_IN]->(f)"""
        with self.driver.session() as session:
            session.run(query, name=str(project_name), folder_path=str(folder_path))
        
    # Allows to add a relationship of ownership betwwen the analyst and a project
    # @params: Owner_initials: Initials of the Lead analyst, project_name: Name of the project the analyst os going to own
    # @returns: JSON format of all relationships
    def add_ownership(self, Owner_initials, project_name):
        query=""" MATCH (u:Analyst {initials: $initials})-[:HAS_ROLE]->(r:Role {role: "Lead"})
                MATCH (p:Project {name: $project})
                WHERE NOT (p)<-[:OWNS]-(:Analyst)
                MERGE (u)-[o:OWNS]->(p)
                RETURN o
                """
        with self.driver.session() as session:
            session.run(query, initials=str(Owner_initials), project=str(project_name))
            result=session.run("MATCH p=()-[]->() RETURN p")
            graph_data=[]
            for record in result:
                if record is None:
                    return {"status":"failure","error":"Proyect or Analyst does not exist or already has an owner"}
                path = record["p"]  # El camino 'p' es una lista de nodos y relaciones
                path_json = []
                #We search for nodes, neo4j has two different types, nodes or relationship (node such as User or project)
                for element in path.nodes:
                     node_json = {
                     "type": "Node",
                     "labels": list(element.labels),
                     "properties": dict(element)
                    }
                     path_json.append(node_json)
                #We search for relationships (OWNS)
                for relation in path.relationships:
                     relationship_json = {
                      "type": "Relationship",
                      "owner": dict(relation.start_node),
                      "project": dict(relation.end_node),
                      "type": relation.type,
                      "properties": dict(relation)
                    }
                     path_json.append(relationship_json)
                graph_data.append(path_json)
            #response_json = json("success")
            #response_json.set_data(graph_data)
            return {"status":"success",}
        
        
    # Allows to change locked property of a project to true
    # @params: Project_ID: Unique id of project to lock
    # @returns: JSON format of the locked project     
    def lock_projects(self, project_name):
        with self.driver.session() as session:
            lock = "MATCH (p:Project {name: $name}) SET p.locked = true"
            result=session.run(lock, name = project_name)
            projects= [{"ID": record["id"], "Name": record["name"], "isLocked": record["locked"], "files": record["files"]}for record in result]
            json_builder=json("succsess")
            json_builder.set_data(projects)
            return {"status":"success"}
            
    # Allows to change the locked property of a project to false
    # @params: Project_ID: Unique id of project to lock
    # @returns: Json format of unlocked project
    def unlock_projects(self, project_name):
        with self.driver.session() as session:
            lock = "MATCH (p:Project {name: $name}) SET p.locked = false"
            result=session.run(lock, name=project_name)
            projects= [{"ID": record["id"], "Name": record["name"], "isLocked": record["locked"], "files": record["files"]}for record in result]
            json_builder=json("succsess")
            json_builder.set_data(projects)
            return {"status":"success"}
            
    # Allows to add a list of files into the files property of a project node
    # @params: project_name: name of the project we want to add files, files: list of files to add into the project
    # @returns:JSON format with status
    def add_placeholderfiles(self, project_name, files):
        with self.driver.session() as session:
            query= """MATCH (p:Project {name: $project}) 
            SET p.files=$file_list
            RETURN p.id AS id, p.name AS name, p.locked AS locked, p.files AS files"""
            result=session.run(query, project=project_name, file_list=files)
            projects= [{"ID": record["id"], "Name": record["name"], "isLocked": record["locked"], "files": record["files"]}for record in result]
            json_builder=json("succsess")
            json_builder.set_data(projects)
            return {"status":"success"}

    # added the following to match project manager file ↓
    def get_project_by_name(self, name):
        query = """
        MATCH (p:Project {name: $name})
        RETURN p
        """
        with self.driver.session() as session:
            result = session.run(query, name=name)
            return [dict(record) for record in result]
    
     # Retreives all  the analysts in the database 
    # @params: no parameters
    # @returns: JSON format of all the Analysts 
    def print_Analyst(self):
        query = """
        MATCH (u:Analyst)
        RETURN u
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [dict(record["u"]) for record in result]
        

    def get_project(self, project_name):
        query = """
        MATCH (p:Project {name: $project_name})<-[:OWNS]-(u:Analyst)
        RETURN p, u.name AS lead_analyst_initials
        """
        with self.driver.session() as session:
            records = session.run(query, project_name=project_name)
            record = records.single()
            if record:
                p = record["p"]
                info = dict(p)
                info["lead_analyst_initials"] = record["lead_analyst_initials"]
                return info
            return {"status": "failure", "error":"Project with that name does not exist"}
    # get all projects to print
    def get_all_projects(self):
        query = """
        MATCH (a:Analyst)-[:OWNS]->(p:Project)
        RETURN p, a.initials AS analyst_initials
        """
        with self.driver.session() as session:
            result = session.run(query)
            projects=[{**dict(record["p"]),"analyst_initials": record["analyst_initials"]}for record in result]
            return projects
        
        
    # get all projects the analyst owns
    def get_my_projects(self, analyst_initials):
        query = """
        MATCH (u:Analyst {initials: $initials})-[:OWNS]->(p:Project)
        RETURN p
        """
        with self.driver.session() as session:
            result = session.run(query, initials=str(analyst_initials).upper())
            return [dict(record["p"]) for record in result]
    
    def get_Analyst(self):
        query="MATCH (a:Analyst) RETRUN a"
        with self.driver.session() as session:
            result= session.run(query)
            return [dict(record["a"]) for record in result]

    def get_shared_projects(self, analyst_initials):
        query = """
        MATCH (other:Analyst)-[:OWNS]->(p:Project)
        WHERE other.name <> $initials
        RETURN p
        """
        with self.driver.session() as session:
            result = session.run(query, initials=analyst_initials)
            return [dict(record["p"]) for record in result]

    
def is_ip_valid(ip):
    parts = ip.split(".")  
    if len(parts) != 4:  
        return False
    
    for part in parts:
        if not part.isdigit():  
            return False
        
        num = int(part)
        if num < 0 or num > 255: 
            return False
        
        if part != str(num):
            return False
    
    return True

