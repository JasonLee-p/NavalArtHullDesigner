"""
邮箱验证相关工具
"""

import re
import smtplib
import dns.resolver
from main_logger import Log

_TAG = "EmailUtils"


__all__ = ['is_valid_email_format', 'has_mx_record', 'verify_email_smtp', 'is_valid_email']


def is_valid_email_format(email) -> bool:
    """
    检查邮箱格式是否正确
    :param email:
    :return:
    """
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None


def has_mx_record(domain):
    """
    检查域名是否有MX记录，即是否有邮箱服务器
    :param domain:
    :return:
    """
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return len(mx_records) > 0
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.NXDOMAIN:
        return False
    except Exception as e:
        print(f"Error checking MX records: {e}")
        return False


def verify_email_smtp(email):
    """
    通过SMTP验证邮箱是否存在
    :param email:
    :return:
    """
    domain = email.split('@')[-1]
    mx_records = dns.resolver.resolve(domain, 'MX')
    mx_record = mx_records[0].exchange.to_text()

    server = smtplib.SMTP()
    server.set_debuglevel(0)

    try:
        server.connect(mx_record)
        server.helo(server.local_hostname)  # server.local_hostname gets the fqdn
        server.mail('your-email@example.com')
        code, message = server.rcpt(email)
        server.quit()
        return code == 250
    except Exception as e:
        Log().warning(_TAG, f"验证邮箱时发生错误: {e}")
        return False


def is_valid_email(email):
    if not is_valid_email_format(email):
        return False
    domain = email.split('@')[-1]
    return has_mx_record(domain)
