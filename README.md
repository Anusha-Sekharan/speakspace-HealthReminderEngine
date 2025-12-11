# SpeakSpace Doctor Summary Sender

This project provides a service to send health summaries from SpeakSpace to doctors via the Gmail API. It integrates with an existing Google OAuth 2.0 flow.

## Quick Start (Run this Project)
To run this project, you need two terminal windows:

### 1. Start the Server
Open a terminal and run:
```bash
uvicorn main:app --reload
```
*Keep this terminal open.*

### 2. Send Commands
Open a **new** terminal and run the test script:
```bash
python send_command.py "your command here"
```
Example:
```bash
python send_command.py "take insulin at 8pm and i have severe headache"
```

---

## Setup

### 1. Google Cloud Console Configuration
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Select your project.
3. Enable the **Gmail API**.
4. Go to **APIs & Services > Credentials**.
5. Ensure you have an **OAuth 2.0 Client ID** configured as **Desktop App**.
6. Download the JSON file and save it as `credentials.json` in the root of this project.
7. Configure the **OAuth Consent Screen**:
   - Add your test users (email addresses) if the app is in "Testing" status.
   - Ensure the scope `https://www.googleapis.com/auth/gmail.send` is added if strictly configuring scopes, though the code requests it dynamically.

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Environment
A `sample_env_example.env` is provided. Copy it to `.env` if you need to override defaults, though currently most config is passed via API or defaults to project root files.

### 4. Authentication
The first time you run the application or send an email, a browser window will open to ask for permission to send emails on your behalf.
- If you have an existing `token.json` from the Calendar integration, this app will attempt to use it.
- **Note**: If the existing token does not include the Gmail Send scope, the app will prompt for re-authentication to update `token.json`.

## Intelligent Command Processing
You can now send natural language commands that combine reminders and summaries.

**Endpoint**: `POST /process-command`

**Example cURL**:
```bash
curl -X POST http://localhost:8000/process-command \
  -H "Content-Type: application/json" \
  -d '{
    "text": "take insulin at 7pm and i have some allergic on my hand",
    "doctor_email": "doctor@example.com"
  }'
```

**What happens:**
1. **Splits the text**: Finds "take insulin at 7pm" (Reminder) and "i have some allergic on my hand" (Summary).
2. **Creates Calendar Event**: "take insulin" at 7:00 PM today/tomorrow.
3. **Sends Email**: "i have some allergic on my hand" sent to the doctor.

## Usage


### Run the Server
```bash
uvicorn main:app --reload
```
The server will start at `http://localhost:8000`.

### Send a Summary (API)
**Endpoint**: `POST /send-summary`

**Example cURL**:
```bash
curl -X POST http://localhost:8000/send-summary \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_email": "doctor@example.com",
    "subject": "Patient Report - John Doe",
    "summary": "Patient reported feeling dizzy after breakfast. BP 120/80.",
    "patient_name": "John Doe",
    "patient_id": "12345"
  }'
```

**Response**:
```json
{
  "success": true,
  "gmail_message_id": "18abc123...",
  "sent_to": "doctor@example.com"
}
```

### CLI Test Utility
You can test the email sending capability without running the full server:

```bash
python main.py --test-email doctor@example.com
```

## Troubleshooting
- **403 Access Denied**:
  - Check if the **Gmail API** is enabled in the Google Cloud Console.
  - Verification: If your app is not verified by Google, you will see a warning screen. Proceed by clicking "Advanced" > "Go to (App Name) (unsafe)".
  - Ensure the user email you are logging in with is added to "Test Users" in the OAuth Consent Screen if the app is in Testing mode.
- **Refresh Token Info**: `token.json` stores the user's access and refresh tokens. If scopes change, delete `token.json` to force re-authentication.

## Testing
Run unit tests (mocks API calls):
```bash
pytest
```
