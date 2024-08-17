"""
    inyoka_theme_ubuntuusers.tasks
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Module that implements ubuntuusers-wiki related tasks that must be executed
    by Inyoka's distributed queue implementation.

    :copyright: (c) 2024 by the Inyoka Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from os.path import dirname

from celery import shared_task
from celery.schedules import crontab
from inyoka.celery_app import app
from inyoka.portal.user import User
from inyoka.portal.utils import get_ubuntu_versions
from inyoka.wiki.models import Page
from jinja2 import Environment, FileSystemLoader


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Execute on the first of April and October
    sender.add_periodic_task(
        10.0,  # crontab(day_of_month="1", month_of_year="4,10"),
        generate_downloads_page,
    )


@shared_task
def generate_downloads_page():
    """
    Generate the downloads page for an upcoming
    Ubuntu version from a template.
    """
    env = Environment(
        loader=FileSystemLoader(f"{dirname(__file__)}/jinja2/wiki")
    )
    downloads_template = env.get_template("downloads.inyoka.jinja")

    # TODO: Populate variables via db query?
    downloads_page = downloads_template.render(
        ubuntu_version="24.04",
        codename="Noble Numbat",
        version_type="Long Term Support",
        eol_date="April 2029",
        eol_date_derivatives="April 2027"
    )

    Page.objects.create(
        name="Baustelle/Noble_Numbat",
        text=downloads_page,
        user=User.objects.get_system_user(),
        note='Seite eingerichtet'
    )
