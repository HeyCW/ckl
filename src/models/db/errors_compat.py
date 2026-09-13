import sqlite3


def db_error_classes():
    """Exception class tuples for except clauses that must catch errors
    from whichever DB-API driver is actually in play. sqlite3 and
    psycopg both follow the PEP 249 exception hierarchy, so the names
    line up; psycopg is only imported if it's installed.
    """
    classes = {
        "Error": (sqlite3.Error,),
        "IntegrityError": (sqlite3.IntegrityError,),
        "OperationalError": (sqlite3.OperationalError,),
    }
    try:
        import psycopg
        classes["Error"] += (psycopg.Error,)
        classes["IntegrityError"] += (psycopg.IntegrityError,)
        classes["OperationalError"] += (psycopg.OperationalError,)
    except ImportError:
        pass
    return classes
