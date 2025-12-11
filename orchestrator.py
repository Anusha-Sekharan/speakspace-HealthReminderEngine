import re
import dateparser
from dateparser.search import search_dates
from datetime import datetime, timedelta
from calendar_client import get_calendar_service, create_event
from gmail_client import get_gmail_service, send_email
from utils import format_email_body

def process_command(text: str, doctor_email: str):
    """
    Parses natural language text into Calendar actions and/or Doctor Summaries.
    Returns a dict with results of operations.
    """
    results = {
        "calendar_event": None,
        "email_status": None,
        "parsed_intents": []
    }

    # 1. Simple heuristic splitting
    parts = [p.strip() for p in re.split(r'\s+and\s+', text, flags=re.IGNORECASE)]

    calendar_intents = []
    summary_intents = []

    # 2. Classify parts
    for part in parts:
        # scan for dates using search_dates for robustness
        dates = search_dates(part, settings={'PREFER_DATES_FROM': 'future'})
        
        valid_date = None
        if dates:
            for match_text, dt in dates:
                # Filter out trivial matches like "on", "at" that dateparser sometimes catches aggressively
                # "on" (2 chars) is too short. "May" (3) is fine. "7pm" (3) is fine.
                if len(match_text) > 2 or any(c.isdigit() for c in match_text):
                    valid_date = dt
                    break

        if valid_date:
            calendar_intents.append((part, valid_date))
        else:
            # It's likely a summary/note
            summary_intents.append(part)


    # 3. Execute Calendar Actions
    if calendar_intents:
        cal_service = get_calendar_service()
        for action_text, start_time in calendar_intents:
            try:
                event = create_event(cal_service, summary=action_text, start_time=start_time)
                results["calendar_event"] = event.get('htmlLink')
                results["parsed_intents"].append(f"Created Calendar Event: {action_text} at {start_time}")
            except Exception as e:
                results["calendar_error"] = str(e)

    # 4. Execute Email Actions
    if summary_intents:
        summary_text = ". ".join(summary_intents)
        
        try:
            gmail_service = get_gmail_service()
            text_body, html_body = format_email_body(
                summary=summary_text,
                patient_name="User",
                include_metadata=True
            )
            
            send_result = send_email(
                service=gmail_service,
                to=doctor_email,
                subject="Patient Update / Symptom Report",
                text_body=text_body,
                html_body=html_body
            )
            results["email_status"] = "Sent"
            results["email_id"] = send_result.get('id')
            results["parsed_intents"].append(f"Sent Summary to Doctor: {summary_text}")
        except Exception as e:
            results["email_error"] = str(e)
            
    return results
