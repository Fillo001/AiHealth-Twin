# this is the previous heuristic logic moved to its own file
from typing import List, Dict

def heuristic_insights(metrics: List[Dict]) -> Dict:
    if not metrics:
        return {
            "summary": "No recent data. Log sleep, steps, mood, and heart rate for insights.",
            "recommendations": ["Aim for 7–9 hours of sleep.", "Take a 20-minute walk today.", "Log your mood daily."],
            "risk_flags": []
        }
    last = metrics[-1]
    recs = []
    risks = []
    sleep = last.get("sleep_hours")
    steps = last.get("steps", 0)
    mood = last.get("mood")
    hr = last.get("heart_rate")

    if sleep is not None and sleep < 6:
        recs.append("Try an earlier wind-down to reach at least 7 hours of sleep.")
        risks.append("Sleep debt risk")
    if steps is not None and steps < 6000:
        recs.append("Add a 15–30 minute walk to increase daily steps.")
    if mood is not None and mood <= 2:
        recs.append("Do a 5-minute breathing exercise and journal.")
        risks.append("Low mood trend")
    if hr is not None and hr > 95:
        recs.append("Hydrate and consider a short rest; elevated heart rate detected.")
        risks.append("Elevated heart rate")

    if not recs:
        recs.append("Great trends! Maintain consistency with sleep and activity.")

    summary = "Based on your latest entry, here are tailored suggestions."
    return {"summary": summary, "recommendations": recs, "risk_flags": risks}
