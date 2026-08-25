"use client";

import { useState } from "react";
import { GoogleMap, Marker, Polyline, useJsApiLoader } from "@react-google-maps/api";
import { MAPS_LOADER_OPTIONS } from "./mapsConfig";

const DAY_COLOURS = ["#C96595", "#4C7CBF", "#3E8E5A", "#C98A3D", "#7A5CC1"];

interface Stop {
  name: string; priority: string; lat: number; lng: number;
  arrival: string; visit_start: string; visit_end: string; warnings: string[];
}
interface Day { day: number; date: string; weekday: string; stops: Stop[]; legs: Leg[] }
export interface Itinerary {
  start_point: { name: string; lat: number; lng: number };
  summary: { num_days: number; total_stops: number; total_walk_min: number };
  days: Day[];
}
interface Leg { from: string; to: string; walk_min: number; mode: string }

export default function ItineraryView({ itinerary }: { itinerary: Itinerary }) {
  const [activeDay, setActiveDay] = useState(0);
  const { isLoaded } = useJsApiLoader(MAPS_LOADER_OPTIONS);

  const day = itinerary.days[activeDay];
  const start = itinerary.start_point;
  const path = [
    { lat: start.lat, lng: start.lng },
    ...day.stops.map((s) => ({ lat: s.lat, lng: s.lng })),
  ];
  const colour = DAY_COLOURS[activeDay % DAY_COLOURS.length];
  const MODE_ICONS: Record<string, string> = {
    walking: "🚶", transit: "🚇", driving: "🚗", bicycling: "🚴",
  };
  return (
    <div style={{ marginTop: 24 }}>
      <p>
        <b>{itinerary.summary.num_days} days · {itinerary.summary.total_stops} stops ·{" "}
        {itinerary.summary.total_walk_min} min travel</b>
      </p>

      <div style={{ display: "flex", gap: 8, margin: "12px 0" }}>
        {itinerary.days.map((d, i) => (
          <button key={d.day} onClick={() => setActiveDay(i)}
            style={{
              padding: "6px 14px", borderRadius: 16, cursor: "pointer",
              border: `2px solid ${DAY_COLOURS[i % DAY_COLOURS.length]}`,
              background: i === activeDay ? DAY_COLOURS[i % DAY_COLOURS.length] : "white",
              color: i === activeDay ? "white" : "inherit",
            }}>
            Day {d.day}
          </button>
        ))}
      </div>

      <p><i>{day.weekday} {day.date}</i></p>
      <ol>
        {day.stops.length === 0 && <p>(free day)</p>}
        {day.stops.map((s) => (
          <li key={s.name}>
            <b>{s.arrival}</b> — {s.name} ({s.visit_start}–{s.visit_end})
            {s.warnings.map((w) => (
              <span key={w} style={{ color: "crimson" }}> ⚠ {w}</span>
            ))}
          </li>
        ))}
        {day.stops.map((s, i) => (
          <li key={s.name}>
            {day.legs[i] && (
              <span style={{ color: "#666" }}>
                {MODE_ICONS[day.legs[i].mode] ?? "🚶"} {day.legs[i].walk_min} min →{" "}
              </span>
            )}
            <b>{s.arrival}</b> — {s.name} ({s.visit_start}–{s.visit_end})
            {s.warnings.map((w) => (
              <span key={w} style={{ color: "crimson" }}> ⚠ {w}</span>
            ))}
          </li>
        ))}
      </ol>

      {isLoaded && (
        <GoogleMap
          mapContainerStyle={{ width: "100%", height: 420, borderRadius: 8 }}
          center={path[0]}
          zoom={13}
        >
          <Marker position={{ lat: start.lat, lng: start.lng }} label="🏠" title={start.name} />
          {day.stops.map((s, i) => (
            <Marker key={s.name} position={{ lat: s.lat, lng: s.lng }}
                    label={String(i + 1)} title={s.name} />
          ))}
          <Polyline path={path}
            options={{ strokeColor: colour, strokeWeight: 4, strokeOpacity: 0.8 }} />
        </GoogleMap>
      )}
    </div>
  );
}