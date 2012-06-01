import sqlalchemy.orm
import sqlalchemy.event

from occams.datastore.model.metadata import updateMetadata
from occams.datastore.model.metadata import Modifiable
from occams.datastore.model.auditing import Auditable
from occams.datastore.model.auditing import createRevision
from occams.datastore.model.schema import setChecksum
from occams.datastore.model.schema import Attribute
from occams.datastore.model.storage import Entity
from occams.datastore.model.storage import enforceSchemaState


class DataStoreSession(sqlalchemy.orm.Session):
    """
    Custom session that registers itself to the various datastore listeners.

    The intention of this class is to allow a client plugin to just be able
    to use this method as a substitute to sqlalchemy's ``Session``
    class to allow comprehensive datastore functionality.

    If the client plugin needs ``scoped_session`` support, this class
    can be used as a parameter in ``sessionmaker`` as follows::

        engine = sqlalchemy.create_engine('sqlite:///')
        factory = sqlalchemy.orm.sessionmaker(engine, class_=DataStoreSession)

    Another key feature of this class is that a ``user`` callback may be
    registered by the implementing system in order for DataStore to be
    able to correctly lookup the user flushing the data in order to maintain
    a proper auditing trail.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor with default parameters overriden. Also registers listeners.
        """
        self.userCallback = kwargs.pop('user')
        kwargs.setdefault('autoflush', True)
        kwargs.setdefault('autocommit', False)
        super(DataStoreSession, self).__init__(*args, **kwargs)
        sqlalchemy.event.listen(self, 'before_flush', onBeforeFlush)


def onBeforeFlush(session, flush_context, instances):
    """
    Handles the ``before_flush`` event of DataStore's custom session
    """
    for instance in iter(session.new):
        dispatch(instance, 'new')
    for instance in iter(session.dirty):
        dispatch(instance, 'dirty')
    for instance in iter(session.deleted):
        dispatch(instance, 'deleted')


def dispatch(instance, state):
    """
    Dispatches the events to the instances
    """

    if isinstance(instance, Attribute) and state in ('new', 'dirty'):
        setChecksum(instance)

    if isinstance(instance, Entity) and state in ('new', 'dirty'):
        enforceSchemaState(instance)

    if isinstance(instance, Modifiable) and state in ('new', 'dirty'):
        updateMetadata(instance, created=(state == 'new'))

    if isinstance(instance, Auditable) and state in ('dirty'):
        createRevision(instance, deleted=False)

    if isinstance(instance, Auditable) and state in ('deleted'):
        # Audit the last revision of the row
        createRevision(instance, deleted=True)
        # If the row keeps track of its metadata, we want to record whom deleted
        # the row as well, so issue a final touch and then audit again
        if isinstance(instance, Modifiable):
            updateMetadata(instance, created=False)
            createRevision(instance, deleted=True)
