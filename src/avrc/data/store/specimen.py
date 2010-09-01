"""
Contains how to: specimen and aliquot
"""
from zope.component import adapts
from zope.schema.fieldproperty import FieldProperty
from zope.interface import implements
from zope.i18nmessageid import MessageFactory

from avrc.data.store._utils import DatastoreConventionalManager
from avrc.data.store import interfaces
from avrc.data.store import model
from avrc.data.store.datastore import named_session

import transaction

_ = MessageFactory(__name__)

class Specimen(object):
    implements(interfaces.ISpecimen)

    __doc__ = interfaces.ISpecimen.__doc__

    dsid = FieldProperty(interfaces.ISpecimen['dsid'])
    subject_zid = FieldProperty(interfaces.ISpecimen['subject_zid'])
    protocol_zid = FieldProperty(interfaces.ISpecimen['protocol_zid'])
    state = FieldProperty(interfaces.ISpecimen['state'])
    date_collected = FieldProperty(interfaces.ISpecimen['date_collected'])
    time_collected = FieldProperty(interfaces.ISpecimen['time_collected'])
    specimen_type = FieldProperty(interfaces.ISpecimen['specimen_type'])
    destination = FieldProperty(interfaces.ISpecimen['destination'])
    tubes = FieldProperty(interfaces.ISpecimen['tubes'])
    tube_type = FieldProperty(interfaces.ISpecimen['tube_type'])
    notes = FieldProperty(interfaces.ISpecimen['notes'])

class DatastoreSpecimenManager(DatastoreConventionalManager):
    adapts(interfaces.IDatastore)
    implements(interfaces.ISpecimenManager)

    __doc__ = interfaces.ISpecimenManager.__doc__

    def __init__(self, datastore):
        self._datastore = datastore
        self._model = model.Specimen
        self._type = Specimen
        Session = named_session(self._datastore)
        self._session = Session()

    def putProperties(self, rslt, source):
        """
        Add the items from the source to ds
        """
#        rslt.schemata.append(;lasdkfjas;lfj;saldfja;sldjfsa;ldjf;saldfjsa;fhsa)

    def get(self, key):
        session = self._session
        SpecimenModel = self._model

        specimen_rslt = session.query(SpecimenModel)\
                        .filter_by(id=int(key))\
                        .first()

        if not specimen_rslt:
            return None

        specimen_obj = Specimen()
        specimen_obj.dsid = specimen_rslt.id
        specimen_obj.subject_zid = specimen_rslt.subject.zid
        specimen_obj.protocol_zid = specimen_rslt.protocol.zid
        specimen_obj.state = specimen_rslt.state.value
        specimen_obj.date_collected = specimen_rslt.collect_date
        specimen_obj.time_collected = specimen_rslt.collect_time
        specimen_obj.specimen_type = specimen_rslt.type.value
        specimen_obj.destination = specimen_rslt.destination.value
        specimen_obj.tubes = specimen_rslt.tubes
        specimen_obj.tube_type = specimen_rslt.tube_type.value
        specimen_obj.notes = specimen_rslt.notes
        return specimen_obj

    def put(self, source):

        session = self._session
        SpecimenModel = self._model

        # Find the 'vocabulary' objects for the database relation
        keywords = ("state", "tube_type", "destination", "specimen_type")
        rslt = {}

        for keyword in keywords:
            if hasattr(source, keyword):
                rslt[keyword] = session.query(model.SpecimenAliquotTerm)\
                                .filter_by(vocabulary_name=unicode(keyword),
                                           value=unicode(getattr(source, keyword))
                                           )\
                                .first()
            else:
                rslt[keyword] = None

        if source.dsid is not None:
            specimen_rslt = session.query(SpecimenModel)\
                            .filter_by(id=source.dsid)\
                            .first()
        else:
            # which enrollment we get the subject from.
            subject_rslt = session.query(model.Subject)\
                            .filter_by(zid=source.subject_zid)\
                            .first()

            protocol_rslt = session.query(model.Protocol)\
                            .filter_by(zid=source.protocol_zid)\
                            .first()

            # specimen is not already in the data base, we need to create one
            specimen_rslt = SpecimenModel(
                subject=subject_rslt,
                protocol=protocol_rslt,
                type=rslt["specimen_type"],
                )

            session.add(specimen_rslt)

        specimen_rslt.destination = rslt["destination"]
        specimen_rslt.state = rslt["state"]
        specimen_rslt.collect_date = source.date_collected
        specimen_rslt.collect_time = source.time_collected
        specimen_rslt.tubes = source.tubes
        specimen_rslt.tube_type = rslt["tube_type"]
        specimen_rslt.notes = source.notes

        transaction.commit()

        if not source.dsid:
            source.dsid = specimen_rslt.id

        return source

class Aliquot(object):
    implements(interfaces.IAliquot)

    __doc__ = interfaces.IAliquot.__doc__

    dsid = FieldProperty(interfaces.IAliquot["dsid"])
    type = FieldProperty(interfaces.IAliquot["type"])
    state = FieldProperty(interfaces.IAliquot["state"])
    volume = FieldProperty(interfaces.IAliquot["volume"])
    cell_amount = FieldProperty(interfaces.IAliquot["cell_amount"])
    store_date = FieldProperty(interfaces.IAliquot["store_date"])
    freezer = FieldProperty(interfaces.IAliquot["freezer"])
    rack = FieldProperty(interfaces.IAliquot["rack"])
    box = FieldProperty(interfaces.IAliquot["box"])
    storage_site = FieldProperty(interfaces.IAliquot["storage_site"])
    thawed_num = FieldProperty(interfaces.IAliquot["thawed_num"])
    analysis_status = FieldProperty(interfaces.IAliquot["analysis_status"])
    sent_date = FieldProperty(interfaces.IAliquot["sent_date"])
    sent_name = FieldProperty(interfaces.IAliquot["sent_name"])
    notes = FieldProperty(interfaces.IAliquot["notes"])
    special_instruction = FieldProperty(interfaces.IAliquot["special_instruction"])

class DatastoreSpecimenAliquotManager(object):
    """
    """
    adapts(interfaces.IDatastore, interfaces.ISpecimen)
    implements(interfaces.IAliquotManager)

    def __init__(self, datastore_obj, specimen_obj):
        """
        """
        self._datastore_obj = datastore_obj
        self._specimen_obj = specimen_obj

    def list(self):
        Session = named_session(self._datastore_obj)
        session = Session()

        # Find the specimen first and from there get the aliquot results
        # to create objects
        specimen_rslt = session.query(model.Specimen)\
                        .filter_by(id=self._specimen_obj.dsid,
                                   is_active=True)\
                        .first()

        aliquot_list = []

        for aliquot_rslt in specimen_rslt.aliquot:
            aliquot_obj = Aliquot()
            aliquot_obj.dsid = aliquot_rslt.id
            aliquot_obj.type = aliquot_rslt.type.value
            aliquot_obj.state = aliquot_rslt.state.value
            aliquot_obj.volume = aliquot_rslt.volume
            aliquot_obj.cell_amount = aliquot_rslt.cell_amount
            aliquot_obj.store_date = aliquot_rslt.store_date
            aliquot_obj.freezer = aliquot_rslt.freezer
            aliquot_obj.rack = aliquot_rslt.rack
            aliquot_obj.box = aliquot_rslt.box
            aliquot_obj.storage_site = aliquot_rslt.storage_site.value
            aliquot_obj.thawed_num = aliquot_rslt.thawed_num
            aliquot_obj.analysis_status = aliquot_rslt.analysis_status.value
            aliquot_obj.sent_date = aliquot_rslt.sent_date
            aliquot_obj.sent_name = aliquot_rslt.sent_name
            aliquot_obj.notes = aliquot_rslt.notes
            aliquot_obj.special_instruction = aliquot_rslt.special_instruction.value

            aliquot_list.append(aliquot_obj)

        return aliquot_list


    def put(self, aliquot_obj):
        pass

    def get(self, aliquot_obj):
        pass

    def keys():
        pass

    def has(key):
        pass

    def purge(key):
        pass

    def retire(key):
        pass

    def restore(key):
        pass

    def put(target):
        pass
