"""
logic for email stuff
"""
from pyramid.renderers import render
from html2text import html2text


def send_email(mailer, to, from_, subject, template, **data):
    m = mailer.new(to=to, subject=subject, author=from_, sender=from_)
    m.rich = render("mailers/%s" % template, data)
    m.plain = html2text(m.rich)
    m.send()
