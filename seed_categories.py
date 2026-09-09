from website import create_app, db
from website.models import Category

app = create_app()

CATEGORIES = [
    'Cult Classic',
    'Foreign Language',
    'Documentary',
    "Arthouse & Independent",
    'Musicals',
    'Blockbuster',
]

with app.app_context():
    for name in CATEGORIES:
        existing = Category.query.filter_by(name=name).first()
        if existing is None:
            db.session.add(Category(name=name))
            print(f"Added category: {name}")
        else:
            print(f"Category already exists: {name}")
    db.session.commit()