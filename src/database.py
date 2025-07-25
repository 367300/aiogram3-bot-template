import os
import ydb
from src.config import YDB_ENDPOINT, YDB_DATABASE

def get_ydb_pool(ydb_endpoint, ydb_database, timeout=30):
    ydb_driver_config = ydb.DriverConfig(
        ydb_endpoint,
        ydb_database,
        credentials=ydb.credentials_from_env_variables(),
        root_certificates=ydb.load_ydb_root_certificate(),
    )
    ydb_driver = ydb.Driver(ydb_driver_config)
    ydb_driver.wait(fail_fast=True, timeout=timeout)
    return ydb.SessionPool(ydb_driver)

def _format_kwargs(kwargs):
    return {f"${key}": value for key, value in kwargs.items()}

def execute_update_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )
    return pool.retry_operation_sync(callee)

def execute_select_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )
        return result_sets[0].rows
    return pool.retry_operation_sync(callee)

pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)

async def create_table():
    query = '''
    CREATE TABLE IF NOT EXISTS quiz_state (
        user_id Uint64, 
        question_index Uint64,
        PRIMARY KEY(user_id)
    );
    '''
    execute_update_query(pool, query)

async def create_results_table():
    query = '''
    CREATE TABLE IF NOT EXISTS quiz_results (
        user_id Uint64,
        username Utf8,
        correct_answers Uint64,
        PRIMARY KEY(user_id)
    );
    '''
    execute_update_query(pool, query)

async def get_quiz_index(user_id):
    query = '''
    DECLARE $user_id AS Uint64;
    SELECT question_index FROM quiz_state WHERE user_id == $user_id;
    '''
    results = execute_select_query(pool, query, user_id=user_id)
    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]

async def update_quiz_index(user_id, index):
    query = '''
    DECLARE $user_id AS Uint64;
    DECLARE $question_index AS Uint64;
    UPSERT INTO quiz_state (user_id, question_index) VALUES ($user_id, $question_index);
    '''
    execute_update_query(pool, query, user_id=user_id, question_index=index)

async def save_quiz_result(user_id, username, correct_answers):
    query = '''
    DECLARE $user_id AS Uint64;
    DECLARE $username AS Utf8;
    DECLARE $correct_answers AS Uint64;
    UPSERT INTO quiz_results (user_id, username, correct_answers) VALUES ($user_id, $username, $correct_answers);
    '''
    execute_update_query(pool, query, user_id=user_id, username=username, correct_answers=correct_answers)

async def get_all_results():
    query = '''
    SELECT username, correct_answers FROM quiz_results ORDER BY correct_answers DESC;
    '''
    results = execute_select_query(pool, query)
    return [(row["username"], row["correct_answers"]) for row in results]

async def get_user_result(user_id):
    query = '''
    DECLARE $user_id AS Uint64;
    SELECT correct_answers FROM quiz_results WHERE user_id == $user_id;
    '''
    results = execute_select_query(pool, query, user_id=user_id)
    if len(results) == 0:
        return None
    return results[0]["correct_answers"]