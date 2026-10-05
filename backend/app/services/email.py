"""
Email service — sends OTP verification emails via SMTP.
Uses the SMTP settings from app.config.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings

logger = logging.getLogger(__name__)


def _build_otp_html(name: str, otp_code: str) -> str:
    """Build a styled HTML email body for OTP verification."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;background:#0a0a0f;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0f;padding:40px 20px;">
            <tr>
                <td align="center">
                    <table width="480" cellpadding="0" cellspacing="0"
                           style="background:linear-gradient(145deg,#13131a,#1a1a25);
                                  border:1px solid rgba(139,92,246,0.2);
                                  border-radius:16px;overflow:hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="padding:32px 32px 0;text-align:center;">
                                <div style="display:inline-block;background:linear-gradient(135deg,#8b5cf6,#06b6d4);
                                            padding:12px;border-radius:12px;margin-bottom:16px;">
                                    <span style="font-size:24px;">✨</span>
                                </div>
                                <h1 style="color:#ffffff;font-size:22px;margin:8px 0 4px;">
                                    Resume<span style="color:#8b5cf6;">Xpert</span>
                                </h1>
                                <p style="color:#9ca3af;font-size:13px;margin:0;">Email Verification</p>
                            </td>
                        </tr>
                        <!-- Body -->
                        <tr>
                            <td style="padding:28px 32px;">
                                <p style="color:#e5e7eb;font-size:15px;line-height:1.6;margin:0 0 20px;">
                                    Hi <strong>{name}</strong>,
                                </p>
                                <p style="color:#d1d5db;font-size:14px;line-height:1.6;margin:0 0 24px;">
                                    Use the verification code below to complete your registration.
                                    This code expires in <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>.
                                </p>
                                <!-- OTP Code -->
                                <div style="background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.25);
                                            border-radius:12px;padding:20px;text-align:center;margin-bottom:24px;">
                                    <span style="font-size:36px;font-weight:700;letter-spacing:10px;
                                                 color:#8b5cf6;font-family:'Courier New',monospace;">
                                        {otp_code}
                                    </span>
                                </div>
                                <p style="color:#9ca3af;font-size:12px;line-height:1.6;margin:0;">
                                    If you didn't request this code, you can safely ignore this email.
                                    Do not share this code with anyone.
                                </p>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="padding:0 32px 28px;">
                                <hr style="border:none;border-top:1px solid rgba(139,92,246,0.15);margin:0 0 16px;">
                                <p style="color:#6b7280;font-size:11px;text-align:center;margin:0;">
                                    &copy; 2026 ResumeXpert &mdash; AI-Powered Resume Analysis
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def send_otp_email(to_email: str, name: str, otp_code: str) -> bool:
    """
    Send an OTP verification email.

    Returns True on success, False on failure.
    Logs errors but does not raise — the caller decides how to handle failures.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.error(
            "SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD "
            "in your .env file to enable email verification."
        )
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your ResumeXpert Verification Code: {otp_code}"
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
    msg["To"] = to_email

    # Plain-text fallback
    text_body = (
        f"Hi {name},\n\n"
        f"Your ResumeXpert verification code is: {otp_code}\n\n"
        f"This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.\n\n"
        f"If you didn't request this, please ignore this email."
    )
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(_build_otp_html(name, otp_code), "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
        logger.info(f"OTP email sent to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Check SMTP_USER / SMTP_PASSWORD.")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending OTP to {to_email}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending OTP to {to_email}: {e}")
        return False
