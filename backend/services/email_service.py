"""
Email service - sends professional emails to candidates via SMTP.

Messages are built as multipart/alternative (plain text + HTML) with proper
From / Reply-To / Date / Message-ID headers to maximize inbox delivery, and
every SMTP connection uses a timeout plus automatic retries so one slow or
hung connection to the mail server can never stall a request indefinitely.
"""
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from flask import current_app

SMTP_TIMEOUT = 30        # seconds per connection attempt
SMTP_MAX_ATTEMPTS = 3    # initial attempt + 2 retries
RETRY_DELAY = 2          # seconds to wait between attempts


def _email_shell(heading, color, icon, body_html):
    """Wrap body content in the branded HireWise HTML shell."""
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;padding:40px 20px;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.06);">
        <!-- Header -->
        <tr>
          <td style="background:{color};padding:32px 40px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <p style="margin:0;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:rgba(255,255,255,0.7);">HireWise Recruiting</p>
                  <h1 style="margin:8px 0 0;font-size:24px;font-weight:800;color:#ffffff;">{heading}</h1>
                </td>
                <td width="48" align="right" valign="top">
                  <div style="width:48px;height:48px;background:rgba(255,255,255,0.2);border-radius:12px;text-align:center;line-height:48px;font-size:24px;color:#ffffff;">{icon}</div>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <!-- Body -->
        <tr>
          <td style="padding:36px 40px;">
            <p style="margin:0;font-size:14px;line-height:1.7;color:#334155;">
              {body_html}
            </p>
          </td>
        </tr>
        <!-- Divider -->
        <tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #e2e8f0;margin:0;"></td></tr>
        <!-- Footer -->
        <tr>
          <td style="padding:24px 40px;">
            <p style="margin:0;font-size:11px;color:#94a3b8;line-height:1.6;">
              This email was sent via the <strong>HireWise</strong> hiring platform.<br>
              If you believe you received this email in error, please disregard it.
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def get_email_template(email_type, candidate_name='Candidate', role_title=''):
    """Get the subject, plain-text body and HTML body for a status email."""

    if email_type == 'shortlisted':
        subject = f"Application Update - Shortlisted for {role_title}" if role_title \
            else "Application Update - You've Been Shortlisted"
        color = '#059669'  # emerald
        icon = '&#10004;'  # checkmark
        heading = "Great News!"
        role_plain = f" for the {role_title} position" if role_title else ''
        role_html = f" for the <strong>{role_title}</strong> position" if role_title else ''
        body_html = (
            f"Dear {candidate_name},<br><br>"
            "We're excited to inform you that <strong>your application has been shortlisted</strong>"
            f"{role_html} for the next stage of our hiring process.<br><br>"
            "Our recruitment team will be in touch shortly with further details regarding "
            "the next steps, which may include an interview or assessment.<br><br>"
            "Please keep an eye on your inbox and don't hesitate to reach out if you have "
            "any questions.<br><br>"
            "We look forward to getting to know you better!<br><br>"
            "Warm regards,<br>HireWise Recruiting"
        )
        body_text = (
            f"Dear {candidate_name},\n\n"
            f"We're excited to inform you that your application has been shortlisted{role_plain} "
            "for the next stage of our hiring process.\n\n"
            "Our recruitment team will be in touch shortly with further details regarding the "
            "next steps, which may include an interview or assessment.\n\n"
            "Please keep an eye on your inbox and don't hesitate to reach out if you have any "
            "questions.\n\n"
            "We look forward to getting to know you better!\n\n"
            "Warm regards,\nHireWise Recruiting"
        )
    else:
        subject = f"Application Status Update - {role_title}" if role_title \
            else "Application Status Update"
        color = '#64748b'  # slate
        icon = '&#8505;'  # info
        heading = "Application Update"
        role_plain = f" for the {role_title} position" if role_title else ''
        role_html = f" for the <strong>{role_title}</strong> position" if role_title else ''
        body_html = (
            f"Dear {candidate_name},<br><br>"
            f"Thank you for taking the time to apply{role_html}. "
            "We truly appreciate your interest in joining our team.<br><br>"
            "After careful review, we regret to inform you that we will not be moving forward "
            "with your application at this time. This was not an easy decision, as we received "
            "many strong applications.<br><br>"
            "We encourage you to apply for future openings that match your skills and experience. "
            "We wish you the very best in your career journey.<br><br>"
            "Warm regards,<br>HireWise Recruiting"
        )
        body_text = (
            f"Dear {candidate_name},\n\n"
            f"Thank you for taking the time to apply{role_plain}. We truly appreciate your "
            "interest in joining our team.\n\n"
            "After careful review, we regret to inform you that we will not be moving forward "
            "with your application at this time. This was not an easy decision, as we received "
            "many strong applications.\n\n"
            "We encourage you to apply for future openings that match your skills and experience. "
            "We wish you the very best in your career journey.\n\n"
            "Warm regards,\nHireWise Recruiting"
        )

    return subject, body_text, _email_shell(heading, color, icon, body_html)


def _build_message(to_addr, subject, text_body, html_body):
    """Build a multipart/alternative message with deliverability-friendly headers."""
    smtp_user = current_app.config.get('SMTP_USER', '')
    smtp_sender = current_app.config.get('SMTP_SENDER', '') or smtp_user
    sender_domain = smtp_sender.split('@')[1] if '@' in smtp_sender else 'hirewise.local'

    msg = MIMEMultipart('alternative')
    msg['From'] = f'HireWise Recruiting <{smtp_sender}>'
    msg['To'] = to_addr
    msg['Reply-To'] = smtp_sender
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid(domain=sender_domain)
    # Plain text first, HTML last (RFC 2046 preference order for readers)
    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    return msg


def _smtp_send(msg):
    """Send a message with a connection timeout and automatic retries.

    Retries only cover transient connection problems (timeouts, dropped or
    refused connections); authentication and recipient errors fail fast.

    Returns: (success: bool, error_message_or_None)
    """
    smtp_host = current_app.config.get('SMTP_HOST', '')
    smtp_port = current_app.config.get('SMTP_PORT', 587)
    smtp_user = current_app.config.get('SMTP_USER', '')
    smtp_pass = current_app.config.get('SMTP_PASS', '')

    last_error = None
    for attempt in range(1, SMTP_MAX_ATTEMPTS + 1):
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=SMTP_TIMEOUT) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            return True, None
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPRecipientsRefused) as e:
            return False, f'{type(e).__name__}: {e}'
        except OSError as e:
            # Covers socket timeouts, dropped connections and SMTP response errors
            last_error = f'{type(e).__name__}: {e}'
            if attempt < SMTP_MAX_ATTEMPTS:
                print(f'[EMAIL] Attempt {attempt} failed ({last_error}); retrying...')
                time.sleep(RETRY_DELAY)
    return False, last_error


def send_custom_email(candidate, subject, body, role_title=''):
    """
    Send a custom email to a candidate with user-defined subject and body.
    Supports template variables: {name}, {position}, {email}
    Returns: (success: bool, message: str)
    """
    if not candidate.email:
        return False, f'No email address for candidate {candidate.id}'

    try:
        smtp_user = current_app.config.get('SMTP_USER', '')
        smtp_pass = current_app.config.get('SMTP_PASS', '')

        if not smtp_user or not smtp_pass:
            print(f"[EMAIL] Would send custom email to {candidate.email} (SMTP not configured)")
            return True, f'Custom email logged for {candidate.email} (SMTP not configured)'

        candidate_name = candidate.name or 'Candidate'

        # Replace template variables
        rendered_subject = (subject
                            .replace('{name}', candidate_name)
                            .replace('{position}', role_title or '')
                            .replace('{email}', candidate.email))
        rendered_body = (body
                         .replace('{name}', candidate_name)
                         .replace('{position}', role_title or '')
                         .replace('{email}', candidate.email))

        html_body = _email_shell(rendered_subject, '#4f46e5', '&#9993;',
                                 rendered_body.replace(chr(10), '<br>'))

        msg = _build_message(candidate.email, rendered_subject, rendered_body, html_body)

        ok, error = _smtp_send(msg)
        if not ok:
            print(f"[EMAIL ERROR] Failed to send custom email to {candidate.email}: {error}")
            return False, f'Failed to send custom email to {candidate.email}: {error}'

        print(f"[EMAIL] Sent custom email to {candidate.email}")
        return True, f'Custom email sent to {candidate.email}'

    except Exception as e:
        error_msg = f'Failed to send custom email to {candidate.email}: {str(e)}'
        print(f"[EMAIL ERROR] {error_msg}")
        return False, error_msg


def send_candidate_email(candidate, email_type, role_title=''):
    """
    Send an email to a candidate.
    Returns: (success: bool, message: str)
    """
    if not candidate.email:
        return False, f'No email address for candidate {candidate.id}'

    try:
        smtp_user = current_app.config.get('SMTP_USER', '')
        smtp_pass = current_app.config.get('SMTP_PASS', '')

        if not smtp_user or not smtp_pass:
            # Email not configured - log but don't fail
            print(f"[EMAIL] Would send {email_type} email to {candidate.email} (SMTP not configured)")
            return True, f'Email logged for {candidate.email} (SMTP not configured - email not actually sent)'

        candidate_name = candidate.name or 'Candidate'
        subject, text_body, html_body = get_email_template(email_type, candidate_name, role_title)
        msg = _build_message(candidate.email, subject, text_body, html_body)

        ok, error = _smtp_send(msg)
        if not ok:
            print(f"[EMAIL ERROR] Failed to send {email_type} email to {candidate.email}: {error}")
            return False, f'Failed to send email to {candidate.email}: {error}'

        print(f"[EMAIL] Sent {email_type} email to {candidate.email}")
        return True, f'Email sent to {candidate.email}'

    except Exception as e:
        error_msg = f'Failed to send email to {candidate.email}: {str(e)}'
        print(f"[EMAIL ERROR] {error_msg}")
        return False, error_msg
