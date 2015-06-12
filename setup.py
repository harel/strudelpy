from distutils.core import setup
setup(
    name = 'strudelpy',
    version = '0.2',
    description = 'Easy as Pie Emails in Python',
    long_description='StrudelPy is an easy to use library to manage sending emails in a OO way.'
                     'The library is comprised of a SMTP object to manage connections to SMTP'
                     'servers and an Email object to handle the messages themselves.',
    author = 'Harel Malka',
    author_email = 'harel@harelmalka.com',
    url = 'https://github.com/harel/strudelpy',
    download_url = 'https://github.com/harel/strudelpy/archive/0.2.tar.gz',
    keywords = ['email', 'smtp'], # arbitrary keywords
    license='MIT',
    packages=['strudelpy', 'strudelpy.tests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Email',
        'Programming Language :: Python :: 2.7',
    ]
)