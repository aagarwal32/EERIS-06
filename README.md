# EERIS Development Startup Guide

1. Run **pip install -r requirements.txt** once you **git pull** and activated your virtual env.
2. For any new packages installed, always run **pip freeze > requirements.txt** before pushing repo.
3. After making any database changes, always run **python manage.py makemigrations** and **python manage.py migrate**.
4. If you added any dummy data for testing, run **python manage.py dumpdata --output=data.json --indent 2** before pushing repo.
   - Others can load that dummy data into their local sqlite by running **python manage.py loaddata data.json**.

#### Update on current code

1. Supervisor will not be allowed to delete other employee submission. 
2. An employee/supervisor is only allowed to delete his/her own submissions.
3. Supervisor can edit any employee's unapproved submissions and an employee can only edit his/her own unapproved submisssions. 

# Media
Login Page             |  Registration
:-------------------------:|:-------------------------:
![eeris-login](https://github.com/user-attachments/assets/0fc16799-4dc0-4efd-8332-aee6e239a8d2) |  ![eeris-register](https://github.com/user-attachments/assets/a95a02b4-138a-42f5-8c7e-087591af3583)

Dashboard        |  Report & Analytics
:-------------------------:|:-------------------------:
![eeris-dashboard](https://github.com/user-attachments/assets/46130f12-9c9d-4573-af1b-5e4fb4267681) |  ![eeris-report](https://github.com/user-attachments/assets/a7b00d66-02e6-42cc-97bb-9d97d56340c2) 

Expense Entry/Upload          |  Expense Viewing
:-------------------------:|:-------------------------:
![eeris-scan](https://github.com/user-attachments/assets/7537c94e-529f-449d-88d4-5b57dff93723) |  ![eeris-view-receipt](https://github.com/user-attachments/assets/2dcb2ef8-2dc1-4782-8a66-3b7788e4b2d4)

# UML Diagrams
Use Case Diagram             |  Interaction Overview Diagram | Activity Diagram
:-------------------------:|:-------------------------:|:-------------------------:
![EERIS-06-UCD](https://github.com/user-attachments/assets/1f1cac31-b1bd-4065-90a5-8854ca3a7b68) | ![EERIS-06-IOD (1)](https://github.com/user-attachments/assets/98122205-8ceb-49d4-8f22-63f908d27335) | ![activity-diagram](https://github.com/user-attachments/assets/e739af35-a1e5-45a3-ad88-cdea33822759)

# User Testing Accounts Created
#### Regular Employee Accounts
1. TestUser@gmail.com, Test12345*
2. Fang@usf.edu, F3489@02@3kni
3. eerisemployee@gmail.com, eerispassword12345

#### Supervisor Accounts
1. Group06@gmail.com, 42c43d496715369f6ba1
