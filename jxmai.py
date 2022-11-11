# -*- coding=utf-8 -*-
import datetime
import json
import logging
import random
import requests
import pymysql
import atexit
import asyncio
import websockets

from identifier import *
from camera import *
from detect0r import *
from playsound import playsound as play_sound
import threading
import pyperclip as pc

LIMIT = 0.85

dbh = pymysql.connect(host='192.168.1.19', user='root', password='abc123456', database='localdb', charset='utf8')
cur = dbh.cursor(cursor=pymysql.cursors.DictCursor)

def playsound(file):
    # play_sound(file)
    try:
        thread = threading.Thread(target=play_sound, args=(file, ))
        thread.start()
    except Exception:
        pass

def detect_new_level(id2):
    r = id2.findPicture('./sub_image/tag.png', dontgetgray=True, part=(900, 232, 319, 82))
    # print(r)
    return r

def detect_death(id2):
    r = id2.findPicture('./sub_image/death.png', dontgetgray=True)
    return r

def detect_start_over(id2):
    r = id2.findPicture('./sub_image/start_over.png', dontgetgray=True, part=(822, 413, 429, 87))
    return r

def level_code_prettify(text: str):
    res = text.strip().upper().replace(" ", "").replace("Z", "2").replace("I", "1").replace("A", "4") \
        .replace("O", "0").replace("(", "C").replace(")", "J").replace("$", "S").replace("§", "S").replace("€", "C")
    return res

def replace_level_code(text : str):
    res = text.strip().upper().replace("-", "").replace(" ", "").replace("Z", "2").replace("I", "1").replace("A", "4")\
        .replace("O", "0").replace("(", "C").replace(")", "J").replace("$", "S").replace("§", "S").replace("€", "C")
    return res

def get_level_info(code):
    try:
        url = "https://tgrcode.com/mm2/level_info/%s" % code
        res = requests.get(url, timeout=30)
        if res.text:
            with open("./level/%s.json" % code, "w", encoding='utf8') as f:
                f.write(res.text)
        try:
            return json.loads(res.text)
        except Exception:
            return res.text
    except Exception as e:
        return {"error": 0, "msg": e.__str__}

def save2mysql(course):
    try:
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
        sql = 'REPLACE INTO t_courses2 ({keys}) VALUES ({values})'.format(keys=keys, values=values)
        cur.execute(sql, tuple(data.values()))
        dbh.commit()
        return 1
    except Exception:
        return 0

@atexit.register
def clean():
    with open("./level_name.txt", "w", encoding="utf-8") as f:
        f.write("")
    with open("./level_loves.txt", "w", encoding="utf-8") as f:
        f.write("")
    with open("./death_count.txt", "w", encoding="utf-8") as f:
        f.write("")
    with open("./tiku.txt", "w", encoding="utf-8") as f:
        f.write("")
    print("Exit")


async def ws(websocket, path):
    print("Web socket started...")
    logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                        filename='./log/logger-%s.log' % (datetime.datetime.now().strftime("%Y-%m-%d")),
                        level=logging.INFO)
    cam = Camera()
    id2 = Identifier(cam)
    detect_flag = 0
    detect_flag_d = 0
    death = 0
    win = 0
    lose = 0
    last_det_level_code = ""
    win_detection = False
    lose_detection = False
    message_from = ""
    msg_text = ""
    while True:
        try:
            await asyncio.sleep(0.5)
            id2.refresh()
            # 检查进图
            tag_detect = detect_new_level(id2)
            if tag_detect['max'] > LIMIT:
                detect_flag += 1
                if detect_flag == 3:
                    level_code_img = id2.getPart(80, 175, 203, 32)
                    level_code_img_2 = 1.0000*level_code_img[:,:,2]
                    level_code_img_2[level_code_img_2 > 180] = 255
                    level_code_img_2[level_code_img_2 <= 180] = 0
                    cv2.imwrite("./test.png", level_code_img_2)
                    level_code_img_2 = Image.fromarray(level_code_img_2)
                    # print(level_code_img_2)
                    if level_code_img_2.mode == "F":
                        level_code = pytesseract.image_to_string(level_code_img_2.convert('RGB'), lang="eng", timeout=2, config="--psm 6")
                    else:
                        level_code = pytesseract.image_to_string(level_code_img_2, lang="eng", timeout=2, config="--psm 6")
                    # print(level_code)
                    level_code = level_code.replace(" ", "").replace("\r", "").replace("\n", "")
                    level_code_0 = replace_level_code(level_code)
                    if len(level_code_0) != 9 or level_code_0 == last_det_level_code:
                        # playsound("./toad_sorry.mp3")
                        if len(level_code_0) != 9:
                            await websocket.send(json.dumps({"type": "level_detected"}))
                            # playsound("./woteme.mp3")
                            print("Bad level code: ", level_code_0)
                        # print(level_code)
                        continue
                    else:
                        last_det_level_code = level_code_0
                    await websocket.send(json.dumps({"type": "level_detected"}))
                    print(level_code_0)
                    pc.copy(level_code_0)
                    sql = 'select * from t_tiku where course_id = %s limit 1'
                    cur.execute(sql, level_code_0)
                    res = cur.fetchone()
                    if res:
                        print(res['course_hint'])
                        with open("./tiku.txt", 'w', encoding='utf-8') as f:
                            f.write(res['course_hint'])
                    else:
                        with open("./tiku.txt", 'w', encoding='utf-8') as f:
                            f.write("")
                    death = 0
                    with open("./death_count.txt", 'w', encoding='utf-8') as f:
                        f.write("Death: %d" % (death))
                    level_info = get_level_info(level_code_0)
                    if 'error' in level_info or isinstance(level_info, str):
                        print(level_info)
                        # playsound("./toad_sorry.mp3")
                        level_name_img = id2.getPart(121, 88, 1051, 41)
                        level_name_img_2 = 1.0000*level_name_img[:,:,2]
                        level_name_img_2[level_name_img_2 > 180] = 255
                        level_name_img_2[level_name_img_2 <= 180] = 0
                        cv2.imwrite("./test.png", level_name_img_2)
                        level_name_img_2 = Image.fromarray(level_name_img_2)
                        # print(level_code_img_2)
                        if level_name_img_2.mode == "F":
                            level_name = pytesseract.image_to_string(level_name_img_2.convert('RGB'), lang="eng+chi_sim+jpn", timeout=2, config="--psm 6")
                        else:
                            level_name = pytesseract.image_to_string(level_name_img_2, lang="eng+chi_sim+jpn", timeout=2, config="--psm 6")
                        with open("./level_name.txt", 'w', encoding='utf-8') as f:
                            f.write("%s (%s)" % (level_name, level_code_prettify(level_code)))
                        with open("./level_loves.txt", 'w', encoding='utf-8') as f:
                            f.write("")
                        print("%s (%s)" % (level_name, level_code_prettify(level_code)))
                        await websocket.send(json.dumps({"type": "level", "message": {"level_name": level_name, "level_code": level_code_prettify(level_code)}}))
                        continue
                    await websocket.send(json.dumps({"type": "new_level", "level_code": level_code_prettify(level_code), "message": level_info}))
                    save2mysql(level_info)
                    level_name = level_info['name']
                    level_creator = level_info['uploader']['name']
                    level_clear_rate = level_info['clear_rate']
                    level_likes = int(level_info['likes'])
                    level_boos = int(level_info['boos'])
                    level_plays = int(level_info['plays'])
                    diff_name = level_info['difficulty_name']
                    time_clear = level_info['upload_time_pretty']
                    if 'world_record_pretty' in level_info:
                        time_clear_wr = level_info['world_record_pretty']
                    else:
                        time_clear_wr = "???"
                    if "record_holder" in level_info and 'name' in level_info['record_holder']:
                        wr_holder = level_info['record_holder']['name']
                    else:
                        wr_holder = '???'
                    in_versus = level_info['versus_matches']
                    with open("./level_name.txt", 'w', encoding='utf-8') as f:
                        f.write("%s by %s (%s, %s)" % (level_name, level_creator, level_code_prettify(level_code), level_clear_rate))
                        print("%s by %s (%s, %s)" % (level_name, level_creator, level_code_prettify(level_code), level_clear_rate))
                    with open("./level_loves.txt", 'w', encoding='utf-8') as f:
                        f.write("赞: %d 孬: %d 玩: %d (%.2f%%) 作者通关: %s\nWR: %s(by %s)  对战游玩%d次  %s" %
                                (level_likes, level_boos, level_plays, level_likes / level_plays * 100.0, time_clear,
                                 time_clear_wr, wr_holder, in_versus, diff_name))
                        print("赞: %d 孬: %d 玩: %d (%.2f%%) 作者通关: %s\nWR: %s(by %s)  对战游玩%d次  %s" %
                                (level_likes, level_boos, level_plays, level_likes / level_plays * 100.0, time_clear,
                                 time_clear_wr, wr_holder, in_versus, diff_name))
                    # if level_likes < level_boos or level_likes / level_plays < 0.12:
                    #     playsound("./sound/follow (%d).mp3" % random.randint(1, 4))
            else:
                detect_flag = 0
            # 检测死亡
            death_detect = detect_death(id2)
            start_over_det = detect_start_over(id2)
            if death_detect['max'] > LIMIT or start_over_det['max'] > 0.90:
                if detect_flag_d == 0:
                    death += 1
                    detect_flag_d = 1
                    await websocket.send(json.dumps({"type": "death", "message": death}))
                    with open("./death_count.txt", 'w', encoding='utf-8') as f:
                        f.write("Death: %d" % (death))
            else:
                detect_flag_d = 0
            # 检查对战输赢
            # 胜
            last_win_detection = win_detection
            win_detection = detect_you_win(id2)
            if not last_win_detection and win_detection:
                win += 1
                await websocket.send(json.dumps({"type": "win", "message": win}))
                logging.info("'You win' detected. WIN + 1")
                continue
            # 负
            last_lose_detection = lose_detection
            lose_detection = detect_you_lose(id2)
            if not last_lose_detection and lose_detection:
                lose += 1
                await websocket.send(json.dumps({"type": "lose", "message": lose}))
                logging.info("'You lose' detected. LOSE + 1")
                continue
            # 发消息
            last_message_from = message_from
            message_from = detect_message(id2)
            if message_from > 0:
                # cv2.imwrite("./temp_image/message_content.png", grayify(id2.getPart(127, 639, 230, 26)))
                last_msg_text = msg_text
                msg_text = detect_message_text(id2)
                if msg_text is not None and (last_message_from != message_from or last_msg_text != msg_text):
                    character = ""
                    if message_from == 1:  # 纯帅发消息
                        logging.info("Message from Mario: %s" % msg_text)
                        character = 'mario'
                    elif message_from == 2:  # 路易发消息
                        logging.info("Message from Luigi: %s" % msg_text)
                        character = 'luigi'
                    elif message_from == 3:  # 小蓝发消息
                        logging.info("Message from Toad: %s" % msg_text)
                        character = 'toad'
                    elif message_from == 4:  # 小坦发消息
                        logging.info("Message from Toadette: %s" % msg_text)
                        character = 'toadette'
                    sound_file = './sound/%s_%s.mp3' % (character, msg_text)
                    await websocket.send(json.dumps({"type": "message", "message": msg_text, "player": character}))
                    if os.path.exists(sound_file):
                        try:
                            playsound(sound_file)
                        except Exception as e:
                            logging.error(e.__str__())
                    continue
                elif msg_text is None:
                    logging.warning(('?', 'Mario', 'Luigi', 'Toad', 'Toadette')[message_from] + ' sent a message '
                                                                                                'but not identified. ')
        except websockets.ConnectionClosed:
            print("ConnectionClosed...", path) # 链接断开
            asyncio.get_event_loop().stop()
        except websockets.InvalidState:
            print("InvalidState...") # 无效状态
            asyncio.get_event_loop().stop()
        except Exception as e:
            print(e.__str__, 'in line ', e.__traceback__.tb_lineno)
            print(e)

print("Starting...")
start_server = websockets.serve(ws, '127.0.0.1', 8099) # 地址改为你自己的地址
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()