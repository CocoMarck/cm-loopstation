import datetime, calendar

DATETIME_FORMAT = "yyyy-MM-ddTHH:mm:ss"

def set_datetime_formatted( obj: datetime.datetime ):
    return str( obj.replace(microsecond=0).isoformat() )


def set_time_formatted( obj: datetime.time ):
    return str( obj.replace(microsecond=0).isoformat() )


def set_date_formatted( obj: datetime.date ):
    return str( obj.isoformatted() )

def get_datetime_now( mode: str="datetime") -> str:
    '''
    Devolver fecha completa actual
    '''
    _datetime = set_datetime_formatted( datetime.datetime.now() )
    if mode == "date" or mode == "time":
        time_or_date = _datetime.split("T")

        if mode == "date":
            return time_or_date[0]
        elif mode == "time":
            return time_or_date[1]
    else:
        return _datetime


def get_first_day_of_the_month( obj: datetime.datetime = datetime.datetime.now() ) -> str:
    '''
    Devolver dia inicial del mes incicado, como fecha completa. Por defecto el mes actual
    '''
    obj_ready = obj.replace( day = 1, hour = 0, minute = 0, second = 0 )
    return set_datetime_formatted( obj_ready )


def get_end_day_of_the_month( obj: datetime.datetime = datetime.datetime.now() ) -> str:
    '''
    Devolver dia final del mes indicado, como fecha completa. Por defect el mes actual
    '''
    final_day = calendar.monthrange( obj.year, obj.month )
    obj_ready = obj.replace(
        day = int(final_day[1]), hour = 0, minute = 0, second = 0
    )

    return set_datetime_formatted(obj_ready)



def separate_datetime_formatted( datetime_formatted: str, return_only: None  ) -> list | str:
    '''
    Separar tiempo y fecha
    '''
    separate = datetime_formatted.split("T")
    if return_only == "date":
        return separate[0]
    elif return_only == "time":
        return separate[1]
    else:
        return sperate


def get_date_from_formatted_datetime( datetime_formatted: str ):
    '''
    Obtener solo la fecha de un datetime
    '''
    return separate_datetime_formatted(
        datetime_formatted=datetime_formatted, return_only="date"
    )


def get_time_from_formatted_datetime( datetime_formatted: str ):
    '''
    Obtener solo el tiempo de un date time
    '''
    return separate_datetime_formatted(
        datetime_formatted=datetime_formatted, return_only="time"
    )
