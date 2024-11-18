"""
An human friendlier way to send emails with Python

smtp = SMTP(host='smtp.example.com', port=21, username='myuser', password='suchsecret')
email = Email(sender='harel@harelmalka.com', recipients=['harel@harelmalka.com'],
            subject='Riches to you!', text='You won the Microsoft Lottery!')
email.send(using=smtp)

or

smtp.send(email)

"""

import os
import six
import base64
import uuid
import ssl
import smtplib
import mimetypes
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formatdate, formataddr, make_msgid
from email.encoders import encode_base64
from email.charset import Charset

__author__ = 'Harel Malka'
__version__ = '0.4.1'

# initialise the mimetypes module
mimetypes.init()

try:
    PROTOCOL_TLS = getattr(ssl, os.environ.get('EMAIL_TLS_VERSION', 'PROTOCOL_TLS'))
except AttributeError:
    PROTOCOL_TLS = getattr(ssl, 'PROTOCOL_TLS')


class InvalidConfiguration(Exception):
    pass


class SMTP(object):
    """
    A wrapper around SMTP accounts.
    This object can be used as a stand alone SMTP wrapper which can accept Email objects to be sent
    out through it (the opposite is also valid - en Email object can receive this SMTP object to
    use as a transport).
    However, a better usage pattern is via the `with` keyword:

    with smtp_instance as smtp:
        Email(...).send()

    """
    def __init__(
        self, host, port, username=None, password=None, ssl=False, tls=False,
        timeout=None, debug_level=None, tls_version=None, tls_context_handler=None
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssl = ssl
        self.tls = tls
        self.tls_version = tls_version
        self.tls_context_handler = tls_context_handler
        self.timeout = timeout
        self.debug_level = debug_level
        self.client = None

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _get_client(self):
        """
        Returns the relevant SMTP client (SMTP or SMTP_SSL)
        """
        connection_args = {
            'host': self.host,
            'port': self.port,
        }
        if self.timeout:
            connection_args['timeout'] = self.timeout
        if self.ssl:
            client = smtplib.SMTP_SSL(**connection_args)
        else:
            client = smtplib.SMTP(**connection_args)
        if self.tls:
            if self.tls_version:
                context = ssl.SSLContext(self.tls_version)
                if self.tls_context_handler:
                    self.tls_context_handler(context)
            else:
                context = ssl.create_default_context()
            client.starttls(context=context)
            client.ehlo_or_helo_if_needed()
        if self.debug_level:
            client.set_debuglevel(self.debug_level)
        return client

    def login(self):
        """
        Connect to the server using the login (with credentials) or connect (without).
        If login() fails, attempt to perform a fallback method using base64 encoded password and
        raw SMTP commands
        """
        self.client = self._get_client()
        if self.username and self.password:
            try:
                self.client.login(six.u(self.username), six.u(self.password))
            except (smtplib.SMTPException, smtplib.SMTPAuthenticationError):
                # if login fails, try again using a manual plain login method
                self.client.connect(host=self.host, port=self.port)
                self.client.docmd("AUTH LOGIN", base64.b64encode(six.b(self.username)))
                self.client.docmd(base64.b64encode(six.b(self.password)), six.b(""))
        else:
            self.client.connect()

    def close(self):
        self.client.quit()

    def send(self, email):
        """
        Send an Email
        """
        return self.client.sendmail(email.sender, email.recipients, email.get_payload())


class Email(object):
    """
    A fully composed email message.
    The email can contain plain text and/or html, multiple recipients, cc and bcc.
    Attachments can be added as well as embedded images
    """
    def __init__(self, sender=None, recipients=[], cc=[], bcc=[],
                 subject=None, text=None, html=None, charset=None,
                 attachments=[], embedded=[], headers=[]):
        self.sender = sender
        self.recipients = recipients if type(recipients) in (list, tuple) else [recipients]
        self.cc = cc
        self.bcc = bcc
        self.subject = subject
        self.text = text
        self.html = html
        self.attachments = attachments
        self.embedded = embedded
        self.charset = charset or 'utf-8'
        self.headers = headers
        self.compiled = False

    def compile_message(self):
        """
        Compile this message with all its parts
        :return: the compiled Message object
        """
        message = self.get_root_message()
        if self.attachments:
            # add the attachments as parts of the Multi part message
            for attachment in self.attachments:
                message.attach(self.get_file_attachment(attachment))
        if self.embedded:
            for embedded in self.embedded:
                message.attach(self.get_embedded_image(embedded))
        self.message = message
        self.compiled = True
        return self.message

    def get_payload(self):
        """
        Return the final payload of this email. Its compiled if not previously done so.
        :return: payload as string
        """
        if not self.compiled:
            self.compile_message()
        return self.message.as_string()

    def is_valid_message(self):
        """
        Validate all the required properties of the email are present and raise an
        InvalidConfiguration exception if some are missing.
        :return: True is the message is valid
        """
        if not self.sender:
            raise InvalidConfiguration('Sender is required')
        if not self.recipients and not self.cc and not self.bcc:
            raise InvalidConfiguration('No recipients provided')
        return True

    def get_root_message(self):
        """
        Return the top level Message object which can be a standard Mime message or a
        Multi Part email. All the initial fields are set on the message.
        :return: email.Message object
        """

        if (self.text and self.html) or self.attachments or self.embedded:
            self.message = MIMEMultipart('mixed')
            message_alt = MIMEMultipart('alternative', None)
            message_rel = MIMEMultipart('related')
            if self.text:
                message_alt.attach(self.get_email_part(self.text, 'plain'))
            elif self.html:
                message_alt.attach(self.get_email_part(self.html, 'html'))
            if self.html:
                message_rel.attach(self.get_email_part(self.html, 'html'))
            message_alt.attach(message_rel)
            self.message.attach(message_alt)
        elif self.text or self.html:
            if self.text:
                self.message = MIMEText(self.text.encode(self.charset), 'plain', self.charset)
            else:
                self.message = MIMEText(self.html.encode(self.charset), 'html', self.charset)
        else:
            self.message = MIMEText('', 'plain', 'us-ascii')
        self.message['From'] = self.format_email_address(email_type='from', emails=[self.sender])
        if self.recipients:
            self.message['To'] = self.format_email_address(email_type='to', emails=self.recipients)

        if self.cc:
            self.message['Cc'] = self.format_email_address(email_type='cc', emails=self.cc)
        if self.bcc:
            self.message['Bcc'] = self.format_email_address(email_type='bcc', emails=self.bcc)

        self.message['Subject'] = self.get_header('subject', self.subject)
        self.message['Date'] = formatdate(localtime=True)  # TODO check formatdate
        self.message['Message-ID'] = make_msgid(str(uuid.uuid4()))
        self.message['X-Mailer'] = 'Strudelpy Python Client'
        return self.message

    def get_header(self, name, value=None):
        """
        Return a single email header
        :param name: the header name
        :return: Header instance
        """
        _header = Header(header_name=name, charset=self.charset)
        if value:
            _header.append(value)
        return _header

    def format_email_address(self, email_type, emails=None):
        """
        returns email headers with email information.
        :param email_type: One of: from|to|cc|bcc
        :param emails: A list of email address or list/tuple of (name, email) pairs.
        :return: the email header
        """
        emails = emails or self.recipients or []
        header = self.get_header(email_type)
        for i, address in enumerate(emails):
            if i > 0:  # ensure emails are separated by commas
                header.append(',', 'us-ascii')
            if isinstance(address, six.string_types):
                # address is a string. use as is. Attempt it as ascii first and
                # if fails, send in the default charset
                try:
                    header.append(address, charset='us-ascii')
                except UnicodeError:
                    header.append(address, charset=self.charset)
            elif type(address) in (tuple, list):
                # address is a list or tuple (name, email): format it
                _name, _address = address
                try:
                    _name.encode('us-ascii')
                    formatted_address = formataddr(address)
                    header.append(formatted_address, charset='us-ascii')
                except UnicodeError:  # this is not an ascii name - append it separately
                    header.append(_name)
                    header.append('<{0}>'.format(_address), charset='us-ascii')
        return header

    def get_embedded_image(self, path):
        email_part = self.get_file_mimetype(path)
        encode_base64(email_part)
        path_basename = os.path.basename(path)
        cid_value = path_basename.split('.')[0]
        email_part.add_header('Content-ID', '<{0}>'.format(cid_value))
        email_part.add_header('X-Attachment-Id', '<{0}>'.format(cid_value))
        email_part.add_header('Content-Disposition', 'attachment; filename="%s"' % path_basename)
        return email_part

    def get_file_attachment(self, path):
        """
        Return a MIMEBase email part with the file under path as payload.
        If the file is not textual, it is encoded as base64
        :param path: Absolute path to the file being attached
        :return: MIMEBase object
        """
        # todo test graceful failure of this
        email_part = self.get_file_mimetype(path)
        if not email_part.get_payload():
            with open(path, 'rb') as attached_file:
                email_part.set_payload(attached_file.read())
        # no need to base64 plain text
        if email_part.get_content_maintype() != "text":
            encode_base64(email_part)
        email_part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(path))
        return email_part

    def get_file_mimetype(self, path, fallback=None):
        """
        Try to assert the mime type of this file.
        If the mime type cannot be guessed, the fallback is used (default to text/plain)
        :param path: The absolute path to the file
        :param fallback: Fallback mime type as a 2 item array, e.g. ["application", "octet-stream"]
        :return: MIMEBase object with the mime type
        """
        # todo look into guess_type
        fallback = fallback or ['text', 'plain']
        asserted_mimetype = mimetypes.guess_type(path, False)[0]
        if asserted_mimetype is None:
            mimetype = MIMEBase(*fallback)
        elif asserted_mimetype.startswith('image'):
            with open(path, 'rb') as embedded_file:
                mimetype = MIMEImage(embedded_file.read(), _subtype=asserted_mimetype.split('/')[1])
        else:
            mimetype = MIMEBase(*asserted_mimetype.split('/'))
        return mimetype

    def get_email_part(self, body, format='html'):
        """
        Return a single MIMEText email part to be used in multipart messages containing both
        plain text and html bodies.
        :param body: the body text
        :param format: html or plain
        :return:MIMEText instance
        """
        charset = Charset(self.charset)
        email_part = MIMEText(body, format, self.charset)
        email_part.set_charset(charset)
        return email_part

    def add_header(self, header):
        """
        Add a custom header to this email
        :param header: header text of Header instance
        """
        if isinstance(header, six.string_types):
            header = Header(header)
        self.headers.append(header)

    def add_recipient(self, recipient):
        """
        Add an additional recipient to this email
        :param recipient: An email address or a name/email tuple
        """
        self.recipients.append(recipient)

    def add_attachment(self, file):
        """
        Add an attachment to this email
        :param file: absolute path to file
        """
        self.attachments.append(file)

    def add_embedded_image(self, image):
        """
        Adds an embedded image path to the embedded list
        :param image: string path to the image
        """
        self.embedded.append(image)
