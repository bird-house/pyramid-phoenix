import os
import sys
import transaction

from sqlalchemy import engine_from_config
from sqlalchemy.exc import IntegrityError

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (DBSession, Base, Group, User, Status,
                     groupfinder, ADMIN_GROUP, USER_GROUP)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    # init db engine
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

     ## Initial Database Setup #################################################
    session = DBSession()

    try:
        Base.metadata.create_all(engine)

        group1 = Group(ADMIN_GROUP)
        group2 = Group(USER_GROUP)
        session.add(group1)
        session.add(group2)

        # TODO: add anonymous login
        user = User(username='admin', firstname='please change',
                    lastname='please change', email='please change',
                    password='admin', disabled=False)
        user.mygroups.append(group1)
        session.add(user)

        # Order is important!
        session.add(Status('Running'))
        session.add(Status('Completed'))
        session.add(Status('Cancelled'))
        session.add(Status('Failed'))

        session.flush()
        transaction.commit()
    except IntegrityError:
        transaction.abort()
        session = DBSession()
    
    ###########################################################################

    
