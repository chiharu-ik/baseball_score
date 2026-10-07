"use client";

import { useEffect, useMemo, useState } from "react";
import { supabase } from "../lib/supabase";

type Team = {
  id: string;
  team_name: string;
  team_code: string;
};

type Player = {
  id: any;
  team_id: string;
  name: string;
  number?: string | number | null;
  grade?: string | null;
  active?: boolean;
};

type Game = {
  id: any;
  team_id: string;
  game_date?: string;
  opponent: string;
  place?: string | null;
  game_type?: string | null;
  tournament?: string | null;
  bat_first: boolean;
  our_score: number;
  their_score: number;
  status: string;
  current_inning?: number;
  current_mode?: string;
  current_batter_index?: number;
  current_pitcher_id?: any;
  opponent_batter_index?: number;
};

type InningScore = {
  id?: any;
  game_id: any;
  inning: number;
  side: "our" | "their";
  runs: number;
};

type BattingRow = {
  id: any;
  game_id: any;
  player_id: any;
  inning: number;
  result: string;
  field?: string | null;
  hit_type?: string | null;
  batting_order?: number | null;
  rbi?: number | null;
};

type PitchingRow = {
  id: any;
  game_id: any;
  pitcher_id: any;
  inning: number;
  result: string;
  runs?: number | null;
  batting_order?: number | null;
};

type PitchingGameStat = {
  id?: any;
  game_id: any;
  pitcher_id: any;
  innings_outs: number;
  earned_runs: number;
};

const RECENT_KEY = "baseball_recent_teams_v1";

function n(v: any) {
  return Number(v || 0);
}

function fmt3(v: number | null) {
  if (v === null || Number.isNaN(v)) return "---";
  return v.toFixed(3).replace(/^0/, "");
}

function formatIP(outs: number) {
  const full = Math.floor(outs / 3);
  const rem = outs % 3;
  return rem === 0 ? `${full}` : `${full}.${rem}`;
}

function calcBatting(rows: BattingRow[]) {
  let PA = 0;
  let AB = 0;
  let H = 0;
  let doubles = 0;
  let triples = 0;
  let HR = 0;
  let RBI = 0;
  let BB = 0;
  let HBP = 0;
  let SO = 0;
  let SF = 0;

  for (const r of rows) {
    PA++;
    RBI += n(r.rbi);

    if (r.result === "四球") {
      BB++;
      continue;
    }

    if (r.result === "死球") {
      HBP++;
      continue;
    }

    if (r.result === "犠打") {
      continue;
    }

    if (r.result === "犠飛") {
      SF++;
      continue;
    }

    AB++;

    if (r.result === "三振") SO++;

    if (r.result === "安打") {
      H++;

      if (r.hit_type === "二塁打") doubles++;
      if (r.hit_type === "三塁打") triples++;

      if (r.hit_type === "本塁打") {
        HR++;
      }
    }
  }

  const AVG = AB ? H / AB : null;

  const obpDen = AB + BB + HBP + SF;
  const OBP = obpDen ? (H + BB + HBP) / obpDen : null;

  const singles = H - doubles - triples - HR;
  const TB = singles + doubles * 2 + triples * 3 + HR * 4;
  const SLG = AB ? TB / AB : null;

  const OPS =
    OBP !== null && SLG !== null
      ? OBP + SLG
      : null;

  return {
    PA,
    AB,
    H,
    doubles,
    triples,
    HR,
    RBI,
    BB,
    HBP,
    SO,
    AVG,
    OBP,
    SLG,
    OPS,
  };
}

function calcPitching(
  rows: PitchingRow[],
  finalRows: PitchingGameStat[]
) {
  const H = rows.filter((r) =>
    ["安打", "二塁打", "三塁打", "本塁打"].includes(r.result)
  ).length;

  const SO = rows.filter((r) => r.result === "三振").length;
  const BB = rows.filter((r) => r.result === "四球").length;
  const HBP = rows.filter((r) => r.result === "死球").length;
  const HR = rows.filter((r) => r.result === "本塁打").length;
  const R = rows.reduce((a, r) => a + n(r.runs), 0);

  const outs = finalRows.reduce(
    (a, r) => a + n(r.innings_outs),
    0
  );

  const ER = finalRows.reduce(
    (a, r) => a + n(r.earned_runs),
    0
  );

  const ERA = outs ? (ER * 27) / outs : null;

  return {
    H,
    SO,
    BB,
    HBP,
    HR,
    R,
    outs,
    ER,
    ERA,
  };
}

function saveRecentTeam(team: Team) {
  try {
    const raw = localStorage.getItem(RECENT_KEY);
    const old = raw ? JSON.parse(raw) : [];

    const next = [
      team,
      ...old.filter(
        (x: Team) => x.team_code !== team.team_code
      ),
    ].slice(0, 8);

    localStorage.setItem(
      RECENT_KEY,
      JSON.stringify(next)
    );
  } catch {}
}

export default function Page() {
  const [team, setTeam] = useState<Team | null>(null);
  const [recentTeams, setRecentTeams] = useState<Team[]>([]);
  const [page, setPage] = useState("home");

  useEffect(() => {
    try {
      const raw = localStorage.getItem(RECENT_KEY);
      if (raw) setRecentTeams(JSON.parse(raw));
    } catch {}
  }, []);

  function enterTeam(t: Team) {
    setTeam(t);
    saveRecentTeam(t);

    try {
      const raw = localStorage.getItem(RECENT_KEY);
      if (raw) setRecentTeams(JSON.parse(raw));
    } catch {}

    setPage("home");
  }

  if (!team) {
    return (
      <TeamGate
        recentTeams={recentTeams}
        enterTeam={enterTeam}
      />
    );
  }

  return (
    <main className="wrap">
      {page === "home" && (
        <Home
          team={team}
          go={setPage}
          changeTeam={() => {
            setTeam(null);
            setPage("home");
          }}
        />
      )}

      {page === "players" && (
        <Players
          team={team}
          back={() => setPage("home")}
        />
      )}

      {page === "newgame" && (
        <NewGame
          team={team}
          back={() => setPage("home")}
          openGame={() => setPage("score")}
        />
      )}

      {page === "score" && (
        <LiveScore
          team={team}
          back={() => setPage("home")}
        />
      )}

      {page === "stats" && (
        <Stats
          team={team}
          back={() => setPage("home")}
        />
      )}

      {page === "teamstats" && (
        <TeamStats
          team={team}
          back={() => setPage("home")}
        />
      )}

      {page === "history" && (
        <History
          team={team}
          back={() => setPage("home")}
        />
      )}
    </main>
  );
}

/* =========================================================
   TEAM
========================================================= */

function TeamGate({
  recentTeams,
  enterTeam,
}: {
  recentTeams: Team[];
  enterTeam: (t: Team) => void;
}) {
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [message, setMessage] = useState("");

  async function joinTeam(input?: string) {
    const target = (input || code)
      .trim()
      .toUpperCase();

    if (!target) return;

    setMessage("");

    const { data, error } = await supabase
      .from("teams")
      .select("id,team_name,team_code")
      .eq("team_code", target)
      .maybeSingle();

    if (error) {
      setMessage("チーム情報を取得できませんでした。");
      return;
    }

    if (!data) {
      setMessage("チームが見つかりません。");
      return;
    }

    enterTeam(data as Team);
  }

  async function createTeam() {
    if (!name.trim()) {
      setMessage("チーム名を入力してください。");
      return;
    }

    const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

    let newCode = "";

    for (let i = 0; i < 6; i++) {
      newCode +=
        chars[Math.floor(Math.random() * chars.length)];
    }

    const ownerCode =
      crypto.randomUUID?.() ||
      Math.random().toString(36).slice(2);

    const { data, error } = await supabase
      .from("teams")
      .insert({
        team_name: name.trim(),
        team_code: newCode,
        owner_code: ownerCode,
      })
      .select("id,team_name,team_code")
      .single();

    if (error || !data) {
      setMessage("チームを作成できませんでした。");
      return;
    }

    enterTeam(data as Team);
  }

  return (
    <main className="wrap">
      <div className="brand">Baseball Score</div>

      {recentTeams.length > 0 && (
        <section className="card">
          <h2>最近使ったチーム</h2>

          {recentTeams.map((t) => (
            <button
              key={t.team_code}
              onClick={() => joinTeam(t.team_code)}
            >
              <strong>{t.team_name}</strong>
              <br />
              <small>{t.team_code}</small>
            </button>
          ))}
        </section>
      )}

      <section className="card">
        <h2>チームに参加</h2>

        <input
          value={code}
          placeholder="チームコード"
          onChange={(e) =>
            setCode(e.target.value.toUpperCase())
          }
        />

        <button
          className="primary"
          onClick={() => joinTeam()}
        >
          チームに参加
        </button>
      </section>

      <section className="card">
        <h2>チームを作成</h2>

        <input
          value={name}
          placeholder="例：ベイスターズ"
          onChange={(e) => setName(e.target.value)}
        />

        <button
          className="primary"
          onClick={createTeam}
        >
          チームを作成
        </button>
      </section>

      {message && (
        <div className="notice">{message}</div>
      )}
    </main>
  );
}

/* =========================================================
   HOME
========================================================= */

function Home({
  team,
  go,
  changeTeam,
}: {
  team: Team;
  go: (p: string) => void;
  changeTeam: () => void;
}) {
  return (
    <>
      <div className="top">
        <div>
          <h1>{team.team_name}</h1>
          <span className="pill">
            TEAM CODE {team.team_code}
          </span>
        </div>

        <button onClick={changeTeam}>
          チームを変更
        </button>
      </div>

      <div className="grid2">
        <button
          className="primary"
          onClick={() => go("newgame")}
        >
          新しい試合
        </button>

        <button onClick={() => go("score")}>
          スコア入力
        </button>

        <button onClick={() => go("players")}>
          選手登録
        </button>

        <button onClick={() => go("stats")}>
          個人成績・ランキング
        </button>

        <button onClick={() => go("teamstats")}>
          チーム成績
        </button>

        <button onClick={() => go("history")}>
          過去の試合
        </button>
      </div>
    </>
  );
}

/* =========================================================
   PLAYERS
========================================================= */

function Players({
  team,
  back,
}: {
  team: Team;
  back: () => void;
}) {
  const [players, setPlayers] = useState<Player[]>([]);
  const [name, setName] = useState("");
  const [number, setNumber] = useState("");
  const [grade, setGrade] = useState("1年");
  const [message, setMessage] = useState("");

  async function load() {
    const { data } = await supabase
      .from("players")
      .select("*")
      .eq("team_id", team.id)
      .order("number");

    setPlayers((data || []) as Player[]);
  }

  useEffect(() => {
    load();
  }, [team.id]);

  async function addPlayer() {
    if (!name.trim()) return;

    const { error } = await supabase
      .from("players")
      .insert({
        team_id: team.id,
        name: name.trim(),
        number: number || null,
        grade,
        active: true,
      });

    if (error) {
      setMessage("登録できませんでした。");
      return;
    }

    setName("");
    setNumber("");
    setMessage("選手を登録しました。");
    await load();
  }

  return (
    <>
      <button onClick={back}>‹ ホーム</button>
      <h1>選手登録</h1>

      <section className="card">
        <input
          placeholder="選手名"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <input
          placeholder="背番号"
          value={number}
          onChange={(e) => setNumber(e.target.value)}
        />

        <select
          value={grade}
          onChange={(e) => setGrade(e.target.value)}
        >
          <option>1年</option>
          <option>2年</option>
          <option>3年</option>
          <option>4年</option>
          <option>その他</option>
        </select>

        <button
          className="primary"
          onClick={addPlayer}
        >
          登録
        </button>

        {message && (
          <div className="success">{message}</div>
        )}
      </section>

      <section className="card">
        <h2>登録選手</h2>

        {players.map((p) => (
          <div className="row" key={p.id}>
            <strong>{p.name}</strong>
            <span>
              #{p.number || "-"} ｜ {p.grade || "未設定"}
            </span>
          </div>
        ))}
      </section>
    </>
  );
}

/* =========================================================
   NEW GAME
========================================================= */

function NewGame({
  team,
  back,
  openGame,
}: {
  team: Team;
  back: () => void;
  openGame: () => void;
}) {
  const [opponent, setOpponent] = useState("");
  const [gameDate, setGameDate] = useState(
    new Date().toISOString().slice(0, 10)
  );
  const [place, setPlace] = useState("");
  const [gameType, setGameType] = useState("練習試合");
  const [tournament, setTournament] = useState("");
  const [batFirst, setBatFirst] = useState(true);
  const [players, setPlayers] = useState<Player[]>([]);
  const [lineup, setLineup] = useState<any[]>([]);
  const [pitcher, setPitcher] = useState("");

  useEffect(() => {
    supabase
      .from("players")
      .select("*")
      .eq("team_id", team.id)
      .then(({ data }) => {
        setPlayers((data || []) as Player[]);
      });
  }, [team.id]);

  function setSlot(index: number, value: string) {
    const next = [...lineup];
    next[index] = value;
    setLineup(next);
  }

  async function createGame() {
    if (!opponent.trim()) {
      alert("対戦相手を入力してください。");
      return;
    }

    const { data: game, error } = await supabase
      .from("games")
      .insert({
        team_id: team.id,
        game_date: gameDate,
        opponent: opponent.trim(),
        place: place || null,
        game_type: gameType || null,
        tournament: tournament || null,
        bat_first: batFirst,
        our_score: 0,
        their_score: 0,
        status: "playing",
        current_inning: 1,
        current_mode: batFirst ? "offense" : "defense",
        current_batter_index: 0,
        opponent_batter_index: 0,
        current_pitcher_id: pitcher || null,
      })
      .select()
      .single();

    if (error || !game) {
      alert("試合を作成できませんでした。");
      return;
    }

    const lineupRows = lineup
      .map((playerId, i) => ({
        game_id: game.id,
        slot: i + 1,
        player_id: playerId || null,
      }))
      .filter((x) => x.player_id);

    if (lineupRows.length) {
      await supabase.from("lineup").insert(lineupRows);
    }

    openGame();
  }

  return (
    <>
      <button onClick={back}>‹ ホーム</button>
      <h1>新しい試合</h1>

      <section className="card">
        <label>試合日</label>
        <input
          type="date"
          value={gameDate}
          onChange={(e) => setGameDate(e.target.value)}
        />

        <label>対戦相手</label>
        <input
          value={opponent}
          onChange={(e) => setOpponent(e.target.value)}
        />

        <label>場所</label>
        <input
          value={place}
          onChange={(e) => setPlace(e.target.value)}
        />

        <label>試合種別</label>
        <input
          value={gameType}
          onChange={(e) => setGameType(e.target.value)}
        />

        <label>大会</label>
        <input
          value={tournament}
          onChange={(e) => setTournament(e.target.value)}
        />

        <label>先攻・後攻</label>
        <select
          value={batFirst ? "first" : "second"}
          onChange={(e) =>
            setBatFirst(e.target.value === "first")
          }
        >
          <option value="first">先攻</option>
          <option value="second">後攻</option>
        </select>
      </section>

      <section className="card">
        <h2>オーダー</h2>

        {Array.from({ length: 9 }).map((_, i) => (
          <label key={i}>
            {i + 1}番
            <select
              value={lineup[i] || ""}
              onChange={(e) =>
                setSlot(i, e.target.value)
              }
            >
              <option value="">選択</option>

              {players.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
        ))}

        <label>先発投手</label>

        <select
          value={pitcher}
          onChange={(e) => setPitcher(e.target.value)}
        >
          <option value="">選択</option>

          {players.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>

        <button
          className="primary"
          onClick={createGame}
        >
          試合開始
        </button>
      </section>
    </>
  );
}

/* =========================================================
   SCOREBOARD
   先攻を上・後攻を下
========================================================= */

function Scoreboard({
  game,
  team,
  scores,
}: {
  game: Game;
  team: Team;
  scores: InningScore[];
}) {
  const maxInning = Math.max(
    7,
    ...scores.map((x) => n(x.inning))
  );

  const innings = Array.from(
    { length: maxInning },
    (_, i) => i + 1
  );

  const get = (
    inning: number,
    side: "our" | "their"
  ) => {
    const x = scores.find(
      (s) =>
        n(s.inning) === inning &&
        s.side === side
    );

    return x ? n(x.runs) : "";
  };

  const ourTotal = scores
    .filter((x) => x.side === "our")
    .reduce((a, x) => a + n(x.runs), 0);

  const theirTotal = scores
    .filter((x) => x.side === "their")
    .reduce((a, x) => a + n(x.runs), 0);

  const topName = game.bat_first
    ? team.team_name
    : game.opponent;

  const bottomName = game.bat_first
    ? game.opponent
    : team.team_name;

  const topSide: "our" | "their" =
    game.bat_first ? "our" : "their";

  const bottomSide: "our" | "their" =
    game.bat_first ? "their" : "our";

  const topTotal =
    topSide === "our" ? ourTotal : theirTotal;

  const bottomTotal =
    bottomSide === "our" ? ourTotal : theirTotal;

  return (
    <div className="scroll">
      <table>
        <thead>
          <tr>
            <th>TEAM</th>

            {innings.map((i) => (
              <th key={i}>{i}</th>
            ))}

            <th>R</th>
          </tr>
        </thead>

        <tbody>
          <tr>
            <th>{topName}</th>

            {innings.map((i) => (
              <td key={i}>{get(i, topSide)}</td>
            ))}

            <td>
              <strong>{topTotal}</strong>
            </td>
          </tr>

          <tr>
            <th>{bottomName}</th>

            {innings.map((i) => (
              <td key={i}>
                {get(i, bottomSide)}
              </td>
            ))}

            <td>
              <strong>{bottomTotal}</strong>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

/* =========================================================
   LIVE SCORE
========================================================= */

function LiveScore({
  team,
  back,
}: {
  team: Team;
  back: () => void;
}) {
  const [game, setGame] = useState<Game | null>(null);
  const [scores, setScores] = useState<InningScore[]>([]);
  const [inningRuns, setInningRuns] = useState(0);
  const [finishOpen, setFinishOpen] = useState(false);
  const [finalRuns, setFinalRuns] = useState(0);

  async function load() {
    const { data } = await supabase
      .from("games")
      .select("*")
      .eq("team_id", team.id)
      .eq("status", "playing")
      .order("id", { ascending: false })
      .limit(1);

    const g = data?.[0] as Game | undefined;

    if (!g) {
      setGame(null);
      return;
    }

    setGame(g);

    const { data: s } = await supabase
      .from("inning_scores")
      .select("*")
      .eq("game_id", g.id);

    setScores((s || []) as InningScore[]);
  }

  useEffect(() => {
    load();
  }, [team.id]);

  async function saveScore(
    inning: number,
    side: "our" | "their",
    runs: number
  ) {
    if (!game) return;

    const { data: existing } = await supabase
      .from("inning_scores")
      .select("*")
      .eq("game_id", game.id)
      .eq("inning", inning)
      .eq("side", side)
      .limit(1);

    if (existing?.length) {
      await supabase
        .from("inning_scores")
        .update({ runs })
        .eq("id", existing[0].id);
    } else {
      await supabase.from("inning_scores").insert({
        game_id: game.id,
        inning,
        side,
        runs,
      });
    }

    const { data: refreshed } = await supabase
      .from("inning_scores")
      .select("*")
      .eq("game_id", game.id);

    const all = (refreshed || []) as InningScore[];

    const our = all
      .filter((x) => x.side === "our")
      .reduce((a, x) => a + n(x.runs), 0);

    const their = all
      .filter((x) => x.side === "their")
      .reduce((a, x) => a + n(x.runs), 0);

    await supabase
      .from("games")
      .update({
        our_score: our,
        their_score: their,
      })
      .eq("id", game.id);
  }

  async function changeSides() {
    if (!game) return;

    const side: "our" | "their" =
      game.current_mode === "offense"
        ? "our"
        : "their";

    await saveScore(
      n(game.current_inning),
      side,
      inningRuns
    );

    const nextMode =
      game.current_mode === "offense"
        ? "defense"
        : "offense";

    let nextInning = n(game.current_inning);

    /*
      裏が終了したら次の回へ。
      自チームが先攻の場合：
        offense = 表
        defense = 裏

      自チームが後攻の場合：
        defense = 表
        offense = 裏
    */
    const wasBottom =
      (game.bat_first &&
        game.current_mode === "defense") ||
      (!game.bat_first &&
        game.current_mode === "offense");

    if (wasBottom) {
      nextInning++;
    }

    await supabase
      .from("games")
      .update({
        current_mode: nextMode,
        current_inning: nextInning,
      })
      .eq("id", game.id);

    setInningRuns(0);
    await load();
  }

  if (!game) {
    return (
      <>
        <button onClick={back}>‹ ホーム</button>
        <h1>スコア入力</h1>
        <div className="notice">
          進行中の試合はありません。
        </div>
      </>
    );
  }

  const currentSide: "our" | "their" =
    game.current_mode === "offense"
      ? "our"
      : "their";

  /*
    ★重要
    最後の回が既に保存されているか確認。
    保存済みならゲームセット時に再入力させない。
  */
  const currentHalfAlreadySaved = scores.some(
    (s) =>
      n(s.inning) === n(game.current_inning) &&
      s.side === currentSide
  );

  async function finishGame() {
    if (!game) return;

    /*
      未確定の場合だけ最後の回を保存。
      既に攻守交替で確定済みなら再保存しない。
    */
    if (!currentHalfAlreadySaved) {
      await saveScore(
        n(game.current_inning),
        currentSide,
        finalRuns
      );
    }

    await supabase
      .from("games")
      .update({
        status: "finished",
      })
      .eq("id", game.id);

    setFinishOpen(false);
    await load();
    alert("試合を終了しました。");
  }

  return (
    <>
      <button onClick={back}>‹ ホーム</button>

      <h1>スコア入力</h1>

      <div className="score">
        {game.current_inning}回
        {game.bat_first
          ? game.current_mode === "offense"
            ? "表"
            : "裏"
          : game.current_mode === "defense"
          ? "表"
          : "裏"}
        ｜{" "}
        {game.current_mode === "offense"
          ? "攻撃中"
          : "守備中"}
      </div>

      <Scoreboard
        game={game}
        team={team}
        scores={scores}
      />

      <section className="card">
        <h2>
          {game.current_inning}回の得点
        </h2>

        <input
          type="number"
          min={0}
          value={inningRuns}
          onChange={(e) =>
            setInningRuns(n(e.target.value))
          }
        />

        <button
          className="primary"
          onClick={changeSides}
        >
          攻守交替
        </button>
      </section>

      <button
        className="danger"
        onClick={() => {
          setFinalRuns(0);
          setFinishOpen(true);
        }}
      >
        ゲームセット
      </button>

      {finishOpen && (
        <section className="card">
          <h2>ゲームセット</h2>

          {!currentHalfAlreadySaved ? (
            <>
              <p>
                現在の
                {game.current_inning}回
                {game.bat_first
                  ? game.current_mode === "offense"
                    ? "表"
                    : "裏"
                  : game.current_mode === "defense"
                  ? "表"
                  : "裏"}
                の得点がまだ確定していません。
              </p>

              <label>最後の回の得点</label>

              <input
                type="number"
                min={0}
                value={finalRuns}
                onChange={(e) =>
                  setFinalRuns(n(e.target.value))
                }
              />
            </>
          ) : (
            <div className="success">
              最後の回の得点は確定済みです。
            </div>
          )}

          <button
            className="danger"
            onClick={finishGame}
          >
            試合を終了
          </button>

          <button
            onClick={() => setFinishOpen(false)}
          >
            キャンセル
          </button>
        </section>
      )}
    </>
  );
}

/* =========================================================
   STATS
========================================================= */

function Stats({
  team,
  back,
}: {
  team: Team;
  back: () => void;
}) {
  const [players, setPlayers] = useState<Player[]>([]);
  const [batting, setBatting] = useState<BattingRow[]>([]);
  const [mode, setMode] = useState("individual");

  useEffect(() => {
    async function load() {
      const { data: p } = await supabase
        .from("players")
        .select("*")
        .eq("team_id", team.id);

      const { data: games } = await supabase
        .from("games")
        .select("id")
        .eq("team_id", team.id);

      const ids = (games || []).map((g) => g.id);

      let b: any[] = [];

      if (ids.length) {
        const res = await supabase
          .from("batting")
          .select("*")
          .in("game_id", ids);

        b = res.data || [];
      }

      setPlayers((p || []) as Player[]);
      setBatting(b as BattingRow[]);
    }

    load();
  }, [team.id]);

  return (
    <>
      <button onClick={back}>‹ ホーム</button>
      <h1>成績確認</h1>

      <div className="tabs">
        <button
          className={
            mode === "individual" ? "primary" : ""
          }
          onClick={() => setMode("individual")}
        >
          個人成績
        </button>

        <button
          className={
            mode === "ranking" ? "primary" : ""
          }
          onClick={() => setMode("ranking")}
        >
          ランキング
        </button>
      </div>

      {mode === "individual" && (
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>選手</th>
                <th>打席</th>
                <th>打数</th>
                <th>安打</th>
                <th>HR</th>
                <th>打点</th>
                <th>三振</th>
                <th>四球</th>
                <th>死球</th>
                <th>打率</th>
                <th>出塁率</th>
                <th>OPS</th>
              </tr>
            </thead>

            <tbody>
              {players.map((p) => {
                const s = calcBatting(
                  batting.filter(
                    (x) =>
                      String(x.player_id) ===
                      String(p.id)
                  )
                );

                return (
                  <tr key={p.id}>
                    <th>{p.name}</th>
                    <td>{s.PA}</td>
                    <td>{s.AB}</td>
                    <td>{s.H}</td>
                    <td>{s.HR}</td>
                    <td>{s.RBI}</td>
                    <td>{s.SO}</td>
                    <td>{s.BB}</td>
                    <td>{s.HBP}</td>
                    <td>{fmt3(s.AVG)}</td>
                    <td>{fmt3(s.OBP)}</td>
                    <td>{fmt3(s.OPS)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {mode === "ranking" && (
        <Rankings
          players={players}
          batting={batting}
        />
      )}
    </>
  );
}

/* =========================================================
   RANKINGS
========================================================= */

function Rankings({
  players,
  batting,
}: {
  players: Player[];
  batting: BattingRow[];
}) {
  const [category, setCategory] = useState("打率");

  const options = [
    "打率",
    "出塁率",
    "OPS",
    "安打",
    "本塁打",
    "打点",
    "三振",
    "四球",
    "死球",
  ];

  const ranking = useMemo(() => {
    return players
      .map((p) => {
        const s = calcBatting(
          batting.filter(
            (x) =>
              String(x.player_id) === String(p.id)
          )
        );

        let value: number | null = 0;

        if (category === "打率") value = s.AVG;
        if (category === "出塁率") value = s.OBP;
        if (category === "OPS") value = s.OPS;
        if (category === "安打") value = s.H;
        if (category === "本塁打") value = s.HR;
        if (category === "打点") value = s.RBI;
        if (category === "三振") value = s.SO;
        if (category === "四球") value = s.BB;
        if (category === "死球") value = s.HBP;

        return {
          player: p,
          value,
        };
      })
      .filter((x) => x.value !== null)
      .sort(
        (a, b) =>
          n(b.value) - n(a.value)
      );
  }, [players, batting, category]);

  const isRate = [
    "打率",
    "出塁率",
    "OPS",
  ].includes(category);

  return (
    <section className="card">
      <label>ランキング項目</label>

      <select
        value={category}
        onChange={(e) =>
          setCategory(e.target.value)
        }
      >
        {options.map((x) => (
          <option key={x}>{x}</option>
        ))}
      </select>

      {ranking.map((r, i) => (
        <div
          className="row"
          key={r.player.id}
        >
          <strong>
            {i + 1}位　{r.player.name}
          </strong>

          <span>
            {isRate
              ? fmt3(r.value)
              : n(r.value)}
          </span>
        </div>
      ))}
    </section>
  );
}

/* =========================================================
   TEAM STATS
========================================================= */

function TeamStats({
  team,
  back,
}: {
  team: Team;
  back: () => void;
}) {
  const [games, setGames] = useState<Game[]>([]);

  useEffect(() => {
    supabase
      .from("games")
      .select("*")
      .eq("team_id", team.id)
      .eq("status", "finished")
      .then(({ data }) =>
        setGames((data || []) as Game[])
      );
  }, [team.id]);

  const wins = games.filter(
    (g) => n(g.our_score) > n(g.their_score)
  ).length;

  const losses = games.filter(
    (g) => n(g.our_score) < n(g.their_score)
  ).length;

  const draws = games.length - wins - losses;

  return (
    <>
      <button onClick={back}>‹ ホーム</button>
      <h1>チーム成績</h1>

      <section className="card">
        <div className="metric">
          <span>戦績</span>
          <strong>
            {wins}勝 {losses}敗 {draws}分
          </strong>
        </div>

        <div className="metric">
          <span>試合数</span>
          <strong>{games.length}</strong>
        </div>

        <div className="metric">
          <span>総得点</span>
          <strong>
            {games.reduce(
              (a, g) => a + n(g.our_score),
              0
            )}
          </strong>
        </div>

        <div className="metric">
          <span>総失点</span>
          <strong>
            {games.reduce(
              (a, g) => a + n(g.their_score),
              0
            )}
          </strong>
        </div>
      </section>
    </>
  );
}

/* =========================================================
   HISTORY / 過去の試合
========================================================= */

function History({
  team,
  back,
}: {
  team: Team;
  back: () => void;
}) {
  const [games, setGames] = useState<Game[]>([]);
  const [selected, setSelected] = useState<Game | null>(
    null
  );

  async function load() {
    const { data } = await supabase
      .from("games")
      .select("*")
      .eq("team_id", team.id)
      .eq("status", "finished")
      .order("game_date", { ascending: false });

    setGames((data || []) as Game[]);

    if (selected) {
      const fresh = (data || []).find(
        (g) => String(g.id) === String(selected.id)
      );

      if (fresh) setSelected(fresh as Game);
    }
  }

  useEffect(() => {
    load();
  }, [team.id]);

  if (selected) {
    return (
      <GameDetail
        team={team}
        game={selected}
        back={() => {
          setSelected(null);
          load();
        }}
        refresh={async () => {
          const { data } = await supabase
            .from("games")
            .select("*")
            .eq("id", selected.id)
            .single();

          if (data) setSelected(data as Game);

          await load();
        }}
      />
    );
  }

  return (
    <>
      <button onClick={back}>‹ ホーム</button>
      <h1>過去の試合</h1>

      {!games.length && (
        <div className="notice">
          終了済みの試合はありません。
        </div>
      )}

      {games.map((g) => {
        const result =
          n(g.our_score) > n(g.their_score)
            ? "○"
            : n(g.our_score) < n(g.their_score)
            ? "●"
            : "△";

        return (
          <button
            className="card"
            key={g.id}
            onClick={() => setSelected(g)}
          >
            <div className="row">
              <strong>
                {result}　vs {g.opponent}
              </strong>

              <strong>
                {g.our_score} - {g.their_score}
              </strong>
            </div>

            <small>
              {g.game_date || ""}
              {g.place ? ` ｜ ${g.place}` : ""}
              {g.game_type
                ? ` ｜ ${g.game_type}`
                : ""}
            </small>
          </button>
        );
      })}
    </>
  );
}

/* =========================================================
   PAST GAME DETAIL
========================================================= */

function GameDetail({
  team,
  game,
  back,
  refresh,
}: {
  team: Team;
  game: Game;
  back: () => void;
  refresh: () => Promise<void>;
}) {
  const [scores, setScores] = useState<InningScore[]>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  const [batting, setBatting] = useState<BattingRow[]>([]);
  const [pitching, setPitching] = useState<PitchingRow[]>([]);
  const [finalPitching, setFinalPitching] = useState<
    PitchingGameStat[]
  >([]);

  const [editOpen, setEditOpen] = useState(false);
  const [editInning, setEditInning] = useState(1);
  const [editSide, setEditSide] =
    useState<"our" | "their">("our");
  const [editRuns, setEditRuns] = useState(0);

  async function load() {
    const [
      scoresRes,
      playersRes,
      battingRes,
      pitchingRes,
      finalRes,
    ] = await Promise.all([
      supabase
        .from("inning_scores")
        .select("*")
        .eq("game_id", game.id),

      supabase
        .from("players")
        .select("*")
        .eq("team_id", team.id),

      supabase
        .from("batting")
        .select("*")
        .eq("game_id", game.id),

      supabase
        .from("pitching")
        .select("*")
        .eq("game_id", game.id),

      supabase
        .from("pitching_game_stats")
        .select("*")
        .eq("game_id", game.id),
    ]);

    setScores(
      (scoresRes.data || []) as InningScore[]
    );

    setPlayers(
      (playersRes.data || []) as Player[]
    );

    setBatting(
      (battingRes.data || []) as BattingRow[]
    );

    setPitching(
      (pitchingRes.data || []) as PitchingRow[]
    );

    setFinalPitching(
      (finalRes.data || []) as PitchingGameStat[]
    );
  }

  useEffect(() => {
    load();
  }, [game.id]);

  const maxInning = Math.max(
    7,
    n(game.current_inning),
    ...scores.map((s) => n(s.inning))
  );

  function openEditor() {
    setEditOpen(true);

    const found = scores.find(
      (s) =>
        n(s.inning) === 1 &&
        s.side === "our"
    );

    setEditInning(1);
    setEditSide("our");
    setEditRuns(found ? n(found.runs) : 0);
  }

  function changeEditTarget(
    inning: number,
    side: "our" | "their"
  ) {
    setEditInning(inning);
    setEditSide(side);

    const found = scores.find(
      (s) =>
        n(s.inning) === inning &&
        s.side === side
    );

    setEditRuns(found ? n(found.runs) : 0);
  }

  async function saveEditedScore() {
    const existing = scores.find(
      (s) =>
        n(s.inning) === editInning &&
        s.side === editSide
    );

    if (existing?.id) {
      await supabase
        .from("inning_scores")
        .update({
          runs: editRuns,
        })
        .eq("id", existing.id);
    } else {
      /*
        保存されていなかった回も追加できる。
        例：7回裏を入力せずゲームセットした場合。
      */
      await supabase
        .from("inning_scores")
        .insert({
          game_id: game.id,
          inning: editInning,
          side: editSide,
          runs: editRuns,
        });
    }

    const { data } = await supabase
      .from("inning_scores")
      .select("*")
      .eq("game_id", game.id);

    const all = (data || []) as InningScore[];

    const ourTotal = all
      .filter((x) => x.side === "our")
      .reduce((a, x) => a + n(x.runs), 0);

    const theirTotal = all
      .filter((x) => x.side === "their")
      .reduce((a, x) => a + n(x.runs), 0);

    await supabase
      .from("games")
      .update({
        our_score: ourTotal,
        their_score: theirTotal,
      })
      .eq("id", game.id);

    setEditOpen(false);

    await load();
    await refresh();
  }

  const battingPlayers = players
    .map((p) => ({
      player: p,
      rows: batting.filter(
        (r) =>
          String(r.player_id) === String(p.id)
      ),
    }))
    .filter((x) => x.rows.length);

  const pitcherIds = Array.from(
    new Set([
      ...pitching.map((x) =>
        String(x.pitcher_id)
      ),
      ...finalPitching.map((x) =>
        String(x.pitcher_id)
      ),
    ])
  );

  return (
    <>
      <button onClick={back}>
        ‹ 過去の試合
      </button>

      <h1>vs {game.opponent}</h1>

      <p>
        {game.game_date || ""}
        {game.place ? ` ｜ ${game.place}` : ""}
      </p>

      <Scoreboard
        game={game}
        team={team}
        scores={scores}
      />

      <button
        className="primary"
        onClick={openEditor}
      >
        点数を変更
      </button>

      {editOpen && (
        <section className="card">
          <h2>点数を変更</h2>

          <label>回</label>

          <select
            value={editInning}
            onChange={(e) =>
              changeEditTarget(
                n(e.target.value),
                editSide
              )
            }
          >
            {Array.from(
              { length: maxInning },
              (_, i) => i + 1
            ).map((i) => (
              <option key={i} value={i}>
                {i}回
              </option>
            ))}
          </select>

          <label>チーム</label>

          <select
            value={editSide}
            onChange={(e) =>
              changeEditTarget(
                editInning,
                e.target.value as
                  | "our"
                  | "their"
              )
            }
          >
            <option value="our">
              {team.team_name}
            </option>

            <option value="their">
              {game.opponent}
            </option>
          </select>

          <label>得点</label>

          <input
            type="number"
            min={0}
            value={editRuns}
            onChange={(e) =>
              setEditRuns(n(e.target.value))
            }
          />

          <button
            className="primary"
            onClick={saveEditedScore}
          >
            変更を保存
          </button>

          <button
            onClick={() => setEditOpen(false)}
          >
            キャンセル
          </button>
        </section>
      )}

      <h2>打撃個人成績</h2>

      {!battingPlayers.length ? (
        <div className="notice">
          この試合の打撃記録はありません。
        </div>
      ) : (
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>選手</th>
                <th>打席</th>
                <th>打数</th>
                <th>安打</th>
                <th>二塁打</th>
                <th>三塁打</th>
                <th>HR</th>
                <th>打点</th>
                <th>四球</th>
                <th>死球</th>
                <th>三振</th>
                <th>打率</th>
                <th>出塁率</th>
                <th>OPS</th>
              </tr>
            </thead>

            <tbody>
              {battingPlayers.map(
                ({ player, rows }) => {
                  const s = calcBatting(rows);

                  return (
                    <tr key={player.id}>
                      <th>{player.name}</th>
                      <td>{s.PA}</td>
                      <td>{s.AB}</td>
                      <td>{s.H}</td>
                      <td>{s.doubles}</td>
                      <td>{s.triples}</td>
                      <td>{s.HR}</td>
                      <td>{s.RBI}</td>
                      <td>{s.BB}</td>
                      <td>{s.HBP}</td>
                      <td>{s.SO}</td>
                      <td>{fmt3(s.AVG)}</td>
                      <td>{fmt3(s.OBP)}</td>
                      <td>{fmt3(s.OPS)}</td>
                    </tr>
                  );
                }
              )}
            </tbody>
          </table>
        </div>
      )}

      <h2>投手個人成績</h2>

      {!pitcherIds.length ? (
        <div className="notice">
          この試合の投手記録はありません。
        </div>
      ) : (
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>投手</th>
                <th>投球回</th>
                <th>被安打</th>
                <th>奪三振</th>
                <th>与四球</th>
                <th>与死球</th>
                <th>被本塁打</th>
                <th>失点</th>
                <th>自責点</th>
                <th>防御率</th>
              </tr>
            </thead>

            <tbody>
              {pitcherIds.map((pid) => {
                const player = players.find(
                  (p) => String(p.id) === pid
                );

                const rows = pitching.filter(
                  (r) =>
                    String(r.pitcher_id) === pid
                );

                const finals = finalPitching.filter(
                  (r) =>
                    String(r.pitcher_id) === pid
                );

                const s = calcPitching(
                  rows,
                  finals
                );

                return (
                  <tr key={pid}>
                    <th>
                      {player?.name || "投手"}
                    </th>
                    <td>
                      {formatIP(s.outs)}
                    </td>
                    <td>{s.H}</td>
                    <td>{s.SO}</td>
                    <td>{s.BB}</td>
                    <td>{s.HBP}</td>
                    <td>{s.HR}</td>
                    <td>{s.R}</td>
                    <td>{s.ER}</td>
                    <td>
                      {s.ERA === null
                        ? "---"
                        : s.ERA.toFixed(2)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
