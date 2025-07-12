from app import app, db
from models import User, Skill, UserSkillOffered, UserSkillWanted, Availability

def check_database():
    with app.app_context():
        # Check Users
        print("\n=== Users ===")
        users = User.query.all()
        for user in users:
            print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")
        
        # Check Skills
        print("\n=== Skills ===")
        skills = Skill.query.all()
        for skill in skills:
            print(f"ID: {skill.id}, Name: {skill.name}, Category: {skill.category}")
        
        # Check UserSkillOffered
        print("\n=== Offered Skills ===")
        offered_skills = UserSkillOffered.query.all()
        for skill in offered_skills:
            print(f"User ID: {skill.user_id}, Skill ID: {skill.skill_id}, Level: {skill.proficiency_level}")
        
        # Check UserSkillWanted
        print("\n=== Wanted Skills ===")
        wanted_skills = UserSkillWanted.query.all()
        for skill in wanted_skills:
            print(f"User ID: {skill.user_id}, Skill ID: {skill.skill_id}, Level: {skill.desired_level}")
        
        # Check Availability
        print("\n=== Availability ===")
        availabilities = Availability.query.all()
        for avail in availabilities:
            print(f"User ID: {avail.user_id}, Day: {avail.day}, Time: {avail.time_slot}")

if __name__ == '__main__':
    check_database()
