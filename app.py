import streamlit as st
from supabase import create_client
from datetime import date, datetime
import random
import string

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
except Exception as e:
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
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>

/* ================================================
   BASE
================================================ */

.stApp {
    background:
        radial-gradient(circle at top right,
        rgba(36, 107, 70, 0.08),
        transparent 30%),
        #f6f7f5;
}

.block-container {
    max-width: 680px;
    padding-top: 2.2rem;
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

/* ================================================
   TYPOGRAPHY
================================================ */

h1, h2, h3 {
    letter-spacing: -0.03em;
}

.small-muted {
    font-size: 0.78rem;
    color: #7b817d;
}

.section-title {
    font-size: 0.78rem;
    font-weight: 800;
    color: #707771;
    letter-spacing: 0.08em;
    margin-top: 1.2rem;
    margin-bottom: 0.5rem;
}

/* ================================================
   BRAND
================================================ */

.brand-wrap {
    padding: 1.0rem 0 1.6rem 0;
}

.brand {
    font-size: 1.85rem;
    font-weight: 900;
    letter-spacing: -0.05em;
    color: #17251c;
    line-height: 1.1;
}

.brand-sub {
    color: #7a817c;
    font-size: 0.80rem;
    margin-top: 0.30rem;
}

/* ================================================
   CARD
================================================ */

.app-card {
    background: rgba(255,255,255,0.96);
    border: 1px solid #e6e9e6;
    border-radius: 20px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    box-shadow:
        0 1px 2px rgba(0,0,0,0.02),
        0 6px 22px rgba(0,0,0,0.025);
}

.soft-card {
    background: #eef2ef;
    border-radius: 16px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.7rem;
}

/* ================================================
   BUTTON
================================================ */

div.stButton > button {
    min-height: 48px;
    border-radius: 14px;
    border: 1px solid #e2e6e3;
    font-weight: 750;
    background: white;
    color: #17251c;
    box-shadow: 0 2px 8px rgba(0,0,0,0.025);
}

div.stButton > button:hover {
    border-color: #246b46;
    color: #17452f;
}

div.stButton > button[kind="primary"] {
    background: #174d34;
    color: white;
    border: none;
}

/* ================================================
   INPUT
================================================ */

div[data-baseweb="input"] > div {
    border-radius: 13px;
}

div[data-baseweb="select"] > div {
    border-radius: 13px;
}

div[data-testid="stNumberInput"] input {
    text-align: center;
    font-weight: 800;
}

/* ================================================
   SCORE
================================================ */

.score-card {
    background: #17251c;
    color: white;
    border-radius: 22px;
    padding: 1rem 1.1rem;
    margin: 0.45rem 0 0.9rem 0;
    box-shadow: 0 8px 25px rgba(23,37,28,0.14);
}

.score-top {
    text-align: center;
    font-size: 0.74rem;
    color: #cbd6cf;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.score-main {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 0.6rem;
}

.score-team {
    font-size: 0.78rem;
    font-weight: 750;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.score-team.right {
    text-align: right;
}

.score-number {
    font-size: 1.75rem;
    font-weight: 900;
    letter-spacing: 0.06em;
    white-space: nowrap;
}

/* ================================================
   PLAYER
================================================ */

.player-card {
    background: white;
    border: 1px solid #e5e9e6;
    border-radius: 18px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.8rem;
}

.player-name {
    font-size: 1.08rem;
    font-weight: 900;
    color: #17251c;
}

.player-sub {
    color: #747c76;
    font-size: 0.78rem;
    margin-top: 0.2rem;
}

/* ================================================
   SUCCESS
================================================ */

.success-card {
    background: #e8f7ee;
    border: 1px solid #b8e2c7;
    color: #155b35;
    border-radius: 17px;
    padding: 0.9rem 1rem;
    font-weight: 850;
    text-align: center;
    margin-bottom: 0.8rem;
    animation: popin 0.28s ease-out;
}

@keyframes popin {
    0% {
        opacity: 0;
        transform: scale(0.94);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}

/* ================================================
   GAME RESULT
================================================ */

.game-result {
    background: white;
    border: 1px solid #e4e8e5;
    border-radius: 18px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.6rem;
}

.game-score {
    font-size: 1.05rem;
    font-weight: 900;
    color: #18271e;
}

.game-meta {
    font-size: 0.74rem;
    color: #7b817d;
    margin-top: 0.25rem;
}

/* ================================================
   STAT
================================================ */

.stat-number {
    font-size: 1.35rem;
    font-weight: 900;
    color: #183d2b;
}

.stat-label {
    font-size: 0.68rem;
    color: #7b817d;
}

/* ================================================
   MOBILE
================================================ */

@media (max-width: 600px) {

    .block-container {
        padding-top: 2.8rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }

    .brand {
        font-size: 1.65rem;
    }

    .score-number {
        font-size: 1.55rem;
    }

    div.stButton > button {
        min-height: 50px;
        font-size: 0.92rem;
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


def db_select(table, columns="*"):
    return supabase.table(table).select(columns)


def make_team_code():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

    while True:
        code = "".join(random.choices(chars, k=6))

        result = (
            supabase.table("teams")
            .select("id")
            .eq("team_code", code)
            .execute()
            .data
        )

        if not result:
            return code


def make_owner_code():
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=12))


# =========================================================
# TEAM
# =========================================================

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
        raise RuntimeError("チーム作成に失敗しました。")

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

    return result[0] if result else None


def leave_team():
    st.session_state.team = None
    st.session_state.game_id = None
    st.session_state.page = "ホーム"
    rerun()


# =========================================================
# PLAYER
# =========================================================

def get_players(active_only=True):
    query = (
        supabase.table("players")
        .select("*")
        .eq("team_id", team_id())
    )

    if active_only:
        query = query.eq("active", True)

    return query.order("number").execute().data or []


def player_map():
    players = get_players(False)
    return {p["id"]: p for p in players}


def player_name(pid):
    if not pid:
        return "―"

    p = player_map().get(pid)

    if not p:
        return "―"

    number = p.get("number")

    if number:
        return f'{p["name"]} #{number}'

    return p["name"]


# =========================================================
# PLACES
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

    if not existing:
        supabase.table("places").insert({
            "team_id": team_id(),
            "name": name,
        }).execute()


# =========================================================
# GAME
# =========================================================

def get_game(game_id=None):
    gid = game_id or st.session_state.game_id

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

    return result[0] if result else None


def get_active_game():
    result = (
        supabase.table("games")
        .select("*")
        .eq("team_id", team_id())
        .eq("status", "playing")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
        .data
    )

    return result[0] if result else None


def update_game(values):
    if not st.session_state.game_id:
        return

    supabase.table("games").update(values).eq(
        "id", st.session_state.game_id
    ).execute()


def get_lineup(game_id=None):
    gid = game_id or st.session_state.game_id

    if not gid:
        return []

    rows = (
        supabase.table("lineup")
        .select("*")
        .eq("game_id", gid)
        .order("slot")
        .execute()
        .data
        or []
    )

    return rows


def get_lineup_players(game_id=None):
    rows = get_lineup(game_id)
    pmap = player_map()

    result = []

    for row in rows:
        p = pmap.get(row["player_id"])

        if p:
            result.append({
                **p,
                "slot": row["slot"],
            })

    return result


# =========================================================
# BATTING CALCULATION
# =========================================================

def get_batting_rows(game_ids=None, player_id=None):
    query = supabase.table("batting").select("*")

    if player_id:
        query = query.eq("player_id", player_id)

    rows = query.execute().data or []

    if game_ids is not None:
        game_ids = set(game_ids)
        rows = [r for r in rows if r["game_id"] in game_ids]

    return rows


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

    for r in rows:
        result = r["result"]
        hit_type = r.get("hit_type")

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

    stats["AVG"] = (
        stats["H"] / stats["AB"]
        if stats["AB"] else 0
    )

    obp_den = (
        stats["AB"]
        + stats["BB"]
        + stats["HBP"]
        + stats["SF"]
    )

    stats["OBP"] = (
        (stats["H"] + stats["BB"] + stats["HBP"]) / obp_den
        if obp_den else 0
    )

    total_bases = (
        stats["1B"]
        + stats["2B"] * 2
        + stats["3B"] * 3
        + stats["HR"] * 4
    )

    stats["SLG"] = (
        total_bases / stats["AB"]
        if stats["AB"] else 0
    )

    stats["OPS"] = stats["OBP"] + stats["SLG"]

    return stats


def format_avg(value):
    return f"{value:.3f}".replace("0.", ".")


# =========================================================
# PITCHING CALCULATION
# =========================================================

def get_pitching_rows(game_ids=None, pitcher_id=None):
    query = supabase.table("pitching").select("*")

    if pitcher_id:
        query = query.eq("pitcher_id", pitcher_id)

    rows = query.execute().data or []

    if game_ids is not None:
        game_ids = set(game_ids)
        rows = [r for r in rows if r["game_id"] in game_ids]

    return rows


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

    for r in rows:
        result = r["result"]

        stats["BF"] += 1
        stats["R"] += int(r.get("runs") or 0)

        if result in ["安打", "二塁打", "三塁打", "本塁打"]:
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
# GAME FILTER
# =========================================================

def get_games():
    return (
        supabase.table("games")
        .select("*")
        .eq("team_id", team_id())
        .order("game_date", desc=True)
        .execute()
        .data
        or []
    )


def game_filter_ui(key_prefix):
    games = get_games()

    if not games:
        return []

    st.markdown(
        '<div class="section-title">FILTER</div>',
        unsafe_allow_html=True,
    )

    period = st.radio(
        "期間",
        ["全期間", "期間指定"],
        horizontal=True,
        key=f"{key_prefix}_period",
        label_visibility="collapsed",
    )

    filtered = games[:]

    if period == "期間指定":
        c1, c2 = st.columns(2)

        with c1:
            start = st.date_input(
                "開始日",
                value=date.today().replace(month=1, day=1),
                key=f"{key_prefix}_start",
            )

        with c2:
            end = st.date_input(
                "終了日",
                value=date.today(),
                key=f"{key_prefix}_end",
            )

        filtered = [
            g for g in filtered
            if start <= date.fromisoformat(g["game_date"]) <= end
        ]

    game_types = sorted(
        set(
            g.get("game_type")
            for g in games
            if g.get("game_type")
        )
    )

    game_type = st.selectbox(
        "試合区分",
        ["全試合"] + game_types,
        key=f"{key_prefix}_type",
    )

    if game_type != "全試合":
        filtered = [
            g for g in filtered
            if g.get("game_type") == game_type
        ]

    tournaments = sorted(
        set(
            g.get("tournament")
            for g in games
            if g.get("tournament")
        )
    )

    tournament = st.selectbox(
        "大会",
        ["全大会"] + tournaments,
        key=f"{key_prefix}_tournament",
    )

    if tournament != "全大会":
        filtered = [
            g for g in filtered
            if g.get("tournament") == tournament
        ]

    places = sorted(
        set(
            g.get("place")
            for g in games
            if g.get("place")
        )
    )

    place = st.selectbox(
        "試合場所",
        ["全場所"] + places,
        key=f"{key_prefix}_place",
    )

    if place != "全場所":
        filtered = [
            g for g in filtered
            if g.get("place") == place
        ]

    return filtered


# =========================================================
# TEAM LOGIN
# =========================================================

def team_gate():
    st.markdown("""
        <div class="brand-wrap">
            <div class="brand">⚾ Baseball Score</div>
            <div class="brand-sub">
                チームの試合と成績を、ひとつに。
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([
        "チームに入る",
        "チームを作る",
    ])

    with tab1:
        st.markdown(
            '<div class="section-title">TEAM CODE</div>',
            unsafe_allow_html=True,
        )

        code = st.text_input(
            "チームコード",
            placeholder="例：RK7F29",
            max_chars=6,
            label_visibility="collapsed",
        )

        if st.button(
            "チームに入る",
            type="primary",
            use_container_width=True,
        ):
            if not code.strip():
                st.warning("チームコードを入力してください。")

            else:
                team = find_team(code)

                if team:
                    st.session_state.team = team

                    active = get_active_game()

                    if active:
                        st.session_state.game_id = active["id"]

                    flash(
                        f'{team["team_name"]} に入りました'
                    )

                    rerun()

                else:
                    st.error(
                        "チームが見つかりません。コードを確認してください。"
                    )

    with tab2:
        st.markdown(
            '<div class="section-title">CREATE TEAM</div>',
            unsafe_allow_html=True,
        )

        name = st.text_input(
            "チーム名",
            placeholder="例：りこなん",
        )

        if st.button(
            "新しいチームを作る",
            type="primary",
            use_container_width=True,
        ):
            if not name.strip():
                st.warning("チーム名を入力してください。")

            else:
                try:
                    team = create_team(name)

                    st.session_state.team = team

                    st.success("チームを作成しました！")

                    st.markdown(
                        f"""
                        <div class="app-card">
                            <div class="small-muted">
                                チームコード
                            </div>
                            <div style="
                                font-size:2rem;
                                font-weight:900;
                                letter-spacing:.15em;
                                margin-top:.2rem;
                            ">
                                {team["team_code"]}
                            </div>
                            <div class="small-muted"
                                 style="margin-top:.7rem;">
                                このコードをメンバーに共有してください
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.info(
                        "このチームコードは後からホームでも確認できます。"
                    )

                except Exception:
                    st.error(
                        "チームを作成できませんでした。もう一度お試しください。"
                    )


# =========================================================
# HEADER
# =========================================================

def page_header(title, subtitle=None):
    if st.session_state.page != "ホーム":
        if st.button(
            "‹ ホーム",
            key=f"back_{st.session_state.page}",
        ):
            go("ホーム")

    st.markdown(
        f"""
        <div style="margin:.7rem 0 1rem 0;">
            <div style="
                font-size:1.55rem;
                font-weight:900;
                letter-spacing:-.04em;
                color:#17251c;
            ">
                {title}
            </div>
            {
                f'<div class="small-muted">{subtitle}</div>'
                if subtitle else ''
            }
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# HOME
# =========================================================

def home_page():
    team = st.session_state.team

    st.markdown("""
        <div style="height:.5rem;"></div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="brand-wrap">
            <div class="brand">
                ⚾ {team["team_name"]}
            </div>
            <div class="brand-sub">
                Baseball Score & Stats
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    show_flash()

    active = get_active_game()

    if active:
        st.markdown(
            f"""
            <div class="app-card">
                <div class="small-muted">
                    LIVE GAME
                </div>
                <div style="
                    font-weight:900;
                    font-size:1.05rem;
                    margin-top:.25rem;
                ">
                    vs {active["opponent"]}
                </div>
                <div class="small-muted"
                     style="margin-top:.15rem;">
                    {active["current_inning"]}回
                    ・試合中
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
            st.session_state.game_id = active["id"]
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
        '<div class="section-title">TEAM</div>',
        unsafe_allow_html=True,
    )

    with st.expander("チーム情報"):
        st.caption("チームコード")

        st.code(team["team_code"])

        if st.button(
            "このチームから退出",
            use_container_width=True,
        ):
            leave_team()


# =========================================================
# PLAYER REGISTRATION
# =========================================================

def player_page():
    page_header(
        "選手登録",
        st.session_state.team["team_name"],
    )

    show_flash()

    st.markdown(
        '<div class="section-title">NEW PLAYER</div>',
        unsafe_allow_html=True,
    )

    with st.form("player_form", clear_on_submit=True):
        name = st.text_input(
            "選手名",
            placeholder="山田 太郎",
        )

        number = st.text_input(
            "背番号",
            placeholder="10",
        )

        submitted = st.form_submit_button(
            "選手を登録",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not name.strip():
                st.warning("選手名を入力してください。")

            else:
                existing = (
                    supabase.table("players")
                    .select("id")
                    .eq("team_id", team_id())
                    .eq("name", name.strip())
                    .execute()
                    .data
                )

                if existing:
                    st.warning(
                        "同じ名前の選手がすでに登録されています。"
                    )

                else:
                    supabase.table("players").insert({
                        "team_id": team_id(),
                        "name": name.strip(),
                        "number": number.strip() or None,
                        "active": True,
                    }).execute()

                    flash(
                        f"{name.strip()} を登録しました！"
                    )

                    rerun()

    players = get_players()

    st.markdown(
        f'<div class="section-title">PLAYERS　{len(players)}</div>',
        unsafe_allow_html=True,
    )

    if not players:
        st.info("まだ選手が登録されていません。")

    for p in players:
        number = (
            f'#{p["number"]}'
            if p.get("number")
            else ""
        )

        st.markdown(
            f"""
            <div class="player-card">
                <div class="player-name">
                    {p["name"]}
                </div>
                <div class="player-sub">
                    {number}
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
        st.session_state.team["team_name"],
    )

    players = get_players()

    if len(players) < 1:
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

    existing_places = [
        p["name"] for p in get_places()
    ]

    place_options = (
        existing_places
        + ["＋ 新しい場所を追加"]
    )

    place_choice = st.selectbox(
        "試合場所",
        place_options,
    )

    new_place = ""

    if place_choice == "＋ 新しい場所を追加":
        new_place = st.text_input(
            "場所を入力",
            placeholder="○○球場",
        )

    game_type = st.radio(
        "試合区分",
        ["練習試合", "公式戦"],
        horizontal=True,
    )

    tournament = None

    if game_type == "公式戦":
        tournament = st.text_input(
            "大会名",
            placeholder="○○大会",
        )

    bat_first_label = st.radio(
        "先攻・後攻",
        ["先攻", "後攻"],
        horizontal=True,
    )

    st.markdown(
        '<div class="section-title">LINEUP</div>',
        unsafe_allow_html=True,
    )

    player_labels = {
        p["id"]: (
            f'{p["name"]}'
            + (
                f' #{p["number"]}'
                if p.get("number")
                else ""
            )
        )
        for p in players
    }

    ids = list(player_labels.keys())

    lineup_ids = []

    lineup_count = min(9, len(ids))

    for i in range(lineup_count):
        choices = [
            pid for pid in ids
            if pid not in lineup_ids
        ]

        selected = st.selectbox(
            f"{i + 1}番",
            choices,
            format_func=lambda x: player_labels[x],
            key=f"lineup_{i}",
        )

        lineup_ids.append(selected)

    starter = st.selectbox(
        "先発投手",
        ids,
        format_func=lambda x: player_labels[x],
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

        else:
            if place_choice == "＋ 新しい場所を追加":
                place = new_place.strip()

                if place:
                    add_place(place)

            else:
                place = place_choice

            bat_first = (
                bat_first_label == "先攻"
            )

            initial_mode = (
                "offense"
                if bat_first
                else "defense"
            )

            result = (
                supabase.table("games")
                .insert({
                    "team_id": team_id(),
                    "game_date": str(game_date),
                    "opponent": opponent.strip(),
                    "place": place or None,
                    "game_type": game_type,
                    "tournament":
                        tournament.strip()
                        if tournament
                        else None,
                    "bat_first": bat_first,
                    "our_score": 0,
                    "their_score": 0,
                    "status": "playing",
                    "current_inning": 1,
                    "current_mode": initial_mode,
                    "current_batter_index": 0,
                    "current_pitcher_id": starter,
                })
                .execute()
                .data
            )

            game = result[0]

            lineup_rows = []

            for i, pid in enumerate(
                lineup_ids,
                start=1,
            ):
                lineup_rows.append({
                    "game_id": game["id"],
                    "slot": i,
                    "player_id": pid,
                })

            if lineup_rows:
                supabase.table("lineup").insert(
                    lineup_rows
                ).execute()

            st.session_state.game_id = game["id"]

            flash("試合を開始しました！")

            rerun()


# =========================================================
# SCORE HEADER
# =========================================================

def score_header(game):
    inning = game.get("current_inning") or 1
    mode = game.get("current_mode")

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
                {inning}回{half} ｜ {status}
            </div>

            <div class="score-main">
                <div class="score-team">
                    {st.session_state.team["team_name"]}
                </div>

                <div class="score-number">
                    {game["our_score"]}
                    <span style="
                        opacity:.45;
                        font-size:1rem;
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
    lineup = get_lineup_players()

    if not lineup:
        st.error("オーダーがありません。")
        return

    batter_index = (
        game.get("current_batter_index") or 0
    ) % len(lineup)

    batter = lineup[batter_index]

    today_rows = get_batting_rows(
        game_ids=[game["id"]],
        player_id=batter["id"],
    )

    today = batting_stats(today_rows)

    st.markdown(
        f"""
        <div class="player-card">
            <div class="small-muted">
                {batter_index + 1}番打者
            </div>

            <div class="player-name">
                {batter["name"]}
            </div>

            <div class="player-sub">
                今日　
                {today["AB"]}打数
                {today["H"]}安打
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
    )

    field = None
    batted_type = None
    hit_type = None

    if result in ["安打", "アウト"]:
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
        )

    if st.button(
        "この打席を登録",
        type="primary",
        use_container_width=True,
    ):
        supabase.table("batting").insert({
            "game_id": game["id"],
            "player_id": batter["id"],
            "inning": game["current_inning"],
            "result": result,
            "field": field,
            "batted_type": batted_type,
            "hit_type": hit_type,
        }).execute()

        next_index = (
            batter_index + 1
        ) % len(lineup)

        update_game({
            "current_batter_index": next_index,
        })

        flash(
            f'{batter["name"]}：{result} を登録'
        )

        rerun()

    if today_rows:
        if st.button(
            "↶ 直前の打席を取り消す",
            use_container_width=True,
        ):
            last = sorted(
                today_rows,
                key=lambda x: x.get(
                    "created_at", ""
                ),
            )[-1]

            supabase.table("batting").delete().eq(
                "id", last["id"]
            ).execute()

            previous_index = (
                batter_index - 1
            ) % len(lineup)

            update_game({
                "current_batter_index":
                    previous_index,
            })

            flash("直前の打席を取り消しました")

            rerun()


# =========================================================
# PITCHING INPUT
# =========================================================

def pitching_input(game):
    players = get_players()

    current_pitcher = game.get(
        "current_pitcher_id"
    )

    p = next(
        (
            x for x in players
            if x["id"] == current_pitcher
        ),
        None,
    )

    if not p and players:
        p = players[0]

    if not p:
        st.warning("投手が登録されていません。")
        return

    rows = get_pitching_rows(
        game_ids=[game["id"]],
        pitcher_id=p["id"],
    )

    stats = pitching_stats(rows)

    st.markdown(
        f"""
        <div class="player-card">
            <div class="small-muted">
                PITCHER
            </div>

            <div class="player-name">
                {p["name"]}
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
    )

    runs = st.number_input(
        "このプレーで入った得点",
        min_value=0,
        max_value=10,
        value=0,
        step=1,
    )

    if st.button(
        "結果を登録",
        type="primary",
        use_container_width=True,
    ):
        supabase.table("pitching").insert({
            "game_id": game["id"],
            "pitcher_id": p["id"],
            "inning": game["current_inning"],
            "result": result,
            "runs": int(runs),
        }).execute()

        flash(f"{result} を登録しました")

        rerun()

    if rows:
        if st.button(
            "↶ 直前の投球結果を取り消す",
            use_container_width=True,
        ):
            last = sorted(
                rows,
                key=lambda x: x.get(
                    "created_at", ""
                ),
            )[-1]

            supabase.table("pitching").delete().eq(
                "id", last["id"]
            ).execute()

            flash(
                "直前の投球結果を取り消しました"
            )

            rerun()


# =========================================================
# SIDE SWITCH
# =========================================================

def side_switch_panel(game):
    st.markdown(
        '<div class="section-title">GAME CONTROL</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "攻守交替",
            use_container_width=True,
        ):
            st.session_state.switch_open = (
                not st.session_state.switch_open
            )

    with c2:
        if st.button(
            "選手交代",
            use_container_width=True,
        ):
            st.session_state.sub_open = (
                not st.session_state.sub_open
            )

    if st.session_state.switch_open:
        st.markdown(
            '<div class="soft-card">',
            unsafe_allow_html=True,
        )

        runs = st.number_input(
            "この回の得点",
            min_value=0,
            max_value=30,
            value=0,
            step=1,
            key="switch_runs",
        )

        if st.button(
            "攻守を交替する",
            type="primary",
            use_container_width=True,
        ):
            current_mode = game["current_mode"]

            side = (
                "our"
                if current_mode == "offense"
                else "their"
            )

            supabase.table(
                "inning_scores"
            ).insert({
                "game_id": game["id"],
                "inning": game["current_inning"],
                "side": side,
                "runs": int(runs),
            }).execute()

            values = {}

            if current_mode == "offense":
                values["our_score"] = (
                    int(game["our_score"])
                    + int(runs)
                )

                values["current_mode"] = "defense"

                if not game["bat_first"]:
                    values["current_inning"] = (
                        game["current_inning"] + 1
                    )

            else:
                values["their_score"] = (
                    int(game["their_score"])
                    + int(runs)
                )

                values["current_mode"] = "offense"

                if game["bat_first"]:
                    values["current_inning"] = (
                        game["current_inning"] + 1
                    )

            update_game(values)

            st.session_state.switch_open = False

            flash("攻守を交替しました")

            rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


# =========================================================
# SUBSTITUTION
# =========================================================

def substitution_panel(game):
    if not st.session_state.sub_open:
        return

    players = get_players()
    lineup = get_lineup_players()

    st.markdown(
        '<div class="section-title">SUBSTITUTION</div>',
        unsafe_allow_html=True,
    )

    sub_type = st.radio(
        "交代",
        ["代打", "投手交代"],
        horizontal=True,
    )

    if sub_type == "代打":
        if not lineup:
            return

        slot = st.selectbox(
            "打順",
            [p["slot"] for p in lineup],
            format_func=lambda x:
                f"{x}番",
        )

        current = next(
            p for p in lineup
            if p["slot"] == slot
        )

        lineup_ids = {
            p["id"] for p in lineup
        }

        candidates = [
            p for p in players
            if p["id"] not in lineup_ids
        ]

        if not candidates:
            st.info(
                "交代できる控え選手がいません。"
            )

        else:
            new_pid = st.selectbox(
                "新しい選手",
                [p["id"] for p in candidates],
                format_func=lambda x:
                    player_name(x),
            )

            if st.button(
                "代打を登録",
                type="primary",
                use_container_width=True,
            ):
                (
                    supabase.table("lineup")
                    .update({
                        "player_id": new_pid
                    })
                    .eq("game_id", game["id"])
                    .eq("slot", slot)
                    .execute()
                )

                supabase.table(
                    "substitutions"
                ).insert({
                    "game_id": game["id"],
                    "inning":
                        game["current_inning"],
                    "substitution_type":
                        "代打",
                    "old_player_id":
                        current["id"],
                    "new_player_id":
                        new_pid,
                }).execute()

                st.session_state.sub_open = False

                flash("代打を登録しました")

                rerun()

    else:
        current_pid = game.get(
            "current_pitcher_id"
        )

        candidates = [
            p for p in players
            if p["id"] != current_pid
        ]

        if not candidates:
            st.info(
                "交代できる投手がいません。"
            )

        else:
            new_pid = st.selectbox(
                "新しい投手",
                [p["id"] for p in candidates],
                format_func=lambda x:
                    player_name(x),
            )

            if st.button(
                "投手交代を登録",
                type="primary",
                use_container_width=True,
            ):
                update_game({
                    "current_pitcher_id":
                        new_pid,
                })

                supabase.table(
                    "substitutions"
                ).insert({
                    "game_id": game["id"],
                    "inning":
                        game["current_inning"],
                    "substitution_type":
                        "投手交代",
                    "old_player_id":
                        current_pid,
                    "new_player_id":
                        new_pid,
                }).execute()

                st.session_state.sub_open = False

                flash("投手を交代しました")

                rerun()


# =========================================================
# FINISH GAME
# =========================================================

def finish_game_panel(game):
    if st.button(
        "ゲームセット",
        use_container_width=True,
    ):
        st.session_state.finish_open = (
            not st.session_state.finish_open
        )

    if st.session_state.finish_open:
        st.warning(
            "この試合を終了しますか？"
        )

        c1, c2 = st.columns(2)

        with c1:
            if st.button(
                "終了する",
                type="primary",
                use_container_width=True,
            ):
                update_game({
                    "status": "finished"
                })

                st.session_state.game_id = None
                st.session_state.finish_open = False

                flash("試合を終了しました！")

                go("ホーム")

        with c2:
            if st.button(
                "キャンセル",
                use_container_width=True,
            ):
                st.session_state.finish_open = False
                rerun()


# =========================================================
# SCORE PAGE
# =========================================================

def score_page():
    page_header(
        "スコア入力",
        st.session_state.team["team_name"],
    )

    show_flash()

    game = get_game()

    if not game:
        active = get_active_game()

        if active:
            st.session_state.game_id = active["id"]
            game = active

        else:
            st.info(
                "現在進行中の試合はありません。"
            )

            if st.button(
                "＋ 新しい試合を始める",
                type="primary",
                use_container_width=True,
            ):
                go("新規試合")

            return

    score_header(game)

    if game["current_mode"] == "offense":
        batting_input(game)

    else:
        pitching_input(game)

    side_switch_panel(game)
    substitution_panel(game)

    st.markdown("<br>", unsafe_allow_html=True)

    finish_game_panel(game)


# =========================================================
# INDIVIDUAL STATS
# =========================================================

def individual_stats():
    games = game_filter_ui("individual")

    if not games:
        st.info(
            "条件に該当する試合がありません。"
        )
        return

    game_ids = [g["id"] for g in games]

    players = get_players(False)

    if not players:
        return

    player_id = st.selectbox(
        "選手",
        [p["id"] for p in players],
        format_func=lambda x:
            player_name(x),
        key="individual_player",
    )

    batting_tab, pitching_tab = st.tabs([
        "打撃",
        "投手",
    ])

    with batting_tab:
        rows = get_batting_rows(
            game_ids,
            player_id,
        )

        s = batting_stats(rows)

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "打率",
            format_avg(s["AVG"]),
        )

        c2.metric(
            "出塁率",
            format_avg(s["OBP"]),
        )

        c3.metric(
            "OPS",
            format_avg(s["OPS"]),
        )

        st.markdown(
            f"""
            <div class="app-card">
                打席　<b>{s["PA"]}</b><br>
                打数　<b>{s["AB"]}</b><br>
                安打　<b>{s["H"]}</b><br>
                二塁打　<b>{s["2B"]}</b><br>
                三塁打　<b>{s["3B"]}</b><br>
                本塁打　<b>{s["HR"]}</b><br>
                四球　<b>{s["BB"]}</b><br>
                死球　<b>{s["HBP"]}</b><br>
                三振　<b>{s["SO"]}</b><br>
                犠打　<b>{s["SH"]}</b><br>
                犠飛　<b>{s["SF"]}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with pitching_tab:
        rows = get_pitching_rows(
            game_ids,
            player_id,
        )

        s = pitching_stats(rows)

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "対戦打者",
            s["BF"],
        )

        c2.metric(
            "奪三振",
            s["SO"],
        )

        c3.metric(
            "失点",
            s["R"],
        )

        st.markdown(
            f"""
            <div class="app-card">
                被安打　<b>{s["H"]}</b><br>
                被本塁打　<b>{s["HR"]}</b><br>
                四球　<b>{s["BB"]}</b><br>
                死球　<b>{s["HBP"]}</b><br>
                奪三振　<b>{s["SO"]}</b><br>
                失点　<b>{s["R"]}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "※ 現在は走者・失策による自責点判定を記録していないため、防御率ではなく失点を表示しています。"
        )


# =========================================================
# RANKINGS
# =========================================================

def ranking_stats():
    games = game_filter_ui("ranking")

    if not games:
        st.info(
            "条件に該当する試合がありません。"
        )
        return

    game_ids = [g["id"] for g in games]
    players = get_players(False)

    category = st.selectbox(
        "ランキング",
        [
            "打率",
            "安打",
            "本塁打",
            "打点以外のOPS",
            "奪三振",
        ],
    )

    ranking = []

    for p in players:
        if category in [
            "打率",
            "安打",
            "本塁打",
            "打点以外のOPS",
        ]:
            rows = get_batting_rows(
                game_ids,
                p["id"],
            )

            s = batting_stats(rows)

            if category == "打率":
                value = s["AVG"]

            elif category == "安打":
                value = s["H"]

            elif category == "本塁打":
                value = s["HR"]

            else:
                value = s["OPS"]

        else:
            rows = get_pitching_rows(
                game_ids,
                p["id"],
            )

            s = pitching_stats(rows)

            value = s["SO"]

        ranking.append(
            (p["name"], value)
        )

    ranking.sort(
        key=lambda x: x[1],
        reverse=True,
    )

    for i, (name, value) in enumerate(
        ranking,
        start=1,
    ):
        if category in [
            "打率",
            "打点以外のOPS",
        ]:
            display = format_avg(value)

        else:
            display = str(value)

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
                            color:#7c847e;
                            font-size:.8rem;
                            margin-right:.7rem;
                        ">
                            {i}
                        </span>

                        <b>{name}</b>
                    </div>

                    <div style="
                        font-size:1.15rem;
                        font-weight:900;
                        color:#174d34;
                    ">
                        {display}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# GAME HISTORY
# =========================================================

def inning_score_table(game):
    rows = (
        supabase.table("inning_scores")
        .select("*")
        .eq("game_id", game["id"])
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
        set(r["inning"] for r in rows)
    )

    header = "| チーム | " + " | ".join(
        str(i) for i in innings
    ) + " | 計 |"

    divider = "|---|" + "|".join(
        ["---"] * len(innings)
    ) + "|---|"

    our_values = []

    their_values = []

    for inning in innings:
        our = next(
            (
                r["runs"] for r in rows
                if r["inning"] == inning
                and r["side"] == "our"
            ),
            "-",
        )

        their = next(
            (
                r["runs"] for r in rows
                if r["inning"] == inning
                and r["side"] == "their"
            ),
            "-",
        )

        our_values.append(str(our))
        their_values.append(str(their))

    our_line = (
        f'| {st.session_state.team["team_name"]} | '
        + " | ".join(our_values)
        + f' | {game["our_score"]} |'
    )

    their_line = (
        f'| {game["opponent"]} | '
        + " | ".join(their_values)
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
    games = game_filter_ui("teamstats")

    finished = [
        g for g in games
        if g["status"] == "finished"
    ]

    if not finished:
        st.info(
            "条件に該当する終了済み試合がありません。"
        )
        return

    wins = sum(
        1 for g in finished
        if g["our_score"] > g["their_score"]
    )

    losses = sum(
        1 for g in finished
        if g["our_score"] < g["their_score"]
    )

    draws = len(finished) - wins - losses

    game_ids = [g["id"] for g in finished]

    batting_rows = get_batting_rows(game_ids)
    team_bat = batting_stats(batting_rows)

    total_for = sum(
        g["our_score"] for g in finished
    )

    total_against = sum(
        g["their_score"] for g in finished
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "戦績",
        f"{wins}-{losses}-{draws}",
    )

    c2.metric(
        "総得点",
        total_for,
    )

    c3.metric(
        "総失点",
        total_against,
    )

    st.metric(
        "チーム打率",
        format_avg(team_bat["AVG"]),
    )

    st.markdown(
        '<div class="section-title">試合結果・履歴</div>',
        unsafe_allow_html=True,
    )

    for game in finished:
        if game["our_score"] > game["their_score"]:
            mark = "○"

        elif game["our_score"] < game["their_score"]:
            mark = "●"

        else:
            mark = "△"

        meta_parts = [
            game["game_date"],
            game.get("game_type"),
            game.get("place"),
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
            "この試合の詳細"
        ):
            inning_score_table(game)

            if game.get("tournament"):
                st.caption(
                    f'大会：{game["tournament"]}'
                )

            st.markdown("#### 打撃")

            lineup = get_lineup_players(
                game["id"]
            )

            for p in lineup:
                rows = get_batting_rows(
                    [game["id"]],
                    p["id"],
                )

                s = batting_stats(rows)

                st.write(
                    f'{p["name"]}　'
                    f'{s["AB"]}打数 '
                    f'{s["H"]}安打 '
                    f'打率 {format_avg(s["AVG"])}'
                )

            st.markdown("#### 投手")

            pitching_rows = get_pitching_rows(
                [game["id"]]
            )

            pitcher_ids = []

            for row in pitching_rows:
                if (
                    row["pitcher_id"]
                    not in pitcher_ids
                ):
                    pitcher_ids.append(
                        row["pitcher_id"]
                    )

            for pid in pitcher_ids:
                rows = [
                    r for r in pitching_rows
                    if r["pitcher_id"] == pid
                ]

                s = pitching_stats(rows)

                st.write(
                    f'{player_name(pid)}　'
                    f'H {s["H"]} '
                    f'K {s["SO"]} '
                    f'BB {s["BB"]} '
                    f'R {s["R"]}'
                )


# =========================================================
# STATS PAGE
# =========================================================

def stats_page():
    page_header(
        "成績確認",
        st.session_state.team["team_name"],
    )

    tab1, tab2, tab3 = st.tabs([
        "個人成績",
        "ランキング",
        "チーム成績",
    ])

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


page = st.session_state.page


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
    st.session_state.page = "ホーム"
    rerun()
