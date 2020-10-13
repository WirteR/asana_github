from .models import Task, Comment
import asana

class AsanaManager():
    def __init__(self, *args, **kwargs):
        self.client = asana.Client.access_token('1/1197770606849972:6ec58af88e7446f312e7b1c9e435baff')
        self.resource = kwargs.get('type')
        self.author = kwargs.get('author')
        self.body = kwargs.get('body'),
        self.github_id = kwargs.get('github_id')
        
        if self.resource == 'task':
            self.assignee = kwargs.get('assignee')
            self.title = kwargs.get('title')

        else:
            self.task_id = kwargs.get('assignee').github_id

    def create_task(self):
        print(self.title, self.body)
        res = self.client.tasks.create_task({
            'workspace': '1197770606849983',
            'name': str(self.title),
            'notes': str(self.body),
            'projects': [
                '1197769418678393'
            ]
        })
        print(res)
    