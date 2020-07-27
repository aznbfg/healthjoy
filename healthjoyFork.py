import json
from urllib import request, parse


def lambda_handler(event, context):
    access_token = None
    if event['httpMethod'] == 'POST':
        try:
            data = parse.parse_qs(event['body'])
            owner = 'pjfontillas'
            repo = 'healthjoy'
            if 'owner' in data and 'repo' in data:
                owner = data['owner'][0]
                repo = data['repo'][0]
        except Exception as e:
            return bad_response('Invalid post data.')

        if 'cookie' in event['headers']:
            cookies = event['headers']['cookie']
            access_token = get_access_token(cookies)
        
        if access_token is None:
            return bad_response('Unauthorized.', 403)

        return fork_repo(access_token, owner, repo)
    else:
        if 'cookie' in event['headers']:
            cookies = event['headers']['cookie']
            access_token = get_access_token(cookies)
        
        if access_token is None:
            return {
                'statusCode': 302,
                'body': 'Redirecting...',
                'headers': {
                    'Location': 'https://healthjoy.lucis.works/auth'
                }
            }

        if event['queryStringParameters'] is not None:
            qsp = event['queryStringParameters']
            if 'debug' in qsp:
                return {
                    'statusCode': 200,
                    'body': json.dumps(event)
                }
            return bad_response("Unsupported parameter.", 400)
        return form_html('')

def bad_response(msg, code):
    return {
        'statusCode': code,
        'body': msg,
        'headers': {
            'content-type': 'text/plain'
        }
    }
    
def get_access_token(cookies):
    split_cookies = cookies.split(';')
    for cookie in split_cookies:
        split_cookie = cookie.split('=')
        name = split_cookie[0]
        value = split_cookie[1]
        if "access_token" in name:
            return value
    return None
            
def fork_repo(access_token, owner, repo):
    fork_uri = F'https://api.github.com/repos/{owner}/{repo}/forks'
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': F" token {access_token}"
    }
    # return json.dumps(headers)
    req = request.Request(fork_uri, data={}, headers=headers)
    try:
        response = request.urlopen(req)
        return form_html(F'<p>Successfully forked repo: <a href="{repo}">{repo}</a></p>')
    except Exception as e:
        return form_html('Bad fork request.')
    # return {
    #     'statusCode': 202,
    #     'body': response.read().decode('utf-8')
    # }
    
def form_html(msg):
    html = """<html>
    <head>
    <style type="text/css">
    div {
        text-align: center;
    }
    .logout {
        text-align: right;
    }
    .message {
        margin-top: 5%%;
    }
    .hidden {
        display: none;
    }
    button, .logout a {
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
    .logout a {
        background-color: #3d70f4;
    }
    label {
        margin-right: 10px;
    }
    .or {
        margin: 10px 0;
    }
    </style>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script>
    let timer, delay = 500;
    $(function() {
        $('form[name=fork_repo]').on('submit', function (e, bypass) {
            if (!bypass) {
                e.preventDefault();
                _this = $(this);
                let owner = '', repo = '';
                let input = $('input[name=repo_url]');
                let repo_url = input.val();
                console.log(repo_url);
                split_url = repo_url.split('/');
                console.log(split_url);
                if (split_url[0] == 'https:' && (split_url[2] == 'github.com' || split_url[2] == 'www.github.com')) {
                    try {
                        owner = split_url[3];
                        repo = split_url[4];
                    } catch (e) {
                        alert('Invalid owner or repo path!');
                    }
                    console.log('owner:', owner);
                    console.log('repo:', repo);
                    if (owner.length == 0 || repo.length == 0) {
                        input.focus();
                        alert('Not a valid repo.');
                    } else {
                        $('input[name=owner]').val(owner);
                        $('input[name=repo]').val(repo);
                        _this.trigger('submit', [true]);
                    }
                } else {
                    alert('Bad GitHub URL!');
                }
            }
        });
    });
    </script>
    </head>
    <body>
    <div class="logout"><a href="/auth?action=logout">Logout</a></div>
    <div class="message"><p>%s</p></div>
    <div class="option">
        <form name="fork_default" method="post">
            <button type="submit">Fork this repo</button>
        </form>
    </div>
    <div class="or">- OR -</div>
    <div class="option">
        <form name="fork_repo" method="post">
        <label>Fork another repo</label><input name="repo_url" placeholder="https://github.com/owner/repo" />
        <input class="hidden" name="owner" value="pjfontillas" />
        <input class="hidden" name="repo" value="healthjoy" />
        <button type="submit">Get Forkin\'</button>
        </form>
    </div>
    </body>
    </html>
    """ % msg
    return {
        'statusCode': 200,
        'body': html,
        'headers': {
            'content-type': 'text/html'
        }
    }