from sqlalchemy import create_engine, inspect

class ViCMSMixin:

    def formgen_assist(session):
        return None

    @classmethod
    def select_assist(cls):
        return None

    # create table if not exist on dburi
    @classmethod
    def create_table(cls, dburi):
        engine = create_engine(dburi)
        cls.__table__.create(engine, checkfirst=True)
        engine.dispose() #house keeping

    # check if table exists in dburi
    @classmethod
    def table_exists(cls, dburi):
        engine = create_engine(dburi)
        ins = inspect(engine)
        res = cls.__tablename__ in ins.get_table_names()
        engine.dispose()
        return res
