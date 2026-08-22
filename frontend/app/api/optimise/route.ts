import { NextResponse } from "next/server";

const ENGINE_URL = process.env.ENGINE_URL ?? "http://127.0.0.1:8000";

export async function POST(request: Request) {
    const trip = await request.json();
  
    try {
      const res = await fetch(`${ENGINE_URL}/optimise`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(trip),
        signal: AbortSignal.timeout(60_000),
      });
  
      const text = await res.text();
      try {
        return NextResponse.json(JSON.parse(text), { status: res.status });
      } catch {
        console.error("Engine returned non-JSON:", res.status, text.slice(0, 300));
        return NextResponse.json(
          { detail: `Engine answered ${res.status} with non-JSON (see server log).` },
          { status: 502 }
        );
      }
    } catch (err) {
      console.error("Fetch to engine failed:", err);
      return NextResponse.json(
        { detail: "Engine unreachable or timed out — it may be waking up. Try again." },
        { status: 502 }
      );
    }
  }