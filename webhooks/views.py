from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import json
import asana
import pdb


from .models import *
from .managers import *
# Create your views here.

class Settings(View):
    def get(self, request):
        return HttpResponse('get settings')

    def post(self, request):
        return HttpResponse('post settings')


class DashBoard(View):
    def get(self, request):
        client = asana.Client.access_token('your token)
        client.headers["Asana-Enable"] = "string_ids"
        result = client.webhooks.create({
            "target":'your_site', 
            "resource":"your_project_id"
        })
        print(result)


@csrf_exempt
@require_POST
def github_webhook(request):
    if not request.body:
        return HttpResponse(200)

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    Request.objects.create(body=body)

    issue = body['issue']
    comment = body.get('comment')

    task_github_id = issue['id']
    task_data = {
        'title': issue['title'],
        'body': issue.get('body'),
        'author': issue['user']['login'],
        'assignee': issue['assignee']['login'] if issue['assignee'] else '',
        'github_id': task_github_id
    }
    
    asana_task = AsanaTaskManager(type="task", **task_data)

    task_obj = Task.objects.filter(github_id=task_github_id)
    if not task_obj and body['action'] != 'opened':
        Task.objects.create(**task_data)
        asana_task.create()
    #doneget
    if body['action'] == 'opened':
        Task.objects.create(**task_data)
        asana_task.create()

    if comment:
        comment_github_id = comment['id']
        comment_data = {
            'task': Task.objects.get(github_id=task_github_id),
            'body': comment['body'],
            'author': comment['user']['login'],
            'github_id': comment['id']
        }
        asana_comment = AsanaCommentManager(type="comment", **comment_data)
        comment_obj = Comment.objects.filter(github_id=comment_github_id)
        if not comment_obj and body['action'] != 'created':
            Comment.objects.create(**comment_data)
    #done
    if body['action'] == 'created':
        Comment.objects.create(**comment_data)
        asana_comment.create()
    #done
    if body['action'] == 'edited':
        if not body.get('comment'):
            task_obj.update(**task_data)
            asana_task.update()
        else:
            comment_obj.update(**comment_data)
            asana_comment.update()

    if body['action'] == 'assigned':
        task_obj.update(assignee=issue['user']['login'])
        asana_task.assign()

    if body['action'] == 'unassigned':
        task_obj.update(assignee='')
        asana_task.unassign()

    if body['action'] == 'closed':
        task_obj.update(status='DN', is_closed=True)
        asana_task.close()
    #done
    if body['action'] == 'deleted':
        if not body.get('comment'):
            asana_task.delete()
            task_obj.delete()
        else:
            asana_comment.delete()
            comment_obj.delete()
            

    return HttpResponse('pong')


@csrf_exempt
@require_POST
def asana_webhook(request):
    if not request.body:
        try:
            response = HttpResponse(content_type='application/json',)
            response['X-Hook-Secret'] = request.META["HTTP_X_HOOK_SECRET"]
            response.status_code = 200
            return response
        except:
            pass

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    body = body['events']
    output_manager = AsanaOutputManager(body)
    validated_data = output_manager.retrieve_main_data()
    github = GithubManager()

    for k,v in validated_data.items():
        if k == 'added':
            for x in v:
                if x['type'] == "task":
                    Task.objects.create(
                        title=x['title'],
                        body=x['body'],
                        assignee=x['assignee'],
                        author=x['author'],
                        status=x['status'],
                        asana_id=x['asana_id']
                    )
                    github.create(data={
                        'title': x['title'],
                        'body': x['body'],
                        'assignee': x['assignee'],
                        'asana_id': x['asana_id']
                    })

                if x['type'] == "story":
                    if x['recource_subtype'] != 'added_to_project':
                        Comment.objects.create(
                            task=Task.objects.filter(asana_id=x['parent']),
                            body=x['body'],
                            asana_id=x['asana_id'],
                            author=x['author']
                        )
                        github.comment(data={
                            'body': x['body'],
                            'asana_id': x['asana_id']
                        })


        if k == 'changed':
            for x in v:
                if x['type'] == "task":
                    Task.objects.filter(asana_id=x['asana_id']).update(
                        title=x['title'],
                        body=x['body'],
                        assignee=x['assignee'],
                        status=x['status'],
                        is_closed=x['is_closed']
                    )
                    github.update(data={
                        'title': x['title'],
                        'body': x['body'],
                        'assignee': x['assignee'],
                        'state': x['status'],
                        'asana_id': x['asana_id']
                    })

                if x['type'] == "story":
                    Comment.objects.filter(asana_id=x['asana_id']).update(
                        body=x['body']
                    )
                    github.update_comment(data={
                            'body': x['body'],
                            'asana_id': x['asana_id']
                        })

        if k == "deleted":
            for x in v:
                if x['type'] == "task":
                    Task.objects.filter(asana_api=x['asana_id']).delete()
                if x['type'] == "story":
                    obj = Comment.objects.filter(asana_api=x['asana_id'])
                    github.delete_comment(obj.github_id)
                    obj.delete()

    return HttpResponse(200)

    