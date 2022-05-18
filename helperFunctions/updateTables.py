import pandas as pd


def createStagingTables(cur):
    """Deletes previous staging table and creates a new staging table.

    Args:
        cur (cursor): Cursor connected to the database.
    """
    cur.execute('drop table if exists watch_time_staging;')

    create_watch_time = '''create table watch_time_staging as
                (select game_id, game_name, user_id, user_name, thumbnail_url, 
                round(sum(viewer_count)/2,0) as watch_time
                from stream_data_staging
                group by 1, 2, 3, 4, 5);
                '''

    cur.execute(create_watch_time)


def stagingTableExist(cur):
    """Confirms if watch_time_staging table is in database.  If the length of the 
    returned query is zero, the table does not exist.

    Args:
        conn (connection): Connection to PSQL database

    Returns:
        (boolean): True if watch_time_staging exists in database. False otherwise
    """
    cur.execute(
        'select exists(select relname from pg_class where relname=\'watch_time_staging\')')

    exists = cur.fetchone()[0]
    return exists


def updateStagingTables(cur):
    """Updates staging table with data from the most recent Twitch API request. Data is appended and then grouped.

    Args:
        cur (cursor): Cursor connected to the database.
    """
    insert_watch_time = '''
                insert into watch_time_staging
                (select game_id, game_name, user_id, user_name, thumbnail_url, 
                round(sum(viewer_count)/2,0) as watch_time
                from stream_data_staging
                group by 1, 2, 3, 4, 5);
                '''

    group_watch_time = '''
                create temp table watch_time_staging_temp as
                (select game_id, game_name, user_id, user_name, thumbnail_url, 
                sum(watch_time) as watch_time
                from watch_time_staging
                group by 1, 2, 3, 4, 5);
                '''

    recreate_watch_time = '''
                create table watch_time_staging as
                (select * from watch_time_staging_temp);
                '''

    cur.execute(insert_watch_time)
    cur.execute(group_watch_time)
    cur.execute('drop table if exists watch_time_staging;')
    cur.execute(recreate_watch_time)
    cur.execute('drop table if exists watch_time_staging_temp;')


def updateYesterdayTables(cur):
    """Deletes yesterday's tables, which currently contain data for two days ago. Recreates the tables
    with data from one day ago.

    Args:
        cur (cursor): Cursor connected to the database
    """
    cur.execute('drop table if exists watch_time_table;')
    cur.execute('drop table if exists game_watch_time_table;')
    cur.execute('drop table if exists streamer_watch_time_table;')

    create_watch_time = '''
                create table watch_time_table as
                (select game_id, game_name, user_id, user_name, thumbnail_url, 
                watch_time
                from watch_time_staging);
                '''

    create_game = '''
                create table game_watch_time_table as
                (select game_id, game_name, 
                sum(watch_time) as watch_time
                from watch_time_staging
                group by 1, 2);
                '''

    create_streamer = '''
                create table streamer_watch_time_table as
                (select user_id, user_name,
                sum(watch_time) as watch_time
                from watch_time_staging
                group by 1, 2);
                '''

    cur.execute(create_watch_time)
    cur.execute(create_game)
    cur.execute(create_streamer)
