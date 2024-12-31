import pickle
from datetime import datetime
import boto3
import os

def handle_error(message):
    return {
        "statusCode": 500,
        "body": message
    }

def main(event, context):

    bucket_name = os.environ.get("RESULTS_BUCKET")
    pickle_obj = os.environ.get("PICKLE_OBJECT", "run_data_boundary.p")
    s3C = boto3.client('s3')
    response = s3C.get_object(Bucket=bucket_name, Key=pickle_obj)
    eb = pickle.loads(response['Body'].read())
    
    try:
        myLat = float(event['queryStringParameters']['lat'])
        myLon = float(event['queryStringParameters']['lon'])
    except Exception:
         print(event)
         return handle_error("Provide coordinates as 'lat' and 'lon' GET parameters")
    longIndex = None

    # Find index for closest longitude once 
    for i in range(len(eb['long'])):
        if abs(myLon) > abs(eb['long'][i]):
                print('i ' + str(i))
                print('myLon ' + str(myLon))
                print('long ' + str(eb['long'][i]))
                longIndex = i
                break
    
    # For every hour calculated
    body = ""
    for frame in range(len(eb['smooth'])):
        # Determine if point is above view line (boundary - 8)
        if myLat > eb['smooth'][frame][longIndex] - 8:
            frameTime = eb['time'][frame]
            is_in = "in the boundary at " + str(frameTime)
            body = body + is_in + "\n"
            print(is_in)
    if body == "":
         body = "Coords not inside view line"
    return {
         "statusCode": 200,
         "body": body
    }


if __name__ == "__main__":
    main({"lat": 58.540011, "lon": -63.760875}, None)