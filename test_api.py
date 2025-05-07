from requests import get, post, delete

# получение списков
print(get('http://localhost:8080/api/v2/users').json())
print(get('http://localhost:8080/api/v2/tasks').json())
print(get('http://localhost:8080/api/v2/projects').json())

# получение определенных пользователей, задач, проектов (id не существует)
print(get('http://localhost:8080/api/v2/users/1').json())
print(get('http://localhost:8080/api/v2/tasks/1').json())
print(get('http://localhost:8080/api/v2/projects/1').json())

# создание пользователей, задач, проектов (некорректные запросы)
print(post('http://localhost:8080/api/v2/users', json={'name': 'Мда...'}).json())
print(post('http://localhost:8080/api/v2/tasks', json={'name': 'Мда...'}).json())
print(post('http://localhost:8080/api/v2/projects', json={'name': 'Мда...'}).json())

# создание пользователей, задач, проектов (корректный запрос)
print(post('http://localhost:8080/api/v2/users', json={'name': 'Мда...',
                                                       'surname': 'Мдаааааааааа...',
                                                       'email': 's_p@sciencce.org'}).json())
print(post('http://localhost:8080/api/v2/projects', json={'name': 'Мда...',
                                                          'description': 'Мдаааааааааа...',
                                                          'founder': 1,
                                                          'participants': '',
                                                          'is_finished': 1}).json())
print(post('http://localhost:8080/api/v2/tasks', json={'name': 'Мда...',
                                                       'description': 'Мдаааааааааа...',
                                                       'founder': 1,
                                                       'project': 1,
                                                       'category': 3,
                                                       'deadline_date': '2025-05-07',
                                                       'deadline_time': '23:23:00.00000',
                                                       'replay_every_day': 1,
                                                       'replay_every_week': 0,
                                                       'finish_date': None}).json())

# получение списков
print(get('http://localhost:8080/api/v2/users').json())
print(get('http://localhost:8080/api/v2/tasks').json())
print(get('http://localhost:8080/api/v2/projects').json())

# удаление несуществующих пользователей, проектов, задач
print(delete('http://localhost:8080/api/v2/users/123').json())
print(delete('http://localhost:8080/api/v2/tasks/123').json())
print(delete('http://localhost:8080/api/v2/projects/123').json())

# удаление существующих пользователей, проектов, задач
print(delete('http://localhost:8080/api/v2/users/1').json())
print(delete('http://localhost:8080/api/v2/tasks/1').json())
print(delete('http://localhost:8080/api/v2/projects/1').json())

# получение списков
print(get('http://localhost:8080/api/v2/users').json())
print(get('http://localhost:8080/api/v2/tasks').json())
print(get('http://localhost:8080/api/v2/projects').json())