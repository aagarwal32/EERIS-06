# EERIS-06

1. Always work in a **virtual env** and never push that virtual env folder to this repo!
2. Always run **pip install -r requirements.txt** once you **git pull** and activated your virtual env.
3. If you installed any new packages, always run **pip freeze > requirements.txt** before pushing repo.
4. After making any DB or Model changes, always run **python manage.py makemigrations** and **python manage.py migrate**.
5. If you added any dummy data for testing, run **python manage.py dumpdata --output=data.json --indent 2** before pushing repo.
   - Others can load that dummy data into their local sqlite by running **python manage.py loaddata data.json**.

## User Testing Accounts Created

### Regular Employee Accounts
1. TestUser@gmail.com, Test12345*

### Supervisor Accounts
1. Group06@gmail.com, 42c43d496715369f6ba1