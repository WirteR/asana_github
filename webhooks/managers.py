from .models import Task, Comment
import asana
import json
import os
import requests


class AsanaManager:
    def __init__(self, *args, **kwargs):
    
        self.client = asana.Client.access_token('your token')
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
        users = self.client.users.get_users_for_workspace('your_workspace')
        for x in users:
            if x['name'] == self.assignee:
                return x['gid']

    def get_sections(self, section_name):
        sections = self.client.sections.get_sections_for_project('your_project')
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
            'workspace': 'your_workspace',
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
                'workspace': 'your_workspace',
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
                        'your_project'
                    ],
                    "memberships":[{
                        "project": "your_project",
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


class GithubManager:
    def __init__(self):
        self.username = "username"
        self.password = "password-"
        self.created_issue_id = ''
        self.created_issue_url = ''
        self.created_comment_url = ''

    def create(self, data):
        respose = requests.post(
            'https://api.github.com/WirteR/asana_github/issues',
            auth=(self.username, self.password),
            headers={ "Content-Type": "application/json" },
            data = json.dumps({
                'title': data['title'],
                'body': data['body'],
                'assignee': data['assignee']
            }),
        )
        body_unicode = response.decode('utf-8')
        body = json.loads(body_unicode)
        self.created_issue_id = body.get('id')
        self.created_issue_url = body.get('url')
        Task.objects.filter(asana_id=data.get('asana_id')).update(github_id=body.get('id'))

    def update(self, data):
        response = requests.patch(
            self.created_issue_url,
            params = json.dumps({
                'title': data['title'] if data.get('title'),
                'body':  data['body'] if data.get('body'),
                'state': 'closed' if data.is_closed else 'open',
                'assignee': data['assignee'] if data.get('assignee')
            }),
            auth=(self.username, self.password),
            headers={ "Content-Type": "application/json" },
        )
    
    def comment(self, data):
        response = requests.post(
            self.created_issue_url + '/comments',
            data = json.dumps({"body": data.get('body')}),
            auth=(self.username, self.password),
            headers={ "Content-Type": "application/json" },
        )
        body_unicode = response.decode('utf-8')
        body = json.loads(body_unicode)
        Comment.objects.filter(asana_id=data.get('asana_id')).update(github_id=body.get('id'))

    def update_comment(self, data, comment_id):
        response = requests.patch(
            self.created_issue_url + f'/comments/{comment_id}',
            params = json.dumps({
                'body': data.get('body')
            }),
            auth=(self.username, self.password),
            headers={ "Content-Type": "application/json" },
        )

    def delete_comment(self, comment_id):
        response = requests.delete(
            self.created_issue_url + f'/comments/{comment_id}',
            auth=(self.username, self.password),
            headers={ "Content-Type": "application/json" },
        )
    

class AsanaOutputManager:
    def __init__(self, code):
        self.code = code
        self.client = asana.Client.access_token('your token')

    def transform_added_data(self, data):
        response = []
        gid_group = {}
        for x in data:
            if not gid_group.get(x['resource']['gid']):
                gid_group[x['resource']['gid']] = {
                    'author': self.client.users.get_user(x['user']['gid']).get('name'),
                    'type': x['resource']['resource_type'],
                    'action': x['action'],
                    'asana_id': x['resource']['gid'],
                    'resource_subtype': x['resource']['resource_subtype']
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
                    temp['parent'] = x['parent']['gid']

                gid_group[x['resource']['gid']] = {**gid_group[x['resource']['gid']], **temp}
            
            if x['parent']['resource_type'] == 'section':
                gid_group[x['resource']['gid']]['status'] = self.client.sections.get_section(x['parent']['gid']).get('name')
                
        return gid_group.values()

    def transform_changed_data(self, data):
        response = []
        for x in data:
            temp = {
                'user': self.client.users.get_user(x['user']['gid'])
                'action': x['action'],
                'type': x['resource']['recource_type'],
                'asana_id': x['resource']['gid']
            }
            if temp['type'] == task:
                obj = self.client.tasks.get_task(x['resource']['gid'])
                temp['title'] = obj.get('name')
                temp['body'] = obj.get('notes')
                temp['asignee'] = obj.get('assignee')
                temp['status'] = obj.get('memberships')['section']['name']
                temp['is_closed'] = obj.get('completed')

            if temp['type'] == story:
                if x['resource']['recource_subtype'] != 'added_to_project':
                    temp['body'] = self.client.stories.get_story(x['resource']['gid'])
            response.append(temp)

        return response


    def transform_deleted_data(self, data):
        response = []
        for x in data:
            temp = {
                'user': self.client.users.get_user(x['user']['gid'])
                'action': x['action'],
                'type': x['resource']['recource_type']
                'asana_id': x['resource']['gid']
            }
            response.append(temp)
        return response



    def retrieve_main_data(self):
        added = []
        changed = []
        deleted = []
        for x in self.code:
            if x['action'] == 'added':
                added.append(x)
            if x['action'] == 'changed':
                changed.append(x)
            if x['action'] == 'deleted':
                deleted.append(x)

        added = self.transform_added_data(added)
        changed = self.trasform_changed_data(changed)
        deleted = self.transform_deleted_data(changed)

        return {
            'added': added,
            'changed': changed,
            'deleted': deleted
        }

    

