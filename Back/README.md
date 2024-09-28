# AREA POC

This is a proof of concept for the AREA project. It is a simple web application that allows users to create and manage their own reactions and actions.

## Endpoints

### Login

- **PATH**: `/login`
    - header: `Content-Type: application/json`
    - method: `POST`
    - body:
      ```json
      {
          "email": "email@example.xyz",
          "password": "password"
      }
    - Returns a JWT token that can be used to authenticate the user in authenticated endpoints.


- **PATH**: `/register`
    - header: `Authorization: Bearer <token>`
    - method: `POST`
    - body:
      ```json
      {
          "email": "email@example.xyz",
          "username": "didier",
          "password": "password"
      }
    - Returns a 201 status code if the user was created successfully.
    - Note that this endpoint will not log in the user automatically.
 

### Users management

- **PATH**: `/users`
    - header: `Authorization: Bearer <token>`
    - method: `GET`
    - Returns a list of all users in the database if the user is an admin.
      ```json
      {
          [
              {
                  "id": 1,
                  "email": "email1@example",
                  "username": "didier",
                  "createdAt": "2020-11-11T00:00:00.000Z",
                  "role": "user"
              },
              {
                  "id": 2,
                  "email": "email2@example",
                  "username": "giselle",
                  "createdAt": "2020-11-11T00:00:00.000Z",
                  "role": "user"
              }
          ]
      }

- **PATH**: `/users/count`
    - header: `Authorization: Bearer <token>`
    - method: `GET`
    - Returns the number of users in the database if the user is an admin.


- **PATH**: `/users/:id`
    - header: `Authorization: Bearer <token>`
    - method: `GET`
    - Returns the user with the specified id if the user is an admin.
      ```json
      {
          "id": 1,
          "email": "email@example",
          "username": "didier",
          "createdAt": "2020-11-11T00:00:00.000Z",
          "role": "user"
      }

- **PATH**: `/users/:id`
    - header: `Authorization : Bearer <token>
    - method: `PUT`
    - body:
      ```json
      {
          "email": "email@example",
          "username": "didier",
          "role": "admin"
          "password": "password"
      }
    - Returns 200 status code if the user was updated successfully.
    - Note that the password is optional and will not be updated if not provided.


- **PATH**: `/users/:id`
    - header: `Authorization : Bearer <token>
    - method: `DELETE`
    - Returns 204 status code if the user was deleted successfully.
    - Note that the user will not be deleted if it is the last admin in the database or the user is not an admin.


### Actions/reactions management

- **PATH**: `/actions`
    - header: `Authorization: Bearer
    - method: `POST`
      - body:
        ```json
        {
            "name": "string",
            "reaction_type": "string",
            "action_type": "string",
            "reaction_config": {
                "config1": "string",
                ...
                "config": "string"
             }
        }
        ```
    - Returns 201 status code if the action was created successfully.
        - Also returns the action trigger URL.
    - The `reaction_config` object should contain the necessary parameters for the reaction type depending on the action type.
    - Configs encoding:
      - The actions have multiple arguments that are usable in the reaction (like the email title, body, etc...).
      - The reaction JSON takes configs strings that can take action arguments as values: `"You received an email from {{sender}}, the title is {{title}}"`"`
      - If an argument does not exist in the action, it will be replaced by an empty string.
      - Follow the given reference to see the available arguments for each action and reaction.
