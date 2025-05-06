<!--
author:   David Croft
email:    david.croft@warwick.ac.uk
version:  0.1.0
language: en

classroom: enable

@onload
async function waitForConnection() {
  while (!LIA.classroom.connected) {
    await new Promise(resolve => setTimeout(resolve, 100)); // wait 100ms
  }
  // Once window.connection is available
  connectionAvailable();
}

window.canMessage = null;

function connectionAvailable() {
    LIA.classroom.subscribe("can-frame", (message) => {
        console.log("Received message: ", message);
        window.canMessage = message;
    })
}

// Call this function to start the waiting process
waitForConnection();
@end
-->

# Classroom communications test

Test of using LIA classroom pubsub API to emulate CAN bus messages.



## Setup

Joining a classroom.

1. Click on the share <i class="icon icon-social" /> icon in the top right corner of the page.
2. Click on the "Classroom" button.
3. Use the following settings.

    - via Backend: <i class="icon icon-gundb icon-xs"></i> GUN 
    - room: *Use the provided room name*
    - maybe password: *Leave blank*
    - relay server: https://peer.wallie.io/gun
    - persistent storage: *Leave blank*
    - Allow scripts to be executed in the chat: *Leave blank*
4. Click on the "connect" button.
## Test

Status: <span id="status"></span>

<script input="hidden">
    window.status_refresh = setInterval(function()
    {
        document.getElementById("status").innerHTML = LIA.classroom.connected ? "Connected" : "Need to join classroom";
        document.getElementById("status").style.color = LIA.classroom.connected ? "green" : "red";
    }, 1000/16);
</script>

Message:
<div id="message"></div>

<script input="hidden">
    window.message_refresh = setInterval(function()
    {
        document.getElementById("message").innerHTML = window.canMessage ? JSON.stringify(window.canMessage) : "No message received";
    }, 1000/16);
</script>


<label>CAN Frame ID: </label><input class="lia-quiz__input" type="text" id="can_frame_id" placeholder="123">
<label>CAN Data: </label><input class="lia-quiz__input" type="text" id="can_frame_data" placeholder="A1B2C3D4E5F6">

<script default="Send" input="submit">
    console.log("Sending message");
    LIA.classroom.publish("can-frame", {
        id: document.getElementById("can_frame_id").value,
        data: document.getElementById("can_frame_data").value
    });
</script>


