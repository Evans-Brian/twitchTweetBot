from sqlalchemy import create_engine

def createBaseTables(cur):
    cur.execute('drop table game_watch_time;')
    cur.execute('drop table streamer_watch_time;')
    
    game_table = '''create table game_watch_time as
                (select game_id, game_name, round(sum(viewer_count)/3,0)  as watch_time
                from stream_data_staging
                group by 1, 2);
                '''
                
    streamer_table = '''create table streamer_watch_time as
                (select user_id, user_name, thumbnail_url, round(sum(viewer_count)/3,0) as watch_time
                from stream_data_staging
                group by 1, 2, 3);
                '''
    cur.execute(game_table)
    cur.execute(streamer_table)
    

def updateBaseTables(cur):
    insert_game = '''insert into game_watch_time
                (select game_id, game_name, round(sum(viewer_count)/3,0)  as watch_time
                from stream_data_staging
                group by 1, 2)
                '''
    group_game = '''create temp table game_watch_time_temp as
                (select game_id, game_name, sum(watch_time) as watch_time
                from game_watch_time
                group by 1, 2)
                '''
                
    insert_streamer = '''insert into streamer_watch_time
                (select user_id, user_name, thumbnail_url, round(sum(viewer_count)/3,0)  as watch_time
                from stream_data_staging
                group by 1, 2, 3)
                '''
    
    group_streamer = '''create temp table streamer_watch_time_temp as
                (select user_id, user_name, thumbnail_url, sum(watch_time) as watch_time
                from streamer_watch_time
                group by 1, 2, 3)
                '''
    cur.execute(insert_game)
    cur.execute(group_game)
    cur.execute(insert_streamer)
    cur.execute(group_streamer)
    
    cur.execute('drop table game_watch_time;')
    cur.execute('drop table streamer_watch_time;')
    
    cur.execute('''
                create table game_watch_time as
                (select * from game_watch_time_temp);
                ''')
    cur.execute('''
                create table streamer_watch_time as
                (select * from streamer_watch_time_temp);
                ''')
    
    cur.execute('drop table game_watch_time_temp;')
    cur.execute('drop table streamer_watch_time_temp;')