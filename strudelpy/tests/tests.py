#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This test suite relies on the existence of a SMTP server, real or fake to connect to.
By default it will attempt to connect to a 'fake' one that can be run using:

`sudo python -m smtpd -n -c DebuggingServer localhost:25`

Set TEST_CONFIG_NAME to one of the keys in TEST_CONFIGURATIONS to test a specific configuration
"""
import os
import smtplib
import socket
import unittest
from strudelpy import Email, SMTP
from strudelpy import InvalidConfiguration

TEST_CONFIG_NAME = 'fake'

TEST_CONFIGURATIONS = {
    'gmail': {
        'SMTP_HOST': 'smtp.gmail.com',
        'SMTP_PORT': 465,
        'SSL': True,
        'TLS': False,
        'SMTP_USER': 'mygmail@gmail.com',
        'SMTP_PASS': 'gmailpass',
        'FROM': 'mygmail@gmail.com',
        'RECIPIENTS': ['someone@example.com', 'anotherone@example.com'],
        'RECIPIENT_PAIRS': (('Harel Malka', 'someone@example.com'), ('Donkey Kong', 'donkey@example.com'))
    },
    'mailtrap': {
        'SMTP_HOST': 'mailtrap.io',
        'SMTP_PORT': 465,
        'SSL': False,
        'TLS': True,
        'SMTP_USER': '123455',
        'SMTP_PASS': '432123',
        'FROM': 'harel@example.com',
        'RECIPIENTS': ['someone@example.com', 'anotherone@example.com'],
        'RECIPIENT_PAIRS': (('Harel Malka', 'someone@example.com'), ('Donkey Kong', 'donkey@example.com'))
    },
    'fake': {
        'SMTP_HOST': 'localhost',
        'SMTP_PORT': 25,
        'SSL': False,
        'TLS': False,
        'SMTP_USER': 'user',
        'SMTP_PASS': 'pass',
        'FROM': 'harel@harelmalka.com',
        'RECIPIENTS': ['harel@harelmalka.com'],
        'RECIPIENT_PAIRS': (('Harel Malka', 'someone@example.com'), ('Mario Plumber', 'mario@example.com'))
    }
}


TEST_CONFIG = TEST_CONFIGURATIONS[TEST_CONFIG_NAME]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class TestEmailSend(unittest.TestCase):
    def setUp(self):
        self.smtp = SMTP(host=TEST_CONFIG['SMTP_HOST'], port=TEST_CONFIG['SMTP_PORT'],
                         username=TEST_CONFIG['SMTP_USER'], password=TEST_CONFIG['SMTP_PASS'],
                         ssl=TEST_CONFIG['SSL'], tls=TEST_CONFIG['TLS'])

    def test_is_valid_message_no_recipient(self):
        """
        Test email validation fails when no recipient is provided
        """
        email = Email(sender=TEST_CONFIG['FROM'],
                      subject='Test: test_is_valid_message_no_recipient',
                      text='Simple text only body')
        no_recipient = False
        try:
            email.is_valid_message()
        except InvalidConfiguration:
            no_recipient = True
        self.assertEqual(no_recipient, True)

    def test_is_valid_message_no_sender(self):
        """
        Test email validation fails when no sender is provided
        """
        email = Email(recipients=TEST_CONFIG['RECIPIENTS'],
                      subject='Test: test_is_valid_message_no_sender',
                      text='Simple text only body')
        no_sender = False
        try:
            email.is_valid_message()
        except InvalidConfiguration:
            no_sender = True
        self.assertEqual(no_sender, True)

    def test_format_email_address(self):
        email = Email(sender=TEST_CONFIG['FROM'], recipients=TEST_CONFIG['RECIPIENTS'], subject="Subject")
        header = email.format_email_address('from', TEST_CONFIG['RECIPIENTS'])
        self.assertEqual(str(header), "harel@harelmalka.com")


    def test_simple_text_only_single_recipient(self):
        with self.smtp as smtp:
            response = smtp.send(Email(sender=TEST_CONFIG['FROM'],
                            recipients=TEST_CONFIG['RECIPIENTS'][0],
                            subject='Test: test_simple_text_only_single_recipient',
                            text='Simple text only body'))
        self.assertEqual(response, {})

    def test_simple_text_only_multiple_recipient(self):
        with self.smtp as smtp:
            response = smtp.send(Email(sender=TEST_CONFIG['FROM'],
                            recipients=TEST_CONFIG['RECIPIENTS'],
                            subject='Test: test_simple_text_only_multiple_recipient',
                            text='Simple text only body'))
        self.assertEqual(response, {})

    def test_simple_text_only_multiple_recipient_pairs(self):
        with self.smtp as smtp:
            response = smtp.send(Email(sender=TEST_CONFIG['FROM'],
                            recipients=TEST_CONFIG['RECIPIENT_PAIRS'],
                            subject='Test: test_simple_text_only_multiple_recipient_pairs',
                            text='Simple text only body'))
        self.assertEqual(response, {})

    def test_text_html_multiple_recipient(self):
        with self.smtp as smtp:
            response = smtp.send(Email(sender=TEST_CONFIG['FROM'],
                             recipients=TEST_CONFIG['RECIPIENTS'],
                             subject='Test: test_text_html_multiple_recipient',
                             text='Simple text only body',
                             html='<strong>Complicated</strong><BR><BIG>HTML</BIG>'))
        self.assertEqual(response, {})

    def test_unicode_data(self):
        with self.smtp as smtp:
            response = smtp.send(Email(sender="הראל מלכה <harel@harelmalka.com>",
                             recipients=TEST_CONFIG['RECIPIENTS'],
                             subject='Test: עברית test_unicode_data',
                             text='Simple text only body בעברית',
                             html='<strong>Complicated עברית</strong><BR><BIG>HTML</BIG>'))
        self.assertEqual(response, {})

    def test_single_file_attachment(self):
        with self.smtp as smtp:
            response = smtp.send(Email(sender=TEST_CONFIG['FROM'],
                             recipients=TEST_CONFIG['RECIPIENTS'],
                             subject='Test: test_single_file_attachment',
                             text='Simple text only body',
                             attachments=[os.path.join(BASE_DIR, 'tests', 'doctest.doc')]))
        self.assertEqual(response, {})

    def test_multiple_file_attachment(self):
        with self.smtp as smtp:
            response = smtp.send(Email(sender=TEST_CONFIG['FROM'],
                             recipients=TEST_CONFIG['RECIPIENTS'],
                             subject='Test: test_single_file_attachment',
                             text='Simple text only body',
                             attachments=[os.path.join(BASE_DIR, 'tests', 'doctest.doc'),
                                          os.path.join(BASE_DIR, 'tests', 'cat.jpg')]))

    def test_embedded_image(self):
        with self.smtp as smtp:
            response = smtp.send(Email(sender=TEST_CONFIG['FROM'],
                             recipients=TEST_CONFIG['RECIPIENTS'],
                             subject='Test: test_embedded_image',
                             html='<strong>Here is a cat</strong><P><img src="cid:cat.jpg"></P>',
                             embedded=[os.path.join(BASE_DIR, 'tests', 'cat.jpg')]))
        self.assertEqual(response, {})

    def test_multiple_embedded_images(self):
        with self.smtp as smtp:
            response = smtp.send(Email(sender=TEST_CONFIG['FROM'],
                             recipients=TEST_CONFIG['RECIPIENTS'],
                             subject='Test: test_multiple_embedded_images',
                             html='''<strong>Here is a cat</strong><P>
                                    <img src="cid:cat.jpg"></P>
                                    <BR>And another:
                                    <img src="cid:grumpy-cat.gif">
                                    ''',
                             embedded=[os.path.join(BASE_DIR, 'tests', 'cat.jpg'),
                                       os.path.join(BASE_DIR, 'tests', 'grumpy-cat.gif')]))
        self.assertEqual(response, {})

    def test_simple_text_only_single_recipient_debug_level(self):
        smtp = SMTP(host=TEST_CONFIG['SMTP_HOST'], port=TEST_CONFIG['SMTP_PORT'],
                         username=TEST_CONFIG['SMTP_USER'], password=TEST_CONFIG['SMTP_PASS'],
                         ssl=TEST_CONFIG['SSL'], tls=TEST_CONFIG['TLS'], debug_level=5)
        smtp.login()
        response = smtp.send(Email(sender=TEST_CONFIG['FROM'],
                        recipients=TEST_CONFIG['RECIPIENTS'][0],
                        subject='Test: test_simple_text_only_single_recipient_debug_level',
                        text='Simple text only body'))
        smtp.close()
        self.assertEqual(response, {})

    def test_simple_text_only_single_recipient_short_timeout(self):
        timedout = False
        message = ''
        smtp = None
        try:
            # trying some unroutable ip to trigger timeout
            smtp = SMTP(host="10.255.255.1", port=TEST_CONFIG['SMTP_PORT'],
                        username=TEST_CONFIG['SMTP_USER'], password=TEST_CONFIG['SMTP_PASS'],
                        ssl=TEST_CONFIG['SSL'], tls=TEST_CONFIG['TLS'], timeout=1)
            smtp.login()
        except (socket.timeout, smtplib.SMTPServerDisconnected) as e:
            timedout = True
            message = str(e)
        finally:
            if smtp and smtp.client:
                smtp.close()
        self.assertTrue(timedout)
        self.assertTrue('timed out' in message)



if __name__ == '__main__':
    print("Strudel Py Test Suite")
    print("="*80)
    unittest.main()
