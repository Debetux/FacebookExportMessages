## How to install this :

```
virtualenv-3.4 -p /usr/local/bin/python3.4 develop
source develop/bin/activate
pip install -r requirements.txt
cp settings.sample.py settings.py
vim settings.py # Replace your tokens
```

Now, to launch this app :

```
python run.py
```

BIM BIM BAM BAM.
Don't forget to create a Facebook Application and to replace your tokens in settings.py (see settings.sample.py).

## Prod, with gunicorn and nginx

nginx.conf

```
server {

        listen   80; ## listen for ipv4

        keepalive_timeout 3600;

        location / {
                proxy_pass http://127.0.0.1:5151;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_connect_timeout 3600s;
                proxy_read_timeout 3600s;
        }
}
```

```
gunicorn -w 4 -b 127.0.0.1:5151 run:app --keep-alive 3600 --timeout=3600
```
