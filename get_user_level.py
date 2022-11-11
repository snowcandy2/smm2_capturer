# -*- coding: utf-8 -*-
import requests
import json
import pymysql
import time
import random
import os

dbh = pymysql.connect(host='127.0.0.1', user='root',password='A_114514',database='localdb',charset='utf8')
cur = dbh.cursor(cursor=pymysql.cursors.DictCursor)

maker_ids = ['M3XQGYG5G']
tgr_cached = False


def tgrcode(maker_id):
    url = 'https://tgrcode.com/mm2/get_posted/%s' % maker_id
    if os.path.exists('./maker_posted/%s.json' % maker_id):
        tgr_cached = True
        with open('./maker_posted/%s.json' % maker_id, 'r', encoding='utf8') as f:
            try:
                # return json.loads(f.read())
                return {"cached": 1}
            except Exception:
                return {"error": 1}
    tgr_cached = False
    req = requests.get(url)
    if not req.text:
        return {"error": 0}
    with open('./maker_posted/%s.json' % maker_id, "w", encoding='utf8') as f:
        f.write(req.text)
    try:
        return json.loads(req.text)
    except Exception:
        return {"error": 1}

if __name__ == "__main__":
    random.shuffle(maker_ids)
    for maker in maker_ids:
        res = tgrcode(maker_id=maker)
        if tgr_cached:
            print(maker, "Cached!")
            continue
        if isinstance(res, dict) and 'courses' in res:
            print(maker, len(res['courses']))
            for course in res['courses']:
                data = {
                    'level_code': course['course_id'],
                    'level_name': course['name'],
                    'level_desc': course['description'],
                    'level_tag_1': course['tags_name'][0] if len(course['tags_name']) > 0 else None,
                    'level_tag_2': course['tags_name'][1] if len(course['tags_name']) > 1 else None,
                    'maker_id': course['uploader']['code'] if 'uploader' in course else None,
                    'maker_name': course['uploader']['name'] if 'uploader' in course else None,
                    'maker_nation': course['uploader']['country'] if 'uploader' in course else None,
                    'likes': course['likes'],
                    'boos': course['boos'],
                    'plays': course['plays'],
                    'clears': course['clears'],
                    'attempts': course['attempts'],
                    'comments': course['num_comments'],
                    'clear_check_time': course['upload_time'] / 100.0,
                    'first_clear_id': course['first_completer']['code'] if course['clears'] != 0 else None,
                    'first_clear_name': course['first_completer']['name'] if course['clears'] != 0 else None,
                    'world_record_id': course['record_holder']['code'] if course['clears'] != 0 else None,
                    'world_record_name': course['record_holder']['name'] if course['clears'] != 0 else None,
                    'world_record_time': course['world_record'] / 100.0 if course['clears'] != 0 else None,
                    'versus_plays': course['versus_matches'],
                    'coop_plays': course['coop_matches'],
                    'difficulty': course['difficulty_name'],
                    'clear_condition': course['clear_condition_name'] + "(%d)" % course['clear_condition_magnitude'] if 'clear_condition_name' in course else None,
                    'time_limit': 0,
                    'version': course['game_style'],
                    'theme': course['theme_name'],
                }
                keys = ','.join(data.keys())
                values = ','.join(['%s'] * len(data))
                sql = 'REPLACE INTO t_courses ({keys}) VALUES ({values})'.format(keys=keys, values=values)
                cur.execute(sql, tuple(data.values()))
            dbh.commit()
            if not tgr_cached:
                time.sleep(random.uniform(12.0, 20.0))
