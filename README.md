## StrudelPy v0.1
### A tastier way to send emails with Python

### Features
* Attachments, multiple recipients, cc, bcc - the standard stuff
* Embedded Images
* Plays well with Unicode
* Easy OOP approach


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

Unless using SMTP objects with `with`, you'll need to `login()` and `close()` the connection.


#### Email

You can then send emails using the `Email` object:
```
    email = Email(sender='me@example.com,
              recipients=['him@example.com', 'her@example.com'],
              subject='The Subject Matters',
              text='Plain text body',
              html='HTML body',
              attachments=['absolute/path/to/file'],
              embedded=['absolute/path/to/image/'])
    smtp.send(email)
```

Emails can use embedded images by including tags like this in the html content:

```
<img src="cid:filename.jpg">
```

Look at the tests/tests.py file for examples.


#### Tests

This test suite relies on the existence of a SMTP server, real or fake to connect to.  
By default it will attempt to connect to a 'fake' one that can be run using:

`sudo python -m smtpd -n -c DebuggingServer localhost:25`

Set TEST_CONFIG_NAME to one of the keys in TEST_CONFIGURATIONS to test a specific configuration


#### Still to do

* Fix tests to use a fake smtp server by default
* Your issues???