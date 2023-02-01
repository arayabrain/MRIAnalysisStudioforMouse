from sqlmodel import Session, SQLModel, select
from sqlmodel.sql.expression import SelectOfScalar


# pylint: disable=missing-raises-doc
def filter_by(model: SQLModel, **kwargs) -> SelectOfScalar:
    """
    TODO: missing function docstring
    """
    query = select(model)
    for field_name, value in kwargs.items():
        field = model.__table__.columns.get(field_name)
        if field is not None:
            query = query.where(field == value)
        else:
            raise Exception(f"where: {model.__name__}.{field_name} does not exist")
    return query


# pylint: disable=missing-raises-doc
def order_by(query: SelectOfScalar, model: SQLModel, **kwargs) -> SelectOfScalar:
    """
    TODO: missing function docstring
    """
    for field_name, order in kwargs.items():
        field = model.__table__.columns.get(field_name)
        if field is not None:
            if order == 'asc':
                query = query.order_by(field)
            elif order == 'desc':
                query = query.order_by(field.desc())
        else:
            raise Exception(f"order_by: {model.__name__}.{field_name} does not exist")
    return query


async def get_one(db: Session, model: SQLModel, **kwargs):
    """
    TODO: missing function docstring
    """
    query = filter_by(model, **kwargs)
    result = await db.execute(query)
    return result.scalar()


async def get_multi(db: Session, model: SQLModel, offset=0, limit=10, **kwargs):
    """
    TODO: missing function docstring
    """
    query = filter_by(model, **kwargs)
    query = order_by(query, model, id='asc')
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars()
