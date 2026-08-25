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

  const { isLoaded: mapsReady } = useJsApiLoader(MAPS_LOADER_OPTIONS);
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);

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
    <main style={{ maxWidth: 640, margin: "2rem auto", padding: "0 1rem", fontFamily: "system-ui" }}>
      <h1>Route Optimiser</h1>

      <section>
        <h2>Trip</h2>
        <label>
          Start / accommodation:{" "}
          <input value={startPoint} onChange={(e) => setStartPoint(e.target.value)}
                 placeholder="Saint-Germain-des-Prés, Paris" size={32} />
        </label>
        <div style={{ marginTop: 8 }}>
          <label>From: <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} /></label>{" "}
          <label>To: <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} /></label>
        </div>
      </section>

      <section style={{ marginTop: 24 }}>
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
        <select value={newPriority} onChange={(e) => setNewPriority(e.target.value as Priority)}>
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
              style={{ marginTop: 16, padding: "8px 20px" }}>
        {loading ? "Planning…" : "Plan my trip"}
      </button>

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