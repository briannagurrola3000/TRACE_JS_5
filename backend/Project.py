import datetime

class Project:
    def __init__(self, project_name, start_date, time, lead_analyst_initials, 
                 description, machine_ip, list_files = "", file_paths=None, is_locked=False, status="active",
                 created_date=None, last_edit_date=None, folder_path=None):
        self.project_name = project_name #
        self.description = description #
        self.start_date = start_date
        self.time = time
        self.lead_analyst_initials = lead_analyst_initials
        self.is_locked = is_locked #
        self.status = status #
        self.created_date = created_date or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_edit_date = last_edit_date or self.created_date
        self.folder_path = folder_path or f"projects/{project_name}"
        self.machine_ip = machine_ip # Added
        self.list_files = list_files # Added

    def get_info(self):
        return {
            "project_name": self.project_name,
            "description": self.description,
            "start_date": self.start_date,
            "time": self.time,
            "lead_analyst_initials": self.lead_analyst_initials,
            "is_locked": self.is_locked,
            "status": self.status,
            "created_date": self.created_date,
            "last_edit_date": self.last_edit_date,
            "folder_path": self.folder_path,
            "Machine IP": self.machine_ip, 
            "Files": self.list_files
        }

    def lock(self):
        self.is_locked = True

    def unlock(self):
        self.is_locked = False

    def update_status(self, new_status):
        if new_status in ["active", "errors", "inactive"]:
            self.status = new_status
            self.last_edit_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")