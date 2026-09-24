import streamlit as st
import sqlite3
from datetime import date

# =========================================================
# 基本設定
# =========================================================

st.set_page_config(
    page_title="Circle Baseball Score",
    page_icon="⚾",
    layout="centered",
    initial_sidebar_state="expanded"
)

DB = "baseball.db"

conn = sqlite3.connect(DB, check_same_thread=False)
conn.row_factory = sqlite3.Row
c = conn.cursor()


# =========================================================
# データベース
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
    PRIMARY KEY(game_id, slot)
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
# CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 5rem;
    max-width: 850px;
}

div[data-testid="stMetric"] {
    border: 1px solid #e6e6e6;
    padding: 12px;
    border-radius: 12px;
}

.stButton button {
    border-radius: 10px;
    min-height: 44px;
}

.score-box {
    text-align: center;
    padding: 14px;
    border-radius: 14px;
    background: #f5f5f5;
    margin-bottom: 15px;
}

.player-box {
    padding: 14px;
    border: 1px solid #dddddd;
    border-radius: 12px;
    margin-bottom: 10px;
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


def get_player_name(player_id):
    row = c.execute(
        "SELECT name FROM players WHERE id=?",
        (player_id,)
    ).fetchone()

    return row["name"] if row else "-"


def player_map():
    return {
        row["name"]: row["id"]
        for row in get_players()
    }


def get_places():
    rows = c.execute(
        "SELECT name FROM places ORDER BY name"
    ).fetchall()

    return [r["name"] for r in rows]


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


def get_active_game():
    return c.execute("""
        SELECT *
        FROM games
        WHERE status='playing'
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()


def get_lineup(game_id):
    return c.execute("""
        SELECT
            l.slot,
            l.player_id,
            p.name,
            p.number
        FROM lineup l
        JOIN players p
        ON l.player_id=p.id
        WHERE l.game_id=?
        ORDER BY l.slot
    """, (game_id,)).fetchall()


def format_average(value):
    if value is None:
        return "---"

    if value == 0:
        return ".000"

    return f"{value:.3f}".replace("0.", ".")


# =========================================================
# フィルターSQL
# =========================================================

def game_filter_sql(
    start_date=None,
    end_date=None,
    game_type="全試合",
    tournament="全大会",
    place="全場所"
):

    sql = ""
    args = []

    if start_date:
        sql += " AND g.game_date>=?"
        args.append(str(start_date))

    if end_date:
        sql += " AND g.game_date<=?"
        args.append(str(end_date))

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
    player_id=None,
    start_date=None,
    end_date=None,
    game_type="全試合",
    tournament="全大会",
    place="全場所"
):

    q = """
        SELECT
            b.result,
            b.hit_type
        FROM batting b
        JOIN games g
        ON b.game_id=g.id
        WHERE g.status='finished'
    """

    args = []

    if player_id:
        q += " AND b.player_id=?"
        args.append(player_id)

    extra, extra_args = game_filter_sql(
        start_date,
        end_date,
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

    singles = H - doubles - triples - HR

    AB = PA - BB - HBP - SH - SF

    TB = (
        singles
        + doubles * 2
        + triples * 3
        + HR * 4
    )

    AVG = H / AB if AB else 0

    obp_denominator = AB + BB + HBP + SF

    OBP = (
        (H + BB + HBP) / obp_denominator
        if obp_denominator else 0
    )

    SLG = TB / AB if AB else 0

    OPS = OBP + SLG

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
        "OPS": OPS
    }


# =========================================================
# 投手成績
# =========================================================

def pitching_stats(
    player_id=None,
    start_date=None,
    end_date=None,
    game_type="全試合",
    tournament="全大会",
    place="全場所"
):

    q = """
        SELECT
            p.result,
            p.runs
        FROM pitching p
        JOIN games g
        ON p.game_id=g.id
        WHERE g.status='finished'
    """

    args = []

    if player_id:
        q += " AND p.pitcher_id=?"
        args.append(player_id)

    extra, extra_args = game_filter_sql(
        start_date,
        end_date,
        game_type,
        tournament,
        place
    )

    q += extra
    args += extra_args

    rows = c.execute(q, args).fetchall()

    batters = len(rows)

    strikeouts = sum(
        r["result"] == "三振"
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

    HR = sum(
        r["result"] == "本塁打"
        for r in rows
    )

    BB = sum(
        r["result"] == "四球"
        for r in rows
    )

    HBP = sum(
        r["result"] == "死球"
        for r in rows
    )

    runs = sum(r["runs"] for r in rows)

    outs = sum(
        r["result"] in [
            "アウト",
            "三振"
        ]
        for r in rows
    )

    full_innings = outs // 3
    remainder = outs % 3

    innings_display = f"{full_innings}.{remainder}"

    innings_decimal = outs / 3

    RA9 = (
        runs * 9 / innings_decimal
        if innings_decimal else 0
    )

    WHIP = (
        (BB + hits) / innings_decimal
        if innings_decimal else 0
    )

    K9 = (
        strikeouts * 9 / innings_decimal
        if innings_decimal else 0
    )

    BB9 = (
        BB * 9 / innings_decimal
        if innings_decimal else 0
    )

    return {
        "対戦打者": batters,
        "投球回": innings_display,
        "アウト数": outs,
        "被安打": hits,
        "被本塁打": HR,
        "奪三振": strikeouts,
        "与四球": BB,
        "与死球": HBP,
        "失点": runs,
        "失点率": RA9,
        "WHIP": WHIP,
        "K/9": K9,
        "BB/9": BB9
    }


# =========================================================
# セッション初期化
# =========================================================

defaults = {
    "mode": None,
    "inning": 1,
    "batter_index": 0,
    "pitcher": None,
    "switch_open": False,
    "sub_open": False,
    "finish_open": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# サイドバー
# =========================================================

st.sidebar.title("⚾ Baseball")

page = st.sidebar.radio(
    "メニュー",
    [
        "ホーム",
        "スコア入力",
        "成績確認",
        "選手登録"
    ]
)


# =========================================================
# ホーム
# =========================================================

if page == "ホーム":

    st.title("⚾ Circle Baseball Score")

    st.write(
        "サークルの試合記録・個人成績・ランキングを管理します。"
    )

    st.divider()

    active_game = get_active_game()

    if active_game:

        st.warning(
            f"試合中：vs {active_game['opponent']} "
            f"{active_game['our_score']} - "
            f"{active_game['their_score']}"
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### ⚾")
        st.markdown("**スコア入力**")
        st.caption("試合を記録")

    with col2:
        st.markdown("### 📊")
        st.markdown("**成績確認**")
        st.caption("成績・ランキング")

    with col3:
        st.markdown("### 👥")
        st.markdown("**選手登録**")
        st.caption("メンバー管理")


# =========================================================
# 選手登録
# =========================================================

elif page == "選手登録":

    st.title("👥 選手登録")

    with st.form("add_player"):

        name = st.text_input("選手名")

        number = st.text_input("背番号")

        submitted = st.form_submit_button(
            "選手を登録",
            type="primary"
        )

        if submitted:

            if not name.strip():
                st.error("選手名を入力してください。")

            else:

                try:

                    c.execute(
                        """
                        INSERT INTO players(name,number)
                        VALUES(?,?)
                        """,
                        (
                            name.strip(),
                            number.strip()
                        )
                    )

                    conn.commit()

                    st.success("登録しました。")

                    st.rerun()

                except sqlite3.IntegrityError:

                    st.error(
                        "同じ名前の選手が登録されています。"
                    )

    st.divider()

    st.subheader("登録選手")

    all_players = get_players(False)

    if not all_players:

        st.info("まだ選手が登録されていません。")

    for p in all_players:

        col1, col2, col3 = st.columns(
            [3, 1, 1]
        )

        col1.write(
            f"#{p['number'] or '-'}　{p['name']}"
        )

        if p["active"]:

            if col3.button(
                "削除",
                key=f"delete_{p['id']}"
            ):

                c.execute(
                    """
                    UPDATE players
                    SET active=0
                    WHERE id=?
                    """,
                    (p["id"],)
                )

                conn.commit()

                st.rerun()

        else:

            col2.caption("非表示")

            if col3.button(
                "復帰",
                key=f"restore_{p['id']}"
            ):

                c.execute(
                    """
                    UPDATE players
                    SET active=1
                    WHERE id=?
                    """,
                    (p["id"],)
                )

                conn.commit()

                st.rerun()


# =========================================================
# スコア入力
# =========================================================

elif page == "スコア入力":

    st.title("⚾ スコア入力")

    game = get_active_game()

    # -----------------------------------------------------
    # 新規試合
    # -----------------------------------------------------

    if not game:

        ps = get_players()

        if not ps:

            st.warning(
                "先に「選手登録」から選手を登録してください。"
            )

            st.stop()

        st.subheader("新しい試合")

        place_options = get_places()

        place_mode = st.radio(
            "試合場所",
            [
                "登録済みから選択",
                "新しい場所を入力"
            ],
            horizontal=True
        )

        selected_place = ""

        if place_mode == "登録済みから選択":

            if place_options:

                selected_place = st.selectbox(
                    "場所",
                    place_options
                )

            else:

                st.info(
                    "まだ試合場所が登録されていません。"
                )

        else:

            selected_place = st.text_input(
                "新しい試合場所"
            )

        gd = st.date_input(
            "試合日",
            date.today()
        )

        opponent = st.text_input(
            "対戦相手"
        )

        game_type = st.radio(
            "試合区分",
            [
                "公式戦",
                "練習試合"
            ],
            horizontal=True
        )

        tournament = st.text_input(
            "大会名（任意）"
        )

        first = st.radio(
            "先攻・後攻",
            [
                "先攻",
                "後攻"
            ],
            horizontal=True
        )

        st.divider()

        st.subheader("オーダー")

        names = [p["name"] for p in ps]

        chosen = st.multiselect(
            "出場選手を打順通りに選択",
            names
        )

        pitcher_name = st.selectbox(
            "先発投手",
            names
        )

        if chosen:

            st.caption("現在のオーダー")

            for i, n in enumerate(chosen, 1):
                st.write(f"{i}番　{n}")

        if st.button(
            "試合開始",
            type="primary",
            use_container_width=True
        ):

            if not opponent.strip():

                st.error(
                    "対戦相手を入力してください。"
                )

            elif not chosen:

                st.error(
                    "オーダーを選択してください。"
                )

            elif not selected_place.strip():

                st.error(
                    "試合場所を入力してください。"
                )

            else:

                add_place(selected_place)

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
                    selected_place.strip(),
                    game_type,
                    tournament.strip(),
                    1 if first == "先攻" else 0
                ))

                gid = c.lastrowid

                mapping = player_map()

                for slot, player_name in enumerate(
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
                        mapping[player_name]
                    ))

                conn.commit()

                st.session_state.pitcher = (
                    mapping[pitcher_name]
                )

                st.session_state.batter_index = 0

                st.session_state.inning = 1

                st.session_state.mode = (
                    "攻撃"
                    if first == "先攻"
                    else "守備"
                )

                st.rerun()

    # -----------------------------------------------------
    # 試合中
    # -----------------------------------------------------

    else:

        gid = game["id"]

        lineup = get_lineup(gid)

        if not lineup:

            st.error(
                "オーダーデータがありません。"
            )

            st.stop()

        # セッション復元
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

        # 表裏表示
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

        st.markdown(
            f"""
            <div class="score-box">
            <h3>vs {game['opponent']}</h3>
            <h1>
            {game['our_score']}
            -
            {game['their_score']}
            </h1>
            <b>
            {inning}回{half}
            ・{mode}中
            </b><br>
            {game['place']}
            </div>
            """,
            unsafe_allow_html=True
        )

        # =================================================
        # 攻撃
        # =================================================

        if mode == "攻撃":

            batter_index = (
                st.session_state.batter_index
                % len(lineup)
            )

            batter = lineup[batter_index]

            st.caption(
                f"{batter['slot']}番打者"
            )

            st.markdown(
                f"## 🥎 {batter['name']}"
            )

            result = st.radio(
                "打席結果",
                [
                    "安打",
                    "アウト",
                    "三振",
                    "四球",
                    "死球",
                    "犠打",
                    "犠飛"
                ],
                horizontal=True
            )

            field = ""
            batted_type = ""
            hit_type = ""

            if result in [
                "安打",
                "アウト"
            ]:

                st.write("#### 飛んだ場所")

                field = st.radio(
                    "守備位置",
                    [
                        "投",
                        "捕",
                        "一",
                        "二",
                        "三",
                        "遊",
                        "左",
                        "中",
                        "右"
                    ],
                    horizontal=True,
                    label_visibility="collapsed"
                )

                st.write("#### 打球")

                batted_type = st.radio(
                    "打球種類",
                    [
                        "ゴロ",
                        "ライナー",
                        "フライ",
                        "オーバー"
                    ],
                    horizontal=True,
                    label_visibility="collapsed"
                )

            if result == "安打":

                st.write("#### 安打の種類")

                hit_type = st.radio(
                    "安打種類",
                    [
                        "単打",
                        "二塁打",
                        "三塁打",
                        "本塁打"
                    ],
                    horizontal=True,
                    label_visibility="collapsed"
                )

            if st.button(
                "この打席を登録",
                type="primary",
                use_container_width=True
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

                st.session_state.batter_index += 1

                st.rerun()

        # =================================================
        # 守備
        # =================================================

        else:

            pitcher_id = (
                st.session_state.pitcher
            )

            st.caption("現在の投手")

            st.markdown(
                f"## ⚾ {get_player_name(pitcher_id)}"
            )

            pitch_result = st.radio(
                "相手打者の結果",
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
                horizontal=True
            )

            runs = st.number_input(
                "このプレーで入った得点",
                min_value=0,
                max_value=4,
                value=0,
                step=1
            )

            if st.button(
                "結果を登録",
                type="primary",
                use_container_width=True
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

                st.rerun()

        # =================================================
        # 試合操作
        # =================================================

        st.divider()

        col1, col2, col3 = st.columns(3)

        if col1.button(
            "🔄 選手交代",
            use_container_width=True
        ):

            st.session_state.sub_open = (
                not st.session_state.sub_open
            )

        if col2.button(
            "🔁 攻守交替",
            use_container_width=True
        ):

            st.session_state.switch_open = (
                not st.session_state.switch_open
            )

        if col3.button(
            "🏁 ゲームセット",
            use_container_width=True
        ):

            st.session_state.finish_open = True

        # =================================================
        # 選手交代
        # =================================================

        if st.session_state.sub_open:

            st.subheader("🔄 選手交代")

            substitution_type = st.radio(
                "交代の種類",
                [
                    "代打",
                    "投手交代"
                ],
                horizontal=True
            )

            ps = get_players()

            names = [
                p["name"]
                for p in ps
            ]

            mapping = player_map()

            if substitution_type == "代打":

                slots = [
                    f"{r['slot']}番 {r['name']}"
                    for r in lineup
                ]

                target = st.selectbox(
                    "交代する打順",
                    slots
                )

                target_index = slots.index(
                    target
                )

                target_row = lineup[
                    target_index
                ]

                new_name = st.selectbox(
                    "新しい選手",
                    names,
                    key="pinch_player"
                )

                if st.button(
                    "代打を確定"
                ):

                    new_id = mapping[
                        new_name
                    ]

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
                        target_row[
                            "player_id"
                        ],
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
                        target_row["slot"]
                    ))

                    conn.commit()

                    st.session_state.sub_open = False

                    st.rerun()

            else:

                new_name = st.selectbox(
                    "新しい投手",
                    names,
                    key="new_pitcher"
                )

                if st.button(
                    "投手交代を確定"
                ):

                    old_pitcher = (
                        st.session_state.pitcher
                    )

                    new_pitcher = (
                        mapping[new_name]
                    )

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
                        old_pitcher,
                        new_pitcher
                    ))

                    conn.commit()

                    st.session_state.pitcher = (
                        new_pitcher
                    )

                    st.session_state.sub_open = False

                    st.rerun()

        # =================================================
        # 攻守交替
        # =================================================

        if st.session_state.switch_open:

            st.subheader(
                f"{inning}回{half} 終了"
            )

            score = st.number_input(
                "この回の得点",
                min_value=0,
                max_value=30,
                value=0,
                step=1,
                key="inning_score_input"
            )

            if st.button(
                "得点を確定して攻守交替",
                type="primary"
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
                        SET our_score=
                        our_score+?
                        WHERE id=?
                    """, (
                        score,
                        gid
                    ))

                    st.session_state.mode = (
                        "守備"
                    )

                else:

                    c.execute("""
                        UPDATE games
                        SET their_score=
                        their_score+?
                        WHERE id=?
                    """, (
                        score,
                        gid
                    ))

                    st.session_state.mode = (
                        "攻撃"
                    )

                # 裏が終わったら次の回
                if half == "裏":

                    st.session_state.inning += 1

                conn.commit()

                st.session_state.switch_open = False

                st.rerun()

        # =================================================
        # ゲームセット
        # =================================================

        if st.session_state.finish_open:

            st.warning(
                "この試合を終了しますか？"
            )

            col_yes, col_no = st.columns(2)

            if col_yes.button(
                "ゲームセット",
                type="primary",
                use_container_width=True
            ):

                c.execute("""
                    UPDATE games
                    SET status='finished'
                    WHERE id=?
                """, (gid,))

                conn.commit()

                for key in defaults:

                    st.session_state[key] = (
                        defaults[key]
                    )

                st.success(
                    "試合を保存しました。"
                )

                st.rerun()

            if col_no.button(
                "キャンセル",
                use_container_width=True
            ):

                st.session_state.finish_open = False

                st.rerun()


# =========================================================
# 成績確認
# =========================================================

elif page == "成績確認":

    st.title("📊 成績確認")

    # -----------------------------------------------------
    # フィルター
    # -----------------------------------------------------

    with st.expander(
        "🔍 フィルター",
        expanded=True
    ):

        all_period = st.checkbox(
            "全期間",
            value=True
        )

        if not all_period:

            col1, col2 = st.columns(2)

            start_date = col1.date_input(
                "開始日"
            )

            end_date = col2.date_input(
                "終了日"
            )

        else:

            start_date = None
            end_date = None

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
                WHERE tournament IS NOT NULL
                AND tournament<>''
                ORDER BY tournament
            """).fetchall()
        ]

        tournament = st.selectbox(
            "大会",
            ["全大会"] + tournaments
        )

        locations = [
            r["place"]
            for r in c.execute("""
                SELECT DISTINCT place
                FROM games
                WHERE place IS NOT NULL
                AND place<>''
                ORDER BY place
            """).fetchall()
        ]

        selected_place = st.selectbox(
            "試合場所",
            ["全場所"] + locations
        )

    # -----------------------------------------------------
    # タブ
    # -----------------------------------------------------

    individual_tab, ranking_tab, team_tab = (
        st.tabs([
            "個人成績",
            "ランキング",
            "チーム成績"
        ])
    )

    # =====================================================
    # 個人成績
    # =====================================================

    with individual_tab:

        ps = get_players(False)

        if not ps:

            st.info(
                "選手が登録されていません。"
            )

        else:

            player_names = [
                p["name"]
                for p in ps
            ]

            selected_player = st.selectbox(
                "選手",
                player_names,
                key="individual_player"
            )

            selected_id = {
                p["name"]: p["id"]
                for p in ps
            }[selected_player]

            batting_tab, pitching_tab = (
                st.tabs([
                    "打撃成績",
                    "投手成績"
                ])
            )

            # ---------------------------------------------
            # 打撃
            # ---------------------------------------------

            with batting_tab:

                d = batting_stats(
                    selected_id,
                    start_date,
                    end_date,
                    game_type,
                    tournament,
                    selected_place
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "打率",
                    format_average(
                        d["打率"]
                    )
                )

                col2.metric(
                    "安打",
                    d["安打"]
                )

                col3.metric(
                    "OPS",
                    format_average(
                        d["OPS"]
                    )
                )

                st.divider()

                st.write(
                    f"""
                    **打席**　{d['打席']}  
                    **打数**　{d['打数']}  
                    **安打**　{d['安打']}  
                    **単打**　{d['単打']}  
                    **二塁打**　{d['二塁打']}  
                    **三塁打**　{d['三塁打']}  
                    **本塁打**　{d['本塁打']}  
                    **四球**　{d['四球']}  
                    **死球**　{d['死球']}  
                    **三振**　{d['三振']}  
                    **犠打**　{d['犠打']}  
                    **犠飛**　{d['犠飛']}  
                    **出塁率**　{format_average(d['出塁率'])}  
                    **長打率**　{format_average(d['長打率'])}  
                    """
                )

            # ---------------------------------------------
            # 投手
            # ---------------------------------------------

            with pitching_tab:

                p = pitching_stats(
                    selected_id,
                    start_date,
                    end_date,
                    game_type,
                    tournament,
                    selected_place
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "投球回",
                    p["投球回"]
                )

                col2.metric(
                    "奪三振",
                    p["奪三振"]
                )

                col3.metric(
                    "失点率",
                    f"{p['失点率']:.2f}"
                )

                st.divider()

                st.write(
                    f"""
                    **対戦打者**　{p['対戦打者']}  
                    **被安打**　{p['被安打']}  
                    **被本塁打**　{p['被本塁打']}  
                    **奪三振**　{p['奪三振']}  
                    **与四球**　{p['与四球']}  
                    **与死球**　{p['与死球']}  
                    **失点**　{p['失点']}  
                    **WHIP**　{p['WHIP']:.2f}  
                    **K/9**　{p['K/9']:.2f}  
                    **BB/9**　{p['BB/9']:.2f}  
                    """
                )

                st.caption(
                    "※走者・失策状況を記録していないため、"
                    "防御率ではなく失点率を表示しています。"
                )

    # =====================================================
    # ランキング
    # =====================================================

    with ranking_tab:

        ranking_type = st.radio(
            "ランキング",
            [
                "打撃",
                "投手"
            ],
            horizontal=True
        )

        if ranking_type == "打撃":

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

            ranking_rows = []

            for p in get_players(False):

                stats = batting_stats(
                    p["id"],
                    start_date,
                    end_date,
                    game_type,
                    tournament,
                    selected_place
                )

                # 打席0の選手はランキング除外
                if stats["打席"] == 0:
                    continue

                ranking_rows.append(
                    (
                        p["name"],
                        stats[metric]
                    )
                )

            ranking_rows.sort(
                key=lambda x: x[1],
                reverse=True
            )

            if not ranking_rows:

                st.info(
                    "該当する成績がありません。"
                )

            for rank, (
                name,
                value
            ) in enumerate(
                ranking_rows,
                1
            ):

                if metric in [
                    "打率",
                    "出塁率",
                    "長打率",
                    "OPS"
                ]:

                    display = (
                        format_average(value)
                    )

                else:

                    display = str(value)

                st.markdown(
                    f"### {rank}位　{name}　{display}"
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

            ranking_rows = []

            for p in get_players(False):

                stats = pitching_stats(
                    p["id"],
                    start_date,
                    end_date,
                    game_type,
                    tournament,
                    selected_place
                )

                if stats["対戦打者"] == 0:
                    continue

                if metric == "投球回":

                    sort_value = (
                        stats["アウト数"]
                    )

                    display_value = (
                        stats["投球回"]
                    )

                else:

                    sort_value = stats[
                        metric
                    ]

                    display_value = (
                        f"{sort_value:.2f}"
                        if metric in [
                            "失点率",
                            "WHIP",
                            "K/9"
                        ]
                        else str(
                            sort_value
                        )
                    )

                ranking_rows.append(
                    (
                        p["name"],
                        sort_value,
                        display_value
                    )
                )

            # 失点率・WHIP・与四球は少ない順
            ascending_metrics = [
                "失点率",
                "WHIP",
                "与四球"
            ]

            ranking_rows.sort(
                key=lambda x: x[1],
                reverse=(
                    metric
                    not in ascending_metrics
                )
            )

            if not ranking_rows:

                st.info(
                    "該当する成績がありません。"
                )

            for rank, (
                name,
                _,
                display
            ) in enumerate(
                ranking_rows,
                1
            ):

                st.markdown(
                    f"### {rank}位　{name}　{display}"
                )

    # =====================================================
    # チーム成績
    # =====================================================

    with team_tab:

        q = """
            SELECT *
            FROM games g
            WHERE g.status='finished'
        """

        args = []

        extra, extra_args = (
            game_filter_sql(
                start_date,
                end_date,
                game_type,
                tournament,
                selected_place
            )
        )

        q += extra
        args += extra_args

        q += " ORDER BY g.game_date DESC, g.id DESC"

        games = c.execute(
            q,
            args
        ).fetchall()

        total_games = len(games)

        wins = sum(
            g["our_score"]
            > g["their_score"]
            for g in games
        )

        losses = sum(
            g["our_score"]
            < g["their_score"]
            for g in games
        )

        draws = (
            total_games
            - wins
            - losses
        )

        win_rate = (
            wins
            / (wins + losses)
            if wins + losses
            else 0
        )

        total_runs = sum(
            g["our_score"]
            for g in games
        )

        total_allowed = sum(
            g["their_score"]
            for g in games
        )

        team_batting = batting_stats(
            None,
            start_date,
            end_date,
            game_type,
            tournament,
            selected_place
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "試合数",
            total_games
        )

        col2.metric(
            "勝敗",
            f"{wins}勝 {losses}敗 {draws}分"
        )

        col3.metric(
            "勝率",
            f"{win_rate:.3f}"
        )

        st.divider()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "総得点",
            total_runs
        )

        col2.metric(
            "総失点",
            total_allowed
        )

        col3.metric(
            "チーム打率",
            format_average(
                team_batting["打率"]
            )
        )

        st.divider()

        st.subheader("試合結果")

        if not games:

            st.info(
                "該当する試合がありません。"
            )

        for g in games:

            if g["our_score"] > g["their_score"]:

                result_mark = "○"

            elif g["our_score"] < g["their_score"]:

                result_mark = "●"

            else:

                result_mark = "△"

            with st.expander(
                f"{g['game_date']} "
                f"{result_mark} "
                f"vs {g['opponent']} "
                f"{g['our_score']} - "
                f"{g['their_score']}"
            ):

                st.write(
                    f"**場所：** {g['place']}"
                )

                st.write(
                    f"**試合区分：** "
                    f"{g['game_type']}"
                )

                if g["tournament"]:

                    st.write(
                        f"**大会：** "
                        f"{g['tournament']}"
                    )

                # イニングスコア
                innings = c.execute("""
                    SELECT *
                    FROM inning_scores
                    WHERE game_id=?
                    ORDER BY inning,id
                """, (g["id"],)).fetchall()

                if innings:

                    st.write(
                        "**イニング別得点**"
                    )

                    for score in innings:

                        team_label = (
                            "自チーム"
                            if score["side"]
                            == "our"
                            else "相手"
                        )

                        st.write(
                            f"{score['inning']}回 "
                            f"{team_label}："
                            f"{score['runs']}点"
                        )

                # 試合の打撃成績
                st.write(
                    "**打撃成績**"
                )

                game_batters = c.execute("""
                    SELECT DISTINCT
                        b.player_id,
                        p.name
                    FROM batting b
                    JOIN players p
                    ON b.player_id=p.id
                    WHERE b.game_id=?
                """, (g["id"],)).fetchall()

                for batter in game_batters:

                    rows = c.execute("""
                        SELECT result,hit_type
                        FROM batting
                        WHERE game_id=?
                        AND player_id=?
                    """, (
                        g["id"],
                        batter["player_id"]
                    )).fetchall()

                    PA = len(rows)

                    BB = sum(
                        r["result"] == "四球"
                        for r in rows
                    )

                    HBP = sum(
                        r["result"] == "死球"
                        for r in rows
                    )

                    SH = sum(
                        r["result"] == "犠打"
                        for r in rows
                    )

                    SF = sum(
                        r["result"] == "犠飛"
                        for r in rows
                    )

                    H = sum(
                        r["result"] == "安打"
                        for r in rows
                    )

                    AB = (
                        PA
                        - BB
                        - HBP
                        - SH
                        - SF
                    )

                    avg = (
                        H / AB
                        if AB else 0
                    )

                    st.write(
                        f"{batter['name']}　"
                        f"{AB}打数 "
                        f"{H}安打　"
                        f"{format_average(avg)}"
                    )
