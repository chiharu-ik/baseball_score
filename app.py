import streamlit as st
from supabase import create_client
from datetime import date
import random
import html


# =========================================================
# CONFIG
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
        st.secrets["SUPABASE_KEY"],
    )
except Exception:
    st.error("Supabaseへの接続設定を確認してください。")
    st.stop()


# =========================================================
# SESSION
# =========================================================

DEFAULTS = {
    "page": "ホーム",
    "team": None,
    "game_id": None,
    "team_gate_mode": None,
    "created_team": None,
    "switch_open": False,
    "sub_open": False,
    "finish_open": False,
    "tiebreak_open": False,
    "edit_batting_id": None,
    "delete_batting_id": None,
    "edit_pitching_id": None,
    "delete_pitching_id": None,
    "flash_message": None,
    "selected_history_game": None,
    "recent_teams": [],
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        if isinstance(value, list):
            st.session_state[key] = value.copy()
        else:
            st.session_state[key] = value


# =========================================================
# STYLE
# =========================================================

st.markdown(
    """
<style>

:root {
    --green: #123c2b;
    --green2: #19543a;
    --green-soft: #edf5f0;
    --bg: #f7f8f7;
    --border: #e1e6e2;
    --text: #172019;
    --muted: #788079;
}

.stApp {
    background: #f7f8f7;
}

.block-container {
    max-width: 620px;
    padding-top: 2.3rem;
    padding-bottom: 5rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu,
footer {
    visibility: hidden;
}

h1,
h2,
h3 {
    color: #172019;
}


/* =========================================================
   BUTTON
   ========================================================= */

div.stButton > button {
    width: 100%;
    min-height: 52px;
    border-radius: 15px;
    border: 1px solid #dce3de;
    background: #ffffff;
    color: #172019;
    font-weight: 750;
    font-size: .94rem;
    box-shadow: 0 2px 8px rgba(0,0,0,.025);
}

div.stButton > button:hover {
    border-color: #123c2b;
    color: #123c2b;
}

div.stButton > button[kind="primary"] {
    background: #123c2b;
    color: #ffffff;
    border-color: #123c2b;
}

div.stButton > button[kind="primary"]:hover {
    background: #19543a;
    color: #ffffff;
}


/* =========================================================
   INPUT
   ========================================================= */

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    border-radius: 13px;
}

div[data-testid="stNumberInput"] input {
    text-align: center;
}


/* =========================================================
   ALERT
   黄色背景＋白文字を完全にやめる
   ========================================================= */

div[data-testid="stAlert"] {
    background-color: #ffffff !important;
    border: 1px solid #d9e1dc !important;
    border-left: 5px solid #123c2b !important;
    border-radius: 14px !important;
    color: #172019 !important;
    padding: .85rem 1rem !important;
}

div[data-testid="stAlert"] * {
    color: #172019 !important;
}

div[data-testid="stAlert"] svg {
    color: #123c2b !important;
    fill: #123c2b !important;
}


/* =========================================================
   TEXT
   ========================================================= */

.bs-logo {
    font-size: 1.75rem;
    font-weight: 900;
    letter-spacing: -.055em;
    color: #132019;
    margin-bottom: .2rem;
}

.bs-title {
    font-size: 1.55rem;
    font-weight: 900;
    letter-spacing: -.045em;
    color: #152019;
    margin-bottom: .25rem;
}

.bs-caption {
    color: #858c87;
    font-size: .74rem;
    font-weight: 700;
}

.bs-section {
    margin-top: 1.45rem;
    margin-bottom: .55rem;
    font-size: .67rem;
    font-weight: 900;
    letter-spacing: .13em;
    color: #7b837d;
}


/* =========================================================
   TEAM
   ========================================================= */

.team-top {
    padding: .1rem 0 .9rem 0;
}

.team-name {
    font-size: 1.65rem;
    font-weight: 900;
    letter-spacing: -.05em;
    color: #142019;
}

.team-code-inline {
    display: inline-block;
    margin-top: .38rem;
    padding: .32rem .62rem;
    background: #edf2ef;
    border-radius: 8px;
    color: #526058;
    font-size: .69rem;
    font-weight: 850;
    letter-spacing: .06em;
}

.team-code-card {
    background: #123c2b;
    border-radius: 18px;
    padding: 1rem 1.1rem;
    margin: .65rem 0;
    color: #ffffff;
}

.team-code-label {
    font-size: .62rem;
    letter-spacing: .15em;
    font-weight: 900;
    color: #bcd0c4;
}

.team-code-value {
    font-size: 1.45rem;
    letter-spacing: .13em;
    font-weight: 900;
    margin-top: .15rem;
}

.team-code-name {
    margin-top: .25rem;
    font-size: .74rem;
    color: #d7e4dc;
}


/* =========================================================
   CARDS
   ========================================================= */

.player-box {
    background: #ffffff;
    border: 1px solid #e2e7e4;
    border-radius: 15px;
    padding: .8rem .9rem;
    margin-bottom: .55rem;
}

.player-name {
    font-weight: 900;
    color: #172019;
}

.player-meta {
    color: #7b837d;
    font-size: .72rem;
    margin-top: .15rem;
}

.history-card {
    background: #ffffff;
    border: 1px solid #e2e7e4;
    border-radius: 15px;
    padding: .85rem .9rem;
    margin: .55rem 0 .25rem 0;
}

.history-score {
    font-weight: 900;
    font-size: .96rem;
    color: #172019;
}

.history-meta {
    color: #7b837d;
    font-size: .7rem;
    margin-top: .2rem;
}

.success-box {
    padding: .8rem 1rem;
    background: #edf7f1;
    border: 1px solid #c9dfd1;
    border-left: 5px solid #17613a;
    border-radius: 14px;
    color: #17613a;
    font-size: .85rem;
    font-weight: 850;
    margin-bottom: .8rem;
}


/* =========================================================
   SCORE
   ========================================================= */

.score-box {
    background: #123c2b;
    color: #ffffff;
    border-radius: 18px;
    padding: .85rem 1rem;
    margin: .4rem 0 .8rem 0;
}

.score-status {
    text-align: center;
    font-size: .67rem;
    font-weight: 800;
    color: #bcd0c4;
}

.score-row {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: .45rem;
    align-items: center;
    margin-top: .35rem;
}

.score-team {
    font-size: .7rem;
    font-weight: 800;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.score-team.right {
    text-align: right;
}

.score-number {
    font-size: 1.4rem;
    font-weight: 900;
    white-space: nowrap;
}


/* =========================================================
   MOBILE
   ========================================================= */

@media(max-width:600px) {

    .block-container {
        padding-top: 2.5rem;
        padding-left: .8rem;
        padding-right: .8rem;
    }

    .team-name {
        font-size: 1.5rem;
    }

    div.stButton > button {
        min-height: 53px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================

def esc(value):
    if value is None:
        return ""
    return html.escape(str(value))


def go(page):
    st.session_state.page = page
    st.rerun()


def team_id():
    if st.session_state.team:
        return st.session_state.team["id"]
    return None


def flash(message):
    st.session_state.flash_message = message


def show_flash():
    message = st.session_state.get("flash_message")

    if not message:
        return

    st.toast(message, icon="✅")

    st.markdown(
        f'<div class="success-box">✓ {esc(message)}</div>',
        unsafe_allow_html=True,
    )

    st.session_state.flash_message = None


def section(text):
    st.markdown(
        f'<div class="bs-section">{esc(text)}</div>',
        unsafe_allow_html=True,
    )


def page_header(title, subtitle=None):
    if st.button(
        "‹ ホーム",
        key=f"back_{title}",
        use_container_width=False,
    ):
        go("ホーム")

    st.markdown(
        f'<div class="bs-title">{esc(title)}</div>',
        unsafe_allow_html=True,
    )

    if subtitle:
        st.caption(subtitle)


def safe_date(value):
    try:
        return date.fromisoformat(str(value))
    except Exception:
        return date.today()


# =========================================================
# RECENT TEAMS
# =========================================================

def add_recent_team(team):
    if not team:
        return

    existing = [
        t
        for t in st.session_state.recent_teams
        if t.get("id") != team.get("id")
    ]

    st.session_state.recent_teams = [
        {
            "id": team["id"],
            "team_name": team["team_name"],
            "team_code": team["team_code"],
        }
    ] + existing

    st.session_state.recent_teams = st.session_state.recent_teams[:8]


def open_team(team):
    result = (
        supabase.table("teams")
        .select("*")
        .eq("id", team["id"])
        .execute()
        .data
    )

    if not result:
        st.error("このチームが見つかりませんでした。")
        return

    selected = result[0]

    st.session_state.team = selected
    st.session_state.page = "ホーム"
    st.session_state.game_id = None
    st.session_state.team_gate_mode = None
    st.session_state.selected_history_game = None

    add_recent_team(selected)

    active = get_active_game()

    if active:
        st.session_state.game_id = active["id"]

    st.rerun()


def change_team():
    if st.session_state.team:
        add_recent_team(st.session_state.team)

    st.session_state.team = None
    st.session_state.game_id = None
    st.session_state.page = "ホーム"
    st.session_state.team_gate_mode = None
    st.session_state.created_team = None
    st.session_state.selected_history_game = None
    st.session_state.switch_open = False
    st.session_state.sub_open = False
    st.session_state.finish_open = False
    st.session_state.tiebreak_open = False
    st.session_state.edit_batting_id = None
    st.session_state.delete_batting_id = None
    st.session_state.edit_pitching_id = None
    st.session_state.delete_pitching_id = None

    st.rerun()


# =========================================================
# TEAM
# =========================================================

TEAM_CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def make_team_code():
    for _ in range(100):
        code = "".join(
            random.choices(
                TEAM_CODE_CHARS,
                k=6,
            )
        )

        result = (
            supabase.table("teams")
            .select("id")
            .eq("team_code", code)
            .execute()
            .data
        )

        if not result:
            return code

    raise RuntimeError(
        "チームコードを発行できませんでした。"
    )


def make_owner_code():
    return "".join(
        random.choices(
            TEAM_CODE_CHARS,
            k=12,
        )
    )


def create_team(name):
    result = (
        supabase.table("teams")
        .insert(
            {
                "team_name": name.strip(),
                "team_code": make_team_code(),
                "owner_code": make_owner_code(),
            }
        )
        .execute()
        .data
    )

    if not result:
        raise RuntimeError(
            "チームを作成できませんでした。"
        )

    return result[0]


def find_team(code):
    result = (
        supabase.table("teams")
        .select("*")
        .eq(
            "team_code",
            code.strip().upper(),
        )
        .execute()
        .data
    )

    return result[0] if result else None


# =========================================================
# PLAYERS
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
            True,
        )

    return (
        query
        .order("name")
        .execute()
        .data
        or []
    )


def get_player_map():
    return {
        p["id"]: p
        for p in get_players(False)
    }


def player_name(pid):
    p = get_player_map().get(pid)

    if not p:
        return "―"

    if p.get("number"):
        return (
            f'{p["name"]} '
            f'#{p["number"]}'
        )

    return p["name"]


def filter_players_by_grade(
    players,
    selected_grades,
):
    if not selected_grades:
        return players

    return [
        p
        for p in players
        if (
            p.get("grade")
            or "未設定"
        ) in selected_grades
    ]


def grade_filter(players, key):
    grades = [
        "1年",
        "2年",
        "3年",
        "4年",
        "その他",
    ]

    if any(
        not p.get("grade")
        for p in players
    ):
        grades.append("未設定")

    return st.multiselect(
        "学年",
        grades,
        placeholder="全学年",
        key=key,
    )


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
        (
            supabase.table("places")
            .insert(
                {
                    "team_id": team_id(),
                    "name": name,
                }
            )
            .execute()
        )


# =========================================================
# GAMES
# =========================================================

def get_games():
    return (
        supabase.table("games")
        .select("*")
        .eq("team_id", team_id())
        .order(
            "game_date",
            desc=True,
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

    return result[0] if result else None


def get_active_game():
    if not team_id():
        return None

    result = (
        supabase.table("games")
        .select("*")
        .eq("team_id", team_id())
        .eq("status", "playing")
        .order(
            "created_at",
            desc=True,
        )
        .limit(1)
        .execute()
        .data
    )

    return result[0] if result else None


def update_game(values):
    if not st.session_state.game_id:
        return

    (
        supabase.table("games")
        .update(values)
        .eq(
            "id",
            st.session_state.game_id,
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
    pmap = get_player_map()
    result = []

    for row in get_lineup(game_id):
        player = pmap.get(
            row["player_id"]
        )

        if player:
            result.append(
                {
                    **player,
                    "slot": row["slot"],
                }
            )

    return result


# =========================================================
# BATTING
# =========================================================

def get_batting_rows(
    game_ids=None,
    player_id=None,
):
    team_game_ids = {
        g["id"]
        for g in get_games()
    }

    if game_ids is None:
        allowed = team_game_ids
    else:
        allowed = (
            team_game_ids
            & set(game_ids)
        )

    if not allowed:
        return []

    query = (
        supabase.table("batting")
        .select("*")
    )

    if player_id:
        query = query.eq(
            "player_id",
            player_id,
        )

    rows = (
        query
        .order("created_at")
        .execute()
        .data
        or []
    )

    return [
        r
        for r in rows
        if r["game_id"] in allowed
    ]


def batting_stats(rows):
    s = {
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
        "E": 0,
        "SH": 0,
        "SF": 0,
        "RBI": 0,
    }

    for row in rows:
        result = row["result"]
        hit_type = row.get(
            "hit_type"
        )

        s["PA"] += 1
        s["RBI"] += int(row.get("rbi") or 0)

        if result == "四球":
            s["BB"] += 1

        elif result == "死球":
            s["HBP"] += 1

        elif result == "犠打":
            s["SH"] += 1

        elif result == "犠飛":
            s["SF"] += 1

        else:
            s["AB"] += 1

            if result == "三振":
                s["SO"] += 1

            if result == "失策":
                s["E"] += 1

            if result == "安打":
                s["H"] += 1

                if hit_type == "単打":
                    s["1B"] += 1

                elif hit_type == "二塁打":
                    s["2B"] += 1

                elif hit_type == "三塁打":
                    s["3B"] += 1

                elif hit_type == "本塁打":
                    s["HR"] += 1

    s["AVG"] = (
        s["H"] / s["AB"]
        if s["AB"]
        else 0
    )

    obp_denom = (
        s["AB"]
        + s["BB"]
        + s["HBP"]
        + s["SF"]
    )

    s["OBP"] = (
        (
            s["H"]
            + s["BB"]
            + s["HBP"]
        )
        / obp_denom
        if obp_denom
        else 0
    )

    total_bases = (
        s["1B"]
        + 2 * s["2B"]
        + 3 * s["3B"]
        + 4 * s["HR"]
    )

    s["SLG"] = (
        total_bases / s["AB"]
        if s["AB"]
        else 0
    )

    s["OPS"] = (
        s["OBP"]
        + s["SLG"]
    )

    return s


def format_avg(value):
    return (
        f"{value:.3f}"
        .replace(
            "0.",
            ".",
        )
    )


# =========================================================
# PITCHING
# =========================================================

def get_pitching_rows(
    game_ids=None,
    pitcher_id=None,
):
    team_game_ids = {
        g["id"]
        for g in get_games()
    }

    if game_ids is None:
        allowed = team_game_ids
    else:
        allowed = (
            team_game_ids
            & set(game_ids)
        )

    if not allowed:
        return []

    query = (
        supabase.table("pitching")
        .select("*")
    )

    if pitcher_id:
        query = query.eq(
            "pitcher_id",
            pitcher_id,
        )

    rows = (
        query
        .order("created_at")
        .execute()
        .data
        or []
    )

    return [
        r
        for r in rows
        if r["game_id"] in allowed
    ]


def pitching_stats(rows):
    s = {
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

        s["BF"] += 1

        s["R"] += int(
            row.get("runs")
            or 0
        )

        if result in [
            "安打",
            "二塁打",
            "三塁打",
            "本塁打",
        ]:
            s["H"] += 1

        if result == "本塁打":
            s["HR"] += 1

        elif result == "四球":
            s["BB"] += 1

        elif result == "死球":
            s["HBP"] += 1

        elif result == "三振":
            s["SO"] += 1

    return s


# =========================================================
# TEAM GATE
# =========================================================

def team_gate():
    st.markdown(
        '<div class="bs-logo">'
        '⚾ Baseball Score'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="bs-caption">'
        '使用するチームを選択してください'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.created_team:
        team = (
            st.session_state.created_team
        )

        st.markdown(
            '<div class="success-box">'
            '✓ チームを作成しました'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="team-code-card">'
            f'<div class="team-code-label">'
            f'TEAM CODE'
            f'</div>'
            f'<div class="team-code-value">'
            f'{esc(team["team_code"])}'
            f'</div>'
            f'<div class="team-code-name">'
            f'{esc(team["team_name"])}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "初めて参加するメンバーには、"
            "このコードを共有してください。"
        )

        if st.button(
            f'⚾ {team["team_name"]} を開く',
            type="primary",
            use_container_width=True,
        ):
            add_recent_team(team)

            st.session_state.team = team
            st.session_state.created_team = None
            st.session_state.page = "ホーム"

            st.rerun()

        return

    mode = (
        st.session_state.team_gate_mode
    )

    if mode is None:
        if st.session_state.recent_teams:
            section(
                "最近使ったチーム"
            )

            for i, team in enumerate(
                st.session_state.recent_teams
            ):
                if st.button(
                    f'⚾  {team["team_name"]}　›',
                    key=(
                        f"recent_"
                        f"{team['id']}_"
                        f"{i}"
                    ),
                    use_container_width=True,
                ):
                    open_team(team)

        section("その他")

        if st.button(
            "🔑  チームコードで参加",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.team_gate_mode = (
                "join"
            )
            st.rerun()

        if st.button(
            "＋  新しいチームを作成",
            use_container_width=True,
        ):
            st.session_state.team_gate_mode = (
                "create"
            )
            st.rerun()

        return

    if mode == "join":
        st.markdown(
            '<div class="bs-title">'
            'チームに参加'
            '</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "初めて参加するチームの"
            "6桁コードを入力してください。"
        )

        code = st.text_input(
            "チームコード",
            placeholder="例：D5RS59",
            max_chars=6,
        )

        if st.button(
            "このチームに参加",
            type="primary",
            use_container_width=True,
        ):
            if not code.strip():
                st.info(
                    "チームコードを入力してください。"
                )

            else:
                team = find_team(code)

                if not team:
                    st.error(
                        "このコードのチームは"
                        "見つかりませんでした。"
                    )

                else:
                    add_recent_team(team)

                    st.session_state.team = (
                        team
                    )

                    st.session_state.team_gate_mode = (
                        None
                    )

                    st.session_state.page = (
                        "ホーム"
                    )

                    active = (
                        get_active_game()
                    )

                    if active:
                        st.session_state.game_id = (
                            active["id"]
                        )

                    flash(
                        f'{team["team_name"]}'
                        f' に参加しました！'
                    )

                    st.rerun()

        if st.button(
            "← 戻る",
            use_container_width=True,
        ):
            st.session_state.team_gate_mode = (
                None
            )
            st.rerun()

        return

    st.markdown(
        '<div class="bs-title">'
        'チームを作成'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "作成するとメンバー参加用の"
        "チームコードが発行されます。"
    )

    team_name = st.text_input(
        "チーム名",
        placeholder="例：ベイスターズ",
    )

    if st.button(
        "チームを作成してコードを発行",
        type="primary",
        use_container_width=True,
    ):
        if not team_name.strip():
            st.info(
                "チーム名を入力してください。"
            )

        else:
            try:
                team = create_team(
                    team_name
                )

                add_recent_team(team)

                st.session_state.created_team = (
                    team
                )

                st.rerun()

            except Exception as e:
                st.error(
                    "チームを作成できませんでした。"
                )

    if st.button(
        "← 戻る",
        use_container_width=True,
    ):
        st.session_state.team_gate_mode = (
            None
        )
        st.rerun()


# =========================================================
# HOME
# =========================================================

def home_page():
    team = st.session_state.team

    add_recent_team(team)

    st.markdown(
        f'<div class="team-top">'
        f'<div class="team-name">'
        f'⚾ {esc(team["team_name"])}'
        f'</div>'
        f'<div class="team-code-inline">'
        f'TEAM CODE&nbsp;&nbsp;'
        f'{esc(team["team_code"])}'
        f'</div>'
        f'</div>',
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
            f'<div class="history-card">'
            f'<div class="bs-caption">'
            f'LIVE GAME'
            f'</div>'
            f'<div class="history-score">'
            f'vs {esc(active["opponent"])}'
            f'</div>'
            f'<div class="history-meta">'
            f'{inning}回｜{mode}　'
            f'{active["our_score"]}'
            f' - '
            f'{active["their_score"]}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "試合を続ける  ›",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.game_id = (
                active["id"]
            )
            go("スコア入力")

    section("MENU")

    if st.button(
        "⚾　スコア入力　　　　　›",
        use_container_width=True,
    ):
        go("スコア入力")

    if st.button(
        "📊　成績確認　　　　　　›",
        use_container_width=True,
    ):
        go("成績確認")

    if st.button(
        "🗓️　過去の試合　　　　　›",
        use_container_width=True,
    ):
        st.session_state.selected_history_game = (
            None
        )
        go("過去の試合")

    if st.button(
        "👥　選手登録　　　　　　›",
        use_container_width=True,
    ):
        go("選手登録")

    section("TEAM")

    st.markdown(
        f'<div class="team-code-card">'
        f'<div class="team-code-label">'
        f'TEAM CODE'
        f'</div>'
        f'<div class="team-code-value">'
        f'{esc(team["team_code"])}'
        f'</div>'
        f'<div class="team-code-name">'
        f'{esc(team["team_name"])}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "初めて参加するメンバーに"
        "このコードを共有してください。"
    )

    if st.button(
        "⇄ チームを変更",
        use_container_width=True,
    ):
        change_team()


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

    section("NEW PLAYER")

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

        grade = st.selectbox(
            "学年",
            [
                "1年",
                "2年",
                "3年",
                "4年",
                "その他",
            ],
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
            st.info(
                "選手名を入力してください。"
            )

        else:
            existing = (
                supabase.table("players")
                .select("id")
                .eq(
                    "team_id",
                    team_id(),
                )
                .eq(
                    "name",
                    name.strip(),
                )
                .execute()
                .data
            )

            if existing:
                st.info(
                    "同じ名前の選手が"
                    "すでに登録されています。"
                )

            else:
                (
                    supabase.table("players")
                    .insert(
                        {
                            "team_id":
                                team_id(),
                            "name":
                                name.strip(),
                            "number":
                                number.strip()
                                or None,
                            "grade":
                                grade,
                            "active":
                                True,
                        }
                    )
                    .execute()
                )

                flash(
                    f'{name.strip()}'
                    f'（{grade}）を'
                    f'登録しました！'
                )

                st.rerun()

    players = get_players()

    section(
        f"PLAYERS　{len(players)}"
    )

    if not players:
        st.info(
            "まだ選手が"
            "登録されていません。"
        )
        return

    grade_order = {
        "4年": 0,
        "3年": 1,
        "2年": 2,
        "1年": 3,
        "その他": 4,
        None: 5,
    }

    players = sorted(
        players,
        key=lambda p: (
            grade_order.get(
                p.get("grade"),
                5,
            ),
            p["name"],
        ),
    )

    for player in players:
        meta = []

        if player.get("number"):
            meta.append(
                f'#{player["number"]}'
            )

        if player.get("grade"):
            meta.append(
                player["grade"]
            )

        st.markdown(
            f'<div class="player-box">'
            f'<div class="player-name">'
            f'{esc(player["name"])}'
            f'</div>'
            f'<div class="player-meta">'
            f'{esc(" ｜ ".join(meta))}'
            f'</div>'
            f'</div>',
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
        st.info(
            "試合を始めるには、"
            "先に選手を登録してください。"
        )

        if st.button(
            "👥 選手を登録する",
            type="primary",
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
        placeholder="ベイスターズ",
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
            placeholder="横浜スタジアム",
        )

    game_type = st.radio(
        "試合区分",
        [
            "練習試合",
            "公式戦",
        ],
        horizontal=True,
    )

    tournament = None

    if game_type == "公式戦":
        tournament = st.text_input(
            "大会名",
            placeholder="秋季大会",
        )

    bat_order = st.radio(
        "先攻・後攻",
        [
            "先攻",
            "後攻",
        ],
        horizontal=True,
    )

    section("LINEUP")

    labels = {}

    for p in players:
        label = p["name"]
        extra = []

        if p.get("number"):
            extra.append(
                f'#{p["number"]}'
            )

        if p.get("grade"):
            extra.append(
                p["grade"]
            )

        if extra:
            label += (
                "｜"
                + " ".join(extra)
            )

        labels[p["id"]] = label

    player_ids = list(
        labels.keys()
    )

    lineup_ids = []

    lineup_count = min(
        9,
        len(player_ids),
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
            format_func=lambda x: (
                labels[x]
            ),
            key=f"lineup_{i}",
        )

        lineup_ids.append(
            selected
        )

    starter = st.selectbox(
        "先発投手",
        player_ids,
        format_func=lambda x: (
            labels[x]
        ),
    )

    if st.button(
        "試合開始",
        type="primary",
        use_container_width=True,
    ):
        if not opponent.strip():
            st.info(
                "対戦相手を"
                "入力してください。"
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
                add_place(place)

        else:
            place = (
                place_choice
            )

        bat_first = (
            bat_order == "先攻"
        )

        current_mode = (
            "offense"
            if bat_first
            else "defense"
        )

        result = (
            supabase.table("games")
            .insert(
                {
                    "team_id":
                        team_id(),
                    "game_date":
                        str(game_date),
                    "opponent":
                        opponent.strip(),
                    "place":
                        place or None,
                    "game_type":
                        game_type,
                    "tournament":
                        tournament.strip()
                        if tournament
                        else None,
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
                }
            )
            .execute()
            .data
        )

        if not result:
            st.error(
                "試合を開始"
                "できませんでした。"
            )
            return

        game = result[0]

        lineup_rows = [
            {
                "game_id":
                    game["id"],
                "slot":
                    i,
                "player_id":
                    pid,
            }
            for i, pid
            in enumerate(
                lineup_ids,
                start=1,
            )
        ]

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

    status = (
        "攻撃中"
        if mode == "offense"
        else "守備中"
    )

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

    team = (
        st.session_state.team
    )

    st.markdown(
        f'<div class="score-box">'
        f'<div class="score-status">'
        f'{inning}回{half}｜'
        f'{status}'
        f'</div>'
        f'<div class="score-row">'
        f'<div class="score-team">'
        f'{esc(team["team_name"])}'
        f'</div>'
        f'<div class="score-number">'
        f'{game["our_score"]}'
        f' - '
        f'{game["their_score"]}'
        f'</div>'
        f'<div class="score-team right">'
        f'{esc(game["opponent"])}'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# BATTING INPUT
# =========================================================

def batting_input(game):
    lineup = get_lineup_players()

    if not lineup:
        st.info("オーダーが登録されていません。")
        return

    batter_index = (game.get("current_batter_index") or 0) % len(lineup)
    batter = lineup[batter_index]
    batting_order = int(batter.get("slot") or (batter_index + 1))

    batter_rows = get_batting_rows([game["id"]], batter["id"])
    stats = batting_stats(batter_rows)

    st.markdown(
        f'<div class="player-box">'
        f'<div class="player-meta">{batting_order}番</div>'
        f'<div class="player-name">{esc(batter["name"])}</div>'
        f'<div class="player-meta">今日 {stats["AB"]}打数 {stats["H"]}安打 {stats["RBI"]}打点</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    result_options = ["安打", "アウト", "三振", "四球", "死球", "失策", "犠打", "犠飛"]
    result = st.radio(
        "打席結果",
        result_options,
        horizontal=True,
        key="bat_result",
    )

    field = None
    hit_type = None
    field_options = ["投", "捕", "一", "二", "三", "遊", "左", "中", "右"]

    if result in ["安打", "アウト", "失策"]:
        field = st.radio(
            "方向",
            field_options,
            horizontal=True,
            key="bat_field",
        )

    if result == "安打":
        hit_type = st.radio(
            "安打種別",
            ["単打", "二塁打", "三塁打", "本塁打"],
            horizontal=True,
            key="hit_type",
        )

    rbi = st.number_input(
        "打点",
        min_value=0,
        max_value=4,
        value=0,
        step=1,
        key="bat_rbi",
    )

    if st.button(
        "この打席を登録",
        type="primary",
        use_container_width=True,
    ):
        (
            supabase.table("batting")
            .insert({
                "game_id": game["id"],
                "player_id": batter["id"],
                "inning": game["current_inning"],
                "batting_order": batting_order,
                "result": result,
                "field": field,
                "batted_type": None,
                "hit_type": hit_type,
                "rbi": int(rbi),
            })
            .execute()
        )

        update_game({
            "current_batter_index": (batter_index + 1) % len(lineup)
        })
        flash(f'{batter["name"]}：{result} を登録')
        st.rerun()

    # 現在の回の攻撃ログだけ表示
    inning_rows = [
        r for r in get_batting_rows([game["id"]])
        if int(r.get("inning") or 0) == int(game["current_inning"])
    ]

    section(f'{game["current_inning"]}回｜攻撃ログ')

    if not inning_rows:
        st.caption("この回の打席記録はまだありません。")
        return

    pmap = get_player_map()

    for i, row in enumerate(inning_rows, start=1):
        player = pmap.get(row.get("player_id"), {})
        name = player.get("name", "選手")

        # 新しい記録は batting_order を優先。古い記録だけラインナップから補完。
        order = row.get("batting_order")
        if not order:
            order = next(
                (p.get("slot") for p in lineup if p.get("id") == row.get("player_id")),
                None,
            )

        result_text = row.get("result") or ""
        direction = row.get("field") or ""

        if result_text == "安打":
            hit_type = row.get("hit_type") or "単打"
            hit_label = {
                "単打": "安",
                "二塁打": "二塁打",
                "三塁打": "三塁打",
                "本塁打": "本塁打",
            }.get(hit_type, hit_type)
            result_text = f"{direction}{hit_label}"
        elif result_text == "アウト":
            result_text = f"{direction}アウト" if direction else "アウト"
        elif result_text == "失策":
            result_text = f"{direction}失" if direction else "失策"

        row_rbi = int(row.get("rbi") or 0)
        if row_rbi:
            result_text += f"　{row_rbi}打点"

        prefix = f"{order}番" if order else f"{i}人目"

        if st.button(
            f"{prefix}　{name}　　{result_text}　›",
            key=f'open_bat_{row["id"]}',
            use_container_width=True,
        ):
            if st.session_state.edit_batting_id == row["id"]:
                st.session_state.edit_batting_id = None
            else:
                st.session_state.edit_batting_id = row["id"]
            st.session_state.delete_batting_id = None
            st.rerun()

        if st.session_state.get("edit_batting_id") == row["id"]:
            st.caption(f'{prefix} {name} の記録を編集')

            old_result = row.get("result") if row.get("result") in result_options else "アウト"
            edit_result = st.selectbox(
                "打席結果",
                result_options,
                index=result_options.index(old_result),
                key=f'edit_bat_result_{row["id"]}',
            )

            edit_field = None
            edit_hit_type = None

            if edit_result in ["安打", "アウト", "失策"]:
                old_field = row.get("field") if row.get("field") in field_options else "遊"
                edit_field = st.selectbox(
                    "方向",
                    field_options,
                    index=field_options.index(old_field),
                    key=f'edit_bat_field_{row["id"]}',
                )

            if edit_result == "安打":
                hit_types = ["単打", "二塁打", "三塁打", "本塁打"]
                old_hit = row.get("hit_type") if row.get("hit_type") in hit_types else "単打"
                edit_hit_type = st.selectbox(
                    "安打種別",
                    hit_types,
                    index=hit_types.index(old_hit),
                    key=f'edit_hit_type_{row["id"]}',
                )

            edit_rbi = st.number_input(
                "打点",
                min_value=0,
                max_value=4,
                value=int(row.get("rbi") or 0),
                step=1,
                key=f'edit_bat_rbi_{row["id"]}',
            )

            if st.button(
                "変更を保存",
                type="primary",
                key=f'save_bat_{row["id"]}',
                use_container_width=True,
            ):
                (
                    supabase.table("batting")
                    .update({
                        "result": edit_result,
                        "field": edit_field,
                        "batted_type": None,
                        "hit_type": edit_hit_type,
                        "rbi": int(edit_rbi),
                    })
                    .eq("id", row["id"])
                    .execute()
                )
                st.session_state.edit_batting_id = None
                flash("打席記録を変更しました")
                st.rerun()

            if st.button(
                "この記録を削除",
                key=f'ask_delete_bat_{row["id"]}',
                use_container_width=True,
            ):
                st.session_state.delete_batting_id = row["id"]
                st.rerun()

            if st.session_state.get("delete_batting_id") == row["id"]:
                st.info("この打席記録を削除しますか？")
                d1, d2 = st.columns(2)

                with d1:
                    if st.button(
                        "削除する",
                        key=f'delete_bat_{row["id"]}',
                        use_container_width=True,
                    ):
                        (
                            supabase.table("batting")
                            .delete()
                            .eq("id", row["id"])
                            .execute()
                        )

                        latest_game = get_game()
                        latest_index = (latest_game.get("current_batter_index") or 0) % len(lineup)
                        update_game({
                            "current_batter_index": (latest_index - 1) % len(lineup)
                        })

                        st.session_state.edit_batting_id = None
                        st.session_state.delete_batting_id = None
                        flash("打席記録を削除しました")
                        st.rerun()

                with d2:
                    if st.button(
                        "キャンセル",
                        key=f'cancel_delete_bat_{row["id"]}',
                        use_container_width=True,
                    ):
                        st.session_state.delete_batting_id = None
                        st.rerun()


# =========================================================
# PITCHING INPUT
# =========================================================

def pitching_input(game):
    players = get_players()
    current_pid = game.get("current_pitcher_id")

    pitcher = next((p for p in players if p["id"] == current_pid), None)
    if pitcher is None and players:
        pitcher = players[0]

    if not pitcher:
        st.info("投手が登録されていません。")
        return

    pitcher_rows = get_pitching_rows([game["id"]], pitcher["id"])
    stats = pitching_stats(pitcher_rows)

    st.markdown(
        f'<div class="player-box">'
        f'<div class="player-meta">PITCHER</div>'
        f'<div class="player-name">{esc(pitcher["name"])}</div>'
        f'<div class="player-meta">H {stats["H"]}　K {stats["SO"]}　BB {stats["BB"]}　R {stats["R"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    result_options = ["アウト", "三振", "安打", "二塁打", "三塁打", "本塁打", "四球", "死球", "失策"]
    result = st.radio(
        "打者結果",
        result_options,
        horizontal=True,
        key="pitch_result",
    )

    runs = st.number_input(
        "このプレーで入った得点",
        min_value=0,
        max_value=20,
        value=0,
        step=1,
        key="pitch_runs",
    )

    if st.button("結果を登録", type="primary", use_container_width=True):
        (
            supabase.table("pitching")
            .insert({
                "game_id": game["id"],
                "pitcher_id": pitcher["id"],
                "inning": game["current_inning"],
                "result": result,
                "runs": int(runs),
            })
            .execute()
        )
        flash(f"{result} を登録しました")
        st.rerun()

    # 現在の回の守備ログだけ表示
    inning_rows = [
        r for r in get_pitching_rows([game["id"]])
        if int(r.get("inning") or 0) == int(game["current_inning"])
    ]

    section(f'{game["current_inning"]}回｜守備ログ')

    if not inning_rows:
        st.caption("この回の守備記録はまだありません。")
        return

    pmap = get_player_map()

    for i, row in enumerate(inning_rows, start=1):
        row_pitcher = pmap.get(row.get("pitcher_id"), {})
        pitcher_name = row_pitcher.get("name", "投手")
        result_text = row.get("result") or ""
        row_runs = int(row.get("runs") or 0)
        suffix = f"　{row_runs}失点" if row_runs else ""

        if st.button(
            f"{i}人目　{pitcher_name}　　{result_text}{suffix}　›",
            key=f'open_pitch_{row["id"]}',
            use_container_width=True,
        ):
            if st.session_state.edit_pitching_id == row["id"]:
                st.session_state.edit_pitching_id = None
            else:
                st.session_state.edit_pitching_id = row["id"]
            st.session_state.delete_pitching_id = None
            st.rerun()

        if st.session_state.get("edit_pitching_id") == row["id"]:
            st.caption(f'{i}人目の守備記録を編集')

            old_result = row.get("result") if row.get("result") in result_options else "アウト"
            edit_result = st.selectbox(
                "打者結果",
                result_options,
                index=result_options.index(old_result),
                key=f'edit_pitch_result_{row["id"]}',
            )
            edit_runs = st.number_input(
                "このプレーで入った得点",
                min_value=0,
                max_value=20,
                value=row_runs,
                step=1,
                key=f'edit_pitch_runs_{row["id"]}',
            )

            if st.button(
                "変更を保存",
                type="primary",
                key=f'save_pitch_{row["id"]}',
                use_container_width=True,
            ):
                (
                    supabase.table("pitching")
                    .update({"result": edit_result, "runs": int(edit_runs)})
                    .eq("id", row["id"])
                    .execute()
                )
                st.session_state.edit_pitching_id = None
                flash("守備記録を変更しました")
                st.rerun()

            if st.button(
                "この記録を削除",
                key=f'ask_delete_pitch_{row["id"]}',
                use_container_width=True,
            ):
                st.session_state.delete_pitching_id = row["id"]
                st.rerun()

            if st.session_state.get("delete_pitching_id") == row["id"]:
                st.info("この守備記録を削除しますか？")
                d1, d2 = st.columns(2)

                with d1:
                    if st.button(
                        "削除する",
                        key=f'delete_pitch_{row["id"]}',
                        use_container_width=True,
                    ):
                        (
                            supabase.table("pitching")
                            .delete()
                            .eq("id", row["id"])
                            .execute()
                        )
                        st.session_state.edit_pitching_id = None
                        st.session_state.delete_pitching_id = None
                        flash("守備記録を削除しました")
                        st.rerun()

                with d2:
                    if st.button(
                        "キャンセル",
                        key=f'cancel_delete_pitch_{row["id"]}',
                        use_container_width=True,
                    ):
                        st.session_state.delete_pitching_id = None
                        st.rerun()


# =========================================================
# TIEBREAK
# =========================================================

def tiebreak_panel(game):
    # タイブレークでは、その回の先頭打者を手動で指定できる。
    # DBの追加カラムは不要で、games.current_batter_index を更新する。
    lineup = get_lineup_players()
    if not lineup:
        return

    if st.button(
        "タイブレーク設定",
        use_container_width=True,
    ):
        st.session_state.tiebreak_open = not st.session_state.tiebreak_open

    if not st.session_state.tiebreak_open:
        return

    st.info("タイブレークで、この回の先頭打者を選択してください。")
    indices = list(range(len(lineup)))
    current_index = (game.get("current_batter_index") or 0) % len(lineup)
    selected_index = st.selectbox(
        "この回の先頭打者",
        indices,
        index=current_index,
        format_func=lambda i: f'{i + 1}番　{lineup[i]["name"]}',
        key=f'tiebreak_batter_{game["id"]}_{game["current_inning"]}',
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            "この打者から開始",
            type="primary",
            use_container_width=True,
        ):
            update_game({"current_batter_index": int(selected_index)})
            st.session_state.tiebreak_open = False
            flash(f'{lineup[selected_index]["name"]} から開始します')
            st.rerun()
    with c2:
        if st.button(
            "キャンセル",
            key="cancel_tiebreak",
            use_container_width=True,
        ):
            st.session_state.tiebreak_open = False
            st.rerun()


# =========================================================
# SIDE SWITCH
# =========================================================

def side_switch_panel(game):
    section("GAME CONTROL")

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

    if not st.session_state.switch_open:
        return

    st.info(
        "終了したイニングの"
        "得点を入力してください。"
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
            .insert(
                {
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
                }
            )
            .execute()
        )

        values = {}

        if (
            current_mode
            == "offense"
        ):
            values["our_score"] = (
                int(
                    game["our_score"]
                )
                + int(runs)
            )

            values["current_mode"] = (
                "defense"
            )

            if not game["bat_first"]:
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

            values["current_mode"] = (
                "offense"
            )

            if game["bat_first"]:
                values[
                    "current_inning"
                ] = (
                    game[
                        "current_inning"
                    ]
                    + 1
                )

        update_game(values)

        st.session_state.switch_open = (
            False
        )

        flash(
            "攻守を交替しました"
        )

        st.rerun()


# =========================================================
# SUBSTITUTION
# =========================================================

def substitution_panel(game):
    if not st.session_state.sub_open:
        return

    section("SUBSTITUTION")

    players = get_players()
    lineup = (
        get_lineup_players()
    )

    sub_type = st.radio(
        "交代種類",
        [
            "代打",
            "投手交代",
        ],
        horizontal=True,
    )

    if sub_type == "代打":
        if not lineup:
            return

        slot = st.selectbox(
            "打順",
            [
                p["slot"]
                for p in lineup
            ],
            format_func=lambda x: (
                f"{x}番"
            ),
        )

        current = next(
            p
            for p in lineup
            if p["slot"] == slot
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

        new_pid = st.selectbox(
            "新しい選手",
            [
                p["id"]
                for p in candidates
            ],
            format_func=player_name,
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
                .update(
                    {
                        "player_id":
                            new_pid
                    }
                )
                .eq(
                    "game_id",
                    game["id"],
                )
                .eq(
                    "slot",
                    slot,
                )
                .execute()
            )

            (
                supabase.table(
                    "substitutions"
                )
                .insert(
                    {
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
                            new_pid,
                    }
                )
                .execute()
            )

            st.session_state.sub_open = (
                False
            )

            flash(
                "代打を登録しました"
            )

            st.rerun()

    else:
        current_pid = (
            game.get(
                "current_pitcher_id"
            )
        )

        candidates = [
            p
            for p in players
            if p["id"]
            != current_pid
        ]

        if not candidates:
            st.info(
                "交代できる投手が"
                "いません。"
            )
            return

        new_pid = st.selectbox(
            "新しい投手",
            [
                p["id"]
                for p in candidates
            ],
            format_func=player_name,
        )

        if st.button(
            "投手交代を登録",
            type="primary",
            use_container_width=True,
        ):
            update_game(
                {
                    "current_pitcher_id":
                        new_pid
                }
            )

            (
                supabase.table(
                    "substitutions"
                )
                .insert(
                    {
                        "game_id":
                            game["id"],
                        "inning":
                            game[
                                "current_inning"
                            ],
                        "substitution_type":
                            "投手交代",
                        "old_player_id":
                            current_pid,
                        "new_player_id":
                            new_pid,
                    }
                )
                .execute()
            )

            st.session_state.sub_open = (
                False
            )

            flash(
                "投手を交代しました"
            )

            st.rerun()


# =========================================================
# FINISH GAME
# =========================================================

def finish_game_panel(game):
    st.write("")

    if st.button(
        "ゲームセット",
        use_container_width=True,
    ):
        st.session_state.finish_open = (
            not st.session_state.finish_open
        )

    if not st.session_state.finish_open:
        return

    st.info(
        "この試合を終了しますか？"
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "終了する",
            type="primary",
            use_container_width=True,
        ):
            update_game(
                {
                    "status":
                        "finished"
                }
            )

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

    with c2:
        if st.button(
            "キャンセル",
            use_container_width=True,
        ):
            st.session_state.finish_open = (
                False
            )
            st.rerun()


# =========================================================
# TODAY'S GAME STATS
# =========================================================

def today_game_stats(game):
    section("今日の成績")

    batting_tab, pitching_tab = st.tabs(["打撃成績", "投手成績"])

    with batting_tab:
        lineup = get_lineup_players(game["id"])
        if not lineup:
            st.caption("まだ打撃成績はありません。")
        else:
            rows_data = []
            for player in lineup:
                stats = batting_stats(
                    get_batting_rows([game["id"]], player["id"])
                )
                rows_data.append({
                    "選手": player["name"],
                    "打数": stats["AB"],
                    "安打": stats["H"],
                    "打率": format_avg(stats["AVG"]),
                    "2B": stats["2B"],
                    "3B": stats["3B"],
                    "HR": stats["HR"],
                    "打点": stats["RBI"],
                    "四球": stats["BB"],
                    "死球": stats["HBP"],
                    "三振": stats["SO"],
                    "失策出塁": stats.get("E", 0),
                })
            st.dataframe(rows_data, use_container_width=True, hide_index=True)

    with pitching_tab:
        rows = get_pitching_rows([game["id"]])
        pitcher_ids = []
        for row in rows:
            pid = row["pitcher_id"]
            if pid not in pitcher_ids:
                pitcher_ids.append(pid)

        current_pid = game.get("current_pitcher_id")
        if current_pid and current_pid not in pitcher_ids:
            pitcher_ids.append(current_pid)

        if not pitcher_ids:
            st.caption("まだ投手成績はありません。")
        else:
            pmap = get_player_map()
            rows_data = []
            for pid in pitcher_ids:
                pitcher_rows = [r for r in rows if r["pitcher_id"] == pid]
                stats = pitching_stats(pitcher_rows)
                player = pmap.get(pid, {})
                rows_data.append({
                    "投手": player.get("name", "―"),
                    "対戦打者": stats["BF"],
                    "被安打": stats["H"],
                    "奪三振": stats["SO"],
                    "四球": stats["BB"],
                    "死球": stats["HBP"],
                    "被本塁打": stats["HR"],
                    "失点": stats["R"],
                })
            st.dataframe(rows_data, use_container_width=True, hide_index=True)


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
            st.info(
                "進行中の試合は"
                "ありません。"
            )

            if st.button(
                "＋ 新しい試合を始める",
                type="primary",
                use_container_width=True,
            ):
                go("新規試合")

            return

    score_header(game)

    if (
        game["current_mode"]
        == "offense"
    ):
        batting_input(game)

    else:
        pitching_input(game)

    if game["current_mode"] == "offense":
        tiebreak_panel(game)

    side_switch_panel(game)
    substitution_panel(game)
    finish_game_panel(game)

    # 一番下は試合全体の累計成績
    today_game_stats(game)


# =========================================================
# GAME FILTER
# =========================================================

def game_filter_ui(
    prefix,
    games=None,
):
    if games is None:
        games = get_games()

    if not games:
        return []

    with st.expander(
        "試合を絞り込む"
    ):
        period = st.radio(
            "期間",
            [
                "全期間",
                "期間指定",
            ],
            horizontal=True,
            key=f"{prefix}_period",
        )

        filtered = games[:]

        if period == "期間指定":
            c1, c2 = (
                st.columns(2)
            )

            with c1:
                start = (
                    st.date_input(
                        "開始日",
                        value=date(
                            date.today().year,
                            1,
                            1,
                        ),
                        key=(
                            f"{prefix}"
                            f"_start"
                        ),
                    )
                )

            with c2:
                end = (
                    st.date_input(
                        "終了日",
                        value=date.today(),
                        key=(
                            f"{prefix}"
                            f"_end"
                        ),
                    )
                )

            filtered = [
                g
                for g in filtered
                if (
                    start
                    <= safe_date(
                        g["game_date"]
                    )
                    <= end
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

        selected_type = (
            st.selectbox(
                "試合区分",
                ["全試合"] + types,
                key=(
                    f"{prefix}"
                    f"_type"
                ),
            )
        )

        if (
            selected_type
            != "全試合"
        ):
            filtered = [
                g
                for g in filtered
                if (
                    g.get(
                        "game_type"
                    )
                    == selected_type
                )
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
                [
                    "全大会"
                ] + tournaments,
                key=(
                    f"{prefix}"
                    f"_tournament"
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
                if (
                    g.get(
                        "tournament"
                    )
                    == selected_tournament
                )
            ]

        places = sorted(
            {
                g["place"]
                for g in games
                if g.get("place")
            }
        )

        selected_place = (
            st.selectbox(
                "試合場所",
                [
                    "全場所"
                ] + places,
                key=(
                    f"{prefix}"
                    f"_place"
                ),
            )
        )

        if (
            selected_place
            != "全場所"
        ):
            filtered = [
                g
                for g in filtered
                if (
                    g.get("place")
                    == selected_place
                )
            ]

    return filtered


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
            game["id"],
        )
        .order("inning")
        .execute()
        .data
        or []
    )

    if not rows:
        st.caption(
            "イニング別得点は"
            "ありません。"
        )
        return

    innings = sorted(
        {
            r["inning"]
            for r in rows
        }
    )

    our = {
        "チーム":
            st.session_state.team[
                "team_name"
            ]
    }

    their = {
        "チーム":
            game["opponent"]
    }

    for inning in innings:
        our[str(inning)] = next(
            (
                r["runs"]
                for r in rows
                if (
                    r["inning"]
                    == inning
                    and
                    r["side"]
                    == "our"
                )
            ),
            "-",
        )

        their[str(inning)] = next(
            (
                r["runs"]
                for r in rows
                if (
                    r["inning"]
                    == inning
                    and
                    r["side"]
                    == "their"
                )
            ),
            "-",
        )

    our["計"] = (
        game["our_score"]
    )

    their["計"] = (
        game["their_score"]
    )

    st.dataframe(
        [
            our,
            their,
        ],
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# GAME DETAIL
# =========================================================

def game_detail(game):
    st.markdown(
        f'<div class="score-box">'
        f'<div class="score-status">'
        f'{esc(game["game_date"])}'
        f'</div>'
        f'<div class="score-row">'
        f'<div class="score-team">'
        f'{esc(st.session_state.team["team_name"])}'
        f'</div>'
        f'<div class="score-number">'
        f'{game["our_score"]}'
        f' - '
        f'{game["their_score"]}'
        f'</div>'
        f'<div class="score-team right">'
        f'{esc(game["opponent"])}'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    details = []

    if game.get("game_type"):
        details.append(
            game["game_type"]
        )

    if game.get("tournament"):
        details.append(
            game["tournament"]
        )

    if game.get("place"):
        details.append(
            game["place"]
        )

    if details:
        st.caption(
            " ｜ ".join(
                details
            )
        )

    section(
        "イニングスコア"
    )

    inning_score_table(
        game
    )

    section(
        "打撃成績"
    )

    lineup = (
        get_lineup_players(
            game["id"]
        )
    )

    if not lineup:
        st.caption(
            "打撃記録はありません。"
        )

    for player in lineup:
        stats = batting_stats(
            get_batting_rows(
                [game["id"]],
                player["id"],
            )
        )

        meta = []

        if player.get("grade"):
            meta.append(
                player["grade"]
            )

        meta.append(
            f'{stats["AB"]}打数'
        )

        meta.append(
            f'{stats["H"]}安打　'
            f'{stats["RBI"]}打点'
        )

        meta.append(
            format_avg(
                stats["AVG"]
            )
        )

        st.markdown(
            f'<div class="player-box">'
            f'<div class="player-name">'
            f'{esc(player["name"])}'
            f'</div>'
            f'<div class="player-meta">'
            f'{esc(" ｜ ".join(meta))}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    section(
        "投手成績"
    )

    pitching_rows = (
        get_pitching_rows(
            [game["id"]]
        )
    )

    pitcher_ids = []

    for row in pitching_rows:
        pid = (
            row["pitcher_id"]
        )

        if pid not in pitcher_ids:
            pitcher_ids.append(
                pid
            )

    if not pitcher_ids:
        st.caption(
            "投手記録はありません。"
        )

    for pid in pitcher_ids:
        rows = [
            r
            for r in pitching_rows
            if (
                r["pitcher_id"]
                == pid
            )
        ]

        stats = pitching_stats(
            rows
        )

        st.markdown(
            f'<div class="player-box">'
            f'<div class="player-name">'
            f'{esc(player_name(pid))}'
            f'</div>'
            f'<div class="player-meta">'
            f'H {stats["H"]} ｜ '
            f'K {stats["SO"]} ｜ '
            f'BB {stats["BB"]} ｜ '
            f'R {stats["R"]}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# HISTORY PAGE
# =========================================================

def history_page():
    if (
        st.session_state
        .selected_history_game
    ):
        game = get_game(
            st.session_state
            .selected_history_game
        )

        if st.button(
            "‹ 過去の試合一覧",
            use_container_width=False,
        ):
            st.session_state.selected_history_game = (
                None
            )
            st.rerun()

        st.markdown(
            '<div class="bs-title">'
            '試合詳細'
            '</div>',
            unsafe_allow_html=True,
        )

        if not game:
            st.error(
                "試合が"
                "見つかりませんでした。"
            )
            return

        game_detail(game)
        return

    page_header(
        "過去の試合",
        st.session_state.team[
            "team_name"
        ],
    )

    all_games = [
        g
        for g in get_games()
        if (
            g["status"]
            == "finished"
        )
    ]

    if not all_games:
        st.info(
            "まだ終了した試合が"
            "ありません。"
        )
        return

    games = game_filter_ui(
        "history",
        all_games,
    )

    if not games:
        st.info(
            "条件に該当する試合は"
            "ありません。"
        )
        return

    section(
        f"試合結果　"
        f"{len(games)}試合"
    )

    for game in games:
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

        meta = [
            game["game_date"]
        ]

        if game.get("game_type"):
            meta.append(
                game["game_type"]
            )

        if game.get("tournament"):
            meta.append(
                game["tournament"]
            )

        if game.get("place"):
            meta.append(
                game["place"]
            )

        st.markdown(
            f'<div class="history-card">'
            f'<div class="history-score">'
            f'{mark}　'
            f'{game["our_score"]}'
            f' - '
            f'{game["their_score"]}　'
            f'{esc(game["opponent"])}'
            f'</div>'
            f'<div class="history-meta">'
            f'{esc("｜".join(meta))}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "試合詳細を見る  ›",
            key=(
                f'history_'
                f'{game["id"]}'
            ),
            use_container_width=True,
        ):
            st.session_state.selected_history_game = (
                game["id"]
            )

            st.rerun()


# =========================================================
# INDIVIDUAL STATS
# =========================================================

def individual_stats():
    all_players = (
        get_players(False)
    )

    if not all_players:
        st.info(
            "選手が"
            "登録されていません。"
        )
        return

    selected_grades = (
        grade_filter(
            all_players,
            "individual_grades",
        )
    )

    players = (
        filter_players_by_grade(
            all_players,
            selected_grades,
        )
    )

    if not players:
        st.info(
            "選択した学年に"
            "選手がいません。"
        )
        return

    games = game_filter_ui(
        "individual"
    )

    if not games:
        st.info(
            "条件に該当する試合が"
            "ありません。"
        )
        return

    game_ids = [
        g["id"]
        for g in games
    ]

    pid = st.selectbox(
        "選手",
        [
            p["id"]
            for p in players
        ],
        format_func=player_name,
        key="individual_player",
    )

    selected_player = next(
        (
            p
            for p in players
            if p["id"] == pid
        ),
        None,
    )

    if (
        selected_player
        and
        selected_player.get(
            "grade"
        )
    ):
        st.caption(
            f'学年：'
            f'{selected_player["grade"]}'
        )

    batting_tab, pitching_tab = (
        st.tabs(
            [
                "打撃",
                "投手",
            ]
        )
    )

    with batting_tab:
        stats = batting_stats(
            get_batting_rows(
                game_ids,
                pid,
            )
        )

        c1, c2, c3 = (
            st.columns(3)
        )

        c1.metric(
            "打率",
            format_avg(
                stats["AVG"]
            ),
        )

        c2.metric(
            "出塁率",
            format_avg(
                stats["OBP"]
            ),
        )

        c3.metric(
            "OPS",
            format_avg(
                stats["OPS"]
            ),
        )

        st.write(
            f'打席 **{stats["PA"]}**　'
            f'打数 **{stats["AB"]}**　'
            f'安打 **{stats["H"]}**'
        )

        st.write(
            f'二塁打 **{stats["2B"]}**　'
            f'三塁打 **{stats["3B"]}**　'
            f'本塁打 **{stats["HR"]}**　'
            f'打点 **{stats["RBI"]}**'
        )

        st.write(
            f'四球 **{stats["BB"]}**　'
            f'死球 **{stats["HBP"]}**　'
            f'三振 **{stats["SO"]}**'
        )

        st.write(
            f'犠打 **{stats["SH"]}**　'
            f'犠飛 **{stats["SF"]}**　'
            f'長打率 '
            f'**{format_avg(stats["SLG"])}**'
        )

    with pitching_tab:
        stats = pitching_stats(
            get_pitching_rows(
                game_ids,
                pid,
            )
        )

        c1, c2, c3 = (
            st.columns(3)
        )

        c1.metric(
            "対戦打者",
            stats["BF"],
        )

        c2.metric(
            "奪三振",
            stats["SO"],
        )

        c3.metric(
            "失点",
            stats["R"],
        )

        st.write(
            f'被安打 **{stats["H"]}**　'
            f'被本塁打 **{stats["HR"]}**'
        )

        st.write(
            f'四球 **{stats["BB"]}**　'
            f'死球 **{stats["HBP"]}**'
        )

        st.caption(
            "アウト数・自責点を"
            "自動管理していないため、"
            "防御率ではなく失点を"
            "表示しています。"
        )


# =========================================================
# RANKING
# =========================================================

def ranking_stats():
    all_players = (
        get_players(False)
    )

    if not all_players:
        st.info(
            "選手が"
            "登録されていません。"
        )
        return

    selected_grades = (
        grade_filter(
            all_players,
            "ranking_grades",
        )
    )

    players = (
        filter_players_by_grade(
            all_players,
            selected_grades,
        )
    )

    if not players:
        st.info(
            "選択した学年に"
            "選手がいません。"
        )
        return

    games = game_filter_ui(
        "ranking"
    )

    if not games:
        st.info(
            "条件に該当する試合が"
            "ありません。"
        )
        return

    game_ids = [
        g["id"]
        for g in games
    ]

    category = st.selectbox(
        "ランキング項目",
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
            s = batting_stats(
                get_batting_rows(
                    game_ids,
                    player["id"],
                )
            )

            values = {
                "打率":
                    s["AVG"],
                "安打":
                    s["H"],
                "本塁打":
                    s["HR"],
                "OPS":
                    s["OPS"],
            }

            value = (
                values[category]
            )

        else:
            s = pitching_stats(
                get_pitching_rows(
                    game_ids,
                    player["id"],
                )
            )

            value = s["SO"]

        ranking.append(
            {
                "name":
                    player["name"],
                "grade":
                    player.get(
                        "grade"
                    )
                    or "未設定",
                "value":
                    value,
            }
        )

    ranking.sort(
        key=lambda x: (
            x["value"]
        ),
        reverse=True,
    )

    for rank, row in enumerate(
        ranking,
        start=1,
    ):
        display = (
            format_avg(
                row["value"]
            )
            if category
            in [
                "打率",
                "OPS",
            ]
            else str(
                row["value"]
            )
        )

        st.markdown(
            f'<div class="history-card">'
            f'<div style="'
            f'display:flex;'
            f'justify-content:space-between;'
            f'align-items:center;">'
            f'<div>'
            f'<b>{rank}</b>　'
            f'{esc(row["name"])}'
            f'<div class="history-meta">'
            f'{esc(row["grade"])}'
            f'</div>'
            f'</div>'
            f'<div style="'
            f'font-size:1.05rem;">'
            f'<b>{esc(display)}</b>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
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
        if (
            g["status"]
            == "finished"
        )
    ]

    if not finished:
        st.info(
            "条件に該当する"
            "終了済み試合がありません。"
        )
        return

    wins = sum(
        g["our_score"]
        > g["their_score"]
        for g in finished
    )

    losses = sum(
        g["our_score"]
        < g["their_score"]
        for g in finished
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

    team_batting = (
        batting_stats(
            get_batting_rows(
                game_ids
            )
        )
    )

    c1, c2, c3 = (
        st.columns(3)
    )

    c1.metric(
        "戦績",
        f"{wins}-{losses}-{draws}",
    )

    c2.metric(
        "総得点",
        sum(
            int(
                g["our_score"]
            )
            for g in finished
        ),
    )

    c3.metric(
        "総失点",
        sum(
            int(
                g["their_score"]
            )
            for g in finished
        ),
    )

    st.metric(
        "チーム打率",
        format_avg(
            team_batting["AVG"]
        ),
    )

    st.caption(
        "試合ごとの詳細は"
        "ホームの「過去の試合」から"
        "確認できます。"
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

    t1, t2, t3 = st.tabs(
        [
            "個人成績",
            "ランキング",
            "チーム成績",
        ]
    )

    with t1:
        individual_stats()

    with t2:
        ranking_stats()

    with t3:
        team_stats()


# =========================================================
# ROUTER
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

elif page == "過去の試合":
    history_page()

else:
    st.session_state.page = (
        "ホーム"
    )
    st.rerun()
