class AsanaManager():
    def __init__(self, *args, **kwargs):
        self.resource = kwargs.get('resource')
        self.username = kwargs.get('assignee')
        self.title = kwargs.get('title')
        self.body = kwargs.get('body')
        self.github_id = kwargs.get('github_id') 
        print(self.resource, self.username, self.title, self.body)

    