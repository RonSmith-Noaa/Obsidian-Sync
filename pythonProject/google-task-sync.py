import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/tasks']


def authenticate():
    """Authenticate and authorize user."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_tasks():
    """Get the user's tasks from Gmail."""
    creds = authenticate()
    service = build('tasks', 'v1', credentials=creds)

    try:
        results = service.tasks().list(tasklist='@default').execute()
        tasks = results.get('items', [])
        return tasks
    except HttpError as err:
        print(f'Error retrieving tasks: {err}')
        return []


def create_todo_list(tasks):
    """Create Markdown todo list from tasks."""
    todo_list = "# Todo List\n\n"
    if not tasks:
        return todo_list + "No tasks found."

    for task in tasks:
        title = task.get('title', 'Untitled Task')
        status = "[x]" if task.get('status', 'needsAction') == 'completed' else "[ ]"
        todo_list += f"{status} {title}\n"

    return todo_list


def save_to_file(content, filename='todo_list.md'):
    """Save content to a file."""
    with open(filename, 'w') as f:
        f.write(content)


def update_google_task(task_id):
    """Update Google task status to completed."""
    creds = authenticate()
    service = build('tasks', 'v1', credentials=creds)
    task = {'status': 'completed'}
    try:
        service.tasks().update(tasklist='@default', task=task_id, body=task).execute()
        print("Google task updated successfully.")
    except HttpError as err:
        print(f'Error updating Google task: {err}')


def main():
    tasks = get_tasks()
    todo_list = create_todo_list(tasks)
    save_to_file(todo_list)
    print("Todo list created and saved as 'todo_list.md'.")

    # Check if task is marked complete in Markdown file and update Google task
    with open('todo_list.md', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("[x]"):
                task_title = line.split("[x]")[1].strip()
                for task in tasks:
                    if task.get('title') == task_title:
                        update_google_task(task['id'])


if __name__ == '__main__':
    main()
