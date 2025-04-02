import json
import xml.etree.ElementTree as ET
from wsgiref.simple_server import make_server

# Завантажуємо дані про іграшки з файлу
def load_toys():
    try:
        with open('toys.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Збереження іграшок у файл
def save_toys(toys):
    with open('toys.json', 'w', encoding='utf-8') as f:
        json.dump(toys, f, ensure_ascii=False, indent=4)

# Фільтрація іграшок за віком та ціною
def filter_toys(toys, age=None, max_price=None):
    if age is None and max_price is None:
        return toys  # Якщо немає фільтрів – повертаємо всі іграшки
    filtered_toys = [
        toy for toy in toys
        if (age is None or toy["min_age"] <= age <= toy["max_age"]) and
           (max_price is None or toy["price"] <= max_price)
    ]
    return filtered_toys

# Конвертуємо список іграшок у JSON
def toys_to_json(toys):
    return json.dumps(toys, ensure_ascii=False, indent=4)

# Конвертуємо список іграшок у XML
def toys_to_xml(toys):
    root = ET.Element("toys")
    for toy in toys:
        toy_element = ET.SubElement(root, "toy")
        ET.SubElement(toy_element, "name").text = toy["name"]
        ET.SubElement(toy_element, "price").text = str(toy["price"])
        ET.SubElement(toy_element, "min_age").text = str(toy["min_age"])
        ET.SubElement(toy_element, "max_age").text = str(toy["max_age"])
    return ET.tostring(root, encoding='utf-8', method='xml').decode()

# Основна функція обробки HTTP-запитів
def application(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    method = environ['REQUEST_METHOD']
    toys = load_toys()

    if path.startswith('toys'):
        params = environ.get('QUERY_STRING', '')
        param_dict = dict(p.split('=') for p in params.split('&') if '=' in p)

        # Отримання параметрів фільтрації
        age = int(param_dict['age']) if 'age' in param_dict else None
        max_price = int(param_dict['max_price']) if 'max_price' in param_dict else None

        # Фільтрація або повернення всіх іграшок
        filtered_toys = filter_toys(toys, age, max_price)

        if path == 'toys/json':
            response_body = toys_to_json(filtered_toys)
            content_type = 'application/json'
        elif path == 'toys/xml':
            response_body = toys_to_xml(filtered_toys)
            content_type = 'application/xml'
        else:
            response_body = "404 Not Found"
            content_type = 'text/plain'

    elif path == 'add' and method == 'POST':
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            post_data = environ['wsgi.input'].read(content_length)
            new_toy = json.loads(post_data)
            toys.append(new_toy)
            save_toys(toys)
            response_body = json.dumps({"message": "Іграшку додано успішно!"}, ensure_ascii=False)
            content_type = 'application/json'
        except Exception as e:
            response_body = json.dumps({"message": "Помилка при додаванні іграшки", "error": str(e)}, ensure_ascii=False)
            content_type = 'application/json'

    else:
        response_body = "404 Not Found"
        content_type = 'text/plain'

    start_response('200 OK', [('Content-Type', content_type)])
    return [response_body.encode('utf-8')]

# Запуск WSGI-сервера
if __name__ == '__main__':
    httpd = make_server('127.0.0.1', 8000, application)
    print("Сервер WSGI запущено на порту 8000...")
    httpd.serve_forever()
