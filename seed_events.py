"""Seed demo users, venues, events, bookings and comments.

Run AFTER create_db.py and seed_categories.py:
    python create_db.py
    python seed_categories.py
    python seed_events.py

Safe to re-run: anything that already exists is skipped, not duplicated.
Event dates are relative to today, so seeded screenings are always upcoming.

Covers: every category twice, three accounts (two organisers so ownership
rules can be tested), four venues, Open / Sold Out / Cancelled statuses,
enhanced/generic/none acknowledgements, events with and without posters,
comments on several events and bookings for two accounts.
"""

from datetime import date, time, timedelta

from flask_bcrypt import generate_password_hash

from website import create_app, db
from website.models import Category, Comment, Event, Order, User, Venue

app = create_app()

# same password for every seed account - log in as any of them
DEMO_PASSWORD = 'demo1234'

# organiser@ owns half the events, curator@ owns the other half.
# log in as one and open the other's events to see ownership rules work
# (no Edit button, and editing by URL gives 403).
USERS = [
    {'firstname': 'Demo', 'surname': 'Organiser',
     'email': 'organiser@quirkyscreenings.com',
     'contact_number': '0400 000 001',
     'street_address': '1 Cinema Lane, Brisbane QLD 4000'},
    {'firstname': 'Casey', 'surname': 'Curator',
     'email': 'curator@quirkyscreenings.com',
     'contact_number': '0400 000 002',
     'street_address': '2 Reel Street, Brisbane QLD 4000'},
    {'firstname': 'Pat', 'surname': 'Patron',
     'email': 'patron@quirkyscreenings.com',
     'contact_number': '0400 000 003',
     'street_address': '3 Foyer Court, Brisbane QLD 4000'},
]

VENUES = [
    {'name': 'The Tivoli', 'address': '527 Wickham St, Fortitude Valley QLD'},
    {'name': 'GOMA Cinema', 'address': 'Stanley Place, South Brisbane QLD'},
    {'name': 'New Farm Cinemas', 'address': '701 Brunswick St, New Farm QLD'},
    {'name': 'Lumen Room', 'address': 'Metro Arts, 109 Edward St, Brisbane QLD'},
]

AOC_TIVOLI = (
    "Quirky Screenings acknowledges the Turrbal and Yuggera peoples, "
    "Traditional Custodians of the land on which we gather tonight, and pays "
    "respect to Elders past and present. Tonight's screening honours the "
    "world's oldest continuous storytelling culture - a tradition of "
    "gathering to share stories that this cinema proudly continues."
)

AOC_GOMA = (
    "Quirky Screenings acknowledges the Turrbal and Yuggera peoples as the "
    "Traditional Custodians of the lands and waters of South Brisbane, where "
    "this gallery stands, and pays respect to Elders past and present. "
    "Storytelling has happened on this land for tens of thousands of years; "
    "tonight's film is a small part of that much larger tradition."
)

ORG = 'organiser@quirkyscreenings.com'
CUR = 'curator@quirkyscreenings.com'
PAT = 'patron@quirkyscreenings.com'

# day = how many days from today the screening is on
EVENTS = [
    # --- Arthouse & Independent ---
    {'title': 'The Grand Budapest Hotel', 'day': 3, 'organiser': ORG,
     'venue': 'The Tivoli', 'category': 'Arthouse & Independent',
     'synopsis': 'A legendary concierge and his protégé are swept up in the '
                 'theft of a priceless painting between the wars. Wes '
                 'Anderson\'s meticulously framed caper, back on the big screen.',
     'poster_image': '/static/img/grand-budapest.jpg',
     'classification': 'M', 'runtime': 99, 'screening_format': '35mm',
     'start_time': time(18, 30), 'end_time': time(20, 15),
     'ticket_price': 14.00, 'tickets_available': 60,
     'acknowledgement_type': 'generic'},

    {'title': 'Amélie', 'day': 8, 'organiser': CUR,
     'venue': 'New Farm Cinemas', 'category': 'Arthouse & Independent',
     'synopsis': 'A shy Parisian waitress secretly improves the lives of '
                 'those around her. Whimsical, warm and best seen with an audience.',
     'poster_image': None,  # no poster - shows the placeholder image
     'classification': 'M', 'runtime': 122, 'screening_format': 'Digital',
     'start_time': time(18, 0), 'end_time': time(20, 5),
     'ticket_price': 12.00, 'tickets_available': 45,
     'acknowledgement_type': 'generic'},

    # --- Cult Classic ---
    {'title': 'The Rocky Horror Picture Show', 'day': 2, 'organiser': CUR,
     'venue': 'The Tivoli', 'category': 'Cult Classic',
     'synopsis': 'The midnight movie to end all midnight movies. Costumes, '
                 'call-backs and the Time Warp - audience participation '
                 'absolutely encouraged.',
     'poster_image': None,
     'classification': 'MA15+', 'runtime': 100, 'screening_format': '35mm',
     'start_time': time(21, 0), 'end_time': time(22, 45),
     'ticket_price': 16.00, 'tickets_available': 80,
     'acknowledgement_type': 'enhanced', 'acknowledgement_text': AOC_TIVOLI},

    {'title': 'Pulp Fiction', 'day': 7, 'organiser': ORG,
     'venue': 'The Tivoli', 'category': 'Cult Classic',
     'synopsis': 'Hitmen, a boxer, a briefcase and a very good milkshake. '
                 'Tarantino\'s non-linear crime classic from a pristine 35mm print.',
     'poster_image': '/static/img/pulp-fiction.jpg',
     'classification': 'R18+', 'runtime': 154, 'screening_format': '35mm',
     'start_time': time(20, 30), 'end_time': time(23, 10),
     'ticket_price': 15.00, 'tickets_available': 70,
     'acknowledgement_type': 'generic'},

    # --- Foreign Language ---
    {'title': 'Spirited Away', 'day': 5, 'organiser': ORG,
     'venue': 'GOMA Cinema', 'category': 'Foreign Language',
     'synopsis': 'Chihiro must free her parents from a bathhouse for spirits '
                 'in Studio Ghibli\'s dreamlike masterpiece. Presented in '
                 'Japanese with English subtitles.',
     'poster_image': '/static/img/spirited-away.jpg',
     'classification': 'PG', 'runtime': 125, 'screening_format': 'Digital',
     'start_time': time(17, 45), 'end_time': time(19, 55),
     'ticket_price': 12.00, 'tickets_available': 80,
     'acknowledgement_type': 'enhanced', 'acknowledgement_text': AOC_GOMA},

    {'title': 'Parasite', 'day': 9, 'organiser': CUR,
     'venue': 'New Farm Cinemas', 'category': 'Foreign Language',
     'synopsis': 'Bong Joon-ho\'s Palme d\'Or and Oscar winner. A poor family '
                 'cons its way into a wealthy household - then the doorbell rings. '
                 'Korean with English subtitles.',
     'poster_image': None,
     'classification': 'MA15+', 'runtime': 132, 'screening_format': 'Digital',
     'start_time': time(19, 30), 'end_time': time(21, 45),
     'ticket_price': 13.00, 'tickets_available': 50,
     'acknowledgement_type': 'generic'},

    # --- Documentary ---
    {'title': 'Free Solo', 'day': 10, 'organiser': ORG,
     'venue': 'GOMA Cinema', 'category': 'Documentary',
     'synopsis': 'Alex Honnold attempts the first rope-free climb of El '
                 'Capitan. Best experienced with a full cinema holding its breath.',
     'poster_image': '/static/img/free-solo.jpg',
     'classification': 'M', 'runtime': 100, 'screening_format': 'Digital',
     'start_time': time(18, 0), 'end_time': time(19, 45),
     'ticket_price': 10.00, 'tickets_available': 90,
     'acknowledgement_type': 'none'},

    {'title': '20 Feet from Stardom', 'day': 11, 'organiser': CUR,
     'venue': 'New Farm Cinemas', 'category': 'Documentary',
     'synopsis': 'The backup singers behind the biggest hits finally take '
                 'centre stage. Oscar winner for Best Documentary.',
     'poster_image': None,
     'classification': 'M', 'runtime': 91, 'screening_format': 'Digital',
     'start_time': time(18, 30), 'end_time': time(20, 5),
     'ticket_price': 9.00, 'tickets_available': 40,
     'acknowledgement_type': 'generic'},

    # --- Musicals ---
    {'title': "Singin' in the Rain", 'day': 12, 'organiser': ORG,
     'venue': 'The Tivoli', 'category': 'Musicals',
     'synopsis': 'Hollywood\'s bumpy transition to sound, immortalised in '
                 'the greatest movie musical ever made. Umbrellas optional.',
     'poster_image': '/static/img/singin-in-the-rain.jpg',
     'classification': 'G', 'runtime': 103, 'screening_format': '35mm',
     'start_time': time(16, 0), 'end_time': time(17, 50),
     'ticket_price': 11.00, 'tickets_available': 60,
     'acknowledgement_type': 'generic'},

    # cancelled so the homepage shows that badge too
    {'title': 'Moulin Rouge!', 'day': 18, 'organiser': CUR,
     'venue': 'Lumen Room', 'category': 'Musicals',
     'synopsis': 'Baz Luhrmann\'s jukebox spectacular. A poet falls for a '
                 'cabaret star in turn-of-the-century Paris.',
     'poster_image': None,
     'classification': 'M', 'runtime': 127, 'screening_format': 'Digital',
     'start_time': time(19, 0), 'end_time': time(21, 10),
     'ticket_price': 14.00, 'tickets_available': 70,
     'status': 'Cancelled',
     'acknowledgement_type': 'generic'},

    # --- Blockbuster ---
    # sold out so the homepage shows that badge too
    {'title': 'Jurassic Park', 'day': 14, 'organiser': ORG,
     'venue': 'The Tivoli', 'category': 'Blockbuster',
     'synopsis': 'Life finds a way. Spielberg\'s dinosaur landmark, '
                 '65 million years in the making and still the gold standard.',
     'poster_image': '/static/img/jurassic-park.jpg',
     'classification': 'PG', 'runtime': 127, 'screening_format': 'Digital',
     'start_time': time(19, 0), 'end_time': time(21, 10),
     'ticket_price': 13.00, 'tickets_available': 80,
     'tickets_remaining': 0, 'status': 'Sold Out',
     'acknowledgement_type': 'generic'},

    {'title': 'The Matrix', 'day': 16, 'organiser': CUR,
     'venue': 'Lumen Room', 'category': 'Blockbuster',
     'synopsis': 'A hacker learns reality is not what it seems. Take the red '
                 'pill and see it the way 1999 audiences did: huge and loud.',
     'poster_image': None,
     'classification': 'M', 'runtime': 136, 'screening_format': 'Digital',
     'start_time': time(20, 0), 'end_time': time(22, 20),
     'ticket_price': 13.00, 'tickets_available': 100,
     'acknowledgement_type': 'generic'},
]

COMMENTS = [
    {'user': PAT, 'event': 'Spirited Away',
     'content': 'The bathhouse sequence on a cinema screen is going to be '
                'unreal. Grabbed two tickets already!'},
    {'user': ORG, 'event': 'Spirited Away',
     'content': 'Doors open 30 minutes before the session - come early for '
                'the best seats.'},
    {'user': PAT, 'event': 'Pulp Fiction',
     'content': 'First time seeing this on 35mm. The hype is real.'},
    {'user': PAT, 'event': 'The Rocky Horror Picture Show',
     'content': 'Is audience participation actually encouraged? '
                'Asking for a friend.'},
    {'user': CUR, 'event': 'The Grand Budapest Hotel',
     'content': 'The aspect ratio alone is worth the trip. Frame-by-frame '
                'perfection on the big screen.'},
]

# bookings for two accounts so My Bookings is populated either way;
# tickets come out of each event's remaining pool like a real booking
ORDERS = [
    {'user': ORG, 'event': 'Pulp Fiction', 'quantity': 2},
    {'user': PAT, 'event': 'The Grand Budapest Hotel', 'quantity': 3},
    {'user': PAT, 'event': 'Spirited Away', 'quantity': 1},
]

with app.app_context():
    # --- users (password is hashed exactly like the register route does) ---
    users = {}
    for data in USERS:
        user = User.query.filter_by(email=data['email']).first()
        if user is None:
            user = User(
                firstname=data['firstname'],
                surname=data['surname'],
                email=data['email'],
                password_hash=generate_password_hash(DEMO_PASSWORD).decode('utf-8'),
                contact_number=data['contact_number'],
                street_address=data['street_address'],
            )
            db.session.add(user)
            db.session.flush()
            print(f"Added user: {data['email']} (password: {DEMO_PASSWORD})")
        else:
            print(f"User already exists: {data['email']}")
        users[data['email']] = user

    # --- venues (reused by name, same as the create event route) ---
    venues = {}
    for data in VENUES:
        venue = Venue.query.filter_by(name=data['name']).first()
        if venue is None:
            venue = Venue(name=data['name'], address=data['address'])
            db.session.add(venue)
            db.session.flush()
            print(f"Added venue: {data['name']}")
        else:
            print(f"Venue already exists: {data['name']}")
        venues[data['name']] = venue

    # --- events ---
    events = {}
    for data in EVENTS:
        existing = Event.query.filter_by(title=data['title']).first()
        if existing is not None:
            print(f"Event already exists: {data['title']}")
            events[data['title']] = existing
            continue

        cat = Category.query.filter_by(name=data['category']).first()
        if cat is None:
            print(f"SKIPPED {data['title']}: category '{data['category']}' "
                  "not found - run seed_categories.py first")
            continue

        tickets_remaining = data.get('tickets_remaining', data['tickets_available'])
        event = Event(
            title=data['title'],
            synopsis=data['synopsis'],
            poster_image=data.get('poster_image'),
            classification=data['classification'],
            runtime=data['runtime'],
            screening_format=data['screening_format'],
            event_date=date.today() + timedelta(days=data['day']),
            start_time=data['start_time'],
            end_time=data['end_time'],
            ticket_price=data['ticket_price'],
            tickets_available=data['tickets_available'],
            tickets_remaining=tickets_remaining,
            status=data.get('status', 'Open'),
            acknowledgement_type=data['acknowledgement_type'],
            # only keep the text if the enhanced option was actually chosen
            acknowledgement_text=(data.get('acknowledgement_text')
                                  if data['acknowledgement_type'] == 'enhanced'
                                  else None),
            venue_id=venues[data['venue']].id,
            category_id=cat.id,
            organiser_id=users[data['organiser']].id,
        )
        db.session.add(event)
        db.session.flush()
        print(f"Added event: {data['title']} "
              f"({event.event_date.strftime('%d %b %Y')})")
        events[data['title']] = event

    # --- comments ---
    for data in COMMENTS:
        exists = Comment.query.filter_by(
            content=data['content'],
            event_id=events[data['event']].id,
            user_id=users[data['user']].id,
        ).first()
        if exists is None:
            db.session.add(Comment(
                content=data['content'],
                event_id=events[data['event']].id,
                user_id=users[data['user']].id,
            ))
            print(f"Added comment on: {data['event']}")

    # --- orders ---
    for data in ORDERS:
        event = events[data['event']]
        exists = Order.query.filter_by(
            event_id=event.id,
            user_id=users[data['user']].id,
        ).first()
        if exists is None:
            db.session.add(Order(
                quantity=data['quantity'],
                event_id=event.id,
                user_id=users[data['user']].id,
            ))
            event.tickets_remaining -= data['quantity']
            print(f"Added order: {data['quantity']}x {data['event']}")

    db.session.commit()
    print(f"Done. Log in as any seed account with password: {DEMO_PASSWORD}")
