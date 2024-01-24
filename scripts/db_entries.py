

# Declare the default database entry we shoud receive from notion API
class DbEntry:
    def __init__(self, id, created_time, last_edited_time, properties, url, created_by=None, last_edited_by=None):
        self.id = id
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.properties = properties
        self.url = url
        self.created_by = created_by
        self.last_edited_by = last_edited_by
