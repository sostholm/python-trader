# import time

import json
import os
from pywebpush import webpush, WebPushException
# subscription_info = {
#     "endpoint": "https://fcm.googleapis.com/fcm/send/cv0C-9secwc:APA91bEIC_2ymfdQuOtd1_864LX4wW5NlJWrk4ZoGXk5xIzmXFRAWfEcWE8ZsqpUzRjinSRWa2E37EFR-bSN7ghMZ2VT0225QvXq2MEMJ9HPWlGc69n5QrMlXwZK7vkhtXbl5O3IeUzk",
#     "keys": {
#         "p256dh": "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE6c850EyzqM+F8n8X0Sl7KI85zZ1fieILr5X/NJlxFKfZPBGQjiL9N4urGJJNKI+Cbz3fnlJ4BkVmcmn1Ax9apg==",
#         "auth": "abc123..."
#     }
# }

 

# jwt_payload = {
#     "aud": "https://fcm.googleapis.com",
#     "exp":int(time.time() * 1000) + (12 * 60 * 60),
#     "sub": "mailto: eekoren@hotmail.com"
# }

subscription_info = {"endpoint":"https://fcm.googleapis.com/fcm/send/cuqhrwU29Qg:APA91bEiskY6kjUmujgS_s4_eMeZTWjsPNkQeszy6pi_dVtiUr50WlSqL0lppnSw9VrUUeVkmkSreQqok8dftr_g5BFU0dDOxMv5ow6Hl2oDHmcWFd8dgMYe7goHz_gZMDK3hRu-LATh","expirationTime":None,"keys":{"p256dh":"BNorEc8_WgJpCrsBbSrY6Ul9ZS_UZCCqSQPQpzXUs-4Op7KwwndofYMcet71RBUEWi3XnS0SMVXDaTKH-easzh8","auth":"E1gVc0njuaZKa8ouVxOPoA"}}

# DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH = os.getenv("DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH")
# DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH = os.getenv("DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH")
 
VAPID_PRIVATE_KEY = open('private_key.txt', "r+").readline().strip("\n")
VAPID_PUBLIC_KEY = open('public_key.txt', "r+").read().strip("\n")
 
VAPID_CLAIMS = {
"sub": "mailto:eekoren@hotmail.com"
}
 
def send_web_push(subscription_information, message_body):
    return webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims=VAPID_CLAIMS
    )

if __name__ == "__main__":
    response = send_web_push(subscription_info, "this is just a test")
    print('completed')