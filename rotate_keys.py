import boto3
from datetime import datetime, timezone, timedelta

# ✅ Fill your AWS IAM user credentials here (make sure it has permissions)
aws_access_key = 'YOUR_ACCESS_KEY'
aws_secret_key = 'YOUR_SECRET_KEY'
aws_region = 'YOUR_AWS_REGION'  # Example: 'us-west-1'

# ✅ Replace these with verified emails in your SES sandbox
sender_email = 'sender@gmail.com'
receiver_email = 'receiver@gmail.com'

# ---------- Clients ----------
iam_client = boto3.client(
    'iam',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

ses_client = boto3.client(
    'ses',
    region_name=aws_region,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

# ---------- Step 1: Detect old keys ----------
def get_old_keys(min_age_minutes=0, min_age_hours=0, min_age_days=0):
    old_keys = []
    threshold = timedelta(days=min_age_days, hours=min_age_hours, minutes=min_age_minutes)
    threshold_date = datetime.now(timezone.utc) - threshold

    users = iam_client.list_users()['Users']

    for user in users:
        user_name = user['UserName']
        keys = iam_client.list_access_keys(UserName=user_name)['AccessKeyMetadata']

        for key in keys:
            create_date = key['CreateDate']
            if create_date < threshold_date and key['Status'] == 'Active':
                old_keys.append({
                    'UserName': user_name,
                    'AccessKeyId': key['AccessKeyId'],
                    'CreateDate': create_date
                })
    return old_keys

# ---------- Step 2: Rotate keys ----------
def rotate_keys(old_keys):
    new_keys = []
    for key in old_keys:
        user_name = key['UserName']
        access_key_id = key['AccessKeyId']

        print(f"🔄 Rotating key for {user_name} - Old Key: {access_key_id}")

        # Disable old key
        iam_client.update_access_key(
            UserName=user_name,
            AccessKeyId=access_key_id,
            Status='Inactive'
        )
        print(f"🛄 Old key disabled for {user_name}: {access_key_id}")

        # Delete old key
        iam_client.delete_access_key(
            UserName=user_name,
            AccessKeyId=access_key_id
        )
        print(f"🗑 Old key deleted for {user_name}: {access_key_id}")

        # Create new key
        response = iam_client.create_access_key(UserName=user_name)
        new_key = response['AccessKey']
        new_keys.append({
            'UserName': user_name,
            'AccessKeyId': new_key['AccessKeyId'],
            'SecretAccessKey': new_key['SecretAccessKey']
        })

        print(f"✅ New key created for {user_name}: {new_key['AccessKeyId']}")

    return new_keys

# ---------- Step 3: Notify admin ----------
def notify_admin(rotated_keys):
    if not rotated_keys:
        print("No keys rotated. Skipping email.")
        return

    body_text = "🔐 IAM Access Keys Rotated:\n\n"
    for key in rotated_keys:
        body_text += (
            f"User: {key['UserName']}\n"
            f"Access Key ID: {key['AccessKeyId']}\n"
            f"Secret Access Key: {key['SecretAccessKey']}\n\n"
        )

    response = ses_client.send_email(
        Source=sender_email,
        Destination={'ToAddresses': [receiver_email]},
        Message={
            'Subject': {'Data': '✅ IAM Access Keys Rotated'},
            'Body': {'Text': {'Data': body_text}}
        }
    )
    print("📧 Email notification sent. Message ID:", response['MessageId'])

# ---------- Run the automation ----------
if __name__ == "__main__":
    # Use small time threshold for testing (e.g. 5 minutes)
    old_keys = get_old_keys(min_age_minutes=3)
    print(f"Found {len(old_keys)} old key(s)")

    if old_keys:
        rotated_keys = rotate_keys(old_keys)
        notify_admin(rotated_keys)
    else:
        print("✅ No old keys to rotate.")
