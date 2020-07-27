import json, os, urllib
from uuid import uuid4
from urllib import request, parse

CLIENT_ID = "b8e35e5145051c62b925"
CLIENT_SECRET = "544c56c197a830815410014816d38471e68922aa"
REDIRECT_URI = 'https://healthjoy.lucis.works/auth'
AUTHORIZE_URI = 'https://github.com/login/oauth/authorize?%s'
TOKEN_URI = 'https://github.com/login/oauth/access_token'

def lambda_handler(event, context):
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps(event),
    #     'headers': {
    #         'content-type': 'application/json'
    #     }
    # }
    if event['queryStringParameters'] is not None:
        qsp = event['queryStringParameters']
        if 'code' in qsp:
            return get_token(qsp['code'], qsp['state'])
        # elif 'access_token' in qsp:
        #     get_forked(qsp['access_token'])
        if 'action' in qsp:
            action = qsp['action']
            if action == 'logout':
                return auth_html('logout')
        if 'error' in qsp:
            return auth_html(None)
        else:
            return bad_response('Invalid parameter.')
    else:
        return auth_html(None)

def bad_response(msg):
    return {
        'statusCode': 400,
        'body': msg,
        'headers': {
            'content-type': 'text/plain'
        }
    }
    
def auth_html(action):
    # state is used for security purposes, but for the sake of this exercise it just a placeholder
    params = {
        'client_id': CLIENT_ID,
        'state': str(uuid4()),
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'duration': 'temporary',
        'scope': 'repo'
    }
    encoded_params = parse.urlencode(params)
    url = '<a class="get_started" href="' + AUTHORIZE_URI % encoded_params + '">Get Started</a>'
    html = """
    <html>
    <head>
    <style type="text/css">
    .description {
        text-align: center;
        margin-top: 5%%;
    }
    .get_started {
        background-color: #682db3;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        border-radius: 20px;
        cursor: pointer;
    }
    </style>
    </head>
    <body>
    <div class="description">
    <p>This service lets you fork GitHub repositories via their API. By default the one hosting this code, or by providing a valid GitHub url you can fork
    just about any other repo you have access to.</p>
    %s
    </div>
    </body>
    </html>
    """ % url
    headers = {
        'content-type': 'text/html'
    }
    if (action == 'logout'):
        headers['Set-Cookie'] = 'access_token=deleted; Domain=.healthjoy.lucis.works; expires=Thu, 01 Jan 1970 00:00:00 GMT'
    return {
        'statusCode': 200,
        'body': html,
        'headers': headers
    }
    
def get_token(code, state):
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'state': state
    }
    encoded_data = parse.urlencode(data).encode('utf-8')
    req = request.Request(TOKEN_URI, encoded_data, {'Accept': 'application/json'})
    response = request.urlopen(req)
    # token = response.read().decode()
    token = json.loads(response.read().decode())['access_token']
    return get_forked(token)
    # return {
    #     'statusCode': 200,
    #     'body': token,
    #     'headers': {
    #         'content-type': 'text/plain'
    #     }     
    # }
    
def get_forked(access_token):
    # return {
    #     'statusCode': 200,
    #     'body': access_token,
    #     'headers': {
    #         'content-type': 'text/plain'
    #     }
    # }
    return {
        'statusCode': 302,
        'body': 'Redirecting...',
        'headers': {
            'content-type': 'text/plain',
            'Location': 'https://healthjoy.lucis.works/fork',
            'Set-Cookie': 'access_token=%s;Domain=.healthjoy.lucis.works' % access_token
        }     
    }
    # return {
    #     'statusCode': 200,
    #     'body': 'Redirecting...',
    #     'headers': {
    #         'content-type': 'text/html',
    #         'Location': 'https://healthjoy.lucis.works/fork',
    #         'Set-Cookie': ['access_token=%s' % access_token]
    #     }
    # }