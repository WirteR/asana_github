from .models import Task, Comment
import asana
import json
import os


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
    def get_user_gid(self):
        users = self.client.users.get_users_for_workspace('1197770606849983')
        for x in users:
            if x['name'] == self.assignee:
                return x['gid']

    def get_sections(self, section_name):
        sections = self.client.sections.get_sections_for_project('1197769418678393')
        if section_name == 'TD':
            section_name = 'To do'
        elif section_name == 'DO':
            section_name = 'Doing'
        else:
            section_name = 'Done'
        for x in sections:
            if x['name'] == section_name:
                return x['gid']

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
            str(Task.objects.get(github_id=self.github_id).asana_id),
            {
                'name': self.title,
                'notes': self.body,
            }
        )

    def delete(self):
        self.client.tasks.delete_task(str(Task.objects.get(github_id=self.github_id).asana_id))

    def assign(self):
        user_gid = self.get_user_gid()
        self.client.tasks.update_task(
            str(Task.objects.get(github_id=self.github_id).asana_id),
            {
                'assignee': f"{user_gid}",
                'workspace': '1197770606849983',
            })

    def unassign(self):
        self.client.tasks.update_task(
            str(Task.objects.get(github_id=self.github_id).asana_id),
            {'assignee': None})

    def close(self):
        obj = Task.objects.get(github_id=self.github_id)
        section_gid = self.get_sections(obj.status)
        response = self.client.tasks.update_task(
            str(obj.asana_id),
            {
                    'completed': True,
                    'projects': [
                        '1197769418678393'
                    ],
                    "memberships":[{
                        "project": "1197769418678393",
                        "section": '{}'.format(section_gid)
                    }]}
            )
        print(response)
        


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
                str(gid),
                {
                    "text": self.body
                }
            )

    def delete(self):
        self.client.stories.delete_story(str(Comment.objects.get(github_id=self.github_id).asana_id))


class GitGubManager:
    def __init__(self, *args, **kwargs):
        self.auth = ('WirteR', 'PesVasil10-')

    

class AsanaOutputManager:
    def __init__(self, code):
        self.code = code
        self.client = asana.Client.access_token('1/1197770606849972:6ec58af88e7446f312e7b1c9e435baff')

    def transform_data(self, data):
        response = []
        gid_group = {}
        for x in data:
            if not recource_gid_group.get(x['resource']['gid']):
                gid_group[x['resource']['gid']] = {
                    'author': self.client.users.get_user(x['user']['gid']).get('name'),
                    'type': x['resource']['resource_type'],
                    'action': x['action'],
                    'asana_id': x['resource']['gid'],
                }
                temp = {}
                if x['resource']['resource_type'] == 'task':
                    obj = self.client.tasks.get_task(x['resource']['gid'])
                    temp['assignee'] = self.client.users.get_user(obj.get('assignee')).get('name')
                    temp['body'] = obj.get('notes')
                    temp['title'] = obj.get('name')

                if x['resource']['resource_type'] == 'story':
                    obj = self.client.stories.get_story(x['resource']['gid'])
                    temp['body'] = obj.get("text")
            
            if x['parent']['resource_type'] == 'section':
                gid_group[x['resource']['gid']]['status'] = self.client.sections.get_section(x['parent']['gid'])
                
        return gid_group.values()


    def retrieve_main_data(self):
        transformed_data = self.transform_data(self.code)
        print(transformed_data)

    

