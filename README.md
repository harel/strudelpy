## StrudelPy v0.4.1
### A tastier way to send emails with Python

### Features
* Attachments, multiple recipients, cc, bcc - the standard stuff
* Embedded Images
* Plays well with Unicode
* Easy OOP approach
* Supports Python 2 and 3 (with six)


### Setup

```
pip install strudelpy
```

### TL;DR

```
from strudelpy import SMTP, Email

smtpclient = SMTP('smtp.example.com', 456, 'myuser', 'muchsecret', ssl=True)
with smtpclient as smtp:
    smtp.send(
        Email(
            sender='me@example.com,
            recipients=['him@example.com', 'her@example.com'],
            subject='The Subject Matters',
            text='Plain text body',
            html='HTML body'
        )
    )
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
              cc=['cc@me.com'],
              bcc=['shh@dontell.com'],
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


#### Email & Gmail etc.

The Email class can be used to construct emails to be delivered via the Gmail (or other)
api:

```
email = Email(
    sender="me@example.com",
    recipients=['them@example.com'],
    subject='The Subject Matters',
    html='Dear so and so',  
    attachments=["/path/to/file.png"]
)
_message = {'raw': base64.urlsafe_b64encode(
    bytes(email.get_payload(), 'utf-8')
).decode('utf-8')}
client = get_gmail_client_thingy()
client.users().messages().send(userId='me', body=_message).execute()
```


#### TLS
(v0.3.8): It's possible to pass a specific TLS version (ssl.PROTOCOL_TLS*) to the SMTP 
init, as well as function to work on the context if required (like setting min/max TLS versions, cert location etc.). By default the default context is generated. 

`tls_version`: e.g. ssl.PROTOCOL_TLSv1_2
`tls_context_handler`: Any function that receives SSLContext instance as first argument. 

#### Tests

This test suite relies on the existence of a SMTP server, real or fake to connect to.
By default it will attempt to connect to a 'fake' one that can be run using:

`sudo python -m smtpd -n -c DebuggingServer localhost:25`

Set TEST_CONFIG_NAME to one of the keys in TEST_CONFIGURATIONS to test a specific configuration


#### Still to do

* Fix tests to use a fake smtp server by default
* Your issues???

##### Motivation and Similar Projects
StrudelPy was created because I needed just that kind of functionality, in that exact way. I had an itch and my searches for a scratcher did not produce anything suitable. I took some inspiration from an older similar project of mine from way back in 2007, and [Pyzmail](http://www.magiksys.net/pyzmail/) which was nice but not as simple as I'd like to have had it. However after releasing I've found out about  [mailthon](https://github.com/eugene-eeo/mailthon) which shares the same motives and motivation behind StrudelPy. I might have not done this had I known about Mialthon.

And by the way, StrudelPy is named after the `at` sign: @, which in Israel is called "The Strudel"...
