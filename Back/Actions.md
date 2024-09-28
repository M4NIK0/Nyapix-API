# Actions and reactions reference

This document describes the actions and reactions that can be configured in the application.

## Actions

### Discord bot DM

- **Description**: Trigger a reaction on Discord bot DM received.
- **Type name**: `discord-bot-dm`
- **Action endpoint**: `/actions/discord/bot-dm/{id}/{token}`
- **Method**: `POST`
- **Parameters**:
  - **username**: User who sent the message.
  - **nickname**: Nickname of the user who sent the message.
  - **message**: Message sent by the user.


- **Example o JSON for API call**:
  ```json
  {
      "username": "didier42",
      "nickname": "Didier",
      "message": "Hello!"
  }
  ```

## Reactions

### Discord webhook

- **Description**: Send a message to a Discord channel using a webhook.
- **Type name**: `discord-webhook`
- **Parameters**:
  - **webhookUrl**: URL of the webhook.
  - **message**: Message to send.


### Teams webhook

- **Description**: Send a message to a Microsoft Teams channel using a webhook.
- **Type name**: `teams-webhook`
- **Parameters**:
  - **webhookUrl**: URL of the webhook.
  - **message**: Message to send.
