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


from orchestrator import process_command

class ExecuteRequest(BaseModel):
    text: str
    doctor_email: EmailStr

@app.post("/process-command")
async def process_command_endpoint(request: ExecuteRequest):
    """
    Smart endpoint: Parses natural language to perform Reminder+Summary actions.
    """
    try:
        results = process_command(request.text, request.doctor_email)
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
        # Run the server
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
