import asyncio, math, os, struct, subprocess, tempfile, wave
import edge_tts

VOICE_STORY = "zh-HK-HiuMaanNeural"
VOICE_QUIZ = "zh-HK-WanLungNeural"
VOICE_ENG = "en-GB-SoniaNeural"
RATE_HK = "-8%"
RATE_EN = "-15%"
OUT_DIR = "廣東話有聲書_MP3輸出"

SCRIPTS = {
    "01_中文_三上單元一_中華文化.mp3": [
        ("story", "各位小朋友好呀！歡迎嚟到我哋嘅廣東話有聲書小電台。今日曉曼姐姐同雲龍老師，會陪大家一齊溫習小三中文，單元一《中華文化》。", 0.7),
        ("story", "喺第一課《有趣的中國文字》入面講到，古人見到天上面圓碌碌嘅太陽，就畫出「日」字；見到彎彎嘅月亮，就畫出「月」字；見到高山同流水，就畫出「山」字同「水」字。呢啲照住實物畫公仔出嚟嘅字，就叫做「象形字」喇！", 0.8),
        ("quiz", "小朋友，輪到雲龍老師考考你喇！如果我要寫「晴天」個「晴」字，同埋「清潔」個「清」字，佢哋右邊都有個「青」字喎，點解左邊一個係「日」、一個係「三點水」呢？試下諗一諗啦！", 2.5),
        ("story", "好似我哋頭先觀察到，原來古人發明咗「形聲字」，將兩個拍檔合體！左邊嘅部首叫做「形旁」，負責講意思：例如「晴」有日字旁，代表好天氣；「清」有三點水，代表河水清澈；「蜻」有虫字旁，代表蜻蜓係昆蟲！右邊嘅「青」就叫做「聲旁」，負責提示讀音。記住口訣：「形旁睇意思，聲旁睇讀音」！", 0.8),
        ("story", "跟住睇埋第二課《中國人的姓》同埋《油炸鬼》。課文一開始就問：「為甚麼叫油炸鬼呢？原來這與宋朝奸臣秦檜有關。」", 0.7),
        ("quiz", "小朋友，作者明明心入面已經知道答案，點解仲要故意先問一句，然後自己即刻答返呢？呢種修辭手法叫咩名呢？", 2.5),
        ("story", "答啱喇！自己問、自己即刻答返，就叫做「設問」！最後記住：人名、地名、朝代名下底要畫一條直線嘅「專名號」；寫「直述句」時，句號一定要擺喺收引號入面呀！", 1.0),
    ],
    "02_中文_三上單元二_走進大自然.mp3": [
        ("story", "歡迎返嚟廣東話有聲書！上一單元我哋認識咗象形字同形聲字，今日曉曼姐姐帶大家去單元二《走進大自然》。", 0.7),
        ("story", "喺第三課《小螃蟹和浪花》入面，小螃蟹喺沙灘行路嗰陣「一搖一擺」，而海邊雪白嘅浪花就「一蹦一跳」跑上沙灘同小螃蟹玩捉迷藏！", 0.8),
        ("quiz", "小朋友，雲龍老師問下你：「螃蟹」有「虫」字部首，咁「珍珠」個「珠」字左邊係個「王」字，佢關唔關皇帝國王事呢？", 2.5),
        ("story", "其實左邊個「王」叫做「斜玉旁」，係美玉個「玉」字少咗一點，代表亮晶晶嘅玉石寶石（好似珍珠、玫瑰、碧綠），唔關國王事㗎！", 0.8),
        ("story", "跟住聽第四課新詩《瀑布》：遠望瀑布好似「一道白色的帶子」，近望水珠飛濺好似「一座珍珠的屏風」，一陣風吹過，水珠飛揚，「如煙，如霧，如塵」。將量詞重疊兩次，好似「朵朵白雲、陣陣清風、疊疊波浪」，就代表數量好多或者接連不斷喇！", 1.0),
    ],
    "03_中文_三上單元三_書信寄真情.mp3": [
        ("story", "各位小朋友好！今日我哋嚟到單元三《書信寄真情》。寫信俾親友有「書信格式六步曲」：第一稱謂語、第二問候語、第三正文、第四祝頌語、第五署名、第六日期！", 0.8),
        ("quiz", "小朋友，如果你寫信俾外公，喺信尾寫祝頌語嗰陣，可唔可以寫「祝你快高長大、學業進步」呢？對長輩應該寫咩祝頌語先啱禮貌呢？", 2.5),
        ("story", "哈哈，外公係大人長輩，唔使返學同快高長大喇！所以對長輩問候要用有心字底嘅「您好嗎？」，祝頌語要寫「祝 身體健康」；對同學同輩先至寫「祝 學業進步」！", 0.8),
        ("story", "仲要記實署名口訣：「開頭稱謂寫對方，結尾署名寫自己，最後一行寫日期」！喺《感謝林叔叔》入面，記住條件句式：「無論碰到多大的困難，我都要努力克服。」最後分清三個部首：細口旁同嘴巴有關；大四方框「囗部」（國、園、團、圍）代表包圍嘅範圍；言部就同說話有關！", 1.0),
    ],
    "04_中文_三上單元四_水的奇妙旅程.mp3": [
        ("story", "各位小朋友好！今日嚟到單元四《水的奇妙旅程》，跟住《小雨點旅行記》同《千變萬化的雲》去旅行！課文寫道：「天上的雲千變萬化，有時像軟綿綿的棉花糖，有時像溫馴的小綿羊，有時像奔馳的駿馬。」", 0.8),
        ("quiz", "小朋友，作者連用咗三句「有時像……」，排得好似操兵咁整齊，呢種修辭手法叫咩名呢？如果只寫兩句又算唔算數呀？", 2.5),
        ("story", "無錯，就叫做「排比」喇！記住排比一定要夠三句或以上結構相同嘅句子先算數！", 0.8),
        ("story", "跟住學埋動態助詞三寶「着、了、過」：「着」代表動作進行緊；「了」代表動作完成咗；「過」代表曾經試過。寫信封寄信時，中間一定要寫收信人真實全名加稱呼，而且「橫寫信封郵票貼右上角，直寫信封郵票貼左上角」！", 1.0),
    ],
    "05_中文_三上單元五_人間有情.mp3": [
        ("story", "歡迎返嚟廣東話有聲書！今日嚟到單元五《人間有情》，聽《交換》、《雪孩子》同《送暖二人組》嘅感人故事。《雪孩子》順住時間先後寫：兔媽媽堆雪人陪小白兔（起因），屋企失火雪孩子衝入屋救兔（經過），最後小白兔得救而雪孩子化作白雲（結果）。", 0.8),
        ("quiz", "小朋友，順住「起因、經過、結果」嘅時間先後次序講故事，喺中文入面叫咩記事手法呢？", 2.5),
        ("story", "就叫做「順敘法」喇！本單元仲有兩條黃金句式：第一條係轉折句「雖然外面的北風呼呼地吹，但是送暖二人組仍然堅持去探望獨居長者」；第二條係「經過他一番努力，屋子裏終於變暖和了」。最後用部首拆字法分清：用手「交換」係手部，用口大聲「呼喚」係口部！", 1.0),
    ],
    "06_中文_三上單元六_童年故事.mp3": [
        ("story", "各位小朋友好！今日我哋進入單元六《童年故事》，睇《慧娟怎樣長大》、《小凡請客》同《會走路的帽子》。課文有兩條必背排比句式：「慧娟不用穿媽媽的鞋，不用戴外婆的眼鏡，也不用披姐姐的圍巾。」同埋「小凡點了很多點心，有蝦餃，有蘿蔔糕，還有包子。」", 0.8),
        ("quiz", "小朋友，喺《會走路的帽子》入面，小男孩見到帽子識得自己行路，先大叫「咦？」，後來揭開見到小花貓，就話「噢！原來係小花貓！」呢啲擺喺句首嘅字叫咩詞呢？", 2.5),
        ("story", "呢啲擺喺句首表達語氣嘅字叫做「歎詞」：哇、啊代表驚喜讚嘆；咦代表奇怪疑問；噢代表恍然大悟；唉代表傷心嘆氣！另外記住「女」部多數係女性親屬，「心」部就同心情有關！", 1.0),
    ],
    "07_中文_三上單元七_成語園地.mp3": [
        ("story", "各位小朋友好！今日嚟到單元七《成語園地》，聽三個必考成語故事：《濫竽充數》、《自相矛盾》同《望梅止渴》！南郭先生唔識吹竽，卻混入三百人樂隊扮吹，新國王要逐個獨奏時佢就嚇到逃走，「濫竽充數」比喻無真才實學、混水摸魚充數！", 0.8),
        ("story", "而楚國人既話自己個盾乜嘢矛都刺唔穿，又話自己枝矛乜嘢盾都刺得穿，「自相矛盾」比喻說話或做事前後抵觸！至於曹操話前面有梅林令士兵流口水唔渴，「望梅止渴」就比喻用空想安慰自己。", 0.8),
        ("quiz", "小朋友，如果志明朝早話自己從來唔食甜嘢，下晝卻食咗一大塊朱古力蛋糕，應該話佢「濫竽充數」定係「自相矛盾」呢？", 2.5),
        ("story", "答案係「自相矛盾」！因為佢講嘢前後唔一致。最後記住「記敘六要素」：時間、地點、人物、起因、經過、結果！仲有「竽」係竹部，「刺」同「利」係刀部！", 1.0),
    ],
    "08_中文_三上單元八_神童小檔案.mp3": [
        ("story", "各位小朋友好！今日嚟到單元八《神童小檔案》，認識《文彥博灌水浮球》同《曹沖稱象》兩位古代小神童！皮球跌入深樹洞，文彥博叫大家灌水入樹洞令皮球浮上嚟；而七歲嘅曹沖就分三步「以石代象」：先趕象上船沿水面畫線，再趕象上岸裝石頭到同一條水位線，最後分批稱石頭加埋！", 0.8),
        ("quiz", "小朋友，如果我要將直述句「曹沖說：『我有辦法。』」改成複述句（轉述句），標點同埋「我」字要點樣變身呢？", 2.5),
        ("story", "記住兩步魔法：第一，刪走冒號同引號改成逗號；第二，將「我」改成「他」，變成「曹沖說，他有辦法。」最後記住：六點省略號「……」已經代表列舉未完，有省略號就千祈唔好再寫「等等」兩個字喇！", 1.0),
    ],
    "09_英文_Book3A_Ch1_School_Days.mp3": [
        ("story", "Hello 各位小朋友！歡迎嚟到英文科廣東話伴讀電台。今日我哋溫習 Book 3A Chapter 1，講返學嘅日子同每日習慣。講平時日日做嘅習慣，要用簡單現在式，常見嘅時間路標字有：", 0.5),
        ("eng", "every day, always, usually, often, sometimes, on Mondays.", 0.7),
        ("story", "而家請聽英國 Sonia 老師慢速讀出三句核心課文句子：", 0.5),
        ("eng", "Leo usually does his homework at five o'clock in the afternoon. Jenny practises the violin in the music room every Tuesday. My brother doesn't go to school by bus. He walks to school every day.", 0.8),
        ("quiz", "小朋友，記住「超人 S 口訣」，當主角係單數一個人嗰陣，動詞要加 s、es 或者 ies。但如果句首已經出現咗 Does 或者 doesn't，後面個動詞仲使唔使加 s 呀？", 2.5),
        ("story", "千祈唔使呀！記住「照妖鏡口訣」：見到 do、does、don't、doesn't，後面動詞即刻打回原形！例如：", 0.5),
        ("eng", "Does your father read newspapers in the morning?", 0.8),
        ("story", "最後造句時記實「四色積木造句法」：第一塊 Who 邊個，第二塊 Action 做咩動作，第三塊 Where 喺邊度，第四塊 When 幾時！就唔會寫出中式英文喇！", 1.0),
    ],
    "10_英文_Book3A_Ch2_Fun_Places_and_Rules.mp3": [
        ("story", "Hello 各位小朋友！今日我哋溫習 Book 3A Chapter 2，去公園同海灘玩，仲要學現在進行式！當見到呢幾個時間路標字，就代表動作而家呢一刻正在發生：", 0.5),
        ("eng", "Look! Listen! now, right now, at the moment.", 0.7),
        ("story", "請聽英國 Sonia 老師慢速讀出課文例句：", 0.5),
        ("eng", "Look! The children are making sandcastles on the beach right now. Listen! Mum is singing in the kitchen at the moment. Sam and his dog are running in the park now.", 0.8),
        ("quiz", "小朋友，寫現在進行式可唔可以淨係寫動詞 ing，漏咗前面嘅 am、is、are 呀？仲有 make 同 run 加 ing 要點變身呢？", 2.5),
        ("story", "記住「孖公仔口訣」：am、is、are 同動詞 ing 係孖公仔，永不分離！字尾有不發音 e 要踢走 e 加 ing（好似 making）；短母音加單子音要雙寫尾字母加 ing（好似 running）。最後記住場所標誌嘅「原形保護罩口訣」：喺 must、mustn't 同 Don't 後面，動詞永遠用原形！例如：", 0.5),
        ("eng", "You must keep quiet in the library. You mustn't climb the trees in the park. Don't walk on the grass!", 1.0),
    ],
}

def make_wav(path, duration_sec, is_chime=False):
    sr = 24000
    n = int(sr * duration_sec)
    buf = bytearray()
    if is_chime:
        for i in range(n):
            t = i / sr
            freq = 587.33 if t < 0.22 else 880.0
            lt = t if t < 0.22 else (t - 0.22)
            env = math.exp(-lt * 7.5)
            val = int(12000 * env * (0.7 * math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)))
            buf.extend(struct.pack("<h", max(-32767, min(32767, val))))
    else:
        buf.extend(b"\x00\x00" * n)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(bytes(buf))
    mp3_p = path.replace(".wav", ".mp3")
    subprocess.run(["ffmpeg", "-y", "-i", path, "-ar", "24000", "-ac", "1", "-b:a", "48k", mp3_p], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return mp3_p

async def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        chime_mp3 = make_wav(os.path.join(tmpdir, "chime.wav"), 0.65, True)
        pauses = {}
        for dur in [0.4, 0.5, 0.7, 0.8, 1.0, 2.5]:
            pauses[dur] = make_wav(os.path.join(tmpdir, f"p_{int(dur*10)}.wav"), dur, False)

        sem = asyncio.Semaphore(6)
        async def synth(role, text, out_p):
            async with sem:
                v = VOICE_ENG if role == "eng" else (VOICE_QUIZ if role == "quiz" else VOICE_STORY)
                r = RATE_EN if role == "eng" else RATE_HK
                await edge_tts.Communicate(text, v, rate=r).save(out_p)

        for fname, segs in SCRIPTS.items():
            tasks = []
            seg_files = []
            for idx, (role, text, pause_s) in enumerate(segs):
                sp = os.path.join(tmpdir, f"{fname}_{idx}.mp3")
                seg_files.append((role, sp, pause_s))
                tasks.append(synth(role, text, sp))
            await asyncio.gather(*tasks)

            lst_path = os.path.join(tmpdir, f"{fname}_list.txt")
            with open(lst_path, "w", encoding="utf-8") as lf:
                for role, sp, pause_s in seg_files:
                    if role == "quiz":
                        lf.write(f"file '{chime_mp3}'\nfile '{pauses[0.4]}'\n")
                    lf.write(f"file '{sp}'\nfile '{pauses[pause_s]}'\n")
            out_path = os.path.join(OUT_DIR, fname)
            subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst_path, "-ar", "24000", "-ac", "1", "-b:a", "64k", out_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    asyncio.run(main())
