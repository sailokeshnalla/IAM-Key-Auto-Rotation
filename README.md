🔐 Automated IAM Access Key Rotation with Email Notifications

This project automates the detection and rotation of old AWS IAM access keys to enhance security.  
It scans IAM users for outdated keys, disables and deletes them, generates new access keys, and sends an email notification via **AWS SES** with the updated credentials.  
This ensures better compliance, reduces security risks, and maintains a secure AWS environment with minimal manual effort.  

Features
- ✅ Detects old and unused IAM access keys.  
- 🔄 Automatically disables and deletes outdated keys.  
- 🔑 Generates new access keys for IAM users.  
- 📧 Sends email notifications with new keys using AWS SES.  
- 🛡 Improves AWS security posture by enforcing key rotation.  

Usage
-----
Open rotate_keys.py and update the following values:

- aws_access_key = 'YOUR_ACCESS_KEY'
- aws_secret_key = 'YOUR_SECRET_KEY'
- aws_region = 'YOUR_AWS_REGION'  # e.g. us-west-1

- sender_email = 'sender@example.com'
- receiver_email = 'receiver@example.com'


Run the script:
---------------
- pip install -r requirements.txt
- python rotate_keys.py


The script will:
----------------
- Find old IAM keys (older than the set threshold).
- Disable & delete them.
- Create new keys.
- Send an email notification via SES.
