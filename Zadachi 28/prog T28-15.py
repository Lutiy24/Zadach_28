from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
import json

airports = {
    "KBP": {"name": "Бориспіль", "city": "Київ"},
    "IEV": {"name": "Київ", "city": "Київ"},
    "CDG": {"name": "Шарль-де-Голль", "city": "Париж"}
}

flights = [
    {"from": "KBP", "to": "CDG", "flight": "AF2268", "days": "1030060", "depart": "10:35", "arrive": "13:50", "class": "E", "cost": 8350},
    {"from": "IEV", "to": "CDG", "flight": "PS765", "days": "0204060", "depart": "10:35", "arrive": "13:50", "class": "E", "cost": 7500}
]

def application(environ, start_response):
    params = parse_qs(environ['QUERY_STRING'])
    from_id = params.get('from', [''])[0]
    to_id = params.get('to', [''])[0]
    day = params.get('day', [''])[0]
    
    if from_id and to_id and day:
        available_flights = [
            flight for flight in flights
            if flight["from"] == from_id and flight["to"] == to_id and day in flight["days"]
        ]
        response_body = json.dumps(available_flights, ensure_ascii=False)
    else:
        response_body = "Please provide 'from', 'to', and 'day' parameters."
    
    start_response('200 OK', [('Content-Type', 'application/json; charset=utf-8')])
    return [response_body.encode('utf-8')]

if __name__ == "__main__":
    with make_server('', 8000, application) as httpd:
        print("Serving on port 8000...")
        httpd.serve_forever()
