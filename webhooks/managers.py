class AsanaManager():
    def __init__(self, resource, *args, **kwargs):
        self.resource = kwargs.get('type')
        self.username = kwargs.get('assignee')
        self.title = kwargs.get('title')
        self.body = kwargs.get('body')
        self.github_id = kwargs.get('github_id') 

    