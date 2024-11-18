from setuptools import setup

setup(
    name='strudelpy',
    version='0.4.1',
    description='Easy as Pie Emails in Python',
    long_description='StrudelPy is an easy to use library to manage sending emails in a OO way.'
                     'The library is comprised of a SMTP object to manage connections to SMTP'
                     'servers and an Email object to handle the messages themselves.'
                     'Supports Python 2 and 3.',
    author='Harel Malka',
    author_email='harel@harelmalka.com',
    url='https://github.com/harel/strudelpy',
    download_url='https://github.com/harel/strudelpy/archive/0.3.tar.gz',
    keywords=['email', 'smtp'],  # arbitrary keywords
    install_requires=['six'],
    license='MIT',
    packages=['strudelpy', 'strudelpy.tests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Email',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ]
)