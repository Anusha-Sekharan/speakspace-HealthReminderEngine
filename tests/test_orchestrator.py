import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from orchestrator import process_command

@patch('orchestrator.get_calendar_service')
@patch('orchestrator.get_gmail_service')
@patch('orchestrator.create_event')
@patch('orchestrator.send_email')
def test_process_command_split(mock_send_email, mock_create_event, mock_get_gmail, mock_get_cal):
    """
    Test that the orchestrator correctly splits a compound command.
    Command: "take insulin at 7pm and i have some allergic on my hand"
    Expectation: 
      - 1 Calendar event ("take insulin at 7pm")
      - 1 Email ("i have some allergic on my hand")
    """
    # Setup Mocks
    mock_cal_service = MagicMock()
    mock_get_cal.return_value = mock_cal_service
    
    mock_gmail_service = MagicMock()
    mock_get_gmail.return_value = mock_gmail_service
    
    mock_create_event.return_value = {'htmlLink': 'http://calendar.google.com/event123'}
    mock_send_email.return_value = {'id': 'msg123'}

    # Execute
    text = "take insulin at 7pm and i have some allergic on my hand"
    doctor_email = "doc@example.com"
    
    results = process_command(text, doctor_email)

    # Validations
    print(results)
    
    # 1. Check Calendar Call
    assert mock_create_event.called
    # Arg verification: first arg is service, second is description. 
    # The heuristic might pass "take insulin at 7pm" as the summary.
    call_args = mock_create_event.call_args
    assert "take insulin" in call_args.kwargs['summary'] or "take insulin" in call_args.args[1]
    # Verify time parsing happened (7pm should be a datetime)
    assert isinstance(call_args.kwargs['start_time'], datetime)

    # 2. Check Email Call
    assert mock_send_email.called
    email_call_args = mock_send_email.call_args
    # The text body should contain the allergy part
    assert "allergic on my hand" in email_call_args.kwargs['text_body']
    
    # 3. Check Results Structure
    assert results['calendar_event'] is not None
    assert results['email_status'] == 'Sent'
