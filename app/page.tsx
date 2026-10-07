"use client";

import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";

type Team = any;
type Player = any;
type Game = any;

const RECENT = "baseball_recent_teams_v1";

const grades = ["1年", "2年", "3年", "4年", "その他"];

const batResults = [
  "安打",
  "アウト",
  "三振",
  "四球",
  "死球",
  "失策",
  "犠打",
  "犠飛",
];

const pitchResults = [
  "アウト",
  "三振",
  "安打",
  "二塁打",
  "三塁打",
  "本塁打",
  "四球",
  "死球",
  "失策",
];

const fields = ["投", "捕", "一", "二", "三", "遊", "左", "中", "右"];

function recentGet() {
  try {
    return JSON.parse(localStorage.getItem(RECENT) || "[]");
  } catch {
    return [];
  }
}

function recentPut(team: any) {
  const data = [
    team,
    ...recentGet().filter((x: any) => x.id !== team.id),
  ].slice(0, 8);

  localStorage.setItem(RECENT, JSON.stringify(data));
}

function average(n: number) {
  if (!Number.isFinite(n)) return "---";

  return n.toFixed(3).replace(/^0/, "");
}

function innings(outs: number) {
  return `${Math.floor((outs || 0) / 3)}.${(outs || 0) % 3}`;
}

function battingStats(rows: any[]) {
  const s: any = {
    PA: 0,
    AB: 0,
    H: 0,
    B1: 0,
    B2: 0,
    B3: 0,
    HR: 0,
    BB: 0,
    HBP: 0,
    SO: 0,
    SF: 0,
    SH: 0,
    RBI: 0,
  };

  for (const r of rows) {
    s.PA++;
    s.RBI += Number(r.rbi || 0);

    if (r.result === "四球") {
      s.BB++;
    } else if (r.result === "死球") {
      s.HBP++;
    } else if (r.result === "犠打") {
      s.SH++;
    } else if (r.result === "犠飛") {
      s.SF++;
    } else {
      s.AB++;

      if (r.result === "三振") {
        s.SO++;
      }

      if (r.result === "安打") {
        s.H++;

        if (r.hit_type === "二塁打") {
          s.B2++;
        } else if (r.hit_type === "三塁打") {
          s.B3++;
        } else if (r.hit_type === "本塁打") {
          s.HR++;
        } else {
          s.B1++;
        }
      }
    }
  }

  s.AVG = s.AB ? s.H / s.AB : 0;

  const obpDenominator =
    s.AB + s.BB + s.HBP + s.SF;

  s.OBP = obpDenominator
    ? (s.H + s.BB + s.HBP) / obpDenominator
    : 0;

  s.SLG = s.AB
    ? (s.B1 + 2 * s.B2 + 3 * s.B3 + 4 * s.HR) / s.AB
    : 0;

  s.OPS = s.OBP + s.SLG;

  return s;
}

/* =========================================================
   MAIN
========================================================= */

export default function Page() {
  const [team, setTeam] = useState<Team | null>(null);
  const [recent, setRecent] = useState<any[]>([]);

  const [page, setPage] = useState("home");

  const [players, setPlayers] = useState<Player[]>([]);
  const [games, setGames] = useState<Game[]>([]);

  const [game, setGame] = useState<Game | null>(null);

  const [message, setMessage] = useState("");

  useEffect(() => {
    setRecent(recentGet());
  }, []);

  useEffect(() => {
    if (team) {
      loadCore();
    }
  }, [team]);

  async function loadCore() {
    if (!team) return;

    const playerResult = await supabase
      .from("players")
      .select("*")
      .eq("team_id", team.id)
      .order("name");

    setPlayers(playerResult.data || []);

    const gameResult = await supabase
      .from("games")
      .select("*")
      .eq("team_id", team.id)
      .order("game_date", {
        ascending: false,
      });

    const loadedGames = gameResult.data || [];

    setGames(loadedGames);

    const active = loadedGames.find(
      (x: any) => x.status === "playing"
    );

    setGame(active || null);
  }

  function enterTeam(t: any) {
    setTeam(t);

    recentPut({
      id: t.id,
      team_name: t.team_name,
      team_code: t.team_code,
    });

    setRecent(recentGet());

    setPage("home");
  }

  if (!team) {
    return (
      <TeamGate
        recent={recent}
        enter={enterTeam}
      />
    );
  }

  return (
    <div className="wrap">
      <div className="top">
        <div>
          <h1>{team.team_name}</h1>

          <span className="pill">
            TEAM CODE {team.team_code}
          </span>
        </div>

        <button
          onClick={() => {
            setTeam(null);
            setPage("home");
          }}
        >
          変更
        </button>
      </div>

      {message && (
        <div className="success">
          {message}
        </div>
      )}

      {page === "home" && (
        <Home
          game={game}
          go={setPage}
        />
      )}

      {page === "players" && (
        <Players
          team={team}
          players={players}
          reload={loadCore}
          done={setMessage}
        />
      )}

      {page === "score" && (
        <Score
          team={team}
          players={players}
          game={game}
          reload={loadCore}
          done={setMessage}
        />
      )}

      {page === "stats" && (
        <Stats
          players={players}
          games={games}
        />
      )}

      {page === "history" && (
        <History
          games={games}
        />
      )}

      <div className="nav">
        <button
          className={
            page === "home"
              ? "active"
              : ""
          }
          onClick={() =>
            setPage("home")
          }
        >
          ⌂
          <br />
          ホーム
        </button>

        <button
          className={
            page === "score"
              ? "active"
              : ""
          }
          onClick={() =>
            setPage("score")
          }
        >
          ⚾
          <br />
          スコア
        </button>

        <button
          className={
            page === "stats"
              ? "active"
              : ""
          }
          onClick={() =>
            setPage("stats")
          }
        >
          ▥
          <br />
          成績
        </button>

        <button
          className={
            page === "history"
              ? "active"
              : ""
          }
          onClick={() =>
            setPage("history")
          }
        >
          ◷
          <br />
          履歴
        </button>
      </div>
    </div>
  );
}

/* =========================================================
   TEAM
========================================================= */

function TeamGate({
  recent,
  enter,
}: any) {
  const [mode, setMode] =
    useState("");

  const [code, setCode] =
    useState("");

  const [name, setName] =
    useState("");

  const [error, setError] =
    useState("");

  async function joinTeam(
    teamCode: string
  ) {
    setError("");

    const result = await supabase
      .from("teams")
      .select("*")
      .eq(
        "team_code",
        teamCode
          .trim()
          .toUpperCase()
      )
      .maybeSingle();

    if (result.data) {
      enter(result.data);
    } else {
      setError(
        "チームが見つかりません。"
      );
    }
  }

  async function createTeam() {
    if (!name.trim()) return;

    const teamCode =
      Math.random()
        .toString(36)
        .slice(2, 8)
        .toUpperCase();

    const ownerCode =
      Math.random()
        .toString(36)
        .slice(2, 10)
        .toUpperCase();

    const result = await supabase
      .from("teams")
      .insert({
        team_name:
          name.trim(),
        team_code:
          teamCode,
        owner_code:
          ownerCode,
      })
      .select()
      .single();

    if (result.data) {
      enter(result.data);
    } else {
      setError(
        result.error?.message ||
          "チームを作成できませんでした。"
      );
    }
  }

  return (
    <div className="wrap">
      <div className="brand">
        ⚾ Baseball Score
      </div>

      <h1>
        使用するチームを選択
      </h1>

      {recent.length > 0 && (
        <>
          <h2>
            最近使ったチーム
          </h2>

          {recent.map(
            (t: any) => (
              <button
                className="card log"
                key={t.id}
                onClick={() =>
                  joinTeam(
                    t.team_code
                  )
                }
              >
                <b>
                  {t.team_name}
                </b>

                <div className="tiny">
                  {t.team_code}
                </div>
              </button>
            )
          )}
        </>
      )}

      {!mode && (
        <div className="grid2">
          <button
            className="primary"
            onClick={() =>
              setMode("join")
            }
          >
            チームに参加
          </button>

          <button
            onClick={() =>
              setMode("create")
            }
          >
            チームを作成
          </button>
        </div>
      )}

      {mode === "join" && (
        <div className="card">
          <label>
            チームコード
          </label>

          <input
            value={code}
            onChange={(e) =>
              setCode(
                e.target.value.toUpperCase()
              )
            }
            placeholder="ABC123"
          />

          <button
            className="primary"
            style={{
              width: "100%",
              marginTop: 10,
            }}
            onClick={() =>
              joinTeam(code)
            }
          >
            参加する
          </button>

          <button
            style={{
              width: "100%",
              marginTop: 8,
            }}
            onClick={() =>
              setMode("")
            }
          >
            戻る
          </button>
        </div>
      )}

      {mode === "create" && (
        <div className="card">
          <label>
            チーム名
          </label>

          <input
            value={name}
            onChange={(e) =>
              setName(
                e.target.value
              )
            }
            placeholder="ベイスターズ"
          />

          <button
            className="primary"
            style={{
              width: "100%",
              marginTop: 10,
            }}
            onClick={
              createTeam
            }
          >
            作成する
          </button>

          <button
            style={{
              width: "100%",
              marginTop: 8,
            }}
            onClick={() =>
              setMode("")
            }
          >
            戻る
          </button>
        </div>
      )}

      {error && (
        <div className="notice">
          {error}
        </div>
      )}

      <p className="muted">
        最近使ったチームはこの端末に保存されます。
      </p>
    </div>
  );
}

/* =========================================================
   HOME
========================================================= */

function Home({
  game,
  go,
}: any) {
  return (
    <>
      <div className="card">
        <b>
          {game
            ? "進行中の試合があります"
            : "試合を管理"}
        </b>

        <p className="muted">
          {game
            ? `${game.opponent}戦　${game.current_inning}回`
            : "新しい試合を開始できます"}
        </p>

        <button
          className="primary"
          style={{
            width: "100%",
          }}
          onClick={() =>
            go("score")
          }
        >
          {game
            ? "試合に戻る"
            : "試合を始める"}
        </button>
      </div>

      <div className="grid2">
        <button
          onClick={() =>
            go("players")
          }
        >
          👥 選手登録
        </button>

        <button
          onClick={() =>
            go("stats")
          }
        >
          ▥ 成績確認
        </button>

        <button
          onClick={() =>
            go("history")
          }
        >
          ◷ 過去の試合
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
  players,
  reload,
  done,
}: any) {
  const [name, setName] =
    useState("");

  const [number, setNumber] =
    useState("");

  const [grade, setGrade] =
    useState("1年");

  async function addPlayer() {
    if (!name.trim()) return;

    const result =
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

    if (!result.error) {
      setName("");
      setNumber("");

      done(
        "選手を登録しました"
      );

      reload();
    }
  }

  return (
    <>
      <h2>選手登録</h2>

      <div className="card">
        <label>氏名</label>

        <input
          value={name}
          onChange={(e) =>
            setName(
              e.target.value
            )
          }
        />

        <div className="row">
          <div>
            <label>
              背番号
            </label>

            <input
              value={number}
              onChange={(e) =>
                setNumber(
                  e.target.value
                )
              }
            />
          </div>

          <div>
            <label>
              学年
            </label>

            <select
              value={grade}
              onChange={(e) =>
                setGrade(
                  e.target.value
                )
              }
            >
              {grades.map(
                (x) => (
                  <option
                    key={x}
                  >
                    {x}
                  </option>
                )
              )}
            </select>
          </div>
        </div>

        <button
          className="primary"
          style={{
            width: "100%",
            marginTop: 12,
          }}
          onClick={
            addPlayer
          }
        >
          登録
        </button>
      </div>

      <h2>
        PLAYERS{" "}
        {players.length}
      </h2>

      {players.map(
        (p: any) => (
          <div
            className="card"
            key={p.id}
          >
            <b>{p.name}</b>

            <div className="muted">
              {p.number
                ? `#${p.number}　`
                : ""}
              {p.grade || ""}
            </div>
          </div>
        )
      )}
    </>
  );
}

/* =========================================================
   SCORE
========================================================= */

function Score({
  team,
  players,
  game,
  reload,
  done,
}: any) {
  if (!game) {
    return (
      <NewGame
        team={team}
        players={players}
        reload={reload}
        done={done}
      />
    );
  }

  return (
    <LiveScore
      game={game}
      players={players}
      reload={reload}
      done={done}
    />
  );
}

/* =========================================================
   NEW GAME
========================================================= */

function NewGame({
  team,
  players,
  reload,
  done,
}: any) {
  const [opponent, setOpponent] =
    useState("");

  const [place, setPlace] =
    useState("");

  const [type, setType] =
    useState("練習試合");

  const [tournament, setTournament] =
    useState("");

  const [batFirst, setBatFirst] =
    useState(true);

  const [starter, setStarter] =
    useState(
      players[0]?.id || ""
    );

  const [lineup, setLineup] =
    useState<any[]>(
      players
        .slice(0, 9)
        .map(
          (p: any) => p.id
        )
    );

  if (!players.length) {
    return (
      <div className="notice">
        先に選手を登録してください。
      </div>
    );
  }

  async function startGame() {
    const result =
      await supabase
        .from("games")
        .insert({
          team_id:
            team.id,

          game_date:
            new Date()
              .toISOString()
              .slice(0, 10),

          opponent,

          place:
            place || null,

          game_type:
            type,

          tournament:
            type ===
            "公式戦"
              ? tournament ||
                null
              : null,

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

          current_batter_index: 0,

          current_pitcher_id:
            starter,

          opponent_batter_index: 0,
        })
        .select()
        .single();

    if (!result.data) {
      done(
        result.error?.message ||
          "試合を開始できませんでした"
      );

      return;
    }

    await supabase
      .from("lineup")
      .insert(
        lineup.map(
          (
            playerId: any,
            i: number
          ) => ({
            game_id:
              result.data.id,

            slot:
              i + 1,

            player_id:
              playerId,
          })
        )
      );

    done(
      "試合を開始しました"
    );

    reload();
  }

  return (
    <>
      <h2>
        新しい試合
      </h2>

      <div className="card">
        <label>
          対戦相手
        </label>

        <input
          value={opponent}
          onChange={(e) =>
            setOpponent(
              e.target.value
            )
          }
          placeholder="ベイスターズ"
        />

        <label>
          試合場所
        </label>

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

        <div className="row">
          <button
            className={
              type ===
              "練習試合"
                ? "primary"
                : ""
            }
            onClick={() =>
              setType(
                "練習試合"
              )
            }
          >
            練習試合
          </button>

          <button
            className={
              type ===
              "公式戦"
                ? "primary"
                : ""
            }
            onClick={() =>
              setType(
                "公式戦"
              )
            }
          >
            公式戦
          </button>
        </div>

        {type ===
          "公式戦" && (
          <>
            <label>
              大会名
            </label>

            <input
              value={
                tournament
              }
              onChange={(e) =>
                setTournament(
                  e.target
                    .value
                )
              }
            />
          </>
        )}

        <label>
          先攻・後攻
        </label>

        <div className="row">
          <button
            className={
              batFirst
                ? "primary"
                : ""
            }
            onClick={() =>
              setBatFirst(
                true
              )
            }
          >
            先攻
          </button>

          <button
            className={
              !batFirst
                ? "primary"
                : ""
            }
            onClick={() =>
              setBatFirst(
                false
              )
            }
          >
            後攻
          </button>
        </div>

        <label>打順</label>

        {lineup.map(
          (
            playerId: any,
            i: number
          ) => (
            <select
              key={i}
              value={
                playerId
              }
              onChange={(e) => {
                const copy =
                  [...lineup];

                copy[i] =
                  Number(
                    e.target
                      .value
                  );

                setLineup(
                  copy
                );
              }}
            >
              {players.map(
                (p: any) => (
                  <option
                    key={p.id}
                    value={p.id}
                  >
                    {i + 1}
                    番｜
                    {p.name}
                  </option>
                )
              )}
            </select>
          )
        )}

        <label>
          先発投手
        </label>

        <select
          value={starter}
          onChange={(e) =>
            setStarter(
              Number(
                e.target
                  .value
              )
            )
          }
        >
          {players.map(
            (p: any) => (
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
          style={{
            width: "100%",
            marginTop: 12,
          }}
          disabled={
            !opponent.trim()
          }
          onClick={
            startGame
          }
        >
          試合開始
        </button>
      </div>
    </>
  );
}

/* =========================================================
   LIVE GAME
========================================================= */

function LiveScore({
  game,
  players,
  reload,
  done,
}: any) {
  const [lineup, setLineup] =
    useState<any[]>([]);

  const [logs, setLogs] =
    useState<any[]>([]);

  const [scores, setScores] =
    useState<any[]>([]);

  const [result, setResult] =
    useState("安打");

  const [field, setField] =
    useState("中");

  const [hitType, setHitType] =
    useState("単打");

  const [rbi, setRbi] =
    useState(0);

  const [runs, setRuns] =
    useState(0);

  async function loadGame() {
    const lineupResult =
      await supabase
        .from("lineup")
        .select("*")
        .eq(
          "game_id",
          game.id
        )
        .order("slot");

    setLineup(
      lineupResult.data ||
        []
    );

    const table =
      game.current_mode ===
      "offense"
        ? "batting"
        : "pitching";

    const logResult =
      await supabase
        .from(table)
        .select("*")
        .eq(
          "game_id",
          game.id
        )
        .eq(
          "inning",
          game.current_inning
        )
        .order(
          "created_at"
        );

    setLogs(
      logResult.data ||
        []
    );

    const scoreResult =
      await supabase
        .from(
          "inning_scores"
        )
        .select("*")
        .eq(
          "game_id",
          game.id
        )
        .order("inning");

    setScores(
      scoreResult.data ||
        []
    );
  }

  useEffect(() => {
    loadGame();
  }, [
    game.id,
    game.current_mode,
    game.current_inning,
  ]);

  const playerMap =
    Object.fromEntries(
      players.map(
        (p: any) => [
          p.id,
          p,
        ]
      )
    );

  const batter =
    lineup.length
      ? lineup[
          (game.current_batter_index ||
            0) %
            lineup.length
        ]
      : null;

  const pitcher =
    playerMap[
      game.current_pitcher_id
    ];

  const offense =
    game.current_mode ===
    "offense";

  const half =
    game.bat_first
      ? offense
        ? "表"
        : "裏"
      : offense
        ? "裏"
        : "表";

  async function record() {
    if (
      offense &&
      batter
    ) {
      await supabase
        .from("batting")
        .insert({
          game_id:
            game.id,

          player_id:
            batter.player_id,

          inning:
            game.current_inning,

          batting_order:
            batter.slot,

          result,

          field:
            [
              "安打",
              "アウト",
              "失策",
            ].includes(
              result
            )
              ? field
              : null,

          batted_type:
            null,

          hit_type:
            result ===
            "安打"
              ? hitType
              : null,

          rbi:
            Number(rbi),
        });

      await supabase
        .from("games")
        .update({
          current_batter_index:
            ((game.current_batter_index ||
              0) +
              1) %
            lineup.length,
        })
        .eq(
          "id",
          game.id
        );
    } else if (
      pitcher
    ) {
      const order =
        ((game.opponent_batter_index ||
          0) %
          9) +
        1;

      await supabase
        .from("pitching")
        .insert({
          game_id:
            game.id,

          pitcher_id:
            pitcher.id,

          inning:
            game.current_inning,

          batting_order:
            order,

          result,

          runs:
            Number(runs),
        });

      await supabase
        .from("games")
        .update({
          opponent_batter_index:
            order % 9,
        })
        .eq(
          "id",
          game.id
        );
    }

    done("記録しました");

    await reload();
    await loadGame();
  }

  async function changeSides() {
    const side =
      offense
        ? "our"
        : "their";

    const existing =
      scores.find(
        (x: any) =>
          x.inning ===
            game.current_inning &&
          x.side === side
      );

    if (existing) {
      await supabase
        .from(
          "inning_scores"
        )
        .update({
          runs:
            Number(runs),
        })
        .eq(
          "id",
          existing.id
        );
    } else {
      await supabase
        .from(
          "inning_scores"
        )
        .insert({
          game_id:
            game.id,

          inning:
            game.current_inning,

          side,

          runs:
            Number(runs),
        });
    }

    const allResult =
      await supabase
        .from(
          "inning_scores"
        )
        .select("*")
        .eq(
          "game_id",
          game.id
        );

    const all =
      allResult.data ||
      [];

    const ourScore =
      all
        .filter(
          (x: any) =>
            x.side === "our"
        )
        .reduce(
          (
            a: number,
            x: any
          ) =>
            a +
            Number(
              x.runs || 0
            ),
          0
        );

    const theirScore =
      all
        .filter(
          (x: any) =>
            x.side ===
            "their"
        )
        .reduce(
          (
            a: number,
            x: any
          ) =>
            a +
            Number(
              x.runs || 0
            ),
          0
        );

    const currentHalf =
      game.bat_first
        ? offense
          ? "top"
          : "bottom"
        : offense
          ? "bottom"
          : "top";

    const nextInning =
      currentHalf ===
      "bottom"
        ? game.current_inning +
          1
        : game.current_inning;

    const nextMode =
      offense
        ? "defense"
        : "offense";

    await supabase
      .from("games")
      .update({
        our_score:
          ourScore,

        their_score:
          theirScore,

        current_mode:
          nextMode,

        current_inning:
          nextInning,
      })
      .eq(
        "id",
        game.id
      );

    setRuns(0);

    done(
      "攻守交替しました"
    );

    reload();
  }

  async function finishGame() {
    await supabase
      .from("games")
      .update({
        status:
          "finished",
      })
      .eq(
        "id",
        game.id
      );

    done(
      "試合を終了しました"
    );

    reload();
  }

  return (
    <>
      <div className="score">
        <small>
          {game.current_inning}
          回{half}｜
          {offense
            ? "攻撃中"
            : "守備中"}
        </small>

        {game.our_score} -{" "}
        {game.their_score}

        <small>
          {game.opponent}戦
        </small>
      </div>

      <div className="card">
        <span className="pill">
          {offense
            ? "BATTER"
            : "PITCHER"}
        </span>

        <h2>
          {offense
            ? playerMap[
                batter?.player_id
              ]?.name ||
              "―"
            : pitcher?.name ||
              "―"}
        </h2>

        {offense && (
          <div className="tiny">
            {batter?.slot}
            番
          </div>
        )}

        {!offense && (
          <div className="tiny">
            相手{" "}
            {((game.opponent_batter_index ||
              0) %
              9) +
              1}
            番
          </div>
        )}

        <label>
          {offense
            ? "打席結果"
            : "打者結果"}
        </label>

        <select
          value={result}
          onChange={(e) =>
            setResult(
              e.target.value
            )
          }
        >
          {(offense
            ? batResults
            : pitchResults
          ).map((x) => (
            <option
              key={x}
            >
              {x}
            </option>
          ))}
        </select>

        {offense &&
          [
            "安打",
            "アウト",
            "失策",
          ].includes(
            result
          ) && (
            <>
              <label>
                方向
              </label>

              <select
                value={field}
                onChange={(e) =>
                  setField(
                    e.target
                      .value
                  )
                }
              >
                {fields.map(
                  (x) => (
                    <option
                      key={x}
                    >
                      {x}
                    </option>
                  )
                )}
              </select>
            </>
          )}

        {offense &&
          result ===
            "安打" && (
            <>
              <label>
                安打種別
              </label>

              <select
                value={
                  hitType
                }
                onChange={(e) =>
                  setHitType(
                    e.target
                      .value
                  )
                }
              >
                {[
                  "単打",
                  "二塁打",
                  "三塁打",
                  "本塁打",
                ].map(
                  (x) => (
                    <option
                      key={x}
                    >
                      {x}
                    </option>
                  )
                )}
              </select>
            </>
          )}

        <label>
          {offense
            ? "打点"
            : "このプレーで入った得点"}
        </label>

        <input
          type="number"
          min="0"
          value={
            offense
              ? rbi
              : runs
          }
          onChange={(e) =>
            offense
              ? setRbi(
                  Number(
                    e.target
                      .value
                  )
                )
              : setRuns(
                  Number(
                    e.target
                      .value
                  )
                )
          }
        />

        <button
          className="primary"
          style={{
            width: "100%",
            marginTop: 10,
          }}
          onClick={record}
        >
          登録
        </button>
      </div>

      <h2>
        {game.current_inning}
        回｜
        {offense
          ? "攻撃"
          : "守備"}
        ログ
      </h2>

      {logs.map(
        (r: any) => (
          <div
            className="card"
            key={r.id}
          >
            {r.batting_order}
            番　

            {offense
              ? playerMap[
                  r.player_id
                ]?.name
              : playerMap[
                  r.pitcher_id
                ]?.name}

            　<b>
              {r.result}
            </b>
          </div>
        )
      )}

      <div className="card">
        <label>
          この回の得点
        </label>

        <input
          type="number"
          min="0"
          value={runs}
          onChange={(e) =>
            setRuns(
              Number(
                e.target
                  .value
              )
            )
          }
        />

        <button
          style={{
            width: "100%",
            marginTop: 10,
          }}
          onClick={
            changeSides
          }
        >
          攻守交替
        </button>

        <button
          className="danger"
          style={{
            width: "100%",
            marginTop: 8,
          }}
          onClick={
            finishGame
          }
        >
          ゲームセット
        </button>
      </div>
    </>
  );
}

/* =========================================================
   STATS
========================================================= */

function Stats({
  players,
  games,
}: any) {
  const [tab, setTab] =
    useState("bat");

  const [batting, setBatting] =
    useState<any[]>([]);

  const [pitching, setPitching] =
    useState<any[]>([]);

  const [
    pitchingGame,
    setPitchingGame,
  ] = useState<any[]>([]);

  useEffect(() => {
    loadStats();
  }, [games]);

  async function loadStats() {
    const ids = games
      .filter(
        (g: any) =>
          g.status ===
          "finished"
      )
      .map(
        (g: any) => g.id
      );

    if (!ids.length) {
      setBatting([]);
      setPitching([]);
      setPitchingGame([]);
      return;
    }

    const b =
      await supabase
        .from("batting")
        .select("*")
        .in(
          "game_id",
          ids
        );

    const p =
      await supabase
        .from("pitching")
        .select("*")
        .in(
          "game_id",
          ids
        );

    const pg =
      await supabase
        .from(
          "pitching_game_stats"
        )
        .select("*")
        .in(
          "game_id",
          ids
        );

    setBatting(
      b.data || []
    );

    setPitching(
      p.data || []
    );

    setPitchingGame(
      pg.data || []
    );
  }

  const battingRows =
    players.map(
      (p: any) => ({
        player: p,

        stats:
          battingStats(
            batting.filter(
              (x: any) =>
                x.player_id ===
                p.id
            )
          ),
      })
    );

  return (
    <>
      <div className="tabs">
        <button
          className={
            tab === "bat"
              ? "active"
              : ""
          }
          onClick={() =>
            setTab("bat")
          }
        >
          打撃個人成績
        </button>

        <button
          className={
            tab === "pitch"
              ? "active"
              : ""
          }
          onClick={() =>
            setTab(
              "pitch"
            )
          }
        >
          投球個人成績
        </button>

        <button
          className={
            tab === "rank"
              ? "active"
              : ""
          }
          onClick={() =>
            setTab("rank")
          }
        >
          ランキング
        </button>

        <button
          className={
            tab === "team"
              ? "active"
              : ""
          }
          onClick={() =>
            setTab("team")
          }
        >
          チーム成績
        </button>
      </div>

      {tab === "bat" && (
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>
                  選手
                </th>
                <th>
                  打席
                </th>
                <th>
                  打数
                </th>
                <th>
                  安打
                </th>
                <th>
                  HR
                </th>
                <th>
                  打点
                </th>
                <th>
                  三振
                </th>
                <th>
                  四球
                </th>
                <th>
                  死球
                </th>
                <th>
                  打率
                </th>
                <th>
                  出塁率
                </th>
                <th>
                  OPS
                </th>
              </tr>
            </thead>

            <tbody>
              {battingRows.map(
                ({
                  player,
                  stats,
                }: any) => (
                  <tr
                    key={
                      player.id
                    }
                  >
                    <td>
                      {
                        player.name
                      }
                    </td>

                    <td>
                      {stats.PA}
                    </td>

                    <td>
                      {stats.AB}
                    </td>

                    <td>
                      {stats.H}
                    </td>

                    <td>
                      {stats.HR}
                    </td>

                    <td>
                      {
                        stats.RBI
                      }
                    </td>

                    <td>
                      {stats.SO}
                    </td>

                    <td>
                      {stats.BB}
                    </td>

                    <td>
                      {
                        stats.HBP
                      }
                    </td>

                    <td>
                      {average(
                        stats.AVG
                      )}
                    </td>

                    <td>
                      {average(
                        stats.OBP
                      )}
                    </td>

                    <td>
                      {average(
                        stats.OPS
                      )}
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      )}

      {tab ===
        "pitch" && (
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>
                  投手
                </th>

                <th>
                  登板
                </th>

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
                  四球
                </th>

                <th>
                  死球
                </th>

                <th>
                  被HR
                </th>

                <th>
                  失点
                </th>

                <th>
                  自責
                </th>

                <th>
                  防御率
                </th>
              </tr>
            </thead>

            <tbody>
              {players.map(
                (p: any) => {
                  const rows =
                    pitching.filter(
                      (
                        x: any
                      ) =>
                        x.pitcher_id ===
                        p.id
                    );

                  const finals =
                    pitchingGame.filter(
                      (
                        x: any
                      ) =>
                        x.pitcher_id ===
                        p.id
                    );

                  const outs =
                    finals.reduce(
                      (
                        total:
                          number,
                        x: any
                      ) =>
                        total +
                        Number(
                          x.innings_outs ||
                            0
                        ),
                      0
                    );

                  const er =
                    finals.reduce(
                      (
                        total:
                          number,
                        x: any
                      ) =>
                        total +
                        Number(
                          x.earned_runs ||
                            0
                        ),
                      0
                    );

                  const hits =
                    rows.filter(
                      (
                        x: any
                      ) =>
                        [
                          "安打",
                          "二塁打",
                          "三塁打",
                          "本塁打",
                        ].includes(
                          x.result
                        )
                    ).length;

                  const k =
                    rows.filter(
                      (
                        x: any
                      ) =>
                        x.result ===
                        "三振"
                    ).length;

                  const bb =
                    rows.filter(
                      (
                        x: any
                      ) =>
                        x.result ===
                        "四球"
                    ).length;

                  const hbp =
                    rows.filter(
                      (
                        x: any
                      ) =>
                        x.result ===
                        "死球"
                    ).length;

                  const hr =
                    rows.filter(
                      (
                        x: any
                      ) =>
                        x.result ===
                        "本塁打"
                    ).length;

                  const runs =
                    rows.reduce(
                      (
                        total:
                          number,
                        x: any
                      ) =>
                        total +
                        Number(
                          x.runs ||
                            0
                        ),
                      0
                    );

                  const gamesPitched =
                    new Set(
                      rows.map(
                        (
                          x: any
                        ) =>
                          x.game_id
                      )
                    ).size;

                  return (
                    <tr
                      key={
                        p.id
                      }
                    >
                      <td>
                        {
                          p.name
                        }
                      </td>

                      <td>
                        {
                          gamesPitched
                        }
                      </td>

                      <td>
                        {innings(
                          outs
                        )}
                      </td>

                      <td>
                        {hits}
                      </td>

                      <td>
                        {k}
                      </td>

                      <td>
                        {bb}
                      </td>

                      <td>
                        {hbp}
                      </td>

                      <td>
                        {hr}
                      </td>

                      <td>
                        {runs}
                      </td>

                      <td>
                        {er}
                      </td>

                      <td>
                        {outs
                          ? (
                              (er *
                                27) /
                              outs
                            ).toFixed(
                              2
                            )
                          : "---"}
                      </td>
                    </tr>
                  );
                }
              )}
            </tbody>
          </table>
        </div>
      )}

      {tab ===
        "rank" && (
        <>
          <h2>
            打率ランキング
          </h2>

          {[...battingRows]
            .sort(
              (
                a: any,
                b: any
              ) =>
                b.stats
                  .AVG -
                a.stats
                  .AVG
            )
            .map(
              (
                x: any,
                i: number
              ) => (
                <div
                  className="card"
                  key={
                    x.player
                      .id
                  }
                >
                  <b>
                    {i + 1}
                    　
                    {
                      x.player
                        .name
                    }
                  </b>

                  <span
                    style={{
                      float:
                        "right",
                    }}
                  >
                    {average(
                      x.stats
                        .AVG
                    )}
                  </span>
                </div>
              )
            )}
        </>
      )}

      {tab ===
        "team" && (
        <TeamStats
          games={
            games
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
   TEAM STATS
========================================================= */

function TeamStats({
  games,
  batting,
}: any) {
  const finished =
    games.filter(
      (g: any) =>
        g.status ===
        "finished"
    );

  const wins =
    finished.filter(
      (g: any) =>
        Number(
          g.our_score
        ) >
        Number(
          g.their_score
        )
    ).length;

  const losses =
    finished.filter(
      (g: any) =>
        Number(
          g.our_score
        ) <
        Number(
          g.their_score
        )
    ).length;

  const draws =
    finished.length -
    wins -
    losses;

  const runs =
    finished.reduce(
      (
        total: number,
        g: any
      ) =>
        total +
        Number(
          g.our_score ||
            0
        ),
      0
    );

  const allowed =
    finished.reduce(
      (
        total: number,
        g: any
      ) =>
        total +
        Number(
          g.their_score ||
            0
        ),
      0
    );

  const stats =
    battingStats(
      batting
    );

  return (
    <>
      <h2>
        チーム成績
      </h2>

      <div className="grid3">
        <div className="metric">
          <b>
            {finished.length}
          </b>
          試合
        </div>

        <div className="metric">
          <b>
            {wins}勝
            <br />
            {losses}敗
            <br />
            {draws}分
          </b>
          戦績
        </div>

        <div className="metric">
          <b>
            {average(
              stats.AVG
            )}
          </b>
          チーム打率
        </div>
      </div>

      <div className="grid2">
        <div className="metric">
          <b>{runs}</b>
          得点
        </div>

        <div className="metric">
          <b>
            {allowed}
          </b>
          失点
        </div>
      </div>
    </>
  );
}

/* =========================================================
   HISTORY
========================================================= */

function History({
  games,
}: any) {
  const [selected, setSelected] =
    useState<any>(null);

  const [scores, setScores] =
    useState<any[]>([]);

  async function openGame(
    g: any
  ) {
    setSelected(g);

    const result =
      await supabase
        .from(
          "inning_scores"
        )
        .select("*")
        .eq(
          "game_id",
          g.id
        )
        .order("inning");

    setScores(
      result.data || []
    );
  }

  if (selected) {
    const inningsList =
      [
        ...new Set(
          scores.map(
            (x: any) =>
              x.inning
          )
        ),
      ].sort(
        (
          a: any,
          b: any
        ) => a - b
      );

    return (
      <>
        <button
          onClick={() =>
            setSelected(
              null
            )
          }
        >
          ← 一覧へ
        </button>

        <div className="card">
          <h2>
            {
              selected.opponent
            }
            戦
          </h2>

          <div className="score">
            {
              selected.our_score
            }{" "}
            -{" "}
            {
              selected.their_score
            }
          </div>

          <div className="muted">
            {
              selected.game_date
            }
            　
            {selected.place ||
              ""}
            　
            {selected.game_type ||
              ""}
          </div>
        </div>

        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>
                  回
                </th>

                {inningsList.map(
                  (
                    n: any
                  ) => (
                    <th
                      key={
                        n
                      }
                    >
                      {n}
                    </th>
                  )
                )}

                <th>R</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td>
                  自チーム
                </td>

                {inningsList.map(
                  (
                    n: any
                  ) => (
                    <td
                      key={
                        n
                      }
                    >
                      {scores.find(
                        (
                          x: any
                        ) =>
                          x.inning ===
                            n &&
                          x.side ===
                            "our"
                      )?.runs ??
                        "-"}
                    </td>
                  )
                )}

                <td>
                  {
                    selected.our_score
                  }
                </td>
              </tr>

              <tr>
                <td>
                  相手
                </td>

                {inningsList.map(
                  (
                    n: any
                  ) => (
                    <td
                      key={
                        n
                      }
                    >
                      {scores.find(
                        (
                          x: any
                        ) =>
                          x.inning ===
                            n &&
                          x.side ===
                            "their"
                      )?.runs ??
                        "-"}
                    </td>
                  )
                )}

                <td>
                  {
                    selected.their_score
                  }
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </>
    );
  }

  const finished =
    games.filter(
      (g: any) =>
        g.status ===
        "finished"
    );

  return (
    <>
      <h2>
        過去の試合
      </h2>

      {!finished.length && (
        <div className="notice">
          終了した試合はまだありません。
        </div>
      )}

      {finished.map(
        (g: any) => {
          const result =
            Number(
              g.our_score
            ) >
            Number(
              g.their_score
            )
              ? "○"
              : Number(
                    g.our_score
                  ) <
                  Number(
                    g.their_score
                  )
                ? "●"
                : "△";

          return (
            <button
              className="card log"
              key={g.id}
              onClick={() =>
                openGame(g)
              }
            >
              <b>
                {result}　
                {g.opponent}
              </b>

              <span
                style={{
                  float:
                    "right",
                }}
              >
                {g.our_score} -{" "}
                {
                  g.their_score
                }
              </span>

              <div className="tiny">
                {g.game_date}
                　
                {g.place ||
                  ""}
              </div>
            </button>
          );
        }
      )}
    </>
  );
}
