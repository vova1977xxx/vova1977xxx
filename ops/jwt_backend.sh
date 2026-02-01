#!/bin/bash
USER=$1
SECRET_KEY="your_secret_key"
payload=$(python3 -c "import jwt
import datetime
payload = {
    \"user\": \"$USER\",
    \"exp\": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}
token = jwt.encode(payload, \"$SECRET_KEY\", algorithm=\"HS256\")
print(token)")
echo $payload
