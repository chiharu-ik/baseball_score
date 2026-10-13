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
