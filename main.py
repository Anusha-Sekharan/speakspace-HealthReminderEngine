import argparse
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, EmailStr
from typing import Optional
from googleapiclient.errors import HttpError

from gmail_client import get_gmail_service, send_email
from utils import format_email_body

app = FastAPI(title="SpeakSpace Doctor Summary Sender")

class SummaryRequest(BaseModel):
    doctor_email: EmailStr
    subject: str = "Patient Summary"
    summary: str
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None

@app.post("/send-summary")
async def send_summary_endpoint(request: SummaryRequest):
    """
    Accepts a summary and sends it to the specified doctor's email.
    """
    try:
        service = get_gmail_service()
        
        text_body, html_body = format_email_body(
            summary=request.summary,
            patient_name="Anusha S",
            patient_id="54321"
        )
        
        result = send_email(
            service=service,
            to=request.doctor_email,
            subject=request.subject,
            text_body=text_body,
            html_body=html_body
        )
        
        return {
            "success": True,
            "gmail_message_id": result.get('id'),
            "sent_to": request.doctor_email
        }
        
    except HttpError as e:
        # Google API specific errors
        raise HTTPException(status_code=502, detail=f"Gmail API Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_cli_test(test_email: str):
    """
    Run a CLI smoke test to send an email.
    """
    print(f"Starting CLI test. Sending email to {test_email}...")
    try:
        service = get_gmail_service()
        text_body, html_body = format_email_body(
            summary="This is a test summary from the CLI utility.",
            patient_name="Anusha S",
            patient_id="54321"
        )
        result = send_email(
            service=service,
            to=test_email,
            subject="CLI Test - SpeakSpace",
            text_body=text_body,
            html_body=html_body
        )
        print(f"Successfully sent email! Message ID: {result.get('id')}")
    except Exception as e:
        print(f"Failed to send email: {e}")


import re
from orchestrator import process_command

class ExecuteRequest(BaseModel):
    text: Optional[str] = None
    prompt: Optional[str] = None
    doctor_email: Optional[EmailStr] = None

@app.post("/process-command")
async def process_command_endpoint(request: ExecuteRequest):
    """
    Smart endpoint: Parses natural language to perform Reminder+Summary actions.
    Accepts 'text' or 'prompt' field.
    """
    try:
        # 1. Resolve Text
        command_text = request.prompt or request.text
        if not command_text:
            raise HTTPException(status_code=400, detail="No text or prompt provided")

        # 2. Resolve Email
        target_email = request.doctor_email
        if not target_email:
            # Try to extract from text
            match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', command_text)
            if match:
                target_email = match.group(0)
            else:
                # Fallback: Raise error or use a default if configured? 
                # For now, require it in text if not in field.
                raise HTTPException(status_code=400, detail="Doctor email not provided and could not be found in text.")

        results = process_command(command_text, target_email)
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="SpeakSpace Doctor Email Service")
    parser.add_argument("--test-email", type=str, help="Send a test email to this address and exit")
    
    args = parser.parse_args()
    
    if args.test_email:
        run_cli_test(args.test_email)
    else:
        import os
        port = int(os.environ.get("PORT", 8000))
        # Run the server
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
