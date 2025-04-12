from ProjectManager import ProjectManager
from Project import Project

def main():
    pm = ProjectManager(uri="neo4j://941e739f.databases.neo4j.io", user="neo4j", password="Team_Blue")

    # Dummy project to initialize DELETED label
    pm.create_project("DummyInit", "2025-01-01", "00:00", "XX")
    pm.delete_project("DummyInit")
    pm.delete_forever("DummyInit")  # Clean it up

    print("\nCreating a new project:")
    pm.create_project("DemoProject", "2025-03-20", "09:00", "MR", "Demo for class")
    print("All projects:", pm.get_all_projects())

    print("\nRetrieving my projects (MR):")
    print(pm.get_my_projects("MR"))

    print("\nLocking and trying to delete:")
    pm.lock_project("DemoProject")
    print("Delete locked project:", pm.delete_project("DemoProject"))

    print("\nUnlocking and deleting:")
    project_info = pm.get_project("DemoProject")
    if project_info:
        project = Project(**{k: v for k, v in project_info.items() if k in Project.__init__.__code__.co_varnames})
        project.unlock()
        pm.unlock_project("DemoProject")  # Update DB
        pm.delete_project("DemoProject")
    print("Deleted projects:", pm.get_deleted_projects())

    print("\nRestoring project:")
    pm.restore_project("DemoProject")
    print("All projects after restore:", pm.get_all_projects())

    pm.close()

if __name__ == "__main__":
    main()