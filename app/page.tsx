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
