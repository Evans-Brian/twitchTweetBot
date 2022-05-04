def createStagingTables(cur):
    cur.execute('drop table if exists watch_time_staging;')

    create_watch_time = '''create table watch_time_staging as
                (select game_id, game_name, user_id, user_name, thumbnail_url, 
                round(sum(viewer_count)/3,0) as watch_time
                from stream_data_staging
                group by 1, 2, 3, 4, 5);
                '''

    cur.execute(create_watch_time)


def updateStagingTables(cur):
    insert_watch_time = '''
                insert into watch_time_staging
                (select game_id, game_name, user_id, user_name, thumbnail_url, 
                round(sum(viewer_count)/3,0) as watch_time
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
    cur.execute('drop table if exists watch_time_table;')
    cur.execute('drop table if exists game_watch_time_table;')
    cur.execute('drop table if exists streamer_watch_time_table;')

    create_watch_time = '''
                create table watch_time_table as
                (select game_id, game_name, user_id, user_name, thumbnail_url, 
                TO_CHAR(watch_time, \'fm999G999D99\') as watch_time_pretty,
                watch_time as watch_time
                from watch_time_staging);
                '''

    create_game = '''
                create table game_watch_time_table as
                (select game_id, game_name, 
                TO_CHAR(sum(watch_time), \'fm999G999D99\') as watch_time_pretty,
                sum(watch_time) as watch_time
                from watch_time_staging
                group by 1, 2);
                '''

    create_streamer = '''
                create table streamer_watch_time_table as
                (select user_id, user_name, max(thumbnail_url),
                TO_CHAR(sum(watch_time), \'fm999G999D99\') as watch_time_pretty,
                sum(watch_time) as watch_time
                from watch_time_staging
                group by 1, 2);
                '''

    cur.execute(create_watch_time)
    cur.execute(create_game)
    cur.execute(create_streamer)
