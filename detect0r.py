# -*- coding=utf-8 -*-
import logging
import json
import re
import time

import pytesseract
from PIL import Image
import cv2
import os.path

SAVE_FILE = './result.json'
OBS_PRINT_FILE = './obs_print.txt'
LIMIT = 0.81

def identify_vs_rating(file):
    text = pytesseract.image_to_string(Image.open(file), lang='eng')
    return text

def detect_you_win(id2):
    r = id2.findPicture('./sub_image/you_win.png')
    if r['max'] > LIMIT:
        logging.debug("'You win' detected. ")
        return True
    return False


def detect_you_lose(id2):
    r = id2.findPicture('./sub_image/you_lose.png')
    if r['max'] > LIMIT:
        logging.debug("'You lose' detected. ")
        return True
    return False

def detect_boo(id2):
    if id2.getGrayColor(497, 397) > 225 or id2.getGrayColor(693, 406) > 225 or id2.getGrayColor(897, 397) > 225:
        return 'no'
    r = id2.findPicture('./sub_image/boo.png', dontgetgray=True, part=[337, 289, 615, 200])
    if r['max'] > 0.95:
        logging.debug("Boo detected.")
        return 'boo'
    r = id2.findPicture('./sub_image/like.png', dontgetgray=True, part=[337, 289, 615, 200])
    if r['max'] > 0.95:
        logging.debug("Like detected.")
        return 'like'
    r = id2.findPicture('./sub_image/meh.png', dontgetgray=True, part=[337, 289, 615, 200])
    if r['max'] > 0.95:
        logging.debug("Meh detected.")
        return 'meh'
    return 'no'



def grayify(pic):
    pic_gray = 0.2126 * pic[:, :, 2] + 0.7152 * pic[:, :, 1] + 0.0722 * pic[:, :, 0]
    return pic_gray


def binarify(pic, limit=128):  # 二值化
    pic_gray = 0.2126 * pic[:, :, 2] + 0.7152 * pic[:, :, 1] + 0.0722 * pic[:, :, 0]
    pic_gray[pic_gray >= limit] = 255
    pic_gray[pic_gray < limit] = 0
    return pic_gray

def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]+"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "", title)  # 替换为下划线
    rstr = r"\s+"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", new_title)  # 替换为下划线
    return new_title

def detect_level_name(img):
    try:
        img_gray = 0.2126*img[:,:,2] + 0.7152*img[:,:,1] + 0.0722*img[:,:,0]
        # cv2.imwrite('./temp_image/sss1.png', img_gray)
        img_gray[img_gray>=210] = 255
        img_gray[img_gray<210] = 0
        img_gray = 255 - img_gray
        # cv2.imwrite('./temp_image/sss.png', img_gray)
        return pytesseract.image_to_string(img_gray, lang="eng+chi_sim+jpn", timeout=2, config="--psm 6")
    except Exception:
        return 'unknown'


def detect_vs_rating(id2):
    r = id2.findPicture('./sub_image/versus_rating.png')
    if r['max'] > LIMIT:
        logging.debug("'VS-rating' detected. ")
        v_rating = id2.getPart(607, 373, 65, 27)
        v_rating_gray = 0.2126*v_rating[:,:,2] + 0.7152*v_rating[:,:,1] + 0.0722*v_rating[:,:,0]
        v_rating_gray[v_rating_gray>=128] = 255
        v_rating_gray[v_rating_gray<128] = 0
        v_rating_gray = 255 - v_rating_gray
        # print(v_rating)
        cv2.imwrite('./debug/v_rating_img.png', v_rating_gray)
        return identify_vs_rating('./debug/v_rating_img.png')
    return False


def write_to_json(win, lose, rating, delta, streak, win_streak):
    global SAVE_FILE, OBS_PRINT_FILE
    delta_str = ("+" if delta >= 0 else "") + "%d" % delta
    with open(SAVE_FILE, 'w') as json_file:
        json.dump({"win": win, "lose": lose, "rating": rating}, json_file)
    with open(OBS_PRINT_FILE, 'w', encoding='utf-8') as f:
        f.write("胜: %d; 负: %d; 胜率: %.2f%%; 当前分数: %s(%s) " % (win, lose, win / (win + lose) * 100.0 if win + lose > 0 else "--.--", rating, delta_str))
        if streak > 1:
            f.write("%d 连%s" % (streak, '胜' if win_streak else '负'))

def detect_message(id2):
    r = id2.findPicture('./sub_image/new_msg_from_mario.png', part=[31, 633, 40, 40])  # 纯帅
    if r['max'] > LIMIT:
        return 1
    r = id2.findPicture('./sub_image/new_msg_from_luigi.png', part=[31, 633, 40, 40])  # 路易
    if r['max'] > LIMIT:
        return 2
    r = id2.findPicture('./sub_image/new_msg_from_toad.png', True, part=[31, 633, 40, 40])  # 大聪明
    if r['max'] > LIMIT:
        return 3
    r = id2.findPicture('./sub_image/new_msg_from_toadette.png', True, part=[31, 633, 40, 40])  # 小坦
    if r['max'] > LIMIT:
        return 4
    return 0


def detect_message_text(id2):
    message_list = ["thanks", "here_we_go", "nice_work", "im_done_for", "sorry", "no_worries", "nice", "how", "gotcha",
                    "so_tough", "oops", "wahoo", "oh_no", "weve_got_this", "teamwork", "follow_me", "help", "run_for_it",
                    "jump", "hop_on", "throw"]
    lang_list = ('eng', 'chi')
    for lang in lang_list:
        for msg in message_list:
            try:
                if os.path.exists('./sub_image/msg_%s_%s.png' % (msg, lang)):
                    r = id2.findPicture('./sub_image/msg_%s_%s.png' % (msg, lang), part=[127, 639, 230, 26])
                    if r['max'] > LIMIT:
                        return msg
            except Exception as e:
                logging.error(e.__str__)
    # return "wahoo"
    cv2.imwrite("./debug/unidentified-%d.png" % time.time(), grayify(id2.getPart(127, 639, 230, 26)))
    return None
