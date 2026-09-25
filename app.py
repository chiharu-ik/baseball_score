import streamlit as st
import sqlite3
from datetime import date

# =========================================================
# 基本設定
# =========================================================

st.set_page_config(
    page_title="Circle Baseball",
    page_icon="⚾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DB = "baseball.db"
conn = sqlite3.connect(DB, check_same_thread=False)
conn.row_factory = sqlite3.Row
c = conn.cursor()


# =========================================================
# DB
# =========================================================

c.executescript("""
CREATE TABLE IF NOT EXISTS players(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    number TEXT,
    active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS places(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS games(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_date TEXT NOT NULL,
    opponent TEXT NOT NULL,
    place TEXT,
    game_type TEXT,
    tournament TEXT,
    bat_first INTEGER,
    our_score INTEGER DEFAULT 0,
    their_score INTEGER DEFAULT 0,
    status TEXT DEFAULT 'playing'
);

CREATE TABLE IF NOT EXISTS lineup(
    game_id INTEGER,
    slot INTEGER,
    player_id INTEGER,
    PRIMARY KEY(game_id,slot)
);

CREATE TABLE IF NOT EXISTS batting(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    player_id INTEGER,
    inning INTEGER,
    result TEXT,
    field TEXT,
    batted_type TEXT,
    hit_type TEXT
);

CREATE TABLE IF NOT EXISTS pitching(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    pitcher_id INTEGER,
    inning INTEGER,
    result TEXT,
    runs INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS inning_scores(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    inning INTEGER,
    side TEXT,
    runs INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS substitutions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    inning INTEGER,
    substitution_type TEXT,
    old_player_id INTEGER,
    new_player_id INTEGER
);
""")

conn.commit()


# =========================================================
# スマホUI
# =========================================================

st.markdown("""
<style>

/* 全体 */
.block-container {
    max-width: 520px;
    padding-top: 0.7rem;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
    padding-bottom: 4rem;
}

h1 {
    font-size: 1.55rem !important;
    margin-bottom: 0.6rem !important;
}

h2 {
    font-size: 1.30rem !important;
}

h3 {
    font-size: 1.10rem !important;
}

/* ボタン */
.stButton > button {
    min-height: 46px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.95rem;
    width: 100%;
}

/* メトリック */
div[data-testid="stMetric"] {
    padding: 7px 8px;
    border: 1px solid rgba(128,128,128,.22);
    border-radius: 10px;
}

div[data-testid="stMetricLabel"] {
    font-size: 0.72rem;
}

div[data-testid="stMetricValue"] {
    font-size: 1.15rem;
}

/* スコア */
.scorebar {
    border: 1px solid rgba(128,128,128,.25);
    border-radius: 10px;
    padding: 7px 10px;
    margin-bottom: 10px;
    text-align: center;
}

.score-state {
    font-size: 0.78rem;
    opacity: 0.72;
    margin-bottom: 2px;
}

.score-main {
    font-size: 1.05rem;
    font-weight: 800;
}

/* 選手表示 */
.current-player {
    text-align: center;
    margin: 5px 0 8px 0;
}

.current-player .sub {
    font-size: 0.76rem;
    opacity: .65;
}

.current-player .name {
    font-size: 1.35rem;
    font-weight: 800;
}

/* 投手情報 */
.pitch-line {
    text-align:center;
    font-size:0.83rem;
    margin-top:-3px;
    margin-bottom:7px;
}

/* OUT */
.out-line {
    text-align:center;
    font-weight:700;
    font-size:0.85rem;
    margin-bottom:8px;
}

/* 成功表示 */
.flash {
    border-radius: 8px;
    padding: 7px 9px;
    margin-bottom: 8px;
    background: rgba(0,180,90,.10);
    border: 1px solid rgba(0,180,90,.28);
    font-size: 0.85rem;
    font-weight: 600;
}

/* ホームボタン */
.home-title {
    font-size:1.65rem;
    font-weight:800;
    margin-bottom:4px;
}

.home-sub {
    opacity:.65;
    font-size:.82rem;
    margin-bottom:16px;
}

/* 余白圧縮 */
hr {
    margin-top: 0.8rem !important;
    margin-bottom: 0.8rem !important;
}

div[data-testid="stRadio"] {
    margin-bottom: 0.2rem;
}

div[data-testid="stSelectbox"] {
    margin-bottom: 0.15rem;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 共通関数
# =========================================================

def get_players(active_only=True):
    if active_only:
        return c.execute(
            "SELECT * FROM players WHERE active=1 ORDER BY id"
        ).fetchall()

    return c.execute(
        "SELECT * FROM players ORDER BY id"
    ).fetchall()


def player_name(pid):
    row = c.execute(
        "SELECT name FROM players WHERE id=?",
        (pid,)
    ).fetchone()

    return row["name"] if row else "-"


def player_mapping():
    return {
        p["name"]: p["id"]
        for p in get_players()
    }


def active_game():
    return c.execute("""
        SELECT *
        FROM games
        WHERE status='playing'
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()


def lineup_for(game_id):
    return c.execute("""
        SELECT
            l.slot,
            l.player_id,
            p.name,
            p.number
        FROM lineup l
        JOIN players p
          ON p.id=l.player_id
        WHERE l.game_id=?
        ORDER BY l.slot
    """, (game_id,)).fetchall()


def fmt_avg(x):
    if not x:
        return ".000"

    return f"{x:.3f}".replace("0.", ".")


def add_place(name):
    name = name.strip()

    if not name:
        return

    try:
        c.execute(
            "INSERT INTO places(name) VALUES(?)",
            (name,)
        )
        conn.commit()

    except sqlite3.IntegrityError:
        pass


def flash(message):
    st.session_state.flash_message = message


def show_flash():
    message = st.session_state.pop(
        "flash_message",
        None
    )

    if message:
        st.markdown(
            f'<div class="flash">✓ {message}</div>',
            unsafe_allow_html=True
        )


# =========================================================
# フィルター
# =========================================================

def filter_sql(
    start=None,
    end=None,
    game_type="全試合",
    tournament="全大会",
    place="全場所"
):
    sql = ""
    args = []

    if start:
        sql += " AND g.game_date>=?"
        args.append(str(start))

    if end:
        sql += " AND g.game_date<=?"
        args.append(str(end))

    if game_type != "全試合":
        sql += " AND g.game_type=?"
        args.append(game_type)

    if tournament != "全大会":
        sql += " AND g.tournament=?"
        args.append(tournament)

    if place != "全場所":
        sql += " AND g.place=?"
        args.append(place)

    return sql, args


# =========================================================
# 打撃成績
# =========================================================

def batting_stats(
    pid=None,
    start=None,
    end=None,
    game_type="全試合",
    tournament="全大会",
    place="全場所",
    finished_only=True,
    game_id=None
):
    q = """
    SELECT b.result,b.hit_type
    FROM batting b
    JOIN games g ON g.id=b.game_id
    WHERE 1=1
    """

    args = []

    if finished_only:
        q += " AND g.status='finished'"

    if pid is not None:
        q += " AND b.player_id=?"
        args.append(pid)

    if game_id is not None:
        q += " AND b.game_id=?"
        args.append(game_id)

    extra, extra_args = filter_sql(
        start,
        end,
        game_type,
        tournament,
        place
    )

    q += extra
    args += extra_args

    rows = c.execute(q, args).fetchall()

    PA = len(rows)

    BB = sum(r["result"] == "四球" for r in rows)
    HBP = sum(r["result"] == "死球" for r in rows)
    SH = sum(r["result"] == "犠打" for r in rows)
    SF = sum(r["result"] == "犠飛" for r in rows)
    SO = sum(r["result"] == "三振" for r in rows)

    H = sum(r["result"] == "安打" for r in rows)

    doubles = sum(r["hit_type"] == "二塁打" for r in rows)
    triples = sum(r["hit_type"] == "三塁打" for r in rows)
    HR = sum(r["hit_type"] == "本塁打" for r in rows)

    singles = max(
        H - doubles - triples - HR,
        0
    )

    AB = PA - BB - HBP - SH - SF

    TB = (
        singles
        + doubles * 2
        + triples * 3
        + HR * 4
    )

    AVG = H / AB if AB else 0

    obp_den = AB + BB + HBP + SF

    OBP = (
        (H + BB + HBP) / obp_den
        if obp_den else 0
    )

    SLG = TB / AB if AB else 0

    return {
        "打席": PA,
        "打数": AB,
        "安打": H,
        "単打": singles,
        "二塁打": doubles,
        "三塁打": triples,
        "本塁打": HR,
        "四球": BB,
        "死球": HBP,
        "三振": SO,
        "犠打": SH,
        "犠飛": SF,
        "打率": AVG,
        "出塁率": OBP,
        "長打率": SLG,
        "OPS": OBP + SLG
    }


# =========================================================
# 投手成績
# =========================================================

def pitching_stats(
    pid=None,
    start=None,
    end=None,
    game_type="全試合",
    tournament="全大会",
    place="全場所",
    finished_only=True,
    game_id=None
):
    q = """
    SELECT p.result,p.runs
    FROM pitching p
    JOIN games g ON g.id=p.game_id
    WHERE 1=1
    """

    args = []

    if finished_only:
        q += " AND g.status='finished'"

    if pid is not None:
        q += " AND p.pitcher_id=?"
        args.append(pid)

    if game_id is not None:
        q += " AND p.game_id=?"
        args.append(game_id)

    extra, extra_args = filter_sql(
        start,
        end,
        game_type,
        tournament,
        place
    )

    q += extra
    args += extra_args

    rows = c.execute(q, args).fetchall()

    outs = sum(
        r["result"] in ["アウト", "三振"]
        for r in rows
    )

    hits = sum(
        r["result"] in [
            "安打",
            "二塁打",
            "三塁打",
            "本塁打"
        ]
        for r in rows
    )

    strikeouts = sum(
        r["result"] == "三振"
        for r in rows
    )

    walks = sum(
        r["result"] == "四球"
        for r in rows
    )

    hbp = sum(
        r["result"] == "死球"
        for r in rows
    )

    hr = sum(
        r["result"] == "本塁打"
        for r in rows
    )

    runs = sum(
        r["runs"] or 0
        for r in rows
    )

    innings_decimal = outs / 3

    inning_display = (
        f"{outs // 3}.{outs % 3}"
    )

    RA9 = (
        runs * 9 / innings_decimal
        if innings_decimal else 0
    )

    WHIP = (
        (hits + walks) / innings_decimal
        if innings_decimal else 0
    )

    K9 = (
        strikeouts * 9 / innings_decimal
        if innings_decimal else 0
    )

    return {
        "対戦打者": len(rows),
        "アウト数": outs,
        "投球回": inning_display,
        "被安打": hits,
        "被本塁打": hr,
        "奪三振": strikeouts,
        "与四球": walks,
        "与死球": hbp,
        "失点": runs,
        "失点率": RA9,
        "WHIP": WHIP,
        "K/9": K9
    }


# =========================================================
# セッション
# =========================================================

defaults = {
    "page": "ホーム",
    "mode": None,
    "inning": 1,
    "batter_index": 0,
    "pitcher": None,
    "switch_open": False,
    "sub_open": False,
    "finish_open": False,
    "flash_message": None
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def go(page):
    st.session_state.page = page
    st.rerun()


# =========================================================
# ナビゲーション
# =========================================================

page = st.session_state.page

# ホーム以外は小さい戻るボタン
if page != "ホーム":
    if st.button("‹ ホーム", key="back_home"):
        go("ホーム")


# =========================================================
# ホーム
# =========================================================

if page == "ホーム":

    st.markdown(
        '<div class="home-title">⚾ Circle Baseball</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="home-sub">サークル用スコア・成績管理</div>',
        unsafe_allow_html=True
    )

    game = active_game()

    if game:
        st.info(
            f"試合中｜vs {game['opponent']}　"
            f"{game['our_score']} - {game['their_score']}"
        )

    if st.button(
        "⚾　スコア入力　›",
        use_container_width=True,
        type="primary"
    ):
        go("スコア入力")

    if st.button(
        "📊　成績確認　›",
        use_container_width=True
    ):
        go("成績確認")

    if st.button(
        "👥　選手登録　›",
        use_container_width=True
    ):
        go("選手登録")


# =========================================================
# 選手登録
# =========================================================

elif page == "選手登録":

    st.title("👥 選手登録")

    show_flash()

    with st.form("player_form"):

        col1, col2 = st.columns([2, 1])

        name = col1.text_input(
            "選手名"
        )

        number = col2.text_input(
            "背番号"
        )

        submit = st.form_submit_button(
            "登録",
            type="primary",
            use_container_width=True
        )

        if submit:

            if not name.strip():
                st.error("選手名を入力してください。")

            else:
                try:
                    c.execute("""
                    INSERT INTO players(name,number)
                    VALUES(?,?)
                    """, (
                        name.strip(),
                        number.strip()
                    ))

                    conn.commit()

                    flash(
                        f"{name.strip()}を登録しました"
                    )

                    st.rerun()

                except sqlite3.IntegrityError:
                    st.error(
                        "同じ名前の選手がいます。"
                    )

    st.subheader("登録選手")

    for p in get_players(False):

        col1, col2 = st.columns(
            [4, 1]
        )

        status = "" if p["active"] else "（非表示）"

        col1.write(
            f"#{p['number'] or '-'}　"
            f"{p['name']} {status}"
        )

        if p["active"]:

            if col2.button(
                "削除",
                key=f"del_{p['id']}"
            ):
                c.execute(
                    "UPDATE players SET active=0 WHERE id=?",
                    (p["id"],)
                )

                conn.commit()
                flash(
                    f"{p['name']}を非表示にしました"
                )
                st.rerun()

        else:
            if col2.button(
                "復帰",
                key=f"restore_{p['id']}"
            ):
                c.execute(
                    "UPDATE players SET active=1 WHERE id=?",
                    (p["id"],)
                )

                conn.commit()
                flash(
                    f"{p['name']}を復帰しました"
                )
                st.rerun()


# =========================================================
# スコア入力
# =========================================================

elif page == "スコア入力":

    show_flash()

    game = active_game()

    # -----------------------------------------------------
    # 試合開始
    # -----------------------------------------------------

    if not game:

        st.title("⚾ 新しい試合")

        ps = get_players()

        if not ps:
            st.warning(
                "先に選手を登録してください。"
            )
            st.stop()

        gd = st.date_input(
            "試合日",
            date.today()
        )

        opponent = st.text_input(
            "対戦相手"
        )

        saved_places = [
            r["name"]
            for r in c.execute(
                "SELECT name FROM places ORDER BY name"
            ).fetchall()
        ]

        place_type = st.radio(
            "試合場所",
            ["登録済み", "新規"],
            horizontal=True
        )

        if place_type == "登録済み" and saved_places:
            place = st.selectbox(
                "場所",
                saved_places
            )
        else:
            place = st.text_input(
                "場所を入力"
            )

        col1, col2 = st.columns(2)

        game_type = col1.selectbox(
            "試合区分",
            ["公式戦", "練習試合"]
        )

        first = col2.selectbox(
            "先攻・後攻",
            ["先攻", "後攻"]
        )

        tournament = st.text_input(
            "大会名（任意）"
        )

        names = [p["name"] for p in ps]

        chosen = st.multiselect(
            "打順通りに選択",
            names
        )

        pitcher_name = st.selectbox(
            "先発投手",
            names
        )

        if chosen:
            st.caption(
                " ｜ ".join(
                    f"{i}.{n}"
                    for i, n in enumerate(
                        chosen,
                        1
                    )
                )
            )

        if st.button(
            "試合開始",
            type="primary",
            use_container_width=True
        ):

            if not opponent.strip():
                st.error(
                    "対戦相手を入力してください。"
                )

            elif not place.strip():
                st.error(
                    "試合場所を入力してください。"
                )

            elif not chosen:
                st.error(
                    "オーダーを選択してください。"
                )

            else:

                add_place(place)

                c.execute("""
                INSERT INTO games(
                    game_date,
                    opponent,
                    place,
                    game_type,
                    tournament,
                    bat_first
                )
                VALUES(?,?,?,?,?,?)
                """, (
                    str(gd),
                    opponent.strip(),
                    place.strip(),
                    game_type,
                    tournament.strip(),
                    1 if first == "先攻" else 0
                ))

                gid = c.lastrowid
                mapping = player_mapping()

                for slot, n in enumerate(
                    chosen,
                    1
                ):
                    c.execute("""
                    INSERT INTO lineup(
                        game_id,
                        slot,
                        player_id
                    )
                    VALUES(?,?,?)
                    """, (
                        gid,
                        slot,
                        mapping[n]
                    ))

                conn.commit()

                st.session_state.pitcher = (
                    mapping[pitcher_name]
                )

                st.session_state.mode = (
                    "攻撃"
                    if first == "先攻"
                    else "守備"
                )

                st.session_state.inning = 1
                st.session_state.batter_index = 0

                flash("試合を開始しました")
                st.rerun()

    # -----------------------------------------------------
    # 試合中
    # -----------------------------------------------------

    else:

        gid = game["id"]
        lineup = lineup_for(gid)

        if not lineup:
            st.error("オーダーがありません。")
            st.stop()

        if st.session_state.mode is None:
            st.session_state.mode = (
                "攻撃"
                if game["bat_first"]
                else "守備"
            )

        if st.session_state.pitcher is None:
            st.session_state.pitcher = (
                lineup[0]["player_id"]
            )

        mode = st.session_state.mode
        inning = st.session_state.inning

        if game["bat_first"]:
            half = (
                "表"
                if mode == "攻撃"
                else "裏"
            )
        else:
            half = (
                "表"
                if mode == "守備"
                else "裏"
            )

        # -------------------------------------------------
        # コンパクトスコア
        # -------------------------------------------------

        st.markdown(
            f"""
            <div class="scorebar">
                <div class="score-state">
                    {inning}回{half}｜{mode}中
                </div>
                <div class="score-main">
                    自チーム&nbsp;&nbsp;
                    {game['our_score']}
                    &nbsp;-&nbsp;
                    {game['their_score']}
                    &nbsp;&nbsp;{game['opponent']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # =================================================
        # 攻撃
        # =================================================

        if mode == "攻撃":

            idx = (
                st.session_state.batter_index
                % len(lineup)
            )

            batter = lineup[idx]

            today = batting_stats(
                pid=batter["player_id"],
                finished_only=False,
                game_id=gid
            )

            st.markdown(
                f"""
                <div class="current-player">
                    <div class="sub">
                    {batter['slot']}番｜
                    今日 {today['打数']}打数{today['安打']}安打
                    </div>
                    <div class="name">
                    {batter['name']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            result = st.radio(
                "結果",
                [
                    "安打",
                    "アウト",
                    "三振",
                    "四球",
                    "死球",
                    "犠打",
                    "犠飛"
                ],
                horizontal=True,
                label_visibility="collapsed"
            )

            field = ""
            batted_type = ""
            hit_type = ""

            if result in ["安打", "アウト"]:

                field = st.radio(
                    "飛んだ場所",
                    [
                        "投",
                        "捕",
                        "一",
                        "二",
                        "遊",
                        "三",
                        "左",
                        "中",
                        "右"
                    ],
                    horizontal=True
                )

                batted_type = st.radio(
                    "打球",
                    [
                        "ゴロ",
                        "ライナー",
                        "フライ",
                        "オーバー"
                    ],
                    horizontal=True
                )

            if result == "安打":

                hit_type = st.radio(
                    "安打の種類",
                    [
                        "単打",
                        "二塁打",
                        "三塁打",
                        "本塁打"
                    ],
                    horizontal=True
                )

            if st.button(
                "✓ 登録",
                type="primary",
                use_container_width=True,
                key="register_batting"
            ):

                c.execute("""
                INSERT INTO batting(
                    game_id,
                    player_id,
                    inning,
                    result,
                    field,
                    batted_type,
                    hit_type
                )
                VALUES(?,?,?,?,?,?,?)
                """, (
                    gid,
                    batter["player_id"],
                    inning,
                    result,
                    field,
                    batted_type,
                    hit_type
                ))

                conn.commit()

                if result == "安打":
                    detail = (
                        f"{field}{batted_type} "
                        f"{hit_type}"
                    )
                elif result == "アウト":
                    detail = (
                        f"{field}{batted_type}"
                    )
                else:
                    detail = result

                flash(
                    f"{batter['name']}："
                    f"{detail}を登録しました"
                )

                st.session_state.batter_index += 1
                st.rerun()

            # 直前取消
            last_bat = c.execute("""
            SELECT b.id,p.name,b.result
            FROM batting b
            JOIN players p ON p.id=b.player_id
            WHERE b.game_id=?
            ORDER BY b.id DESC
            LIMIT 1
            """, (gid,)).fetchone()

            if last_bat:
                with st.expander("直前の入力"):
                    st.caption(
                        f"{last_bat['name']}｜"
                        f"{last_bat['result']}"
                    )

                    if st.button(
                        "直前の打席を取り消す",
                        key="undo_bat"
                    ):
                        c.execute(
                            "DELETE FROM batting WHERE id=?",
                            (last_bat["id"],)
                        )
                        conn.commit()

                        st.session_state.batter_index = max(
                            0,
                            st.session_state.batter_index - 1
                        )

                        flash(
                            "直前の打席を取り消しました"
                        )
                        st.rerun()

        # =================================================
        # 守備
        # =================================================

        else:

            pitcher_id = st.session_state.pitcher

            current = pitching_stats(
                pid=pitcher_id,
                finished_only=False,
                game_id=gid
            )

            outs_this_half = c.execute("""
            SELECT COUNT(*) AS n
            FROM pitching
            WHERE game_id=?
              AND inning=?
              AND pitcher_id IS NOT NULL
              AND result IN ('アウト','三振')
            """, (
                gid,
                inning
            )).fetchone()["n"]

            # 複数投手でもその回全体のアウトを数える
            outs_this_half = c.execute("""
            SELECT COUNT(*) AS n
            FROM pitching
            WHERE game_id=?
              AND inning=?
              AND result IN ('アウト','三振')
            """, (
                gid,
                inning
            )).fetchone()["n"]

            outs_display = min(
                outs_this_half,
                3
            )

            dots = (
                "● " * outs_display
                + "○ " * (3 - outs_display)
            )

            st.markdown(
                f"""
                <div class="current-player">
                    <div class="sub">投手</div>
                    <div class="name">
                    {player_name(pitcher_id)}
                    </div>
                </div>

                <div class="pitch-line">
                {current['投球回']}回｜
                H {current['被安打']}｜
                K {current['奪三振']}｜
                BB {current['与四球']}｜
                R {current['失点']}
                </div>

                <div class="out-line">
                OUT&nbsp;&nbsp;{dots}
                </div>
                """,
                unsafe_allow_html=True
            )

            if outs_this_half >= 3:

                st.success(
                    "⚾ 3アウトです。攻守交替してください。"
                )

            else:

                pitch_result = st.radio(
                    "相手打者",
                    [
                        "アウト",
                        "三振",
                        "安打",
                        "二塁打",
                        "三塁打",
                        "本塁打",
                        "四球",
                        "死球",
                        "失策"
                    ],
                    horizontal=True,
                    label_visibility="collapsed"
                )

                runs = st.number_input(
                    "このプレーの失点",
                    min_value=0,
                    max_value=4,
                    value=0,
                    step=1
                )

                if st.button(
                    "✓ 登録",
                    type="primary",
                    use_container_width=True,
                    key="register_pitching"
                ):

                    c.execute("""
                    INSERT INTO pitching(
                        game_id,
                        pitcher_id,
                        inning,
                        result,
                        runs
                    )
                    VALUES(?,?,?,?,?)
                    """, (
                        gid,
                        pitcher_id,
                        inning,
                        pitch_result,
                        runs
                    ))

                    conn.commit()

                    extra = (
                        f"・{runs}失点"
                        if runs else ""
                    )

                    flash(
                        f"{player_name(pitcher_id)}："
                        f"{pitch_result}{extra}を登録しました"
                    )

                    st.rerun()

            last_pitch = c.execute("""
            SELECT id,result,runs
            FROM pitching
            WHERE game_id=?
            ORDER BY id DESC
            LIMIT 1
            """, (gid,)).fetchone()

            if last_pitch:
                with st.expander("直前の入力"):
                    st.caption(
                        f"{last_pitch['result']}｜"
                        f"{last_pitch['runs']}失点"
                    )

                    if st.button(
                        "直前の投球結果を取り消す",
                        key="undo_pitch"
                    ):
                        c.execute(
                            "DELETE FROM pitching WHERE id=?",
                            (last_pitch["id"],)
                        )

                        conn.commit()

                        flash(
                            "直前の投球結果を取り消しました"
                        )

                        st.rerun()

        # =================================================
        # 試合操作
        # =================================================

        st.divider()

        col1, col2 = st.columns(2)

        if col1.button(
            "選手交代",
            use_container_width=True
        ):
            st.session_state.sub_open = (
                not st.session_state.sub_open
            )

        if col2.button(
            "攻守交替",
            use_container_width=True
        ):
            st.session_state.switch_open = (
                not st.session_state.switch_open
            )

        if st.button(
            "ゲームセット",
            use_container_width=True
        ):
            st.session_state.finish_open = True

        # =================================================
        # 選手交代
        # =================================================

        if st.session_state.sub_open:

            st.subheader("選手交代")

            sub_type = st.radio(
                "種類",
                ["代打", "投手交代"],
                horizontal=True
            )

            names = [
                p["name"]
                for p in get_players()
            ]

            mapping = player_mapping()

            if sub_type == "代打":

                lineup = lineup_for(gid)

                slot_labels = [
                    f"{x['slot']}番 {x['name']}"
                    for x in lineup
                ]

                selected_slot = st.selectbox(
                    "交代する選手",
                    slot_labels
                )

                slot_index = slot_labels.index(
                    selected_slot
                )

                old = lineup[slot_index]

                new_name = st.selectbox(
                    "代打",
                    names,
                    key="pinch_name"
                )

                if st.button(
                    "代打を確定",
                    type="primary"
                ):

                    new_id = mapping[new_name]

                    c.execute("""
                    INSERT INTO substitutions(
                        game_id,
                        inning,
                        substitution_type,
                        old_player_id,
                        new_player_id
                    )
                    VALUES(?,?,?,?,?)
                    """, (
                        gid,
                        inning,
                        "代打",
                        old["player_id"],
                        new_id
                    ))

                    c.execute("""
                    UPDATE lineup
                    SET player_id=?
                    WHERE game_id=?
                      AND slot=?
                    """, (
                        new_id,
                        gid,
                        old["slot"]
                    ))

                    conn.commit()

                    st.session_state.sub_open = False

                    flash(
                        f"{old['name']} → "
                        f"{new_name} に交代しました"
                    )

                    st.rerun()

            else:

                new_name = st.selectbox(
                    "新しい投手",
                    names,
                    key="new_pitcher_name"
                )

                if st.button(
                    "投手交代を確定",
                    type="primary"
                ):

                    old_id = (
                        st.session_state.pitcher
                    )

                    new_id = mapping[new_name]

                    c.execute("""
                    INSERT INTO substitutions(
                        game_id,
                        inning,
                        substitution_type,
                        old_player_id,
                        new_player_id
                    )
                    VALUES(?,?,?,?,?)
                    """, (
                        gid,
                        inning,
                        "投手交代",
                        old_id,
                        new_id
                    ))

                    conn.commit()

                    old_name = player_name(
                        old_id
                    )

                    st.session_state.pitcher = (
                        new_id
                    )

                    st.session_state.sub_open = False

                    flash(
                        f"{old_name} → "
                        f"{new_name} に投手交代しました"
                    )

                    st.rerun()

        # =================================================
        # 攻守交替
        # =================================================

        if st.session_state.switch_open:

            st.subheader(
                f"{inning}回{half}の得点"
            )

            score = st.number_input(
                "得点",
                min_value=0,
                max_value=30,
                value=0,
                step=1,
                key="half_score"
            )

            if st.button(
                "得点を確定して交替",
                type="primary",
                use_container_width=True
            ):

                side = (
                    "our"
                    if mode == "攻撃"
                    else "their"
                )

                c.execute("""
                INSERT INTO inning_scores(
                    game_id,
                    inning,
                    side,
                    runs
                )
                VALUES(?,?,?,?)
                """, (
                    gid,
                    inning,
                    side,
                    score
                ))

                if mode == "攻撃":
                    c.execute("""
                    UPDATE games
                    SET our_score=our_score+?
                    WHERE id=?
                    """, (
                        score,
                        gid
                    ))
                else:
                    c.execute("""
                    UPDATE games
                    SET their_score=their_score+?
                    WHERE id=?
                    """, (
                        score,
                        gid
                    ))

                # 裏終了なら次の回
                if half == "裏":
                    st.session_state.inning += 1

                st.session_state.mode = (
                    "守備"
                    if mode == "攻撃"
                    else "攻撃"
                )

                conn.commit()

                st.session_state.switch_open = False

                flash(
                    f"{inning}回{half} "
                    f"{score}点で確定しました"
                )

                st.rerun()

        # =================================================
        # ゲームセット
        # =================================================

        if st.session_state.finish_open:

            st.warning(
                "この試合を終了しますか？"
            )

            col1, col2 = st.columns(2)

            if col1.button(
                "終了する",
                type="primary",
                use_container_width=True
            ):

                c.execute("""
                UPDATE games
                SET status='finished'
                WHERE id=?
                """, (gid,))

                conn.commit()

                for key in [
                    "mode",
                    "inning",
                    "batter_index",
                    "pitcher",
                    "switch_open",
                    "sub_open",
                    "finish_open"
                ]:
                    st.session_state[key] = defaults[key]

                flash("試合を保存しました")

                go("成績確認")

            if col2.button(
                "戻る",
                use_container_width=True
            ):
                st.session_state.finish_open = False
                st.rerun()


# =========================================================
# 成績確認
# =========================================================

elif page == "成績確認":

    st.title("📊 成績確認")

    show_flash()

    with st.expander(
        "絞り込み",
        expanded=False
    ):

        all_period = st.checkbox(
            "全期間",
            value=True
        )

        if all_period:
            start = None
            end = None
        else:
            col1, col2 = st.columns(2)

            start = col1.date_input(
                "開始日",
                key="filter_start"
            )

            end = col2.date_input(
                "終了日",
                key="filter_end"
            )

        game_type = st.selectbox(
            "試合区分",
            [
                "全試合",
                "公式戦",
                "練習試合"
            ]
        )

        tournaments = [
            r["tournament"]
            for r in c.execute("""
            SELECT DISTINCT tournament
            FROM games
            WHERE tournament<>''
            ORDER BY tournament
            """).fetchall()
        ]

        tournament = st.selectbox(
            "大会",
            ["全大会"] + tournaments
        )

        places = [
            r["place"]
            for r in c.execute("""
            SELECT DISTINCT place
            FROM games
            WHERE place<>''
            ORDER BY place
            """).fetchall()
        ]

        place = st.selectbox(
            "試合場所",
            ["全場所"] + places
        )

    tab1, tab2, tab3 = st.tabs([
        "個人成績",
        "ランキング",
        "チーム成績"
    ])

    # =====================================================
    # 個人成績
    # =====================================================

    with tab1:

        ps = get_players(False)

        if not ps:
            st.info(
                "選手が登録されていません。"
            )

        else:

            names = [
                p["name"]
                for p in ps
            ]

            who = st.selectbox(
                "選手",
                names
            )

            pid = {
                p["name"]: p["id"]
                for p in ps
            }[who]

            bat_tab, pitch_tab = st.tabs([
                "打撃",
                "投手"
            ])

            with bat_tab:

                d = batting_stats(
                    pid,
                    start,
                    end,
                    game_type,
                    tournament,
                    place
                )

                a, b, cc = st.columns(3)

                a.metric(
                    "打率",
                    fmt_avg(d["打率"])
                )

                b.metric(
                    "安打",
                    d["安打"]
                )

                cc.metric(
                    "OPS",
                    fmt_avg(d["OPS"])
                )

                st.write(
                    f"""
                    打席 **{d['打席']}** ｜ 
                    打数 **{d['打数']}** ｜ 
                    HR **{d['本塁打']}**

                    2B **{d['二塁打']}** ｜ 
                    3B **{d['三塁打']}** ｜ 
                    BB **{d['四球']}** ｜ 
                    K **{d['三振']}**

                    出塁率 **{fmt_avg(d['出塁率'])}** ｜ 
                    長打率 **{fmt_avg(d['長打率'])}**
                    """
                )

            with pitch_tab:

                d = pitching_stats(
                    pid,
                    start,
                    end,
                    game_type,
                    tournament,
                    place
                )

                a, b, cc = st.columns(3)

                a.metric(
                    "投球回",
                    d["投球回"]
                )

                b.metric(
                    "奪三振",
                    d["奪三振"]
                )

                cc.metric(
                    "失点率",
                    f"{d['失点率']:.2f}"
                )

                st.write(
                    f"""
                    被安打 **{d['被安打']}** ｜ 
                    HR **{d['被本塁打']}** ｜ 
                    BB **{d['与四球']}**

                    失点 **{d['失点']}** ｜ 
                    WHIP **{d['WHIP']:.2f}** ｜ 
                    K/9 **{d['K/9']:.2f}**
                    """
                )

                st.caption(
                    "自責点判定に必要な走者・失策状況を"
                    "管理していないため、失点率を表示。"
                )

    # =====================================================
    # ランキング
    # =====================================================

    with tab2:

        rank_type = st.radio(
            "種類",
            ["打撃", "投手"],
            horizontal=True
        )

        rows = []

        if rank_type == "打撃":

            metric = st.selectbox(
                "部門",
                [
                    "打率",
                    "安打",
                    "本塁打",
                    "二塁打",
                    "三塁打",
                    "出塁率",
                    "長打率",
                    "OPS",
                    "四球",
                    "三振"
                ]
            )

            for p in get_players(False):

                d = batting_stats(
                    p["id"],
                    start,
                    end,
                    game_type,
                    tournament,
                    place
                )

                if d["打席"] > 0:
                    rows.append(
                        (
                            p["name"],
                            d[metric]
                        )
                    )

            rows.sort(
                key=lambda x: x[1],
                reverse=True
            )

            for i, (name, value) in enumerate(
                rows,
                1
            ):
                if metric in [
                    "打率",
                    "出塁率",
                    "長打率",
                    "OPS"
                ]:
                    value = fmt_avg(value)

                st.write(
                    f"**{i}位**　{name}　{value}"
                )

        else:

            metric = st.selectbox(
                "部門",
                [
                    "失点率",
                    "奪三振",
                    "投球回",
                    "WHIP",
                    "K/9",
                    "与四球"
                ]
            )

            for p in get_players(False):

                d = pitching_stats(
                    p["id"],
                    start,
                    end,
                    game_type,
                    tournament,
                    place
                )

                if d["対戦打者"] == 0:
                    continue

                if metric == "投球回":
                    value = d["アウト数"]
                    display = d["投球回"]
                else:
                    value = d[metric]

                    display = (
                        f"{value:.2f}"
                        if metric in [
                            "失点率",
                            "WHIP",
                            "K/9"
                        ]
                        else str(value)
                    )

                rows.append(
                    (
                        p["name"],
                        value,
                        display
                    )
                )

            ascending = metric in [
                "失点率",
                "WHIP",
                "与四球"
            ]

            rows.sort(
                key=lambda x: x[1],
                reverse=not ascending
            )

            for i, (
                name,
                value,
                display
            ) in enumerate(
                rows,
                1
            ):
                st.write(
                    f"**{i}位**　{name}　{display}"
                )

    # =====================================================
    # チーム成績
    # =====================================================

    with tab3:

        q = """
        SELECT *
        FROM games g
        WHERE status='finished'
        """

        args = []

        extra, extra_args = filter_sql(
            start,
            end,
            game_type,
            tournament,
            place
        )

        q += extra
        args += extra_args

        q += " ORDER BY game_date DESC,id DESC"

        games = c.execute(
            q,
            args
        ).fetchall()

        wins = sum(
            g["our_score"] > g["their_score"]
            for g in games
        )

        losses = sum(
            g["our_score"] < g["their_score"]
            for g in games
        )

        draws = (
            len(games)
            - wins
            - losses
        )

        a, b = st.columns(2)

        a.metric(
            "試合数",
            len(games)
        )

        b.metric(
            "戦績",
            f"{wins}勝 {losses}敗 {draws}分"
        )

        team = batting_stats(
            None,
            start,
            end,
            game_type,
            tournament,
            place
        )

        a, b, cc = st.columns(3)

        a.metric(
            "チーム打率",
            fmt_avg(team["打率"])
        )

        b.metric(
            "得点",
            sum(
                g["our_score"]
                for g in games
            )
        )

        cc.metric(
            "失点",
            sum(
                g["their_score"]
                for g in games
            )
        )

        st.subheader("試合")

        for g in games:

            if g["our_score"] > g["their_score"]:
                mark = "○"
            elif g["our_score"] < g["their_score"]:
                mark = "●"
            else:
                mark = "△"

            with st.expander(
                f"{g['game_date']} "
                f"{mark} {g['opponent']} "
                f"{g['our_score']}-{g['their_score']}"
            ):

                st.caption(
                    f"{g['game_type']}｜"
                    f"{g['place']}"
                )

                if g["tournament"]:
                    st.caption(
                        g["tournament"]
                    )

                scores = c.execute("""
                SELECT inning,side,runs
                FROM inning_scores
                WHERE game_id=?
                ORDER BY inning,id
                """, (g["id"],)).fetchall()

                if scores:
                    st.write("**イニング別得点**")

                    for x in scores:
                        label = (
                            "自"
                            if x["side"] == "our"
                            else "相"
                        )

                        st.write(
                            f"{x['inning']}回 "
                            f"{label}：{x['runs']}点"
                        )

                batters = c.execute("""
                SELECT DISTINCT
                    b.player_id,
                    p.name
                FROM batting b
                JOIN players p
                  ON p.id=b.player_id
                WHERE b.game_id=?
                """, (g["id"],)).fetchall()

                if batters:

                    st.write("**打撃**")

                    for batter in batters:

                        d = batting_stats(
                            pid=batter["player_id"],
                            finished_only=False,
                            game_id=g["id"]
                        )

                        st.write(
                            f"{batter['name']}　"
                            f"{d['打数']}打数"
                            f"{d['安打']}安打"
                        )

                pitchers = c.execute("""
                SELECT DISTINCT
                    p.pitcher_id,
                    pl.name
                FROM pitching p
                JOIN players pl
                  ON pl.id=p.pitcher_id
                WHERE p.game_id=?
                """, (g["id"],)).fetchall()

                if pitchers:

                    st.write("**投手**")

                    for pitcher in pitchers:

                        d = pitching_stats(
                            pid=pitcher["pitcher_id"],
                            finished_only=False,
                            game_id=g["id"]
                        )

                        st.write(
                            f"{pitcher['name']}　"
                            f"{d['投球回']}回 "
                            f"H{d['被安打']} "
                            f"K{d['奪三振']} "
                            f"BB{d['与四球']} "
                            f"R{d['失点']}"
                        )
