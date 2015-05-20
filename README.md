## StrudelPy
### A tastier way to send emails with Python

### Setup

```
pip install strudelpy
```

### TL;DR

```
from strudelpy import SMTP, Email

smtpclient = SMTP('smtp.example.com', 456, 'myuser', 'muchsecret', ssl=True)
with smtpclient as smtp:
    smtp.send(Email(sender='me@example.com,
                     recipients=['him@example.com', 'her@example.com'],
                     subject='The Subject Matters',
                     text='Plain text body',
                     html='HTML body'))
```

### The 'Can Read' Version

Strudelpy consists mainly of two objects: `SMTP` to manage connections to SMTP
servers, and Email to encapsulate an email message.


#### SMTP

```
SMTP(host='some.host.com',
     port=465,
     username='username',
     password='password',
     ssl=True,
     tls=False,
     timeout=None,
     debug_level=None
)
```