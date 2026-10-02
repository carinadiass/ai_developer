# Household Chores Manager

A web app that helps roommates share household chores fairly. It tracks who does what and when.

> Status: early setup. The Django project is scaffolded.

## Goals

- Show everyone in the household the same chore list
- Make it clear whose turn it is
- Track which chores are done and which are overdue

## Documentation

- [Project plan and scope](_docs/plan.md)

## Getting Started

Built with Django 5.2 (Python 3.10+).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

## Project Structure

- `config/`: Django project settings and root URLs
- `chores/`: the app that holds chore models, views and templates

## Author

Carina Sucupira
