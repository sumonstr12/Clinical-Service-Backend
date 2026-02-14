from users.models import User

def run():
    # user1 = User(
    #     username="Patient_user",
    #     full_name="Super Admin",
    #     email="patient@healthcare.com",
    #     phone="+8801500000000",
    #     role="PATIENT",
    #     is_active=True,
    #     is_staff=False,
    #     is_superuser=False
    # )
    
    # user1.set_password("sumon")
    
    # user1.save()

    # print(f"User {user1.username} created successfully!")

    user = User.objects.filter(role="ADMIN")
    print(user.values())