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
      if (r.hit_type === "本塁打") HR++;
    }
  }

  const AVG = AB ? H / AB : null;
  const obpDen = AB + BB + HBP + SF;
  const OBP = obpDen
    ? (H + BB + HBP) / obpDen
    : null;

  const singles = H - doubles - triples - HR;
  const TB =
    singles +
    doubles * 2 +
    triples * 3 +
    HR * 4;

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
    ["安打", "二塁打", "三塁打", "本塁打"].includes(
      r.result
    )
  ).length;

  const SO = rows.filter(
    (r) => r.result === "三振"
  ).length;

  const BB = rows.filter(
    (r) => r.result === "四球"
  ).length;

  const HBP = rows.filter(
    (r) => r.result === "死球"
  ).length;

  const HR = rows.filter(
    (r) => r.result === "本塁打"
  ).length;

  const R = rows.reduce(
    (a, r) => a + n(r.runs),
    0
  );

  const outs = finalRows.reduce(
    (a, r) => a + n(r.innings_outs),
    0
  );

  const ER = finalRows.reduce(
    (a, r) => a + n(r.earned_runs),
    0
  );

  const ERA = outs && finalRows.length
    ? (ER * 27) / outs
    : null;

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
    const raw =
      localStorage.getItem(RECENT_KEY);

    const old = raw
      ? JSON.parse(raw)
      : [];

    const next = [
      team,
      ...old.filter(
        (x: Team) =>
          x.team_code !== team.team_code
      ),
    ].slice(0, 8);

    localStorage.setItem(
      RECENT_KEY,
      JSON.stringify(next)
    );
  } catch {}
}

/* =========================================================
   APP
========================================================= */

export default function Page() {
  const [team, setTeam] =
    useState<Team | null>(null);

  const [recentTeams, setRecentTeams] =
    useState<Team[]>([]);

  const [page, setPage] =
    useState("home");

  const [hasLiveGame, setHasLiveGame] =
    useState(false);

  useEffect(() => {
    try {
      const raw =
        localStorage.getItem(RECENT_KEY);

      if (raw) {
        setRecentTeams(
          JSON.parse(raw)
        );
      }
    } catch {}
  }, []);

  async function checkLiveGame(
    selectedTeam: Team
  ) {
    const { data } = await supabase
      .from("games")
      .select("id")
      .eq("team_id", selectedTeam.id)
      .eq("status", "playing")
      .limit(1);

    setHasLiveGame(
      !!data && data.length > 0
    );
  }

  useEffect(() => {
    if (team) {
      checkLiveGame(team);
    }
  }, [team, page]);

  function enterTeam(t: Team) {
    setTeam(t);
    saveRecentTeam(t);

    try {
      const raw =
        localStorage.getItem(
          RECENT_KEY
        );

      if (raw) {
        setRecentTeams(
          JSON.parse(raw)
        );
      }
    } catch {}

    setPage("home");
  }

  /*
    全画面共通ホーム処理。

    子画面独自の状態に依存せず、
    必ずトップ画面へ戻す。
  */
  function goHome() {
    setPage("home");

    if (team) {
      checkLiveGame(team);
    }

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
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
          hasLiveGame={hasLiveGame}
          changeTeam={() => {
            setTeam(null);
            setPage("home");
            setHasLiveGame(false);
          }}
        />
      )}

      {page === "players" && (
        <Players
          team={team}
          goHome={goHome}
        />
      )}

      {page === "newgame" && (
        <NewGame
          team={team}
          goHome={goHome}
          openGame={() => {
            setHasLiveGame(true);
            setPage("score");
          }}
        />
      )}

      {page === "score" && (
        <LiveScore
          team={team}
          goHome={goHome}
          onGameFinished={() => {
            setHasLiveGame(false);
            setPage("home");
          }}
        />
      )}

      {page === "stats" && (
        <Stats
          team={team}
          goHome={goHome}
        />
      )}

      {page === "teamstats" && (
        <TeamStats
          team={team}
          goHome={goHome}
        />
      )}

      {page === "history" && (
        <History
          team={team}
          goHome={goHome}
        />
      )}
    </main>
  );
}

/* =========================================================
   TEAM GATE
========================================================= */

function TeamGate({
  recentTeams,
  enterTeam,
}: {
  recentTeams: Team[];
  enterTeam: (t: Team) => void;
}) {
  const [code, setCode] =
    useState("");

  const [name, setName] =
    useState("");

  const [message, setMessage] =
    useState("");

  async function joinTeam(
    input?: string
  ) {
    const target = (
      input || code
    )
      .trim()
      .toUpperCase();

    if (!target) return;

    setMessage("");

    const { data, error } =
      await supabase
        .from("teams")
        .select(
          "id,team_name,team_code"
        )
        .eq(
          "team_code",
          target
        )
        .maybeSingle();

    if (error) {
      setMessage(
        "チーム情報を取得できませんでした。"
      );
      return;
    }

    if (!data) {
      setMessage(
        "チームが見つかりません。"
      );
      return;
    }

    enterTeam(data as Team);
  }

  async function createTeam() {
    if (!name.trim()) {
      setMessage(
        "チーム名を入力してください。"
      );
      return;
    }

    const chars =
      "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

    let newCode = "";

    for (let i = 0; i < 6; i++) {
      newCode +=
        chars[
          Math.floor(
            Math.random() *
              chars.length
          )
        ];
    }

    const ownerCode =
      crypto.randomUUID?.() ||
      Math.random()
        .toString(36)
        .slice(2);

    const { data, error } =
      await supabase
        .from("teams")
        .insert({
          team_name:
            name.trim(),
          team_code:
            newCode,
          owner_code:
            ownerCode,
        })
        .select(
          "id,team_name,team_code"
        )
        .single();

    if (error || !data) {
      setMessage(
        "チームを作成できませんでした。"
      );
      return;
    }

    enterTeam(data as Team);
  }

  return (
    <main className="wrap">
      <div className="brand">
        Baseball Score
      </div>

      {recentTeams.length > 0 && (
        <section className="card">
          <h2>
            最近使ったチーム
          </h2>

          {recentTeams.map(
            (t) => (
              <button
                key={
                  t.team_code
                }
                onClick={() =>
                  joinTeam(
                    t.team_code
                  )
                }
              >
                <strong>
                  {t.team_name}
                </strong>

                <br />

                <small>
                  {t.team_code}
                </small>
              </button>
            )
          )}
        </section>
      )}

      <section className="card">
        <h2>チームに参加</h2>

        <input
          value={code}
          placeholder="チームコード"
          onChange={(e) =>
            setCode(
              e.target.value.toUpperCase()
            )
          }
        />

        <button
          className="primary"
          onClick={() =>
            joinTeam()
          }
        >
          チームに参加
        </button>
      </section>

      <section className="card">
        <h2>チームを作成</h2>

        <input
          value={name}
          placeholder="例：ベイスターズ"
          onChange={(e) =>
            setName(
              e.target.value
            )
          }
        />

        <button
          className="primary"
          onClick={createTeam}
        >
          チームを作成
        </button>
      </section>

      {message && (
        <div className="notice">
          {message}
        </div>
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
  hasLiveGame,
}: {
  team: Team;
  go: (p: string) => void;
  changeTeam: () => void;
  hasLiveGame: boolean;
}) {
  return (
    <>
      <div className="top">
        <div>
          <h1>
            {team.team_name}
          </h1>

          <span className="pill">
            TEAM CODE{" "}
            {team.team_code}
          </span>
        </div>

        <button
          onClick={
            changeTeam
          }
        >
          チームを変更
        </button>
      </div>

      <div className="grid2">
        <button
          className="primary"
          onClick={() =>
            go("newgame")
          }
        >
          新しい試合
        </button>

        {hasLiveGame && (
          <button
            onClick={() =>
              go("score")
            }
          >
            試合を続ける
          </button>
        )}

        <button
          onClick={() =>
            go("players")
          }
        >
          選手登録
        </button>

        <button
          onClick={() =>
            go("stats")
          }
        >
          個人成績・ランキング
        </button>

        <button
          onClick={() =>
            go("teamstats")
          }
        >
          チーム成績
        </button>

        <button
          onClick={() =>
            go("history")
          }
        >
          過去の試合
        </button>
      </div>
    </>
  );
}

/* =========================================================
   HOME BUTTON
========================================================= */

function HomeButton({
  onClick,
}: {
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
    >
      ← ホーム
    </button>
  );
}

/* =========================================================
   PLAYERS
========================================================= */

function Players({
  team,
  goHome,
}: {
  team: Team;
  goHome: () => void;
}) {
  const [players, setPlayers] =
    useState<Player[]>([]);

  const [name, setName] =
    useState("");

  const [number, setNumber] =
    useState("");

  const [grade, setGrade] =
    useState("1年");

  const [message, setMessage] =
    useState("");

  async function load() {
    const { data } =
      await supabase
        .from("players")
        .select("*")
        .eq(
          "team_id",
          team.id
        )
        .order("number");

    setPlayers(
      (data || []) as Player[]
    );
  }

  useEffect(() => {
    load();
  }, [team.id]);

  async function addPlayer() {
    if (!name.trim()) return;

    const { error } =
      await supabase
        .from("players")
        .insert({
          team_id:
            team.id,
          name:
            name.trim(),
          number:
            number || null,
          grade,
          active: true,
        });

    if (error) {
      setMessage(
        "登録できませんでした。"
      );
      return;
    }

    setName("");
    setNumber("");

    setMessage(
      "選手を登録しました。"
    );

    await load();
  }

  return (
    <>
      <HomeButton
        onClick={goHome}
      />

      <h1>選手登録</h1>

      <section className="card">
        <input
          placeholder="選手名"
          value={name}
          onChange={(e) =>
            setName(
              e.target.value
            )
          }
        />

        <input
          placeholder="背番号"
          value={number}
          onChange={(e) =>
            setNumber(
              e.target.value
            )
          }
        />

        <select
          value={grade}
          onChange={(e) =>
            setGrade(
              e.target.value
            )
          }
        >
          <option>1年</option>
          <option>2年</option>
          <option>3年</option>
          <option>4年</option>
          <option>その他</option>
        </select>

        <button
          className="primary"
          onClick={
            addPlayer
          }
        >
          登録
        </button>

        {message && (
          <div className="success">
            {message}
          </div>
        )}
      </section>

      <section className="card">
        <h2>登録選手</h2>

        {players.map((p) => (
          <div
            className="row"
            key={p.id}
          >
            <strong>
              {p.name}
            </strong>

            <span>
              #
              {p.number ||
                "-"}{" "}
              ｜{" "}
              {p.grade ||
                "未設定"}
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
  goHome,
  openGame,
}: {
  team: Team;
  goHome: () => void;
  openGame: () => void;
}) {
  const [opponent, setOpponent] =
    useState("");

  const [gameDate, setGameDate] =
    useState(
      new Date()
        .toISOString()
        .slice(0, 10)
    );

  const [place, setPlace] =
    useState("");

  const [gameType, setGameType] =
    useState("練習試合");

  const [
    tournament,
    setTournament,
  ] = useState("");

  const [batFirst, setBatFirst] =
    useState(true);

  const [players, setPlayers] =
    useState<Player[]>([]);

  const [lineup, setLineup] =
    useState<any[]>([]);

  const [pitcher, setPitcher] =
    useState("");

  useEffect(() => {
    supabase
      .from("players")
      .select("*")
      .eq(
        "team_id",
        team.id
      )
      .then(({ data }) => {
        setPlayers(
          (data ||
            []) as Player[]
        );
      });
  }, [team.id]);

  function setSlot(
    index: number,
    value: string
  ) {
    const next = [
      ...lineup,
    ];

    next[index] =
      value;

    setLineup(next);
  }

  async function createGame() {
    if (
      !opponent.trim()
    ) {
      alert(
        "対戦相手を入力してください。"
      );
      return;
    }

    const {
      data: game,
      error,
    } = await supabase
      .from("games")
      .insert({
        team_id:
          team.id,

        game_date:
          gameDate,

        opponent:
          opponent.trim(),

        place:
          place || null,

        game_type:
          gameType ||
          null,

        tournament:
          tournament ||
          null,

        bat_first:
          batFirst,

        our_score: 0,
        their_score: 0,

        status:
          "playing",

        current_inning: 1,

        current_mode:
          batFirst
            ? "offense"
            : "defense",

        current_batter_index:
          0,

        opponent_batter_index:
          0,

        current_pitcher_id:
          pitcher ||
          null,
      })
      .select()
      .single();

    if (
      error ||
      !game
    ) {
      alert(
        "試合を作成できませんでした。"
      );
      return;
    }

    const lineupRows =
      lineup
        .map(
          (
            playerId,
            i
          ) => ({
            game_id:
              game.id,

            batting_order:
              i + 1,

            starter: true,

            player_id:
              playerId ||
              null,
          })
        )
        .filter(
          (x) =>
            x.player_id
        );

    if (
      lineupRows.length
    ) {
      await supabase
        .from("lineup")
        .insert(
          lineupRows
        );
    }

    /*
      新しい試合作成後は
      「試合を続ける」と同じ
      スコア画面へ移動
    */
    openGame();
  }

  return (
    <>
      <HomeButton
        onClick={goHome}
      />

      <h1>
        新しい試合
      </h1>

      <section className="card">
        <label>
          試合日
        </label>

        <input
          type="date"
          value={
            gameDate
          }
          onChange={(e) =>
            setGameDate(
              e.target.value
            )
          }
        />

        <label>
          対戦相手
        </label>

        <input
          value={
            opponent
          }
          onChange={(e) =>
            setOpponent(
              e.target.value
            )
          }
        />

        <label>場所</label>

        <input
          value={place}
          onChange={(e) =>
            setPlace(
              e.target.value
            )
          }
        />

        <label>
          試合種別
        </label>

        <input
          value={
            gameType
          }
          onChange={(e) =>
            setGameType(
              e.target.value
            )
          }
        />

        <label>大会</label>

        <input
          value={
            tournament
          }
          onChange={(e) =>
            setTournament(
              e.target.value
            )
          }
        />

        <label>
          先攻・後攻
        </label>

        <select
          value={
            batFirst
              ? "first"
              : "second"
          }
          onChange={(e) =>
            setBatFirst(
              e.target.value ===
                "first"
            )
          }
        >
          <option value="first">
            先攻
          </option>

          <option value="second">
            後攻
          </option>
        </select>
      </section>

      <section className="card">
        <h2>オーダー</h2>

        {Array.from({
          length: 9,
        }).map(
          (_, i) => (
            <label
              key={i}
            >
              {i + 1}番

              <select
                value={
                  lineup[i] ||
                  ""
                }
                onChange={(
                  e
                ) =>
                  setSlot(
                    i,
                    e.target
                      .value
                  )
                }
              >
                <option value="">
                  選択
                </option>

                {players.map(
                  (p) => (
                    <option
                      key={
                        p.id
                      }
                      value={
                        p.id
                      }
                    >
                      {
                        p.name
                      }
                    </option>
                  )
                )}
              </select>
            </label>
          )
        )}

        <label>
          先発投手
        </label>

        <select
          value={
            pitcher
          }
          onChange={(e) =>
            setPitcher(
              e.target.value
            )
          }
        >
          <option value="">
            選択
          </option>

          {players.map(
            (p) => (
              <option
                key={p.id}
                value={p.id}
              >
                {p.name}
              </option>
            )
          )}
        </select>

        <button
          className="primary"
          onClick={
            createGame
          }
        >
          試合開始
        </button>
      </section>
    </>
  );
}

/* =========================================================
   SCOREBOARD
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
  const maxInning =
    Math.max(
      7,
      ...scores.map(
        (x) =>
          n(x.inning)
      )
    );

  const innings =
    Array.from(
      {
        length:
          maxInning,
      },
      (_, i) =>
        i + 1
    );

  const get = (
    inning: number,
    side:
      | "our"
      | "their"
  ) => {
    const x =
      scores.find(
        (s) =>
          n(
            s.inning
          ) === inning &&
          s.side ===
            side
      );

    return x
      ? n(x.runs)
      : "";
  };

  const ourTotal =
    scores
      .filter(
        (x) =>
          x.side ===
          "our"
      )
      .reduce(
        (a, x) =>
          a +
          n(x.runs),
        0
      );

  const theirTotal =
    scores
      .filter(
        (x) =>
          x.side ===
          "their"
      )
      .reduce(
        (a, x) =>
          a +
          n(x.runs),
        0
      );

  /*
    先攻を必ず上段。
    後攻を必ず下段。
  */
  const topName =
    game.bat_first
      ? team.team_name
      : game.opponent;

  const bottomName =
    game.bat_first
      ? game.opponent
      : team.team_name;

  const topSide:
    | "our"
    | "their" =
    game.bat_first
      ? "our"
      : "their";

  const bottomSide:
    | "our"
    | "their" =
    game.bat_first
      ? "their"
      : "our";

  const topTotal =
    topSide === "our"
      ? ourTotal
      : theirTotal;

  const bottomTotal =
    bottomSide ===
    "our"
      ? ourTotal
      : theirTotal;

  return (
    <div className="scroll">
      <table>
        <thead>
          <tr>
            <th>
              TEAM
            </th>

            {innings.map(
              (i) => (
                <th key={i}>
                  {i}
                </th>
              )
            )}

            <th>R</th>
          </tr>
        </thead>

        <tbody>
          <tr>
            <th>
              {topName}
            </th>

            {innings.map(
              (i) => (
                <td key={i}>
                  {get(
                    i,
                    topSide
                  )}
                </td>
              )
            )}

            <td>
              <strong>
                {topTotal}
              </strong>
            </td>
          </tr>

          <tr>
            <th>
              {bottomName}
            </th>

            {innings.map(
              (i) => (
                <td key={i}>
                  {get(
                    i,
                    bottomSide
                  )}
                </td>
              )
            )}

            <td>
              <strong>
                {
                  bottomTotal
                }
              </strong>
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

function LiveScore({ team, goHome, onGameFinished }: { team: Team; goHome: () => void; onGameFinished: () => void; }) {
  const [game,setGame]=useState<Game|null>(null); const [scores,setScores]=useState<InningScore[]>([]); const [players,setPlayers]=useState<Player[]>([]); const [lineup,setLineup]=useState<any[]>([]); const [batting,setBatting]=useState<BattingRow[]>([]); const [pitching,setPitching]=useState<PitchingRow[]>([]);
  const [inningRuns,setInningRuns]=useState(0); const [message,setMessage]=useState(""); const [batResult,setBatResult]=useState("アウト"); const [field,setField]=useState("遊"); const [hitType,setHitType]=useState("単打"); const [rbi,setRbi]=useState(0); const [pitchResult,setPitchResult]=useState("アウト"); const [pitchRuns,setPitchRuns]=useState(0); const [editBat,setEditBat]=useState<BattingRow|null>(null); const [editPitch,setEditPitch]=useState<PitchingRow|null>(null); const [finishOpen,setFinishOpen]=useState(false); const [gamePitchers,setGamePitchers]=useState<Player[]>([]); const [pitcherInput,setPitcherInput]=useState<Record<string,{full:number;thirds:number;er:number}>>({}); const [saving,setSaving]=useState(false); const [tiebreak,setTiebreak]=useState(false);

  async function load(){
    const gRes=await supabase.from("games").select("*").eq("team_id",team.id).eq("status","playing").order("created_at",{ascending:false}).limit(1);
    const g=(gRes.data||[])[0] as Game|undefined; if(!g){setGame(null);return;} setGame(g);
    const [s,p,l,b,pi]=await Promise.all([
      supabase.from("inning_scores").select("*").eq("game_id",g.id), supabase.from("players").select("*").eq("team_id",team.id).eq("active",true), supabase.from("lineup").select("*").eq("game_id",g.id).order("batting_order"), supabase.from("batting").select("*").eq("game_id",g.id).order("created_at"), supabase.from("pitching").select("*").eq("game_id",g.id).order("created_at")]);
    setScores((s.data||[]) as InningScore[]); setPlayers((p.data||[]) as Player[]); setLineup(l.data||[]); setBatting((b.data||[]) as BattingRow[]); setPitching((pi.data||[]) as PitchingRow[]);
  }
  useEffect(()=>{load();},[team.id]);
  const playerName=(id:any)=>players.find(p=>String(p.id)===String(id))?.name||"選手";
  const currentLineup=lineup.length?lineup:[]; const batterIndex=game&&currentLineup.length?n(game.current_batter_index)%currentLineup.length:0; const batterRow=currentLineup[batterIndex]; const batter=batterRow?players.find(p=>String(p.id)===String(batterRow.player_id)):null;
  const currentInning=n(game?.current_inning||1); const currentBatLogs=batting.filter(x=>n(x.inning)===currentInning); const currentPitchLogs=pitching.filter(x=>n(x.inning)===currentInning);

  async function recordBat(){ if(!game||!batter){setMessage("打者を選択できません。オーダーを確認してください。");return;} const row={game_id:game.id,player_id:batter.id,inning:currentInning,batting_order:batterIndex+1,result:batResult,field:["アウト","失策"].includes(batResult)?field:null,hit_type:batResult==="安打"?hitType:null,rbi:n(rbi)}; const {error}=await supabase.from("batting").insert(row); if(error){setMessage(error.message);return;} await supabase.from("games").update({current_batter_index:(batterIndex+1)%currentLineup.length}).eq("id",game.id); setRbi(0);setMessage("打撃記録を登録しました。");await load(); }
  async function recordPitch(){ if(!game?.current_pitcher_id){setMessage("現在の投手を選択してください。");return;} const order=n(game.opponent_batter_index)%9+1; const {error}=await supabase.from("pitching").insert({game_id:game.id,pitcher_id:game.current_pitcher_id,inning:currentInning,batting_order:order,result:pitchResult,runs:n(pitchRuns)}); if(error){setMessage(error.message);return;} await supabase.from("games").update({opponent_batter_index:n(game.opponent_batter_index)+1}).eq("id",game.id);setPitchRuns(0);setMessage("守備記録を登録しました。");await load(); }
  async function saveBatEdit(){if(!editBat)return;const {error}=await supabase.from("batting").update({result:editBat.result,field:editBat.field||null,hit_type:editBat.hit_type||null,rbi:n(editBat.rbi)}).eq("id",editBat.id);if(error){setMessage(error.message);return;}setEditBat(null);await load();}
  async function deleteBat(row:BattingRow){if(!confirm("この打撃記録を削除しますか？"))return;await supabase.from("batting").delete().eq("id",row.id);if(game&&currentLineup.length)await supabase.from("games").update({current_batter_index:(n(game.current_batter_index)-1+currentLineup.length)%currentLineup.length}).eq("id",game.id);await load();}
  async function savePitchEdit(){if(!editPitch)return;const {error}=await supabase.from("pitching").update({result:editPitch.result,runs:n(editPitch.runs)}).eq("id",editPitch.id);if(error){setMessage(error.message);return;}setEditPitch(null);await load();}
  async function deletePitch(row:PitchingRow){if(!confirm("この守備記録を削除しますか？"))return;await supabase.from("pitching").delete().eq("id",row.id);if(game)await supabase.from("games").update({opponent_batter_index:Math.max(0,n(game.opponent_batter_index)-1)}).eq("id",game.id);await load();}
  async function changePitcher(id:string){if(!game)return;const {error}=await supabase.from("games").update({current_pitcher_id:id||null}).eq("id",game.id);if(error)setMessage(error.message);else await load();}
  async function saveScore(inning:number,side:"our"|"their",runs:number){if(!game)return false;const {error}=await supabase.from("inning_scores").upsert({game_id:game.id,inning,side,runs:n(runs)},{onConflict:"game_id,inning,side"});if(error){setMessage(error.message);return false;}const {data}=await supabase.from("inning_scores").select("*").eq("game_id",game.id);const all=(data||[]) as InningScore[];const our=all.filter(x=>x.side==="our").reduce((a,x)=>a+n(x.runs),0);const their=all.filter(x=>x.side==="their").reduce((a,x)=>a+n(x.runs),0);await supabase.from("games").update({our_score:our,their_score:their}).eq("id",game.id);return true;}
  async function changeSides(){if(!game)return;const side=game.current_mode==="offense"?"our":"their";if(!(await saveScore(currentInning,side,inningRuns)))return;const wasBottom=(game.bat_first&&game.current_mode==="defense")||(!game.bat_first&&game.current_mode==="offense");const nextMode=game.current_mode==="offense"?"defense":"offense";await supabase.from("games").update({current_mode:nextMode,current_inning:wasBottom?currentInning+1:currentInning}).eq("id",game.id);setInningRuns(0);await load();}
  async function setTiebreakLead(){if(!game)return; if(game.current_mode==="offense"&&currentLineup.length){const raw=prompt("先頭打者の打順を入力してください（1〜"+currentLineup.length+"）",String(batterIndex+1));if(!raw)return;const idx=Math.max(1,Math.min(currentLineup.length,n(raw)))-1;await supabase.from("games").update({current_batter_index:idx,tiebreak_active:true}).eq("id",game.id);}else{const raw=prompt("相手の先頭打者の打順を入力してください（1〜9）",String(n(game.opponent_batter_index)%9+1));if(!raw)return;await supabase.from("games").update({opponent_batter_index:Math.max(1,Math.min(9,n(raw)))-1,tiebreak_active:true}).eq("id",game.id);}setTiebreak(true);await load();}
  async function openFinish(){if(!game)return;const ids=Array.from(new Set([...pitching.map(x=>String(x.pitcher_id)),...(game.current_pitcher_id?[String(game.current_pitcher_id)]:[])]));const ps=players.filter(p=>ids.includes(String(p.id)));setGamePitchers(ps);const init:Record<string,{full:number;thirds:number;er:number}>={};ps.forEach(p=>init[String(p.id)]={full:0,thirds:0,er:0});setPitcherInput(init);setFinishOpen(true);}
  async function finishGame(){if(!game||saving)return;setSaving(true);try{const side=game.current_mode==="offense"?"our":"their";const exists=scores.some(s=>n(s.inning)===currentInning&&s.side===side);if(!exists)await saveScore(currentInning,side,inningRuns);for(const p of gamePitchers){const v=pitcherInput[String(p.id)]||{full:0,thirds:0,er:0};const {error}=await supabase.from("pitching_game_stats").upsert({game_id:game.id,pitcher_id:p.id,innings_outs:n(v.full)*3+n(v.thirds),earned_runs:n(v.er)},{onConflict:"game_id,pitcher_id"});if(error)throw error;}const {error}=await supabase.from("games").update({status:"finished",finished_at:new Date().toISOString()}).eq("id",game.id);if(error)throw error;onGameFinished();}catch(e:any){setMessage("ゲームセットの保存に失敗しました："+(e?.message||""));}finally{setSaving(false);}}
  if(!game)return <><HomeButton onClick={goHome}/><h1>試合を続ける</h1><div className="notice">進行中の試合はありません。</div></>;
  const halfText=game.bat_first?(game.current_mode==="offense"?"表":"裏"):(game.current_mode==="defense"?"表":"裏");
  return <><HomeButton onClick={goHome}/><h1>vs {game.opponent}</h1><div className="score">{currentInning}回{halfText} ｜ {game.current_mode==="offense"?"攻撃中":"守備中"}</div><Scoreboard game={game} team={team} scores={scores}/>{message&&<div className="notice">{message}</div>}
    {game.current_mode==="offense"?<section className="card"><h2>攻撃入力</h2><div className="metric">現在の打者：{batter?`${batterIndex+1}番 ${batter.name}`:"オーダー未設定"}</div><label>結果</label><select value={batResult} onChange={e=>setBatResult(e.target.value)}>{["安打","アウト","三振","四球","死球","失策","犠打","犠飛"].map(x=><option key={x}>{x}</option>)}</select>{["アウト","失策"].includes(batResult)&&<><label>守備位置</label><select value={field} onChange={e=>setField(e.target.value)}>{["投","捕","一","二","三","遊","左","中","右"].map(x=><option key={x}>{x}</option>)}</select></>}{batResult==="安打"&&<><label>何塁打</label><select value={hitType} onChange={e=>setHitType(e.target.value)}>{["単打","二塁打","三塁打","本塁打"].map(x=><option key={x}>{x}</option>)}</select></>}<label>打点</label><input type="number" min={0} value={rbi} onChange={e=>setRbi(n(e.target.value))}/><button className="primary" onClick={recordBat}>この打席を登録</button></section>
    :<section className="card"><h2>守備入力</h2><div className="metric">相手打順：{n(game.opponent_batter_index)%9+1}番</div><label>現在の投手</label><select value={String(game.current_pitcher_id||"")} onChange={e=>changePitcher(e.target.value)}><option value="">選択</option>{players.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select><label>結果</label><select value={pitchResult} onChange={e=>setPitchResult(e.target.value)}>{["アウト","三振","安打","二塁打","三塁打","本塁打","四球","死球","失策"].map(x=><option key={x}>{x}</option>)}</select><label>この打者で入った失点</label><input type="number" min={0} value={pitchRuns} onChange={e=>setPitchRuns(n(e.target.value))}/><button className="primary" onClick={recordPitch}>この打者を登録</button></section>}
    <section className="card"><h2>{currentInning}回{halfText}の記録</h2>{game.current_mode==="offense"?(currentBatLogs.length?currentBatLogs.map(r=><div className="log" key={r.id}><div><strong>{r.batting_order}番 {playerName(r.player_id)}</strong><br/><small>{r.result}{r.hit_type?`・${r.hit_type}`:""}　打点{n(r.rbi)}</small></div><div><button onClick={()=>setEditBat({...r})}>編集</button><button className="danger" onClick={()=>deleteBat(r)}>削除</button></div></div>):<p>この回の攻撃記録はまだありません。</p>):(currentPitchLogs.length?currentPitchLogs.map(r=><div className="log" key={r.id}><div><strong>相手{r.batting_order}番 ｜ {playerName(r.pitcher_id)}</strong><br/><small>{r.result}　失点{n(r.runs)}</small></div><div><button onClick={()=>setEditPitch({...r})}>編集</button><button className="danger" onClick={()=>deletePitch(r)}>削除</button></div></div>):<p>この回の守備記録はまだありません。</p>)}</section>
    {editBat&&<section className="card"><h2>打撃記録を編集</h2><select value={editBat.result} onChange={e=>setEditBat({...editBat,result:e.target.value})}>{["安打","アウト","三振","四球","死球","失策","犠打","犠飛"].map(x=><option key={x}>{x}</option>)}</select><input type="number" min={0} value={n(editBat.rbi)} onChange={e=>setEditBat({...editBat,rbi:n(e.target.value)})}/><button className="primary" onClick={saveBatEdit}>保存</button><button onClick={()=>setEditBat(null)}>キャンセル</button></section>}
    {editPitch&&<section className="card"><h2>守備記録を編集</h2><select value={editPitch.result} onChange={e=>setEditPitch({...editPitch,result:e.target.value})}>{["アウト","三振","安打","二塁打","三塁打","本塁打","四球","死球","失策"].map(x=><option key={x}>{x}</option>)}</select><input type="number" min={0} value={n(editPitch.runs)} onChange={e=>setEditPitch({...editPitch,runs:n(e.target.value)})}/><button className="primary" onClick={savePitchEdit}>保存</button><button onClick={()=>setEditPitch(null)}>キャンセル</button></section>}
    <section className="card"><h2>{currentInning}回{halfText}の得点</h2><input type="number" min={0} value={inningRuns} onChange={e=>setInningRuns(n(e.target.value))}/><button className="primary" onClick={changeSides}>攻守交替</button></section><div className="grid2"><button onClick={setTiebreakLead}>タイブレーク{tiebreak||game.tiebreak_active?"設定済":""}</button><button className="danger" onClick={openFinish}>ゲームセット</button></div>
    {finishOpen&&<section className="card"><h2>ゲームセット</h2><p>投手ごとに投球回と自責点を入力してください。</p>{gamePitchers.length?gamePitchers.map(p=>{const v=pitcherInput[String(p.id)]||{full:0,thirds:0,er:0};return <div key={p.id} className="card"><strong>{p.name}</strong><label>投球回（整数部分）</label><input type="number" min={0} value={v.full} onChange={e=>setPitcherInput({...pitcherInput,[String(p.id)]:{...v,full:n(e.target.value)}})}/><label>端数</label><select value={v.thirds} onChange={e=>setPitcherInput({...pitcherInput,[String(p.id)]:{...v,thirds:n(e.target.value)}})}><option value={0}>0/3</option><option value={1}>1/3</option><option value={2}>2/3</option></select><label>自責点</label><input type="number" min={0} value={v.er} onChange={e=>setPitcherInput({...pitcherInput,[String(p.id)]:{...v,er:n(e.target.value)}})}/></div>}):<p>投手記録がありません。</p>}<button className="danger" disabled={saving} onClick={finishGame}>{saving?"保存中…":"試合終了を確定"}</button><button onClick={()=>setFinishOpen(false)}>キャンセル</button></section>}
  </>;
}


/* =========================================================
   STATS
========================================================= */

function Stats({
  team,
  goHome,
}: {
  team: Team;
  goHome: () => void;
}) {
  const [players, setPlayers] =
    useState<Player[]>([]);

  const [batting, setBatting] =
    useState<
      BattingRow[]
    >([]);

  const [mode, setMode] =
    useState("individual");
  const [pitching, setPitching] = useState<PitchingRow[]>([]);
  const [finalPitching, setFinalPitching] = useState<PitchingGameStat[]>([]);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function load() {
      const { data: p } =
        await supabase
          .from(
            "players"
          )
          .select("*")
          .eq(
            "team_id",
            team.id
          );

      const {
        data: games,
      } = await supabase
        .from("games")
        .select("id")
        .eq(
          "team_id",
          team.id
        );

      const ids =
        (games || []).map(
          (g) => g.id
        );

      let b: any[] = [];
      let pitchingRows: PitchingRow[] = [];
      let finalRows: PitchingGameStat[] = [];

      if (ids.length) {
        const res =
          await supabase
            .from(
              "batting"
            )
            .select("*")
            .in(
              "game_id",
              ids
            );

        b = res.data || [];
        const [pr, fr] = await Promise.all([
          supabase.from("pitching").select("*").in("game_id", ids),
          supabase.from("pitching_game_stats").select("*").in("game_id", ids),
        ]);
        if (pr.error || fr.error) setErrorMessage(`投手データの取得エラー：${[pr.error?.message, fr.error?.message].filter(Boolean).join(" / ")}`);
        pitchingRows = (pr.data || []) as PitchingRow[];
        finalRows = (fr.data || []) as PitchingGameStat[];
      }

      setPlayers(
        (p ||
          []) as Player[]
      );

      setBatting(b as BattingRow[]);
      setPitching(pitchingRows);
      setFinalPitching(finalRows);
    }

    load();
  }, [team.id]);

  return (
    <>
      <HomeButton
        onClick={goHome}
      />

      <h1>
        成績確認
      </h1>

      {errorMessage && <div className="notice">{errorMessage}</div>}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 6, marginBottom: 16, width: "100%" }}>
        {([
          ["individual", "打撃個人成績"],
          ["pitching", "投手個人成績"],
          ["ranking", "ランキング"],
        ] as const).map(([key, label]) => (
          <button
            key={key}
            type="button"
            className={mode === key || (key === "ranking" && mode === "pitchranking") ? "primary" : ""}
            style={{ width: "100%", minWidth: 0, padding: "12px 3px", fontSize: 12, lineHeight: 1.4, whiteSpace: "normal", overflowWrap: "anywhere", color: mode === key || (key === "ranking" && mode === "pitchranking") ? "#fff" : "#123c2b", background: mode === key || (key === "ranking" && mode === "pitchranking") ? "#123c2b" : "#f1f5f2", border: "1px solid #cbd5ce", borderRadius: 8 }}
            onClick={() => setMode(key)}
          >
            {label}
          </button>
        ))}
      </div>
      {mode === "ranking" && (
        <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
          <button type="button" className="primary" onClick={() => setMode("ranking")}>打撃ランキング</button>
          <button type="button" onClick={() => setMode("pitchranking")}>投手ランキング</button>
        </div>
      )}
      {mode === "pitchranking" && (
        <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
          <button type="button" onClick={() => setMode("ranking")}>打撃ランキング</button>
          <button type="button" className="primary" onClick={() => setMode("pitchranking")}>投手ランキング</button>
        </div>
      )}

      {mode === "pitching" && <PitcherStatsTable players={players} pitching={pitching} finals={finalPitching} />}
      {mode === "pitchranking" && <PitcherRankings players={players} pitching={pitching} finals={finalPitching} />}

      {mode ===
        "individual" && (
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
                <th>
                  出塁率
                </th>
                <th>OPS</th>
              </tr>
            </thead>

            <tbody>
              {players.map(
                (p) => {
                  const s =
                    calcBatting(
                      batting.filter(
                        (
                          x
                        ) =>
                          String(
                            x.player_id
                          ) ===
                          String(
                            p.id
                          )
                      )
                    );

                  return (
                    <tr
                      key={
                        p.id
                      }
                    >
                      <th>
                        {
                          p.name
                        }
                      </th>

                      <td>
                        {
                          s.PA
                        }
                      </td>

                      <td>
                        {
                          s.AB
                        }
                      </td>

                      <td>
                        {s.H}
                      </td>

                      <td>
                        {
                          s.HR
                        }
                      </td>

                      <td>
                        {
                          s.RBI
                        }
                      </td>

                      <td>
                        {
                          s.SO
                        }
                      </td>

                      <td>
                        {
                          s.BB
                        }
                      </td>

                      <td>
                        {
                          s.HBP
                        }
                      </td>

                      <td>
                        {fmt3(
                          s.AVG
                        )}
                      </td>

                      <td>
                        {fmt3(
                          s.OBP
                        )}
                      </td>

                      <td>
                        {fmt3(
                          s.OPS
                        )}
                      </td>
                    </tr>
                  );
                }
              )}
            </tbody>
          </table>
        </div>
      )}

      {mode ===
        "ranking" && (
        <Rankings
          players={
            players
          }
          batting={
            batting
          }
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
  const [
    category,
    setCategory,
  ] = useState("打率");

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

  const ranking =
    useMemo(() => {
      return players
        .map((p) => {
          const s =
            calcBatting(
              batting.filter(
                (x) =>
                  String(
                    x.player_id
                  ) ===
                  String(
                    p.id
                  )
              )
            );

          let value:
            | number
            | null = 0;

          if (
            category ===
            "打率"
          )
            value =
              s.AVG;

          if (
            category ===
            "出塁率"
          )
            value =
              s.OBP;

          if (
            category ===
            "OPS"
          )
            value =
              s.OPS;

          if (
            category ===
            "安打"
          )
            value =
              s.H;

          if (
            category ===
            "本塁打"
          )
            value =
              s.HR;

          if (
            category ===
            "打点"
          )
            value =
              s.RBI;

          if (
            category ===
            "三振"
          )
            value =
              s.SO;

          if (
            category ===
            "四球"
          )
            value =
              s.BB;

          if (
            category ===
            "死球"
          )
            value =
              s.HBP;

          return {
            player: p,
            value,
          };
        })
        .filter(
          (x) =>
            x.value !==
            null
        )
        .sort(
          (a, b) =>
            n(b.value) -
            n(a.value)
        );
    }, [
      players,
      batting,
      category,
    ]);

  const isRate =
    [
      "打率",
      "出塁率",
      "OPS",
    ].includes(
      category
    );

  return (
    <section className="card">
      <label>
        ランキング項目
      </label>

      <select
        value={
          category
        }
        onChange={(e) =>
          setCategory(
            e.target.value
          )
        }
      >
        {options.map(
          (x) => (
            <option
              key={x}
            >
              {x}
            </option>
          )
        )}
      </select>

      {ranking.map(
        (r, i) => (
          <div
            className="row"
            key={
              r.player.id
            }
          >
            <strong>
              {i + 1}位　
              {
                r.player
                  .name
              }
            </strong>

            <span>
              {isRate
                ? fmt3(
                    r.value
                  )
                : n(
                    r.value
                  )}
            </span>
          </div>
        )
      )}
    </section>
  );
}

/* =========================================================
   TEAM STATS
========================================================= */

function TeamStats({
  team,
  goHome,
}: {
  team: Team;
  goHome: () => void;
}) {
  const [games, setGames] =
    useState<Game[]>([]);

  useEffect(() => {
    supabase
      .from("games")
      .select("*")
      .eq(
        "team_id",
        team.id
      )
      .eq(
        "status",
        "finished"
      )
      .then(
        ({ data }) =>
          setGames(
            (data ||
              []) as Game[]
          )
      );
  }, [team.id]);

  const wins =
    games.filter(
      (g) =>
        n(
          g.our_score
        ) >
        n(
          g.their_score
        )
    ).length;

  const losses =
    games.filter(
      (g) =>
        n(
          g.our_score
        ) <
        n(
          g.their_score
        )
    ).length;

  const draws =
    games.length -
    wins -
    losses;

  return (
    <>
      <HomeButton
        onClick={goHome}
      />

      <h1>
        チーム成績
      </h1>

      <section className="card">
        <div className="metric">
          <span>戦績</span>

          <strong>
            {wins}勝{" "}
            {losses}敗{" "}
            {draws}分
          </strong>
        </div>

        <div className="metric">
          <span>
            試合数
          </span>

          <strong>
            {games.length}
          </strong>
        </div>

        <div className="metric">
          <span>
            総得点
          </span>

          <strong>
            {games.reduce(
              (a, g) =>
                a +
                n(
                  g.our_score
                ),
              0
            )}
          </strong>
        </div>

        <div className="metric">
          <span>
            総失点
          </span>

          <strong>
            {games.reduce(
              (a, g) =>
                a +
                n(
                  g.their_score
                ),
              0
            )}
          </strong>
        </div>
      </section>
    </>
  );
}

/* =========================================================
   HISTORY
========================================================= */

function History({
  team,
  goHome,
}: {
  team: Team;
  goHome: () => void;
}) {
  const [games, setGames] =
    useState<Game[]>([]);

  const [
    selected,
    setSelected,
  ] =
    useState<Game | null>(
      null
    );

  async function loadGames() {
    const { data } =
      await supabase
        .from("games")
        .select("*")
        .eq(
          "team_id",
          team.id
        )
        .eq(
          "status",
          "finished"
        )
        .order(
          "game_date",
          {
            ascending:
              false,
          }
        );

    setGames(
      (data ||
        []) as Game[]
    );
  }

  useEffect(() => {
    loadGames();
  }, [team.id]);

  /*
    詳細画面から一覧へ戻る専用。
    ここでは再びselectedをセットしない。
  */
  function backToHistory() {
    setSelected(null);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });

    loadGames();
  }

  /*
    ホームへ戻る場合も
    詳細選択をリセットしてから
    親のgoHomeを呼ぶ。
  */
  function historyGoHome() {
    setSelected(null);
    goHome();
  }

  if (selected) {
    return (
      <GameDetail
        team={team}
        game={selected}
        backToHistory={
          backToHistory
        }
        goHome={
          historyGoHome
        }
        refreshGame={async () => {
          const { data } =
            await supabase
              .from(
                "games"
              )
              .select("*")
              .eq(
                "id",
                selected.id
              )
              .single();

          if (data) {
            setSelected(
              data as Game
            );
          }

          await loadGames();
        }}
      />
    );
  }

  return (
    <>
      <HomeButton
        onClick={
          historyGoHome
        }
      />

      <h1>
        過去の試合
      </h1>

      {!games.length && (
        <div className="notice">
          終了済みの試合はありません。
        </div>
      )}

      {games.map(
        (g) => {
          const result =
            n(
              g.our_score
            ) >
            n(
              g.their_score
            )
              ? "○"
              : n(
                    g.our_score
                  ) <
                  n(
                    g.their_score
                  )
              ? "●"
              : "△";

          return (
            <button
              className="card"
              key={g.id}
              onClick={() => {
                setSelected(
                  g
                );

                window.scrollTo({
                  top: 0,
                });
              }}
            >
              <div className="row">
                <strong>
                  {result}　vs{" "}
                  {
                    g.opponent
                  }
                </strong>

                <strong>
                  {
                    g.our_score
                  }{" "}
                  -{" "}
                  {
                    g.their_score
                  }
                </strong>
              </div>

              <small>
                {g.game_date ||
                  ""}

                {g.place
                  ? ` ｜ ${g.place}`
                  : ""}

                {g.game_type
                  ? ` ｜ ${g.game_type}`
                  : ""}
              </small>
            </button>
          );
        }
      )}
    </>
  );
}

/* =========================================================
   GAME DETAIL
========================================================= */

function GameDetail({
  team,
  game,
  backToHistory,
  goHome,
  refreshGame,
}: {
  team: Team;
  game: Game;
  backToHistory: () => void;
  goHome: () => void;
  refreshGame: () => Promise<void>;
}) {
  const [scores, setScores] =
    useState<
      InningScore[]
    >([]);

  const [players, setPlayers] =
    useState<Player[]>([]);

  const [batting, setBatting] =
    useState<
      BattingRow[]
    >([]);

  const [pitching, setPitching] =
    useState<
      PitchingRow[]
    >([]);

  const [
    finalPitching,
    setFinalPitching,
  ] = useState<
    PitchingGameStat[]
  >([]);

  const [
    editOpen,
    setEditOpen,
  ] = useState(false);

  const [
    editInning,
    setEditInning,
  ] = useState(1);

  const [
    editSide,
    setEditSide,
  ] =
    useState<
      "our" | "their"
    >("our");

  const [
    editRuns,
    setEditRuns,
  ] = useState(0);
  const [editNotPlayed, setEditNotPlayed] = useState(false);
  const [scoreError, setScoreError] = useState("");

  async function load() {
    const [
      scoresRes,
      playersRes,
      battingRes,
      pitchingRes,
      finalRes,
    ] =
      await Promise.all([
        supabase
          .from(
            "inning_scores"
          )
          .select("*")
          .eq(
            "game_id",
            game.id
          ),

        supabase
          .from(
            "players"
          )
          .select("*")
          .eq(
            "team_id",
            team.id
          ),

        supabase
          .from(
            "batting"
          )
          .select("*")
          .eq(
            "game_id",
            game.id
          ),

        supabase
          .from(
            "pitching"
          )
          .select("*")
          .eq(
            "game_id",
            game.id
          ),

        supabase
          .from(
            "pitching_game_stats"
          )
          .select("*")
          .eq(
            "game_id",
            game.id
          ),
      ]);

    setScores(
      (scoresRes.data ||
        []) as InningScore[]
    );

    setPlayers(
      (playersRes.data ||
        []) as Player[]
    );

    setBatting(
      (battingRes.data ||
        []) as BattingRow[]
    );

    setPitching(
      (pitchingRes.data ||
        []) as PitchingRow[]
    );

    setFinalPitching(
      (finalRes.data ||
        []) as PitchingGameStat[]
    );
  }

  useEffect(() => {
    load();
  }, [game.id]);

  const maxInning =
    Math.max(
      7,
      n(
        game.current_inning
      ),
      ...scores.map(
        (s) =>
          n(s.inning)
      )
    );

  function changeEditTarget(
    inning: number,
    side:
      | "our"
      | "their"
  ) {
    setEditInning(
      inning
    );

    setEditSide(side);

    const found =
      scores.find(
        (s) =>
          n(
            s.inning
          ) === inning &&
          s.side ===
            side
      );

    setEditRuns(
      found
        ? n(found.runs)
        : 0
    );
    setEditNotPlayed(!found);
  }

  function openEditor() {
    setEditOpen(true);

    changeEditTarget(
      1,
      "our"
    );
  }

  async function saveEditedScore() {
    setScoreError("");
    const existing = scores.find(s => n(s.inning) === editInning && s.side === editSide);
    if (editNotPlayed) {
      if (existing?.id) {
        const { error } = await supabase.from("inning_scores").delete().eq("id", existing.id);
        if (error) { setScoreError(`未実施への変更に失敗しました：${error.message}`); return; }
      }
    } else if (existing?.id) {
      const { error } = await supabase.from("inning_scores").update({ runs: editRuns }).eq("id", existing.id);
      if (error) { setScoreError(`得点の変更に失敗しました：${error.message}`); return; }
    } else {
      const { error } = await supabase.from("inning_scores").insert({ game_id: game.id, inning: editInning, side: editSide, runs: editRuns });
      if (error) { setScoreError(`得点の登録に失敗しました：${error.message}`); return; }
    }
    const { data, error } = await supabase.from("inning_scores").select("*").eq("game_id", game.id);
    if (error) { setScoreError(`得点の再取得に失敗しました：${error.message}`); return; }
    const all = (data || []) as InningScore[];
    const ourTotal = all.filter(x => x.side === "our").reduce((a,x) => a + n(x.runs),0);
    const theirTotal = all.filter(x => x.side === "their").reduce((a,x) => a + n(x.runs),0);
    const updated = await supabase.from("games").update({ our_score: ourTotal, their_score: theirTotal }).eq("id", game.id);
    if (updated.error) { setScoreError(`合計点の更新に失敗しました：${updated.error.message}`); return; }
    setEditOpen(false);
    await load();
    await refreshGame();
  }

  const battingPlayers =
    players
      .map((p) => ({
        player: p,

        rows:
          batting.filter(
            (r) =>
              String(
                r.player_id
              ) ===
              String(
                p.id
              )
          ),
      }))
      .filter(
        (x) =>
          x.rows.length
      );

  const pitcherIds =
    Array.from(
      new Set([
        ...pitching.map(
          (x) =>
            String(
              x.pitcher_id
            )
        ),

        ...finalPitching.map(
          (x) =>
            String(
              x.pitcher_id
            )
        ),
      ])
    );

  return (
    <>
      <div
        style={{
          display: "flex",
          gap: "8px",
          flexWrap: "wrap",
        }}
      >
        <button
          type="button"
          onClick={
            backToHistory
          }
        >
          ← 過去の試合
        </button>

        <button
          type="button"
          onClick={goHome}
        >
          ホーム
        </button>
      </div>

      <h1>
        vs {game.opponent}
      </h1>

      <p>
        {game.game_date ||
          ""}

        {game.place
          ? ` ｜ ${game.place}`
          : ""}
      </p>

      <Scoreboard
        game={game}
        team={team}
        scores={scores}
      />

      <button
        className="primary"
        onClick={
          openEditor
        }
      >
        点数を変更
      </button>

      {editOpen && (
        <section className="card">
          <h2>
            点数を変更
          </h2>

          <label>回</label>

          <select
            value={
              editInning
            }
            onChange={(e) =>
              changeEditTarget(
                n(
                  e.target
                    .value
                ),
                editSide
              )
            }
          >
            {Array.from(
              {
                length:
                  maxInning,
              },
              (_, i) =>
                i + 1
            ).map(
              (i) => (
                <option
                  key={i}
                  value={i}
                >
                  {i}回
                </option>
              )
            )}
          </select>

          <label>
            チーム
          </label>

          <select
            value={
              editSide
            }
            onChange={(e) =>
              changeEditTarget(
                editInning,
                e.target
                  .value as
                  | "our"
                  | "their"
              )
            }
          >
            <option value="our">
              {
                team.team_name
              }
            </option>

            <option value="their">
              {
                game.opponent
              }
            </option>
          </select>

          <label style={{display:"flex",alignItems:"center",gap:8,marginBottom:12}}>
            <input type="checkbox" checked={editNotPlayed} onChange={e => setEditNotPlayed(e.target.checked)} style={{width:20,height:20}} />
            未実施（この回の得点を空欄にする）
          </label>
          <label>得点（0点と未実施は別）</label>

          <input
            disabled={editNotPlayed}
            type="number"
            min={0}
            value={
              editRuns
            }
            onChange={(e) =>
              setEditRuns(
                n(
                  e.target
                    .value
                )
              )
            }
          />

          {scoreError && <div className="notice">{scoreError}</div>}
          <button
            className="primary"
            onClick={
              saveEditedScore
            }
          >
            変更を保存
          </button>

          <button
            onClick={() =>
              setEditOpen(
                false
              )
            }
          >
            キャンセル
          </button>
        </section>
      )}

      <h2>
        打撃個人成績
      </h2>

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
                <th>
                  二塁打
                </th>
                <th>
                  三塁打
                </th>
                <th>HR</th>
                <th>打点</th>
                <th>四球</th>
                <th>死球</th>
                <th>三振</th>
                <th>打率</th>
                <th>
                  出塁率
                </th>
                <th>OPS</th>
              </tr>
            </thead>

            <tbody>
              {battingPlayers.map(
                ({
                  player,
                  rows,
                }) => {
                  const s =
                    calcBatting(
                      rows
                    );

                  return (
                    <tr
                      key={
                        player.id
                      }
                    >
                      <th>
                        {
                          player.name
                        }
                      </th>

                      <td>
                        {
                          s.PA
                        }
                      </td>

                      <td>
                        {
                          s.AB
                        }
                      </td>

                      <td>
                        {s.H}
                      </td>

                      <td>
                        {
                          s.doubles
                        }
                      </td>

                      <td>
                        {
                          s.triples
                        }
                      </td>

                      <td>
                        {
                          s.HR
                        }
                      </td>

                      <td>
                        {
                          s.RBI
                        }
                      </td>

                      <td>
                        {
                          s.BB
                        }
                      </td>

                      <td>
                        {
                          s.HBP
                        }
                      </td>

                      <td>
                        {
                          s.SO
                        }
                      </td>

                      <td>
                        {fmt3(
                          s.AVG
                        )}
                      </td>

                      <td>
                        {fmt3(
                          s.OBP
                        )}
                      </td>

                      <td>
                        {fmt3(
                          s.OPS
                        )}
                      </td>
                    </tr>
                  );
                }
              )}
            </tbody>
          </table>
        </div>
      )}

      <h2>
        投手個人成績
      </h2>

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
                <th>
                  投球回
                </th>
                <th>
                  被安打
                </th>
                <th>
                  奪三振
                </th>
                <th>
                  与四球
                </th>
                <th>
                  与死球
                </th>
                <th>
                  被本塁打
                </th>
                <th>失点</th>
                <th>
                  自責点
                </th>
                <th>
                  防御率
                </th>
              </tr>
            </thead>

            <tbody>
              {pitcherIds.map(
                (pid) => {
                  const player =
                    players.find(
                      (p) =>
                        String(
                          p.id
                        ) ===
                        pid
                    );

                  const rows =
                    pitching.filter(
                      (r) =>
                        String(
                          r.pitcher_id
                        ) ===
                        pid
                    );

                  const finals =
                    finalPitching.filter(
                      (r) =>
                        String(
                          r.pitcher_id
                        ) ===
                        pid
                    );

                  const s =
                    calcPitching(
                      rows,
                      finals
                    );

                  return (
                    <tr
                      key={pid}
                    >
                      <th>
                        {player?.name ||
                          "投手"}
                      </th>

                      <td>
                        {finals.length ? formatIP(s.outs) : "---"}
                      </td>

                      <td>
                        {s.H}
                      </td>

                      <td>
                        {
                          s.SO
                        }
                      </td>

                      <td>
                        {
                          s.BB
                        }
                      </td>

                      <td>
                        {
                          s.HBP
                        }
                      </td>

                      <td>
                        {
                          s.HR
                        }
                      </td>

                      <td>
                        {s.R}
                      </td>

                      <td>
                        {finals.length ? s.ER : "---"}
                      </td>

                      <td>
                        {s.ERA ===
                        null
                          ? "---"
                          : s.ERA.toFixed(
                              2
                            )}
                      </td>
                    </tr>
                  );
                }
              )}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

/* 投手の通算成績・ランキング（過去の未登録投球回は推測しない） */
function pitcherSummary(players: Player[], pitching: PitchingRow[], finals: PitchingGameStat[]) {
  const ids = Array.from(new Set([...pitching.map(r => String(r.pitcher_id)), ...finals.map(r => String(r.pitcher_id))]));
  return ids.map(id => {
    const rows = pitching.filter(r => String(r.pitcher_id) === id);
    const saved = finals.filter(r => String(r.pitcher_id) === id);
    const s = calcPitching(rows, saved);
    const appearances = new Set([...rows.map(r => String(r.game_id)), ...saved.map(r => String(r.game_id))]).size;
    const recordedGames = new Set(saved.map(r => String(r.game_id)));
    const missing = [...new Set(rows.map(r => String(r.game_id)))].some(gid => !recordedGames.has(gid));
    const complete = saved.length > 0 && !missing;
    return { id, name: players.find(p => String(p.id) === id)?.name || "投手", s, appearances, complete };
  });
}

function PitcherStatsTable({ players, pitching, finals }: { players: Player[]; pitching: PitchingRow[]; finals: PitchingGameStat[] }) {
  const items = pitcherSummary(players, pitching, finals);
  if (!items.length) return <div className="notice">投手記録はありません。</div>;
  return <div className="scroll"><table><thead><tr>{["投手", "登板", "投球回", "被安打", "奪三振", "与四球", "与死球", "被本塁打", "失点", "自責点", "防御率"].map(h => <th key={h}>{h}</th>)}</tr></thead><tbody>
    {items.map(x => <tr key={x.id}><th>{x.name}</th><td>{x.appearances}</td><td>{x.complete ? formatIP(x.s.outs) : "---"}</td><td>{x.s.H}</td><td>{x.s.SO}</td><td>{x.s.BB}</td><td>{x.s.HBP}</td><td>{x.s.HR}</td><td>{x.s.R}</td><td>{x.complete ? x.s.ER : "---"}</td><td>{x.complete && x.s.ERA !== null ? x.s.ERA.toFixed(2) : "---"}</td></tr>)}
  </tbody></table></div>;
}

function PitcherRankings({ players, pitching, finals }: { players: Player[]; pitching: PitchingRow[]; finals: PitchingGameStat[] }) {
  const [metric, setMetric] = useState("奪三振");
  const options = ["登板", "投球回", "防御率", "奪三振", "被安打", "与四球", "与死球", "被本塁打", "失点", "自責点"];
  const items = pitcherSummary(players, pitching, finals).map(x => {
    const values: Record<string, number | null> = { "登板": x.appearances, "投球回": x.complete ? x.s.outs : null, "防御率": x.complete ? x.s.ERA : null, "奪三振": x.s.SO, "被安打": x.s.H, "与四球": x.s.BB, "与死球": x.s.HBP, "被本塁打": x.s.HR, "失点": x.s.R, "自責点": x.complete ? x.s.ER : null };
    return { ...x, value: values[metric] };
  }).filter(x => x.value !== null).sort((a,b) => metric === "防御率" ? n(a.value) - n(b.value) : n(b.value) - n(a.value));
  return <section className="card"><label>投手ランキング項目</label><select value={metric} onChange={e => setMetric(e.target.value)}>{options.map(o => <option key={o}>{o}</option>)}</select>
    {items.length ? items.map((x,i) => <div className="row" key={x.id}><strong>{i+1}位　{x.name}</strong><span>{metric === "投球回" ? formatIP(n(x.value)) : metric === "防御率" ? n(x.value).toFixed(2) : x.value}</span></div>) : <div className="notice">この項目の記録はありません。</div>}
  </section>;
}
