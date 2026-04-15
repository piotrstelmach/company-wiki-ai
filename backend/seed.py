import os
from uuid import uuid4
from sqlmodel import Session, select
from models import Chat, Message, UserRole, Department, JobTitle, User
from auth import get_password_hash
from database import engine, create_db_and_tables


def seed_data():
    # Ensure tables exist
    create_db_and_tables()

    with Session(engine) as session:
        print("Checking database status...")
        
        # 2. Seed Roles
        role_admin = session.exec(select(UserRole).where(UserRole.name == "ADMIN")).first()
        role_hr = session.exec(select(UserRole).where(UserRole.name == "HR")).first()
        role_employee = session.exec(select(UserRole).where(UserRole.name == "EMPLOYEE")).first()

        if not role_admin or not role_hr or not role_employee:
            print("Seeding roles...")
            if not role_admin:
                role_admin = UserRole(name="ADMIN", description="Full system access")
                session.add(role_admin)
            if not role_hr:
                role_hr = UserRole(name="HR", description="Human Resources management")
                session.add(role_hr)
            if not role_employee:
                role_employee = UserRole(name="EMPLOYEE", description="Access to own data and general policies")
                session.add(role_employee)
            session.commit()
            session.refresh(role_admin)
            session.refresh(role_hr)
            session.refresh(role_employee)
        else:
            print("Roles already exist.")

        # 3. Seed Departments
        dept_it = session.exec(select(Department).where(Department.name == "IT")).first()
        dept_hr = session.exec(select(Department).where(Department.name == "Human Resources")).first()
        dept_sales = session.exec(select(Department).where(Department.name == "Sales")).first()

        if not dept_it or not dept_hr or not dept_sales:
            print("Seeding departments...")
            if not dept_it:
                dept_it = Department(name="IT")
                session.add(dept_it)
            if not dept_hr:
                dept_hr = Department(name="Human Resources")
                session.add(dept_hr)
            if not dept_sales:
                dept_sales = Department(name="Sales")
                session.add(dept_sales)
            session.commit()
            session.refresh(dept_it)
            session.refresh(dept_hr)
            session.refresh(dept_sales)
        else:
            print("Departments already exist.")

        # 4. Seed Job Titles
        title_devops = session.exec(select(JobTitle).where(JobTitle.name == "DevOps Engineer")).first()
        title_dev = session.exec(select(JobTitle).where(JobTitle.name == "Software Developer")).first()
        title_recruiter = session.exec(select(JobTitle).where(JobTitle.name == "Senior Recruiter")).first()

        if not title_devops or not title_dev or not title_recruiter:
            print("Seeding job titles...")
            if not title_devops:
                title_devops = JobTitle(name="DevOps Engineer", department_id=dept_it.id)
                session.add(title_devops)
            if not title_dev:
                title_dev = JobTitle(name="Software Developer", department_id=dept_it.id)
                session.add(title_dev)
            if not title_recruiter:
                title_recruiter = JobTitle(name="Senior Recruiter", department_id=dept_hr.id)
                session.add(title_recruiter)
            session.commit()
            session.refresh(title_devops)
            session.refresh(title_dev)
            session.refresh(title_recruiter)
        else:
            print("Job titles already exist.")

        # 5. Seed Users
        admin_user = session.exec(select(User).where(User.username == "admin")).first()
        dev_user = session.exec(select(User).where(User.username == "dev")).first()

        if not admin_user or not dev_user:
            print("Seeding test users...")
            if not admin_user:
                admin_user = User(
                    username="admin",
                    email="admin@company.com",
                    hashed_password=get_password_hash("admin123"),
                    role_id=role_admin.id,
                    department_id=dept_it.id,
                    job_title_id=title_devops.id,
                    is_active=True
                )
                session.add(admin_user)
            if not dev_user:
                dev_user = User(
                    username="dev",
                    email="dev@company.com",
                    hashed_password=get_password_hash("dev123"),
                    role_id=role_employee.id,
                    department_id=dept_it.id,
                    job_title_id=title_dev.id,
                    is_active=True
                )
                session.add(dev_user)
            session.commit()
            if admin_user: session.refresh(admin_user)
            if dev_user: session.refresh(dev_user)
            print(f"Users seeded.")
        else:
            print("Users already exist.")

        # 6. Seed Chats (only if dev user exists and has no chats)
        if dev_user:
            existing_chats = session.exec(select(Chat).where(Chat.user_id == dev_user.id)).all()
            if not existing_chats:
                print("Seeding database with 5 chats...")

                chats_data = [
                    {
                        "title": "Onboarding and First Steps",
                        "messages": [
                            {"role": "user",
                             "content": "Hi! I just joined the company. Where can I find the onboarding documents?"},
                            {"role": "ai",
                             "content": "Welcome to the team! You can find all onboarding materials in the 'Human Resources' section of our Wiki. Specifically, look for the 'New Hire Checklist' and 'Company Handbook' documents."},
                            {"role": "user", "content": "Thanks! And what about my workstation setup?"},
                            {"role": "ai",
                             "content": "For your workstation setup, please refer to the 'IT Support' page. There's a step-by-step guide for setting up your laptop, VPN, and essential software like Slack and Jira."}
                        ]
                    },
                    {
                        "title": "Remote Work Policy",
                        "messages": [
                            {"role": "user", "content": "What is our current policy on remote work?"},
                            {"role": "ai",
                             "content": "We follow a hybrid model. Most teams are expected to be in the office 2 days a week, but this can vary by department. You should check with your manager for your team's specific arrangement."},
                            {"role": "user", "content": "Can I work from another country for a short period?"},
                            {"role": "ai",
                             "content": "Working from abroad (Workation) is allowed for up to 30 days per year, subject to manager approval and tax/legal considerations. Please see the 'Workation Policy' document for more details."}
                        ]
                    },
                    {
                        "title": "Benefits and Healthcare",
                        "messages": [
                            {"role": "user", "content": "What healthcare benefits do we have?"},
                            {"role": "ai",
                             "content": "We provide comprehensive private medical insurance through LuxMed. This includes dental care and mental health support. You can also add family members at a discounted rate."},
                            {"role": "user", "content": "Is there a fitness card available?"},
                            {"role": "ai",
                             "content": "Yes, we offer the MultiSport card. The company subsidizes 50% of the cost, and the remaining amount is deducted from your monthly salary."}
                        ]
                    },
                    {
                        "title": "Project Management Tools",
                        "messages": [
                            {"role": "user", "content": "Which tools do we use for project management?"},
                            {"role": "ai",
                             "content": "We primarily use Jira for task tracking and Confluence for documentation. For quick communication, we use Slack, and for meetings, we use Google Meet."},
                            {"role": "user", "content": "How do I get access to Jira?"},
                            {"role": "ai",
                             "content": "You can request access by submitting a ticket through the IT Service Desk portal. Your manager will then need to approve the request."}
                        ]
                    },
                    {
                        "title": "Internal Training and Development",
                        "messages": [
                            {"role": "user", "content": "Does the company offer any training budgets?"},
                            {"role": "ai",
                             "content": "Yes, every employee has an annual personal development budget of $2000. You can use it for courses, certifications, or attending conferences related to your role."},
                            {"role": "user", "content": "How do I apply for a conference?"},
                            {"role": "ai",
                             "content": "First, discuss it with your manager during your 1-on-1. Once approved, you can fill out the 'Training Request' form on the HR portal with the conference details and estimated costs."}
                        ]
                    }
                ]

                # All initial chats are linked to the 'dev' user
                for chat_data in chats_data:
                    chat = Chat(id=uuid4(), title=chat_data["title"], user_id=dev_user.id)
                    session.add(chat)
                    session.commit()
                    session.refresh(chat)

                    for msg_data in chat_data["messages"]:
                        message = Message(
                            role=msg_data["role"],
                            content=msg_data["content"],
                            chat_id=chat.id
                        )
                        session.add(message)

                    session.commit()

                print("Chats seeded.")
            else:
                print("Chats already exist for 'dev' user.")

        print("Seeding completed successfully.")
        print("Final Users in database:")
        all_users = session.exec(select(User)).all()
        for u in all_users:
            print(f" - {u.username} ({u.email}, role_id: {u.role_id})")


if __name__ == "__main__":
    seed_data()
