import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('User')
reels_table = dynamodb.Table('Reel')

def generate_unique_id():
    return str(uuid.uuid4())

def lambda_handler(event, context):
    print(event)
    body = {}
    statusCode = 200
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        route_key = event['routeKey']

        if route_key == 'POST /users':  # Create User
            request_body = json.loads(event['body'])
            user_id = generate_unique_id()
            user = {
                'id': user_id,
                'username': request_body.get('username'),
                'bio': request_body.get('bio'),
                'profilePictureUrl': request_body.get('profilePictureUrl'),
                'followers': request_body.get('followers', 0), # Default to 0
                'following': request_body.get('following', 0)
            }
            table.put_item(Item=user)
            body = {'userId': user_id}

        elif route_key == 'GET /users':  # Get All Users
            response = table.scan()
            items = response.get('Items', [])
            body = items

        elif route_key == 'GET /users/{id}':  # Get User by ID
            user_id = event['pathParameters']['id']
            response = table.get_item(Key={'id': user_id})
            if 'Item' in response:
                body = response['Item']
            else:
                statusCode = 404
                body = {'message': 'User not found'}

        elif route_key == 'PUT /users/{id}':  # Update User
            user_id = event['pathParameters']['id']
            request_body = json.loads(event['body'])
            update_expression = 'SET '
            expression_attribute_values = {}
            for key, value in request_body.items():
                update_expression += f'{key} = :{key}, '
                expression_attribute_values[f':{key}'] = value
            update_expression = update_expression[:-2] # Remove trailing comma and space

            table.update_item(
                Key={'id': user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            body = {'message': 'User updated'}

        elif route_key == 'DELETE /users/{id}':  # Delete User
            user_id = event['pathParameters']['id']
            table.delete_item(Key={'id': user_id})
            body = {'message': 'User deleted'}

        elif route_key == 'POST /reels':  # Create Reel
            request_body = json.loads(event['body'])
            reel_id = generate_unique_id()
            reel = {
                'id': reel_id,
                'userId': request_body.get('userId'),
                'videoUrl': request_body.get('videoUrl'),
                'thumbnailUrl': request_body.get('thumbnailUrl'),
                'title': request_body.get('title'),
                'likes': request_body.get('likes', 0),
                'comments': request_body.get('comments', 0),
                'shares': request_body.get('shares', 0),
                'author': request_body.get('author'),
            }
            reels_table.put_item(Item=reel)
            body = {'reelId': reel_id}

        elif route_key == 'GET /reels':  # Get All Reels
            response = reels_table.scan()
            items = response.get('Items', [])
            body = items

        elif route_key == 'GET /reels/{id}':  # Get Reel by ID
            reel_id = event['pathParameters']['id']
            response = reels_table.get_item(Key={'id': reel_id})
            if 'Item' in response:
                body = response['Item']
            else:
                statusCode = 404
                body = {'message': 'Reel not found'}

        elif route_key == 'PUT /reels/{id}':  # Update Reel
            reel_id = event['pathParameters']['id']
            request_body = json.loads(event['body'])
            update_expression = 'SET '
            expression_attribute_values = {}
            for key, value in request_body.items():
                update_expression += f'{key} = :{key}, '
                expression_attribute_values[f':{key}'] = value
            update_expression = update_expression[:-2]

            reels_table.update_item(
                Key={'id': reel_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            body = {'message': 'Reel updated'}

        elif route_key == 'DELETE /reels/{id}':  # Delete Reel
            reel_id = event['pathParameters']['id']
            reels_table.delete_item(Key={'id': reel_id})
            body = {'message': 'Reel deleted'}

        else:
            statusCode = 400
            body = {'message': 'Invalid route'}

    except KeyError as e:
        statusCode = 400
        body = {'message': f'Missing key: {e}'}
    except Exception as e:
        statusCode = 500
        print(f"Error: {e}") # Important for debugging
        body = {'message': 'Internal server error'}

    body = json.dumps(body, default=str)
    return {
        'statusCode': statusCode,
        'headers': headers,
        'body': body
    }
