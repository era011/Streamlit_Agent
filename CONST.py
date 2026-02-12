WV_SCHEMA="""
Коллекция - Chunk(
    content - содержимое чанка,
    type_doc - тип документа: РЕГЛАМЕНТ/ДИ/ПРОЦЕДУРА/ИНСТРУКЦИЯ/ПОРЯДОК/ПОЛОЖЕНИЕ/other/КОДЕКС/ПРАВИЛА/ПОЛИТИКА,
    section - номер секции документа,
    organization - ,
    added_date_to_weaviate - datetime.datetime(2025, 9, 23, 4, 57, 22, tzinfo=datetime.timezone.utc),
    name - наименование документа,
    source - ссылка на гугл диск,
    )
"""

DB_SCHEMA="""
Схема БД:
    Все документы всех организаций - documents(
        id_doc TEXT - id_doc метаданная чанка в weaviate, 
        name TEXT - наименование документа, 
        type_doc TEXT - тип документа: , 
        organization TEXT - организация: , 
        source TEXT - ссылка на гугл диск, 
        added_date TIMESTAMP WITH TIME ZONE yyyy-mm-dd hh:mm:ss
        )
    ВАЖНО!!! НЕ ИСПОСЛЬЗОВАТЬ ФИЛЬТР "WHERE organization = ' '" ДЛЯ ТАБЛИЦ acronyms, departments, job_instructions!!!
    список сокращений в  - acronyms(
        long_name TEXT - полная формулировка, 
        short_name TEXT - сокращенная запись
        )
    список отделов в  - departments(
        id INT - просто id,
        id_doc - id_doc документа отдела и метаданная чанка в weaviate,
        long_name - полное наименование отдела, например "Отдел по правовым вопросам"
        short_name - сокращенное название отдел, например "ОПВ"
        )
    список должностей в , касается сотрудников отдела, не самих отделов - job_instructions(
        id - bigserial,
        department_id - int4, к какому отделу относится должность
        position_name - text, название должности
        di_doc_title - text, название документа должностной инструкции
        di_doc_date - date, дата разработки документа, может быть null
        tasks - text, задачи должности
        responsibilities - text, объязаннсти должности
        rights - text, права должности
        requirements - text, требования
        conditions - text, условия
        source_file - text, названия файла
        raw_json - jsonb,
        created_at - timestamptz, 
        updated_at - timestamptz
        )
"""
