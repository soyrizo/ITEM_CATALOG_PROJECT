from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Sport, Base, Item

engine = create_engine('sqlite:///sportscatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# SOCCER
sport1 = Sport(name="Soccer")
session.add(sport1)
session.commit()

soccer1 = Item(name="Soccer Ball", description="A ball used in the sport of
               Soccer or association football. The is spherical in shape and
               is stitched together with pentagon shaped patches of 24, 32,
               or 42 panels.", sport=sport1)
session.add(soccer1)
session.commit()

soccer2 = Item(name="Shin Pads", description="Protection for your shins when
               playing soccer.", sport=sport1)
session.add(soccer2)
session.commit()

soccer3 = Item(name="Cleats", description="The shoe type required for soccer.
               This can vary depending on indoor or outdoor field types.",
               sport=sport1)
session.add(soccer3)
session.commit()

# GOLF
sport2 = Sport(name="Golf")
session.add(sport2)
session.commit()

golf1 = Item(name="Club", description="A golf club is used for hitting
             the golf ball. There are different types of clubs depending
             on factors like terrain and distance required to hit the
             ball.", sport=sport2)
session.add(golf1)
session.commit()

golf2 = Item(name="Golf Ball", description="The golf ball is hit using golf
             clubs.", sport=sport2)
session.add(golf2)
session.commit()

# HOCKEY
sport3 = Sport(name="Hockey")
session.add(sport3)
session.commit()

hockey1 = Item(name="Puck", description="The puck is a disk made of rubber that
               serves as the ball.", sport=sport3)
session.add(hockey1)
session.commit()

# TENNIS
sport4 = Sport(name="Tennis")
session.add(sport4)
session.commit()

tennis1 = Item(name="Racquet", description="The tennis racquet is used to hit
               the tennis ball. They come in various styles and designs.",
               sport=sport4)
session.add(tennis1)
session.commit()

tennis2 = Item(name="Tennis Ball", description="The tennis ball is hit back and
               forth between two players with the tennis racquet.",
               sport=sport4)
session.add(tennis2)
session.commit()

# BASEBALL
sport5 = Sport(name="Baseball")
session.add(sport5)
session.commit()

baseball1 = Item(name="Bat", description="The baseball bat is used to hit the
                 baseball.", sport=sport5)
session.add(baseball1)
session.commit()

baseball2 = Item(name="Baseball", description="The baseball is hit with the
                 baseball bat. It is used to strike people out, tag folks
                 in addition to other uses.", sport=sport5)
session.add(baseball2)
session.commit()

# BASKETBALL
sport6 = Sport(name="Basketball")
session.add(sport6)
session.commit()

basketball1 = Item(name="Basketball", description="The bascketball is the ball
                   used by the players. It is passed and shot through the hoop
                   to score points.", sport=sport6)
session.add(basketball1)
session.commit()
