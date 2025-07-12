import mysql.connector

def add_sample_skills():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="ShreeKrishna@7",
        database="skill_swap"
    )
    
    cursor = connection.cursor()
    
    sample_skills = [
        ('Python Programming', 'Technology'),
        ('JavaScript', 'Technology'),
        ('React.js', 'Technology'),
        ('Node.js', 'Technology'),
        ('MySQL Database', 'Technology'),
        ('Photoshop', 'Design'),
        ('Illustrator', 'Design'),
        ('UI/UX Design', 'Design'),
        ('Digital Marketing', 'Marketing'),
        ('Content Writing', 'Writing'),
        ('Excel', 'Office'),
        ('Data Analysis', 'Analytics'),
        ('Project Management', 'Management'),
        ('Public Speaking', 'Communication'),
        ('Guitar Playing', 'Music'),
        ('Cooking', 'Lifestyle'),
        ('Fitness Training', 'Health'),
        ('Language Translation', 'Language'),
        ('Video Editing', 'Media'),
        ('3D Modeling', 'Design')
    ]
    
    for skill_name, category in sample_skills:
        try:
            cursor.execute("INSERT INTO skills (name, category) VALUES (%s, %s)", (skill_name, category))
        except mysql.connector.IntegrityError:
            print(f"Skill '{skill_name}' already exists, skipping...")
    
    connection.commit()
    cursor.close()
    connection.close()
    print("Sample skills added successfully!")

if __name__ == '__main__':
    add_sample_skills()
