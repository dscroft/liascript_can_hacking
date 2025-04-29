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
    LIA.classroom.subscribe("can-recv", (message) => {
        console.log("Received message: ", message);
        window.canMessage = message;
    })
}

// Call this function to start the waiting process
waitForConnection();
@end
-->

# Classroom communications test

Over the next couple of pages we will be looking at the format of CAN data and how it can be represented in a more human readable format.

Status: 
<div id="status"></div>

Message:
<div id="message"></div>

<script>
    window.message_refresh = setInterval(function()
    {
        document.getElementById("message").innerHTML = window.canMessage ? JSON.stringify(window.canMessage) : "No message received";
    }, 1000/16);

    console.log( "init" );
</script>


