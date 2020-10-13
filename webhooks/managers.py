from .models import Task, Comment
import asana

class AsanaManager:
    def __init__(self, *args, **kwargs):
    
        self.client = asana.Client.access_token('1/1197770606849972:6ec58af88e7446f312e7b1c9e435baff')
        self.resource = kwargs.get('type')
        self.author = kwargs.get('author')
        self.body = kwargs.get('body')
        self.github_id = kwargs.get('github_id')
        
        if self.resource == 'task':
            self.assignee = kwargs.get('assignee')
            self.title = kwargs.get('title')
            self.task_obj = Task.objects.filter(github_id=self.github_id)

        else:
            print('here')
            print(kwargs.get('task').asana_id)
            self.task_obj = kwargs.get('task')
    

class AsanaTaskManager(AsanaManager):
    def create(self):
        response = self.client.tasks.create_task({
            'workspace': '1197770606849983',
            'name': self.title,
            'notes': self.body,
            'projects': [
                '1197769418678393'
            ]
        })
        self.task_obj.update(asana_id=response.get('gid'))

    def update(self):
        self.client.tasks.update_task(
            self.task_obj.asana_id, 
            {
                'name': self.title,
                'notes': self.body,
            }
        )


class AsanaCommentManager(AsanaManager):
    def create(self):
        result = self.client.stories.create_story_for_task(
            str(self.task_obj.asana_id),{
                "text":self.body
            }
        )
        Comment.objects.filter(github_id=self.github_id).update(asana_id=result['gid'])

    def update(self):
        gid = Comment.objects.get(github_id=self.github_id).asana_id
        self.client.stories.update_story(
                asana_id,
                {
                    "text": self.body
                }
            )