import streamlit as st
from supabase import create_client
from datetime import date
import random


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Baseball Score",
    page_icon="⚾",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# SUPABASE
# =========================================================

try:
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
except Exception:
    st.error("Supabaseへの接続設定を確認してください。")
    st.stop()


# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "page": "ホーム",
    "team": None,
    "game_id": None,
    "switch_open": False,
    "sub_open": False,
    "finish_open": False,
    "flash_message": None,
    "created_team": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

/* ==============================
   BASE
============================== */

.stApp {
    background:
        radial-gradient(
            circle at 100% 0%,
            rgba(31, 95, 62, 0.08),
            transparent 28%
        ),
        #f5f7f5;
}

.block-container {
    max-width: 680px;
    padding-top: 2.8rem;
    padding-bottom: 5rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

h1, h2, h3 {
    letter-spacing: -0.04em;
}


/* ==============================
   BRAND
============================== */

.brand-wrap {
    padding: 1.1rem 0 1.6rem 0;
}

.brand {
    font-size: 1.9rem;
    font-weight: 900;
    color: #14241a;
    letter-spacing: -0.055em;
    line-height: 1.1;
}

.team-brand {
    font-size: 1.9rem;
    font-weight: 900;
    color: #14241a;
    letter-spacing: -0.055em;
}

.team-brand-sub {
    margin-top: .28rem;
    color: #828982;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .09em;
}


/* ==============================
   SECTION
============================== */

.section-title {
    margin-top: 1.35rem;
    margin-bottom: .55rem;
    color: #7a817b;
    font-size: .69rem;
    font-weight: 900;
    letter-spacing: .12em;
}

.small-muted {
    color: #7c847e;
    font-size: .76rem;
}


/* ==============================
   BUTTONS
============================== */

div.stButton > button {
    min-height: 50px;
    border-radius: 15px;
    border: 1px solid #e1e6e2;
    background: rgba(255,255,255,.96);
    color: #17251c;
    font-weight: 800;
    box-shadow: 0 3px 12px rgba(0,0,0,.025);
    transition: .15s ease;
}

div.stButton > button:hover {
    border-color: #1c6541;
    color: #17492f;
    transform: translateY(-1px);
}

div.stButton > button[kind="primary"] {
    background: #174d34;
    color: white;
    border: none;
    box-shadow: 0 6px 18px rgba(23,77,52,.15);
}


/* ==============================
   INPUT
============================== */

div[data-baseweb="input"] > div {
    border-radius: 14px;
}

div[data-baseweb="select"] > div {
    border-radius: 14px;
}

div[data-testid="stNumberInput"] input {
    text-align: center;
    font-weight: 850;
}


/* ==============================
   CARDS
============================== */

.app-card {
    background: rgba(255,255,255,.97);
    border: 1px solid #e4e8e5;
    border-radius: 20px;
    padding: 1rem;
    margin-bottom: .75rem;
    box-shadow:
        0 1px 2px rgba(0,0,0,.02),
        0 8px 25px rgba(0,0,0,.025);
}

.soft-card {
    background: #edf1ee;
    border: 1px solid #e3e8e4;
    border-radius: 17px;
    padding: .9rem 1rem;
    margin-bottom: .7rem;
}


/* ==============================
   TEAM CODE
============================== */

.code-card {
    background:
        linear-gradient(
            145deg,
            #17271d,
            #1c5138
        );
    border-radius: 22px;
    padding: 1.3rem 1rem;
    color: white;
    text-align: center;
    margin: .8rem 0;
    box-shadow: 0 10px 30px rgba(23,77,52,.17);
}

.code-label {
    color: #b9cbc0;
    font-size: .68rem;
    font-weight: 900;
    letter-spacing: .15em;
}

.code-value {
    margin-top: .3rem;
    font-size: 2rem;
    font-weight: 950;
    letter-spacing: .18em;
}

.code-team {
    margin-top: .7rem;
    color: #dce6e0;
    font-size: .8rem;
}


/* ==============================
   SUCCESS
============================== */

.success-card {
    background: #e7f6ed;
    border: 1px solid #b9dfc6;
    color: #145b34;
    border-radius: 17px;
    padding: .9rem 1rem;
    font-weight: 900;
    text-align: center;
    margin: .6rem 0 .9rem 0;
    animation: pop .25s ease-out;
}

@keyframes pop {
    0% {
        opacity: 0;
        transform: scale(.94);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}


/* ==============================
   SCORE
============================== */

.score-card {
    background:
        linear-gradient(
            145deg,
            #14251a,
            #1a3d2a
        );
    color: white;
    border-radius: 22px;
    padding: .95rem 1rem;
    margin: .4rem 0 .85rem 0;
    box-shadow: 0 10px 28px rgba(20,50,32,.16);
}

.score-top {
    text-align: center;
    color: #bfd0c5;
    font-size: .7rem;
    font-weight: 850;
    margin-bottom: .45rem;
}

.score-main {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: .45rem;
}

.score-team {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: .74rem;
    font-weight: 800;
}

.score-team.right {
    text-align: right;
}

.score-number {
    white-space: nowrap;
    font-size: 1.65rem;
    font-weight: 950;
    letter-spacing: .04em;
}


/* ==============================
   PLAYER
============================== */

.player-card {
    background: white;
    border: 1px solid #e3e8e4;
    border-radius: 18px;
    padding: .85rem 1rem;
    margin-bottom: .7rem;
}

.player-name {
    color: #17251c;
    font-size: 1.06rem;
    font-weight: 900;
}

.player-sub {
    margin-top: .18rem;
    color: #79817b;
    font-size: .75rem;
}


/* ==============================
   GAME HISTORY
============================== */

.game-result {
    background: white;
    border: 1px solid #e3e8e4;
    border-radius: 18px;
    padding: .9rem 1rem;
    margin-bottom: .55rem;
}

.game-score {
    color: #18271e;
    font-size: 1.03rem;
    font-weight: 900;
}

.game-meta {
    margin-top: .25rem;
    color: #7b827c;
    font-size: .72rem;
}


/* ==============================
   MOBILE
============================== */

@media (max-width: 600px) {

    .block-container {
        padding-top: 3.3rem;
        padding-left: .75rem;
        padding-right: .75rem;
    }

    .brand,
    .team-brand {
        font-size: 1.7rem;
    }

    .score-number {
        font-size: 1.5rem;
    }

    .code-value {
        font-size: 1.8rem;
    }

    div.stButton > button {
        min-height: 51px;
        font-size: .91rem;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# BASIC HELPERS
# =========================================================

def rerun():
    st.rerun()


def go(page):
    st.session_state.page = page
    rerun()


def flash(message):
    st.session_state.flash_message = message


def show_flash():
    message = st.session_state.get("flash_message")

    if message:
        st.toast(message, icon="✅")

        st.markdown(
            f"""
            <div class="success-card">
                ✓ {message}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.session_state.flash_message = None


def team_id():
    if not st.session_state.team:
        return None

    return st.session_state.team["id"]


# =========================================================
# TEAM
# =========================================================

TEAM_CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def make_team_code():

    for _ in range(100):

        code = "".join(
            random.choices(
                TEAM_CODE_CHARS,
                k=6
            )
        )

        existing = (
            supabase.table("teams")
            .select("id")
            .eq("team_code", code)
            .execute()
            .data
        )

        if not existing:
            return code

    raise RuntimeError(
        "チームコードを発行できませんでした。"
    )


def make_owner_code():

    return "".join(
        random.choices(
            TEAM_CODE_CHARS,
            k=12
        )
    )


def create_team(name):

    code = make_team_code()

    owner_code = make_owner_code()

    result = (
        supabase.table("teams")
        .insert({
            "team_name": name.strip(),
            "team_code": code,
            "owner_code": owner_code,
        })
        .execute()
        .data
    )

    if not result:
        raise RuntimeError(
            "チームを作成できませんでした。"
        )

    return result[0]


def find_team(code):

    code = code.strip().upper()

    result = (
        supabase.table("teams")
        .select("*")
        .eq("team_code", code)
        .execute()
        .data
    )

    if not result:
        return None

    return result[0]


def leave_team():

    st.session_state.team = None
    st.session_state.game_id = None
    st.session_state.page = "ホーム"

    st.session_state.switch_open = False
    st.session_state.sub_open = False
    st.session_state.finish_open = False

    rerun()


# =========================================================
# PLAYER HELPERS
# =========================================================

def get_players(active_only=True):

    query = (
        supabase.table("players")
        .select("*")
        .eq("team_id", team_id())
    )

    if active_only:
        query = query.eq(
            "active",
            True
        )

    return (
        query
        .order("name")
        .execute()
        .data
        or []
    )


def get_player_map():

    players = get_players(False)

    return {
        p["id"]: p
        for p in players
    }


def player_name(player_id):

    if not player_id:
        return "―"

    p = get_player_map().get(
        player_id
    )

    if not p:
        return "―"

    if p.get("number"):
        return (
            f'{p["name"]} '
            f'#{p["number"]}'
        )

    return p["name"]


# =========================================================
# PLACE
# =========================================================

def get_places():

    return (
        supabase.table("places")
        .select("*")
        .eq("team_id", team_id())
        .order("name")
        .execute()
        .data
        or []
    )


def add_place(name):

    name = name.strip()

    if not name:
        return

    existing = (
        supabase.table("places")
        .select("id")
        .eq("team_id", team_id())
        .eq("name", name)
        .execute()
        .data
    )

    if existing:
        return

    supabase.table("places").insert({
        "team_id": team_id(),
        "name": name,
    }).execute()


# =========================================================
# GAME HELPERS
# =========================================================

def get_games():

    return (
        supabase.table("games")
        .select("*")
        .eq("team_id", team_id())
        .order(
            "game_date",
            desc=True
        )
        .execute()
        .data
        or []
    )


def get_game(game_id=None):

    gid = (
        game_id
        or st.session_state.game_id
    )

    if not gid:
        return None

    result = (
        supabase.table("games")
        .select("*")
        .eq("id", gid)
        .eq("team_id", team_id())
        .execute()
        .data
    )

    if not result:
        return None

    return result[0]


def get_active_game():

    result = (
        supabase.table("games")
        .select("*")
        .eq("team_id", team_id())
        .eq("status", "playing")
        .order(
            "created_at",
            desc=True
        )
        .limit(1)
        .execute()
        .data
    )

    if not result:
        return None

    return result[0]


def update_game(values):

    if not st.session_state.game_id:
        return

    (
        supabase.table("games")
        .update(values)
        .eq(
            "id",
            st.session_state.game_id
        )
        .execute()
    )


# =========================================================
# LINEUP
# =========================================================

def get_lineup(game_id=None):

    gid = (
        game_id
        or st.session_state.game_id
    )

    if not gid:
        return []

    return (
        supabase.table("lineup")
        .select("*")
        .eq("game_id", gid)
        .order("slot")
        .execute()
        .data
        or []
    )


def get_lineup_players(game_id=None):

    rows = get_lineup(game_id)

    pmap = get_player_map()

    result = []

    for row in rows:

        player = pmap.get(
            row["player_id"]
        )

        if player:

            result.append({
                **player,
                "slot": row["slot"]
            })

    return result


# =========================================================
# BATTING
# =========================================================

def get_batting_rows(
    game_ids=None,
    player_id=None
):

    games = get_games()

    team_game_ids = {
        g["id"]
        for g in games
    }

    if game_ids is not None:

        allowed_ids = (
            team_game_ids
            & set(game_ids)
        )

    else:

        allowed_ids = team_game_ids

    if not allowed_ids:
        return []

    query = (
        supabase.table("batting")
        .select("*")
    )

    if player_id:

        query = query.eq(
            "player_id",
            player_id
        )

    rows = (
        query
        .order("created_at")
        .execute()
        .data
        or []
    )

    return [
        row
        for row in rows
        if row["game_id"]
        in allowed_ids
    ]


def batting_stats(rows):

    stats = {
        "PA": 0,
        "AB": 0,
        "H": 0,
        "1B": 0,
        "2B": 0,
        "3B": 0,
        "HR": 0,
        "BB": 0,
        "HBP": 0,
        "SO": 0,
        "SH": 0,
        "SF": 0,
    }

    for row in rows:

        result = row["result"]

        hit_type = row.get(
            "hit_type"
        )

        stats["PA"] += 1

        if result == "四球":

            stats["BB"] += 1

        elif result == "死球":

            stats["HBP"] += 1

        elif result == "犠打":

            stats["SH"] += 1

        elif result == "犠飛":

            stats["SF"] += 1

        else:

            stats["AB"] += 1

            if result == "三振":
                stats["SO"] += 1

            if result == "安打":

                stats["H"] += 1

                if hit_type == "単打":
                    stats["1B"] += 1

                elif hit_type == "二塁打":
                    stats["2B"] += 1

                elif hit_type == "三塁打":
                    stats["3B"] += 1

                elif hit_type == "本塁打":
                    stats["HR"] += 1

    if stats["AB"]:

        stats["AVG"] = (
            stats["H"]
            / stats["AB"]
        )

    else:

        stats["AVG"] = 0


    obp_denominator = (
        stats["AB"]
        + stats["BB"]
        + stats["HBP"]
        + stats["SF"]
    )

    if obp_denominator:

        stats["OBP"] = (
            stats["H"]
            + stats["BB"]
            + stats["HBP"]
        ) / obp_denominator

    else:

        stats["OBP"] = 0


    total_bases = (
        stats["1B"]
        + stats["2B"] * 2
        + stats["3B"] * 3
        + stats["HR"] * 4
    )

    if stats["AB"]:

        stats["SLG"] = (
            total_bases
            / stats["AB"]
        )

    else:

        stats["SLG"] = 0


    stats["OPS"] = (
        stats["OBP"]
        + stats["SLG"]
    )

    return stats


def format_avg(value):

    return (
        f"{value:.3f}"
        .replace(
            "0.",
            "."
        )
    )


# =========================================================
# PITCHING
# =========================================================

def get_pitching_rows(
    game_ids=None,
    pitcher_id=None
):

    games = get_games()

    team_game_ids = {
        g["id"]
        for g in games
    }

    if game_ids is not None:

        allowed_ids = (
            team_game_ids
            & set(game_ids)
        )

    else:

        allowed_ids = team_game_ids

    if not allowed_ids:
        return []

    query = (
        supabase.table("pitching")
        .select("*")
    )

    if pitcher_id:

        query = query.eq(
            "pitcher_id",
            pitcher_id
        )

    rows = (
        query
        .order("created_at")
        .execute()
        .data
        or []
    )

    return [
        row
        for row in rows
        if row["game_id"]
        in allowed_ids
    ]


def pitching_stats(rows):

    stats = {
        "BF": 0,
        "H": 0,
        "HR": 0,
        "BB": 0,
        "HBP": 0,
        "SO": 0,
        "R": 0,
    }

    for row in rows:

        result = row["result"]

        stats["BF"] += 1

        stats["R"] += int(
            row.get("runs")
            or 0
        )

        if result in [
            "安打",
            "二塁打",
            "三塁打",
            "本塁打",
        ]:

            stats["H"] += 1

        if result == "本塁打":

            stats["HR"] += 1

        elif result == "四球":

            stats["BB"] += 1

        elif result == "死球":

            stats["HBP"] += 1

        elif result == "三振":

            stats["SO"] += 1

    return stats


# =========================================================
# PAGE HEADER
# =========================================================

def page_header(
    title,
    subtitle=None
):

    if (
        st.session_state.page
        != "ホーム"
    ):

        if st.button(
            "‹ ホーム",
            key=(
                "back_"
                + st.session_state.page
            )
        ):

            go("ホーム")

    subtitle_html = ""

    if subtitle:

        subtitle_html = (
            f'<div class="small-muted">'
            f'{subtitle}'
            f'</div>'
        )

    st.markdown(
        f"""
        <div style="
            margin:.65rem 0 1rem 0;
        ">
            <div style="
                font-size:1.55rem;
                font-weight:950;
                letter-spacing:-.045em;
                color:#17251c;
            ">
                {title}
            </div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# TEAM GATE
# =========================================================

def team_gate():

    st.markdown("""
        <div class="brand-wrap">
            <div class="brand">
                ⚾ Baseball Score
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ---------------------------------
    # TEAM CREATED SCREEN
    # ---------------------------------

    if st.session_state.created_team:

        team = (
            st.session_state.created_team
        )

        st.markdown(
            """
            <div class="success-card">
                ✓ チームを作成しました
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="code-card">

                <div class="code-label">
                    TEAM CODE
                </div>

                <div class="code-value">
                    {team["team_code"]}
                </div>

                <div class="code-team">
                    {team["team_name"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "このコードをメンバーに共有してください。"
        )

        st.warning(
            "チームコードを知っている人は、このチームに参加できます。"
        )

        if st.button(
            f'{team["team_name"]} を開く',
            type="primary",
            use_container_width=True,
        ):

            st.session_state.team = team

            st.session_state.created_team = None

            flash(
                f'{team["team_name"]} を作成しました！'
            )

            rerun()

        return


    # ---------------------------------
    # NORMAL TEAM GATE
    # ---------------------------------

    join_tab, create_tab = st.tabs([
        "チームに入る",
        "チームを作る",
    ])


    # =================================
    # JOIN TEAM
    # =================================

    with join_tab:

        st.markdown(
            '<div class="section-title">'
            'TEAM CODE'
            '</div>',
            unsafe_allow_html=True,
        )

        code = st.text_input(
            "チームコード",
            placeholder="例：RK7F29",
            max_chars=6,
            label_visibility="collapsed",
            key="join_team_code",
        )

        if st.button(
            "チームに入る",
            type="primary",
            use_container_width=True,
            key="join_team_button",
        ):

            if not code.strip():

                st.warning(
                    "チームコードを入力してください。"
                )

            else:

                team = find_team(code)

                if not team:

                    st.error(
                        "チームが見つかりません。"
                    )

                else:

                    st.session_state.team = (
                        team
                    )

                    active = (
                        get_active_game()
                    )

                    if active:

                        st.session_state.game_id = (
                            active["id"]
                        )

                    flash(
                        f'{team["team_name"]} に入りました'
                    )

                    rerun()


    # =================================
    # CREATE TEAM
    # =================================

    with create_tab:

        st.markdown(
            '<div class="section-title">'
            'NEW TEAM'
            '</div>',
            unsafe_allow_html=True,
        )

        team_name = st.text_input(
            "チーム名",
            placeholder="例：りこなん",
            key="new_team_name",
        )

        st.caption(
            "作成すると、メンバー参加用のチームコードが自動で発行されます。"
        )

        if st.button(
            "チームを作成してコードを発行",
            type="primary",
            use_container_width=True,
            key="create_team_button",
        ):

            if not team_name.strip():

                st.warning(
                    "チーム名を入力してください。"
                )

            else:

                try:

                    team = create_team(
                        team_name
                    )

                    st.session_state.created_team = (
                        team
                    )

                    rerun()

                except Exception as e:

                    st.error(
                        "チームを作成できませんでした。"
                    )


# =========================================================
# HOME
# =========================================================

def home_page():

    team = st.session_state.team

    st.markdown(
        '<div style="height:.7rem;"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="brand-wrap">

            <div class="team-brand">
                ⚾ {team["team_name"]}
            </div>

            <div class="team-brand-sub">
                BASEBALL SCORE
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    show_flash()

    active = get_active_game()

    if active:

        inning = (
            active.get(
                "current_inning"
            )
            or 1
        )

        mode = (
            "攻撃中"
            if active.get(
                "current_mode"
            ) == "offense"
            else "守備中"
        )

        st.markdown(
            f"""
            <div class="app-card">

                <div class="small-muted">
                    LIVE GAME
                </div>

                <div style="
                    font-size:1.08rem;
                    font-weight:900;
                    margin-top:.25rem;
                ">
                    vs {active["opponent"]}
                </div>

                <div class="small-muted"
                     style="margin-top:.2rem;">
                    {inning}回 ｜ {mode}
                    &nbsp;&nbsp;
                    {active["our_score"]}
                    -
                    {active["their_score"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "⚾ 試合を続ける",
            type="primary",
            use_container_width=True,
        ):

            st.session_state.game_id = (
                active["id"]
            )

            go("スコア入力")


    if st.button(
        "⚾　スコア入力　›",
        use_container_width=True,
    ):

        go("スコア入力")


    if st.button(
        "📊　成績確認　›",
        use_container_width=True,
    ):

        go("成績確認")


    if st.button(
        "👥　選手登録　›",
        use_container_width=True,
    ):

        go("選手登録")


    st.markdown(
        '<div class="section-title">'
        'TEAM'
        '</div>',
        unsafe_allow_html=True,
    )


    with st.expander(
        "チーム情報"
    ):

        st.markdown(
            f"""
            <div class="code-card">

                <div class="code-label">
                    TEAM CODE
                </div>

                <div class="code-value">
                    {team["team_code"]}
                </div>

                <div class="code-team">
                    {team["team_name"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "このコードをチームメンバーに共有してください。"
        )

        if st.button(
            "このチームから退出",
            use_container_width=True,
        ):

            leave_team()


# =========================================================
# PLAYER PAGE
# =========================================================

def player_page():

    page_header(
        "選手登録",
        st.session_state.team[
            "team_name"
        ],
    )

    show_flash()

    st.markdown(
        '<div class="section-title">'
        'NEW PLAYER'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form(
        "player_form",
        clear_on_submit=True,
    ):

        name = st.text_input(
            "選手名",
            placeholder="山田 太郎",
        )

        number = st.text_input(
            "背番号",
            placeholder="10",
        )

        submitted = (
            st.form_submit_button(
                "選手を登録",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:

            if not name.strip():

                st.warning(
                    "選手名を入力してください。"
                )

            else:

                existing = (
                    supabase.table(
                        "players"
                    )
                    .select("id")
                    .eq(
                        "team_id",
                        team_id()
                    )
                    .eq(
                        "name",
                        name.strip()
                    )
                    .execute()
                    .data
                )

                if existing:

                    st.warning(
                        "同じ名前の選手がすでに登録されています。"
                    )

                else:

                    (
                        supabase.table(
                            "players"
                        )
                        .insert({
                            "team_id":
                                team_id(),

                            "name":
                                name.strip(),

                            "number":
                                (
                                    number.strip()
                                    or None
                                ),

                            "active":
                                True,
                        })
                        .execute()
                    )

                    flash(
                        f'{name.strip()} を登録しました！'
                    )

                    rerun()


    players = get_players()

    st.markdown(
        f"""
        <div class="section-title">
            PLAYERS　{len(players)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not players:

        st.info(
            "まだ選手が登録されていません。"
        )

        return


    for player in players:

        number_text = ""

        if player.get("number"):

            number_text = (
                f'#{player["number"]}'
            )

        st.markdown(
            f"""
            <div class="player-card">

                <div class="player-name">
                    {player["name"]}
                </div>

                <div class="player-sub">
                    {number_text}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# NEW GAME
# =========================================================

def new_game_page():

    page_header(
        "試合を始める",
        st.session_state.team[
            "team_name"
        ],
    )

    players = get_players()

    if not players:

        st.warning(
            "先に選手を登録してください。"
        )

        if st.button(
            "選手登録へ",
            use_container_width=True,
        ):

            go("選手登録")

        return


    game_date = st.date_input(
        "試合日",
        value=date.today(),
    )


    opponent = st.text_input(
        "対戦相手",
        placeholder="○○大学",
    )


    places = get_places()

    place_names = [
        p["name"]
        for p in places
    ]

    place_options = (
        place_names
        + ["＋ 新しい場所"]
    )


    place_choice = st.selectbox(
        "試合場所",
        place_options,
    )


    new_place = ""

    if (
        place_choice
        == "＋ 新しい場所"
    ):

        new_place = st.text_input(
            "新しい試合場所",
            placeholder="○○球場",
        )


    game_type = st.radio(
        "試合区分",
        [
            "練習試合",
            "公式戦"
        ],
        horizontal=True,
    )


    tournament = None

    if game_type == "公式戦":

        tournament = st.text_input(
            "大会名",
            placeholder="○○大会",
        )


    bat_order = st.radio(
        "先攻・後攻",
        [
            "先攻",
            "後攻"
        ],
        horizontal=True,
    )


    st.markdown(
        '<div class="section-title">'
        'LINEUP'
        '</div>',
        unsafe_allow_html=True,
    )


    player_labels = {}

    for p in players:

        label = p["name"]

        if p.get("number"):

            label += (
                f' #{p["number"]}'
            )

        player_labels[
            p["id"]
        ] = label


    player_ids = list(
        player_labels.keys()
    )


    lineup_ids = []

    lineup_count = min(
        9,
        len(player_ids)
    )


    for i in range(
        lineup_count
    ):

        candidates = [
            pid
            for pid in player_ids
            if pid not in lineup_ids
        ]

        selected = st.selectbox(
            f"{i + 1}番",
            candidates,
            format_func=lambda x:
                player_labels[x],
            key=f"lineup_{i}",
        )

        lineup_ids.append(
            selected
        )


    starter = st.selectbox(
        "先発投手",
        player_ids,
        format_func=lambda x:
            player_labels[x],
    )


    if st.button(
        "試合開始",
        type="primary",
        use_container_width=True,
    ):

        if not opponent.strip():

            st.warning(
                "対戦相手を入力してください。"
            )

            return


        if (
            place_choice
            == "＋ 新しい場所"
        ):

            place = (
                new_place.strip()
            )

            if place:

                add_place(
                    place
                )

        else:

            place = (
                place_choice
            )


        bat_first = (
            bat_order
            == "先攻"
        )


        current_mode = (
            "offense"
            if bat_first
            else "defense"
        )


        result = (
            supabase.table("games")
            .insert({

                "team_id":
                    team_id(),

                "game_date":
                    str(game_date),

                "opponent":
                    opponent.strip(),

                "place":
                    (
                        place
                        or None
                    ),

                "game_type":
                    game_type,

                "tournament":
                    (
                        tournament.strip()
                        if tournament
                        else None
                    ),

                "bat_first":
                    bat_first,

                "our_score":
                    0,

                "their_score":
                    0,

                "status":
                    "playing",

                "current_inning":
                    1,

                "current_mode":
                    current_mode,

                "current_batter_index":
                    0,

                "current_pitcher_id":
                    starter,
            })
            .execute()
            .data
        )


        if not result:

            st.error(
                "試合を開始できませんでした。"
            )

            return


        game = result[0]


        lineup_rows = []

        for i, pid in enumerate(
            lineup_ids,
            start=1
        ):

            lineup_rows.append({
                "game_id":
                    game["id"],

                "slot":
                    i,

                "player_id":
                    pid,
            })


        if lineup_rows:

            (
                supabase.table(
                    "lineup"
                )
                .insert(
                    lineup_rows
                )
                .execute()
            )


        st.session_state.game_id = (
            game["id"]
        )

        flash(
            "試合を開始しました！"
        )

        go("スコア入力")


# =========================================================
# SCORE HEADER
# =========================================================

def score_header(game):

    inning = (
        game.get(
            "current_inning"
        )
        or 1
    )

    mode = game.get(
        "current_mode"
    )


    if mode == "offense":

        status = "攻撃中"

    else:

        status = "守備中"


    if game["bat_first"]:

        half = (
            "表"
            if mode == "offense"
            else "裏"
        )

    else:

        half = (
            "裏"
            if mode == "offense"
            else "表"
        )


    st.markdown(
        f"""
        <div class="score-card">

            <div class="score-top">
                {inning}回{half}
                ｜ {status}
            </div>

            <div class="score-main">

                <div class="score-team">
                    {
                        st.session_state.team[
                            "team_name"
                        ]
                    }
                </div>

                <div class="score-number">

                    {game["our_score"]}

                    <span style="
                        opacity:.45;
                        font-size:.9rem;
                    ">
                        -
                    </span>

                    {game["their_score"]}

                </div>

                <div class="score-team right">
                    {game["opponent"]}
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# BATTING INPUT
# =========================================================

def batting_input(game):

    lineup = (
        get_lineup_players()
    )

    if not lineup:

        st.error(
            "オーダーが登録されていません。"
        )

        return


    batter_index = (
        game.get(
            "current_batter_index"
        )
        or 0
    )

    batter_index %= len(
        lineup
    )


    batter = lineup[
        batter_index
    ]


    rows = get_batting_rows(
        [game["id"]],
        batter["id"]
    )


    stats = batting_stats(
        rows
    )


    st.markdown(
        f"""
        <div class="player-card">

            <div class="small-muted">
                {batter_index + 1}番
            </div>

            <div class="player-name">
                {batter["name"]}
            </div>

            <div class="player-sub">
                今日　
                {stats["AB"]}打数
                {stats["H"]}安打
            </div>

        </div>
        """,
        unsafe_allow_html=True,
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
            "犠飛",
        ],
        horizontal=True,
        key="bat_result",
    )


    field = None
    batted_type = None
    hit_type = None


    if result in [
        "安打",
        "アウト"
    ]:

        field = st.radio(
            "方向",
            [
                "投",
                "捕",
                "一",
                "二",
                "三",
                "遊",
                "左",
                "中",
                "右",
            ],
            horizontal=True,
            key="bat_field",
        )


        batted_type = st.radio(
            "打球",
            [
                "ゴロ",
                "ライナー",
                "フライ",
                "オーバー",
            ],
            horizontal=True,
            key="bat_type",
        )


    if result == "安打":

        hit_type = st.radio(
            "安打種別",
            [
                "単打",
                "二塁打",
                "三塁打",
                "本塁打",
            ],
            horizontal=True,
            key="hit_type",
        )


    if st.button(
        "この打席を登録",
        type="primary",
        use_container_width=True,
    ):

        (
            supabase.table(
                "batting"
            )
            .insert({

                "game_id":
                    game["id"],

                "player_id":
                    batter["id"],

                "inning":
                    game[
                        "current_inning"
                    ],

                "result":
                    result,

                "field":
                    field,

                "batted_type":
                    batted_type,

                "hit_type":
                    hit_type,
            })
            .execute()
        )


        next_index = (
            batter_index + 1
        ) % len(lineup)


        update_game({
            "current_batter_index":
                next_index
        })


        flash(
            f'{batter["name"]}：'
            f'{result} を登録'
        )

        rerun()


    if rows:

        if st.button(
            "↶ 直前の打席を取り消す",
            use_container_width=True,
        ):

            last = rows[-1]

            (
                supabase.table(
                    "batting"
                )
                .delete()
                .eq(
                    "id",
                    last["id"]
                )
                .execute()
            )


            previous_index = (
                batter_index - 1
            ) % len(lineup)


            update_game({
                "current_batter_index":
                    previous_index
            })


            flash(
                "直前の打席を取り消しました"
            )

            rerun()


# =========================================================
# PITCHING INPUT
# =========================================================

def pitching_input(game):

    players = get_players()

    current_pitcher_id = (
        game.get(
            "current_pitcher_id"
        )
    )


    pitcher = next(
        (
            p
            for p in players
            if p["id"]
            == current_pitcher_id
        ),
        None
    )


    if (
        pitcher is None
        and players
    ):

        pitcher = players[0]


    if not pitcher:

        st.warning(
            "投手が登録されていません。"
        )

        return


    rows = get_pitching_rows(
        [game["id"]],
        pitcher["id"]
    )


    stats = pitching_stats(
        rows
    )


    st.markdown(
        f"""
        <div class="player-card">

            <div class="small-muted">
                PITCHER
            </div>

            <div class="player-name">
                {pitcher["name"]}
            </div>

            <div class="player-sub">
                H {stats["H"]}
                　K {stats["SO"]}
                　BB {stats["BB"]}
                　R {stats["R"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    result = st.radio(
        "打者結果",
        [
            "アウト",
            "三振",
            "安打",
            "二塁打",
            "三塁打",
            "本塁打",
            "四球",
            "死球",
            "失策",
        ],
        horizontal=True,
        key="pitch_result",
    )


    runs = st.number_input(
        "このプレーで入った得点",
        min_value=0,
        max_value=20,
        value=0,
        step=1,
    )


    if st.button(
        "結果を登録",
        type="primary",
        use_container_width=True,
    ):

        (
            supabase.table(
                "pitching"
            )
            .insert({

                "game_id":
                    game["id"],

                "pitcher_id":
                    pitcher["id"],

                "inning":
                    game[
                        "current_inning"
                    ],

                "result":
                    result,

                "runs":
                    int(runs),
            })
            .execute()
        )


        flash(
            f"{result} を登録しました"
        )

        rerun()


    if rows:

        if st.button(
            "↶ 直前の投球結果を取り消す",
            use_container_width=True,
        ):

            last = rows[-1]

            (
                supabase.table(
                    "pitching"
                )
                .delete()
                .eq(
                    "id",
                    last["id"]
                )
                .execute()
            )


            flash(
                "直前の投球結果を取り消しました"
            )

            rerun()


# =========================================================
# SIDE SWITCH
# =========================================================

def side_switch_panel(game):

    st.markdown(
        '<div class="section-title">'
        'GAME CONTROL'
        '</div>',
        unsafe_allow_html=True,
    )


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "攻守交替",
            use_container_width=True,
        ):

            st.session_state.switch_open = (
                not st.session_state.switch_open
            )


    with col2:

        if st.button(
            "選手交代",
            use_container_width=True,
        ):

            st.session_state.sub_open = (
                not st.session_state.sub_open
            )


    if not st.session_state.switch_open:
        return


    st.markdown(
        """
        <div class="soft-card">
            <b>攻守交替</b><br>
            <span class="small-muted">
                終了したイニングの得点を入力
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


    runs = st.number_input(
        "この回の得点",
        min_value=0,
        max_value=30,
        value=0,
        step=1,
        key="inning_runs",
    )


    if st.button(
        "得点を確定して攻守交替",
        type="primary",
        use_container_width=True,
    ):

        current_mode = (
            game["current_mode"]
        )


        side = (
            "our"
            if current_mode
            == "offense"
            else "their"
        )


        (
            supabase.table(
                "inning_scores"
            )
            .insert({

                "game_id":
                    game["id"],

                "inning":
                    game[
                        "current_inning"
                    ],

                "side":
                    side,

                "runs":
                    int(runs),
            })
            .execute()
        )


        values = {}


        if (
            current_mode
            == "offense"
        ):

            values[
                "our_score"
            ] = (
                int(
                    game["our_score"]
                )
                + int(runs)
            )

            values[
                "current_mode"
            ] = "defense"


            if not game[
                "bat_first"
            ]:

                values[
                    "current_inning"
                ] = (
                    game[
                        "current_inning"
                    ]
                    + 1
                )


        else:

            values[
                "their_score"
            ] = (
                int(
                    game[
                        "their_score"
                    ]
                )
                + int(runs)
            )

            values[
                "current_mode"
            ] = "offense"


            if game[
                "bat_first"
            ]:

                values[
                    "current_inning"
                ] = (
                    game[
                        "current_inning"
                    ]
                    + 1
                )


        update_game(
            values
        )


        st.session_state.switch_open = (
            False
        )


        flash(
            "攻守を交替しました"
        )

        rerun()


# =========================================================
# SUBSTITUTION
# =========================================================

def substitution_panel(game):

    if not st.session_state.sub_open:
        return


    players = get_players()

    lineup = (
        get_lineup_players()
    )


    st.markdown(
        '<div class="section-title">'
        'SUBSTITUTION'
        '</div>',
        unsafe_allow_html=True,
    )


    sub_type = st.radio(
        "交代種類",
        [
            "代打",
            "投手交代"
        ],
        horizontal=True,
    )


    # ---------------------------------
    # PINCH HITTER
    # ---------------------------------

    if sub_type == "代打":

        if not lineup:
            return


        slots = [
            p["slot"]
            for p in lineup
        ]


        slot = st.selectbox(
            "打順",
            slots,
            format_func=lambda x:
                f"{x}番",
        )


        current = next(
            p
            for p in lineup
            if p["slot"]
            == slot
        )


        lineup_ids = {
            p["id"]
            for p in lineup
        }


        candidates = [
            p
            for p in players
            if p["id"]
            not in lineup_ids
        ]


        if not candidates:

            st.info(
                "控え選手がいません。"
            )

            return


        new_player_id = (
            st.selectbox(
                "新しい選手",
                [
                    p["id"]
                    for p
                    in candidates
                ],
                format_func=lambda x:
                    player_name(x),
            )
        )


        if st.button(
            "代打を登録",
            type="primary",
            use_container_width=True,
        ):

            (
                supabase.table(
                    "lineup"
                )
                .update({
                    "player_id":
                        new_player_id
                })
                .eq(
                    "game_id",
                    game["id"]
                )
                .eq(
                    "slot",
                    slot
                )
                .execute()
            )


            (
                supabase.table(
                    "substitutions"
                )
                .insert({

                    "game_id":
                        game["id"],

                    "inning":
                        game[
                            "current_inning"
                        ],

                    "substitution_type":
                        "代打",

                    "old_player_id":
                        current["id"],

                    "new_player_id":
                        new_player_id,
                })
                .execute()
            )


            st.session_state.sub_open = (
                False
            )


            flash(
                "代打を登録しました"
            )

            rerun()


    # ---------------------------------
    # PITCHER CHANGE
    # ---------------------------------

    else:

        current_pitcher = (
            game.get(
                "current_pitcher_id"
            )
        )


        candidates = [
            p
            for p in players
            if p["id"]
            != current_pitcher
        ]


        if not candidates:

            st.info(
                "交代できる投手がいません。"
            )

            return


        new_pitcher_id = (
            st.selectbox(
                "新しい投手",
                [
                    p["id"]
                    for p
                    in candidates
                ],
                format_func=lambda x:
                    player_name(x),
            )
        )


        if st.button(
            "投手交代を登録",
            type="primary",
            use_container_width=True,
        ):

            update_game({
                "current_pitcher_id":
                    new_pitcher_id
            })


            (
                supabase.table(
                    "substitutions"
                )
                .insert({

                    "game_id":
                        game["id"],

                    "inning":
                        game[
                            "current_inning"
                        ],

                    "substitution_type":
                        "投手交代",

                    "old_player_id":
                        current_pitcher,

                    "new_player_id":
                        new_pitcher_id,
                })
                .execute()
            )


            st.session_state.sub_open = (
                False
            )


            flash(
                "投手を交代しました"
            )

            rerun()


# =========================================================
# GAME FINISH
# =========================================================

def finish_game_panel(game):

    st.markdown("<br>",
                unsafe_allow_html=True)


    if st.button(
        "ゲームセット",
        use_container_width=True,
    ):

        st.session_state.finish_open = (
            not st.session_state.finish_open
        )


    if not st.session_state.finish_open:
        return


    st.warning(
        "この試合を終了しますか？"
    )


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "終了する",
            type="primary",
            use_container_width=True,
        ):

            update_game({
                "status":
                    "finished"
            })


            st.session_state.game_id = (
                None
            )

            st.session_state.finish_open = (
                False
            )

            st.session_state.switch_open = (
                False
            )

            st.session_state.sub_open = (
                False
            )


            flash(
                "試合を終了しました！"
            )

            go("ホーム")


    with col2:

        if st.button(
            "キャンセル",
            use_container_width=True,
        ):

            st.session_state.finish_open = (
                False
            )

            rerun()


# =========================================================
# SCORE PAGE
# =========================================================

def score_page():

    page_header(
        "スコア入力",
        st.session_state.team[
            "team_name"
        ],
    )

    show_flash()


    game = get_game()


    if not game:

        active = get_active_game()

        if active:

            st.session_state.game_id = (
                active["id"]
            )

            game = active

        else:

            st.markdown(
                """
                <div class="app-card">
                    <b>進行中の試合はありません</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "＋ 新しい試合を始める",
                type="primary",
                use_container_width=True,
            ):

                go("新規試合")

            return


    score_header(
        game
    )


    if (
        game["current_mode"]
        == "offense"
    ):

        batting_input(
            game
        )

    else:

        pitching_input(
            game
        )


    side_switch_panel(
        game
    )


    substitution_panel(
        game
    )


    finish_game_panel(
        game
    )


# =========================================================
# FILTER
# =========================================================

def game_filter_ui(
    key_prefix
):

    games = get_games()

    if not games:
        return []


    st.markdown(
        '<div class="section-title">'
        'FILTER'
        '</div>',
        unsafe_allow_html=True,
    )


    period = st.radio(
        "期間",
        [
            "全期間",
            "期間指定"
        ],
        horizontal=True,
        key=(
            key_prefix
            + "_period"
        ),
    )


    filtered = games[:]


    if period == "期間指定":

        col1, col2 = (
            st.columns(2)
        )


        with col1:

            start_date = (
                st.date_input(
                    "開始日",
                    value=date(
                        date.today().year,
                        1,
                        1
                    ),
                    key=(
                        key_prefix
                        + "_start"
                    ),
                )
            )


        with col2:

            end_date = (
                st.date_input(
                    "終了日",
                    value=date.today(),
                    key=(
                        key_prefix
                        + "_end"
                    ),
                )
            )


        filtered = [
            g
            for g in filtered
            if (
                start_date
                <= date.fromisoformat(
                    g["game_date"]
                )
                <= end_date
            )
        ]


    types = sorted(
        {
            g["game_type"]
            for g in games
            if g.get(
                "game_type"
            )
        }
    )


    selected_type = st.selectbox(
        "試合区分",
        ["全試合"]
        + types,
        key=(
            key_prefix
            + "_type"
        ),
    )


    if selected_type != "全試合":

        filtered = [
            g
            for g in filtered
            if g.get(
                "game_type"
            )
            == selected_type
        ]


    tournaments = sorted(
        {
            g["tournament"]
            for g in games
            if g.get(
                "tournament"
            )
        }
    )


    selected_tournament = (
        st.selectbox(
            "大会",
            ["全大会"]
            + tournaments,
            key=(
                key_prefix
                + "_tournament"
            ),
        )
    )


    if (
        selected_tournament
        != "全大会"
    ):

        filtered = [
            g
            for g in filtered
            if g.get(
                "tournament"
            )
            == selected_tournament
        ]


    places = sorted(
        {
            g["place"]
            for g in games
            if g.get(
                "place"
            )
        }
    )


    selected_place = (
        st.selectbox(
            "試合場所",
            ["全場所"]
            + places,
            key=(
                key_prefix
                + "_place"
            ),
        )
    )


    if selected_place != "全場所":

        filtered = [
            g
            for g in filtered
            if g.get(
                "place"
            )
            == selected_place
        ]


    return filtered


# =========================================================
# INDIVIDUAL STATS
# =========================================================

def individual_stats():

    games = game_filter_ui(
        "individual"
    )


    if not games:

        st.info(
            "条件に該当する試合がありません。"
        )

        return


    game_ids = [
        g["id"]
        for g in games
    ]


    players = get_players(
        False
    )


    if not players:
        return


    selected_player = (
        st.selectbox(
            "選手",
            [
                p["id"]
                for p in players
            ],
            format_func=lambda x:
                player_name(x),
            key="individual_player",
        )
    )


    batting_tab, pitching_tab = (
        st.tabs([
            "打撃",
            "投手"
        ])
    )


    # =================================
    # BATTING
    # =================================

    with batting_tab:

        rows = get_batting_rows(
            game_ids,
            selected_player
        )


        stats = batting_stats(
            rows
        )


        col1, col2, col3 = (
            st.columns(3)
        )


        col1.metric(
            "打率",
            format_avg(
                stats["AVG"]
            )
        )


        col2.metric(
            "出塁率",
            format_avg(
                stats["OBP"]
            )
        )


        col3.metric(
            "OPS",
            format_avg(
                stats["OPS"]
            )
        )


        st.markdown(
            f"""
            <div class="app-card">

                打席　<b>{stats["PA"]}</b><br>
                打数　<b>{stats["AB"]}</b><br>
                安打　<b>{stats["H"]}</b><br>
                二塁打　<b>{stats["2B"]}</b><br>
                三塁打　<b>{stats["3B"]}</b><br>
                本塁打　<b>{stats["HR"]}</b><br>
                四球　<b>{stats["BB"]}</b><br>
                死球　<b>{stats["HBP"]}</b><br>
                三振　<b>{stats["SO"]}</b><br>
                犠打　<b>{stats["SH"]}</b><br>
                犠飛　<b>{stats["SF"]}</b>

            </div>
            """,
            unsafe_allow_html=True,
        )


    # =================================
    # PITCHING
    # =================================

    with pitching_tab:

        rows = get_pitching_rows(
            game_ids,
            selected_player
        )


        stats = pitching_stats(
            rows
        )


        col1, col2, col3 = (
            st.columns(3)
        )


        col1.metric(
            "対戦打者",
            stats["BF"]
        )


        col2.metric(
            "奪三振",
            stats["SO"]
        )


        col3.metric(
            "失点",
            stats["R"]
        )


        st.markdown(
            f"""
            <div class="app-card">

                被安打　<b>{stats["H"]}</b><br>
                被本塁打　<b>{stats["HR"]}</b><br>
                四球　<b>{stats["BB"]}</b><br>
                死球　<b>{stats["HBP"]}</b><br>
                奪三振　<b>{stats["SO"]}</b><br>
                失点　<b>{stats["R"]}</b>

            </div>
            """,
            unsafe_allow_html=True,
        )


        st.caption(
            "※ 走者状況や失策による自責点判定を記録していないため、防御率ではなく失点を表示しています。"
        )


# =========================================================
# RANKING
# =========================================================

def ranking_stats():

    games = game_filter_ui(
        "ranking"
    )


    if not games:

        st.info(
            "条件に該当する試合がありません。"
        )

        return


    game_ids = [
        g["id"]
        for g in games
    ]


    players = get_players(
        False
    )


    category = st.selectbox(
        "ランキング",
        [
            "打率",
            "安打",
            "本塁打",
            "OPS",
            "奪三振",
        ],
    )


    ranking = []


    for player in players:

        if category in [
            "打率",
            "安打",
            "本塁打",
            "OPS",
        ]:

            rows = get_batting_rows(
                game_ids,
                player["id"]
            )


            stats = batting_stats(
                rows
            )


            if category == "打率":

                value = (
                    stats["AVG"]
                )

            elif category == "安打":

                value = (
                    stats["H"]
                )

            elif category == "本塁打":

                value = (
                    stats["HR"]
                )

            else:

                value = (
                    stats["OPS"]
                )


        else:

            rows = get_pitching_rows(
                game_ids,
                player["id"]
            )


            stats = pitching_stats(
                rows
            )


            value = (
                stats["SO"]
            )


        ranking.append(
            (
                player["name"],
                value
            )
        )


    ranking.sort(
        key=lambda x: x[1],
        reverse=True
    )


    for rank, item in enumerate(
        ranking,
        start=1
    ):

        name, value = item


        if category in [
            "打率",
            "OPS"
        ]:

            display_value = (
                format_avg(
                    value
                )
            )

        else:

            display_value = (
                str(value)
            )


        st.markdown(
            f"""
            <div class="game-result">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                ">

                    <div>

                        <span style="
                            color:#7b827c;
                            font-size:.78rem;
                            margin-right:.75rem;
                        ">
                            {rank}
                        </span>

                        <b>{name}</b>

                    </div>

                    <div style="
                        font-size:1.15rem;
                        font-weight:950;
                        color:#174d34;
                    ">
                        {display_value}
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# INNING SCORE
# =========================================================

def inning_score_table(game):

    rows = (
        supabase.table(
            "inning_scores"
        )
        .select("*")
        .eq(
            "game_id",
            game["id"]
        )
        .order("inning")
        .execute()
        .data
        or []
    )


    if not rows:

        st.caption(
            "イニング別得点はありません。"
        )

        return


    innings = sorted(
        {
            row["inning"]
            for row in rows
        }
    )


    header = (
        "| チーム | "
        + " | ".join(
            str(i)
            for i in innings
        )
        + " | 計 |"
    )


    divider = (
        "|---|"
        + "|".join(
            ["---"]
            * len(innings)
        )
        + "|---|"
    )


    our_scores = []

    their_scores = []


    for inning in innings:

        our = next(
            (
                row["runs"]
                for row in rows
                if (
                    row["inning"]
                    == inning
                    and row["side"]
                    == "our"
                )
            ),
            "-"
        )


        their = next(
            (
                row["runs"]
                for row in rows
                if (
                    row["inning"]
                    == inning
                    and row["side"]
                    == "their"
                )
            ),
            "-"
        )


        our_scores.append(
            str(our)
        )


        their_scores.append(
            str(their)
        )


    our_line = (
        "| "
        + st.session_state.team[
            "team_name"
        ]
        + " | "
        + " | ".join(
            our_scores
        )
        + f' | {game["our_score"]} |'
    )


    their_line = (
        f'| {game["opponent"]} | '
        + " | ".join(
            their_scores
        )
        + f' | {game["their_score"]} |'
    )


    st.markdown(
        "\n".join([
            header,
            divider,
            our_line,
            their_line,
        ])
    )


# =========================================================
# TEAM STATS
# =========================================================

def team_stats():

    games = game_filter_ui(
        "teamstats"
    )


    finished = [
        g
        for g in games
        if g["status"]
        == "finished"
    ]


    if not finished:

        st.info(
            "条件に該当する終了済み試合がありません。"
        )

        return


    wins = sum(
        1
        for g in finished
        if (
            g["our_score"]
            > g["their_score"]
        )
    )


    losses = sum(
        1
        for g in finished
        if (
            g["our_score"]
            < g["their_score"]
        )
    )


    draws = (
        len(finished)
        - wins
        - losses
    )


    game_ids = [
        g["id"]
        for g in finished
    ]


    batting_rows = (
        get_batting_rows(
            game_ids
        )
    )


    team_batting = (
        batting_stats(
            batting_rows
        )
    )


    total_runs = sum(
        int(
            g["our_score"]
        )
        for g in finished
    )


    total_allowed = sum(
        int(
            g["their_score"]
        )
        for g in finished
    )


    col1, col2, col3 = (
        st.columns(3)
    )


    col1.metric(
        "戦績",
        f"{wins}-{losses}-{draws}"
    )


    col2.metric(
        "総得点",
        total_runs
    )


    col3.metric(
        "総失点",
        total_allowed
    )


    st.metric(
        "チーム打率",
        format_avg(
            team_batting[
                "AVG"
            ]
        )
    )


    st.markdown(
        '<div class="section-title">'
        '試合結果・履歴'
        '</div>',
        unsafe_allow_html=True,
    )


    for game in finished:

        if (
            game["our_score"]
            > game["their_score"]
        ):

            mark = "○"

        elif (
            game["our_score"]
            < game["their_score"]
        ):

            mark = "●"

        else:

            mark = "△"


        meta_parts = [
            game["game_date"],
            game.get(
                "game_type"
            ),
            game.get(
                "place"
            ),
        ]


        meta = "｜".join(
            str(x)
            for x in meta_parts
            if x
        )


        st.markdown(
            f"""
            <div class="game-result">

                <div class="game-score">
                    {mark}
                    &nbsp;
                    {game["our_score"]}
                    -
                    {game["their_score"]}
                    &nbsp;
                    {game["opponent"]}
                </div>

                <div class="game-meta">
                    {meta}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


        with st.expander(
            "試合詳細"
        ):

            inning_score_table(
                game
            )


            if game.get(
                "tournament"
            ):

                st.caption(
                    "大会："
                    + game[
                        "tournament"
                    ]
                )


            st.markdown(
                "#### 打撃成績"
            )


            lineup = (
                get_lineup_players(
                    game["id"]
                )
            )


            if not lineup:

                st.caption(
                    "打撃記録なし"
                )


            for player in lineup:

                rows = (
                    get_batting_rows(
                        [game["id"]],
                        player["id"]
                    )
                )


                stats = (
                    batting_stats(
                        rows
                    )
                )


                st.write(
                    f'{player["name"]}　'
                    f'{stats["AB"]}打数 '
                    f'{stats["H"]}安打　'
                    f'{format_avg(stats["AVG"])}'
                )


            st.markdown(
                "#### 投手成績"
            )


            pitching_rows = (
                get_pitching_rows(
                    [game["id"]]
                )
            )


            pitcher_ids = []


            for row in pitching_rows:

                pid = (
                    row[
                        "pitcher_id"
                    ]
                )

                if pid not in pitcher_ids:

                    pitcher_ids.append(
                        pid
                    )


            if not pitcher_ids:

                st.caption(
                    "投手記録なし"
                )


            for pid in pitcher_ids:

                rows = [
                    row
                    for row
                    in pitching_rows
                    if (
                        row[
                            "pitcher_id"
                        ]
                        == pid
                    )
                ]


                stats = (
                    pitching_stats(
                        rows
                    )
                )


                st.write(
                    f'{player_name(pid)}　'
                    f'H {stats["H"]}　'
                    f'K {stats["SO"]}　'
                    f'BB {stats["BB"]}　'
                    f'R {stats["R"]}'
                )


# =========================================================
# STATS PAGE
# =========================================================

def stats_page():

    page_header(
        "成績確認",
        st.session_state.team[
            "team_name"
        ],
    )


    tab1, tab2, tab3 = (
        st.tabs([
            "個人成績",
            "ランキング",
            "チーム成績",
        ])
    )


    with tab1:

        individual_stats()


    with tab2:

        ranking_stats()


    with tab3:

        team_stats()


# =========================================================
# ROUTING
# =========================================================

if not st.session_state.team:

    team_gate()

    st.stop()


page = (
    st.session_state.page
)


if page == "ホーム":

    home_page()


elif page == "スコア入力":

    score_page()


elif page == "新規試合":

    new_game_page()


elif page == "選手登録":

    player_page()


elif page == "成績確認":

    stats_page()


else:

    st.session_state.page = (
        "ホーム"
    )

    rerun()
