"use client";

import { useState } from "react";
import ItineraryView, { type Itinerary } from "./ItineraryView";
import { Autocomplete, useJsApiLoader } from "@react-google-maps/api";
import { MAPS_LOADER_OPTIONS } from "./mapsConfig";
import { useRef } from "react";

type Priority = "must" | "want" | "optional";

interface PlaceInput {
  name: string;
  priority: Priority;
}

export default function Home() {
  // ---- state: the single source of truth the screen renders from ----
  const [places, setPlaces] = useState<PlaceInput[]>([]);
  const [newName, setNewName] = useState("");
  const [newPriority, setNewPriority] = useState<Priority>("want");
  const [startPoint, setStartPoint] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const ALL_MODES = [
    { id: "walking", label: " Walk" },
    { id: "transit", label: " Transit" },
    { id: "driving", label: " Drive" },
    { id: "bicycling", label: " Cycle" },
  ] as const;
  type Mode = (typeof ALL_MODES)[number]["id"];
  
  const [modes, setModes] = useState<Mode[]>(["walking"]);
  
  function toggleMode(m: Mode) {
    setModes((prev) =>
      prev.includes(m)
        ? prev.length > 1 ? prev.filter((x) => x !== m) : prev  // never allow zero
        : [...prev, m]
    );
  }

  const { isLoaded: mapsReady } = useJsApiLoader(MAPS_LOADER_OPTIONS);
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);
  const startAutocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);

  // ---- actions: functions that change state; React redraws ----
  function addPlace() {
    if (!newName.trim()) return;
    setPlaces([...places, { name: newName.trim(), priority: newPriority }]);
    setNewName("");
  }

  function removePlace(index: number) {
    setPlaces(places.filter((_, i) => i !== index));
  }

  function recordSelection(place: { name: string; placeId?: string }) {
    // v2: persist selections and use them to rank/pre-suggest. Deliberate no-op for now.
    console.log("selection:", place);
  }
  
  function onPlaceChosen() {
    const p = autocompleteRef.current?.getPlace();
    if (!p) return;
    const label = p.name && p.formatted_address
      ? `${p.name}, ${p.formatted_address}`
      : p.name ?? "";
    if (!label) return;
    recordSelection({ name: label, placeId: p.place_id });
    setPlaces((prev) => [...prev, { name: label, priority: newPriority }]);
    setNewName("");
  }
  function onStartChosen() {
    const p = startAutocompleteRef.current?.getPlace();
    if (!p) return;
    const label = p.name && p.formatted_address
      ? `${p.name}, ${p.formatted_address}`
      : p.name ?? "";
    if (!label) return;
    recordSelection({ name: label, placeId: p.place_id });
    setStartPoint(label);
  }

  async function planTrip() {
    setLoading(true);
    setError(null);
    setItinerary(null);
    try {
      const res = await fetch("/api/optimise", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dates: { start: startDate, end: endDate },
          region: "fr",
          start_point: { name: startPoint },
          places,
          modes, 
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(JSON.stringify(data.detail ?? data, null, 2));
      } else {
        setItinerary(data);
      }
    } catch {
      setError("Could not reach the engine. Is it running?");
    } finally {
      setLoading(false);
    }
  }

  const ready =
    places.length > 0 && startPoint.trim() && startDate && endDate;

  // ---- render: what the screen looks like, given the state ----
  return (
    <main style={{ maxWidth: 680, margin: "0 auto", padding: "64px 24px" }}>
      <h1>Route Optimiser</h1>
      <p style={{
        display: "inline-block",
        background: "var(--blush)",
        color: "var(--sienna)",
        padding: "8px 18px",
        borderRadius: "var(--r-pill)",
        fontSize: 15,
        fontWeight: 500,
        marginTop: 12,
      }}>
        Plan routes across your day, automatically
      </p>

      <section 
      style={{
        background: "var(--mist)",
        borderRadius: "var(--r-card)",
        padding: 24,
        marginTop: 24,
        display: "flex",
        flexDirection: "column",
        gap: 16,
      }}>
        <h2>Trip</h2>
        <label>
          Start / accommodation:{" "}
          {mapsReady ? (
            <Autocomplete
              onLoad={(ac) => { startAutocompleteRef.current = ac; }}
              onPlaceChanged={onStartChosen}
            >
              <input value={startPoint} onChange={(e) => setStartPoint(e.target.value)}
                placeholder="Start typing your hotel / start point…" size={32} 
                style={{
                  padding: "12px 16px",
                  borderRadius: "var(--r-input)",
                  border: "1px solid var(--line)",
                  background: "var(--paper)",
                  fontSize: 16,
                  fontFamily: "inherit",
                  color: "var(--ink)",
                  outline: "none",
                  width: "100%",
                  boxSizing: "border-box",
                }}/>
            </Autocomplete>
          ) : (
            <input value={startPoint} onChange={(e) => setStartPoint(e.target.value)}
              placeholder="Start typing your hotel / start point…" size={32} />
          )}
        </label>
        <div style={{ marginTop: 8 }}>
          <label>From: <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} 
          style={{
            padding: "12px 16px",
            borderRadius: "var(--r-input)",
            border: "1px solid var(--line)",
            background: "var(--paper)",
            fontSize: 16,
            fontFamily: "inherit",
            color: "var(--ink)",
            outline: "none",
            width: "100%",
            boxSizing: "border-box",
          }}/></label>{" "}
          <label>To: <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} 
            style={{
              padding: "12px 16px",
              borderRadius: "var(--r-input)",
              border: "1px solid var(--line)",
              background: "var(--paper)",
              fontSize: 16,
              fontFamily: "inherit",
              color: "var(--ink)",
              outline: "none",
              width: "100%",
              boxSizing: "border-box",
            }}/></label>
        </div>
        <div style={{ marginTop: 8 }}>
          <span>Travel by: </span>
          {ALL_MODES.map((m) => (
            <button key={m.id} onClick={() => toggleMode(m.id)}
            style={{
              marginRight: 6,
              padding: "8px 14px",
              borderRadius: "var(--r-pill)",
              border: modes.includes(m.id) ? "1px solid var(--ink)" : "1px solid var(--line)",
              background: modes.includes(m.id) ? "var(--ink)" : "var(--paper)",
              color: modes.includes(m.id) ? "var(--paper)" : "var(--ink)",
              fontSize: 14,
              fontWeight: 500,
              cursor: "pointer",
            }}>
              {m.label}
            </button>
          ))}
        </div>
      </section>

      <section 
      style={{
        background: "var(--mist)",
        borderRadius: "var(--r-card)",
        padding: 24,
        marginTop: 24,
        display: "flex",
        flexDirection: "column",
        gap: 16,
      }}>
        <h2>Places</h2>
        {mapsReady ? (
          <Autocomplete
            onLoad={(ac) => { autocompleteRef.current = ac; }}
            onPlaceChanged={onPlaceChosen}
          >
            <input value={newName} onChange={(e) => setNewName(e.target.value)}
                  placeholder="Start typing a place…" size={28} />
          </Autocomplete>
        ) : (
          <input value={newName} onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addPlace()}
            placeholder="Louvre Museum, Paris" size={28} />
        )}
        <select value={newPriority} onChange={(e) => setNewPriority(e.target.value as Priority)}
          style={{
            padding: "8px 14px",
            borderRadius: "var(--r-pill)",
            border: "1px solid var(--line)",
            background: "var(--paper)",
            color: "var(--ink)",
            fontSize: 14,
            fontWeight: 500,
            cursor: "pointer",
            appearance: "none",
            WebkitAppearance: "none",
          }}>
          <option value="must">must</option>
          <option value="want">want</option>
          <option value="optional">optional</option>
        </select>{" "}
        <button onClick={addPlace}>Add</button>

        <ul>
          {places.map((p, i) => (
            <li key={i}>
              [{p.priority}] {p.name}{" "}
              <button onClick={() => removePlace(i)}>✕</button>
            </li>
          ))}
        </ul>
      </section>

      <button onClick={planTrip} disabled={!ready || loading}
        style={{
          marginTop: 24,
          padding: "12px 24px",
          borderRadius: "var(--r-pill)",
          background: "var(--ink)",
          color: "var(--paper)",
          border: "none",
          fontSize: 16,
          fontWeight: 500,
          cursor: "pointer",
          opacity: !ready || loading ? 0.4 : 1,
        }}>
        {loading ? "Planning…" : "Plan my trip"}
      </button>
      {loading && (
        <div style={{
          marginTop: 24, padding: 24,
          background: "var(--mist)", borderRadius: "var(--r-card)",
          color: "var(--slate)", fontSize: 15,
          display: "flex", alignItems: "center", gap: 12,
        }}>
          <span className="pulse-dot" />
          Geocoding places, computing routes, building your days…
        </div>
      )}

      {error && (
        <pre style={{ color: "crimson", whiteSpace: "pre-wrap", marginTop: 16 }}>{error}</pre>
      )}

      {itinerary != null && (
        <pre style={{ background: "#f6f6f6", padding: 12, marginTop: 16, overflow: "auto" }}>
          {itinerary != null && <ItineraryView itinerary={itinerary} />}
        </pre>
      )}
    </main>
  );
}