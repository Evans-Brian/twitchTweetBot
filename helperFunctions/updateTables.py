def createStagingTables(cur):
    cur.execute('drop table if exists game_watch_time_staging;')
    cur.execute('drop table if exists game_streamer_watch_time_staging;')
    cur.execute('drop table if exists streamer_watch_time_staging;')

    game_table = '''create table game_watch_time_staging as
                (select game_id, game_name, round(sum(viewer_count)/3,0)  as watch_time
                from stream_data_staging
                group by 1, 2);
                '''

    game_streamer_table = '''create table game_streamer_watch_time_staging as
                (select  user_name, game_name, round(sum(viewer_count)/3,0) as watch_time
                from stream_data_staging
                group by 1, 2);
                '''

    streamer_table = '''create table streamer_watch_time_staging as
                (select user_id, user_name, thumbnail_url, round(sum(viewer_count)/3,0) as watch_time
                from stream_data_staging
                group by 1, 2, 3);
                '''
    cur.execute(game_table)
    cur.execute(game_streamer_table)
    cur.execute(streamer_table)


def updateStagingTables(cur):
    insert_game = '''insert into game_watch_time_staging
                (select game_id, game_name, round(sum(viewer_count)/3,0)  as watch_time
                from stream_data_staging
                group by 1, 2)
                '''

    group_game = '''create temp table game_watch_time_staging_temp as
                (select game_id, game_name, sum(watch_time) as watch_time
                from game_watch_time_staging
                group by 1, 2)
                '''

    insert_game_streamer = '''insert into game_streamer_watch_time_staging
                (select user_name, game_name, round(sum(viewer_count)/3,0)  as watch_time
                from stream_data_staging
                group by 1, 2)
                '''

    group_game_streamer = '''create temp table game_streamer_watch_time_staging_temp as
                (select user_name, game_name, sum(watch_time) as watch_time
                from game_streamer_watch_time_staging
                group by 1, 2)
                '''

    insert_streamer = '''insert into streamer_watch_time_staging
                (select user_id, user_name, thumbnail_url, round(sum(viewer_count)/3,0)  as watch_time
                from stream_data_staging
                group by 1, 2, 3)
                '''

    group_streamer = '''create temp table streamer_watch_time_staging_temp as
                (select user_id, user_name, thumbnail_url, sum(watch_time) as watch_time
                from streamer_watch_time_staging
                group by 1, 2, 3)
                '''
    cur.execute(insert_game)
    cur.execute(group_game)

    cur.execute(insert_game_streamer)
    cur.execute(group_game_streamer)

    cur.execute(insert_streamer)
    cur.execute(group_streamer)

    cur.execute('drop table if exists game_watch_time_staging;')
    cur.execute('drop table if exists game_streamer_watch_time_staging;')
    cur.execute('drop table if exists streamer_watch_time_staging;')

    cur.execute('''
                create table game_watch_time_staging as
                (select * from game_watch_time_staging_temp);
                ''')
    cur.execute('''
                create table game_streamer_watch_time_staging as
                (select * from game_streamer_watch_time_staging_temp);
                ''')
    cur.execute('''
                create table streamer_watch_time_staging as
                (select * from streamer_watch_time_staging_temp);
                ''')

    cur.execute('drop table game_watch_time_staging_temp;')
    cur.execute('drop table game_streamer_watch_time_staging_temp;')
    cur.execute('drop table streamer_watch_time_staging_temp;')


def updateYesterdayTables(cur):
    cur.execute('drop table if exists game_watch_time;')
    cur.execute('drop table if exists game_streamer_watch_time;')
    cur.execute('drop table if exists streamer_watch_time;')

    game_table = '''create table game_watch_time as
                (select game_id, game_name, watch_time
                from game_watch_time_staging);
                '''

    game_streamer_table = '''create table game_streamer_watch_time as
                (select user_name, game_name, watch_time
                from game_streamer_watch_time_staging);
                '''

    streamer_table = '''create table streamer_watch_time as
                (select user_id, user_name, thumbnail_url, watch_time
                from  streamer_watch_time_staging);
                '''
    cur.execute(game_table)
    cur.execute(game_streamer_table)
    cur.execute(streamer_table)
