import pytest
from unittest.mock import MagicMock, patch
from gmail_client import send_email

def test_send_email_success():
    """
    Test that send_email constructs the message correctly and calls the API.
    """
    # Mock the service object and its chain of methods
    mock_service = MagicMock()
    mock_users = mock_service.users.return_value
    mock_messages = mock_users.messages.return_value
    mock_send = mock_messages.send.return_value
    
    # Configure the mock to return a success dict
    expected_response = {'id': '1234567890abcdef', 'threadId': '0987654321fedcba'}
    mock_send.execute.return_value = expected_response

    # Call the code under test
    to_addr = "doctor@test.com"
    subject = "Test Subject"
    body = "Test Body"
    
    result = send_email(mock_service, to_addr, subject, body, html_body="<p>Test Body</p>")

    # Assertions
    assert result == expected_response
    
    # Verify the API was called with the correct structure
    mock_messages.send.assert_called_once()
    call_args = mock_messages.send.call_args
    # call_args.kwargs should contain 'userId' and 'body'
    assert call_args.kwargs['userId'] == 'me'
    assert 'raw' in call_args.kwargs['body']
    
    # Verify the 'raw' content is base64 encoded string
    raw_content = call_args.kwargs['body']['raw']
    assert isinstance(raw_content, str)
    # Be optimistic about base64 decoding to check content simply
    import base64
    decoded = base64.urlsafe_b64decode(raw_content).decode()
    assert f"To: {to_addr}" in decoded
    assert f"Subject: {subject}" in decoded
    assert "Content-Type: multipart/alternative" in decoded

def test_send_email_failure():
    """
    Test that send_email raises an exception if the API fails.
    """
    from googleapiclient.errors import HttpError
    
    mock_service = MagicMock()
    mock_messages = mock_service.users.return_value.messages.return_value
    
    # Create a mock HttpError
    mock_resp = MagicMock()
    mock_resp.status = 403
    error = HttpError(resp=mock_resp, content=b'Access Denied')
    
    mock_messages.send.execute.side_effect = error
    
    with pytest.raises(HttpError):
        send_email(mock_service, "doc@test.com", "Subj", "Body")
