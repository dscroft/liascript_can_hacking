<!--
author:   David Croft
email:    david.croft@warwick.ac.uk
version:  0.1.0
language: en
narrator: UK English Female

classroom: enable
mode: Presentation
icon: https://dscroft.github.io/liascript_materials/assets/logo.svg

import: macros_interface.md
import: macros_dashboard.md

@style
.lia-effect__circle {
    display: none;
}

.flex-container {
    display: flex;
    flex-wrap: wrap; /* Allows the items to wrap as needed */
    align-items: stretch;
    gap: 20px; /* Adds both horizontal and vertical spacing between items */
}

.flex-child { 
    flex: 1;
    margin-right: 20px; /* Adds space between the columns */
}

@media (max-width: 600px) {
    .flex-child {
        flex: 100%; /* Makes the child divs take up the full width on slim devices */
        margin-right: 0; /* Removes the right margin */
    }
}
@end

@onload
// frame receiver
LIA.classroom.subscribe("can-frame", (message) => {
    window.can_message_handler(message["id"], message["data"]);
})

// frame sender
window.send_can_frame = function(frameid, data) {
    LIA.classroom.publish("can-frame", {
        id: frameid,
        data: data
    });
}
@end


@Classroom.defaultManager
------------------------

**CAN bus status: ** 
<script>
    function status()
    {
        if (LIA.classroom.connected) {
            send.lia("LIASCRIPT: **Emulated**<!-- style='color: green;' -->");
        } else {
            send.lia("LIASCRIPT: **Disconnected**<!-- style='color: red;' -->");
        }
    }

    setInterval(() => status, 1000);
    status();
</script> 

------------------------

@end
-->

# Introduction

This activity is designed to demonstrate how a malicious attacker can intercept and retransmit CAN frames on a CAN bus.

This sort of attack should not work in a modern vehicle but certainly was possible in older vehicles and is still possible in other systems that use CAN.

------------------------------

This activity works best in groups of 3, ideally every member will have their own computer.

In the event that there are insufficient participants or computers then groups of 2 or 4 will also work, individuals on their own will struggle.

------------------------------

You can navigate through the activity using:

- The arrow buttons at the bottom of the page.
- The arrow keys on your keyboard.
- The navigation bar on the left.

-----------------------------

<!--
style="background-color: firebrick; color: white"
-->
>⚠️**Warning**
>
> For the practical part of the activity you will need to be using a reasonably up to date version of Chrome, Edge or Opera.
>
> - Smartphone and tablet browsers generally will not work.


# CAN data format

Over the next couple of pages we will be looking at the format of CAN data and how it can be represented in a more human readable format.

## DBC Format

Various ways to represent CAN frame structure, we are going to use DBC.

For example: the accelerator pedal position information for a 2010 Toyota Prius could be represented as shown below.

```ascii
Frame ID     Frame Name
     \         /       .------ Frame Length (in bytes)
      \       /       /              Max value
       v      V       V                  |
   BO_ 81 GAS_PEDAL: 8 XXX               V
    SG_ GAS_PEDAL : 23|8@0+ (0.005,0) [0|1] '' XXX
           ^        ^ ^  ^ ^    ^   ^   ^ 
          /        / /   |  \    \   \   \
Signal name       / /    |   \    \   \   Min value
      Starting bit /     |    \    \  Offset
        Length (in bits) |     \  Scaling factor
                         |  Signed/Unsigned
                Motorola/Intel Format 
```                        

What this specifies is that accelerator pedal position will be transmitted as a value between 0 and 200, stored in bits 23 to 16 and that pedal position can be sent in 0.5% increments.

<details>
<summary>**Umm, actually...**</summary>

> In reality the frame ID is 581 but for the sake of simplicity for this task we are using classic CAN and so have to keep our frame IDs <256
</details>

## Encoding information

An accelerator pedal pressed three quarters down would have a value of 0.75.

Below is our 8 byte CAN frame, for the pedal position we set bits 23-16.

<!--
style="
  max-width: 600px;" -->
```ascii
         +----+----+----+----+----+----+----+----+
       0 |  7 |  6 |  5 |  4 |  3 |  2 |  1 |  0 |
         +----+----+----+----+----+----+----+----+
       1 | 15 | 14 | 13 | 12 | 11 | 10 |  9 |  8 |
         ╔════╦════╦════╦════╦════╦════╦════╦════╗
       2 ║ 23 ║ 22 ║ 21 ║ 20 ║ 19 ║ 18 ║ 17 ║ 16 ║
         ╚════╩════╩════╩════╩════╩════╩════╩════╝
Bytes  3 | 31 | 30 | 29 | 28 | 27 | 26 | 25 | 24 |
         +----+----+----+----+----+----+----+----+
       4 | 39 | 38 | 37 | 36 | 35 | 34 | 33 | 32 |
         +----+----+----+----+----+----+----+----+
       5 | 47 | 46 | 45 | 44 | 43 | 42 | 41 | 40 |
         +----+----+----+----+----+----+----+----+
       6 | 55 | 54 | 53 | 52 | 51 | 50 | 49 | 48 |
         +----+----+----+----+----+----+----+----+
       7 | 63 | 62 | 61 | 60 | 59 | 58 | 57 | 56 |
         +----+----+----+----+----+----+----+----+
```

Apply the scaling factor 0.75 / 0.005 = 150, that's 0x96 in hexadecimal or 10010110 in binary.

Which appears as shown below:

<!--
style="
  max-width: 600px;" -->
```ascii
         +----+----+----+----+----+----+----+----+
       0 |    |    |    |    |    |    |    |    |
         +----+----+----+----+----+----+----+----+
       1 |    |    |    |    |    |    |    |    |
         ╔════╦════╦════╦════╦════╦════╦════╦════╗
       2 ║  1 ║  0 ║  0 ║  1 ║  0 ║  1 ║  1 ║  0 ║
         ╚════╩════╩════╩════╩════╩════╩════╩════╝
Bytes  3 |    |    |    |    |    |    |    |    |
         +----+----+----+----+----+----+----+----+
       4 |    |    |    |    |    |    |    |    |
         +----+----+----+----+----+----+----+----+
       5 |    |    |    |    |    |    |    |    |
         +----+----+----+----+----+----+----+----+
       6 |    |    |    |    |    |    |    |    |
         +----+----+----+----+----+----+----+----+
       7 |    |    |    |    |    |    |    |    |
         +----+----+----+----+----+----+----+----+
```

Assuming that there was no other information being sent in this frame, the complete message could look something like:

0000000000000000100101100000000000000000000000000000000000000000

But as that's quite unwheldly it's not common to represent the information in hexademical (base 16) format. 
In which case it appears as 0x0000960000000000


# Activity 

These instructions are written on the assumption that you are working as part of a group with 3 computers, each computer fills a specific role.

These roles will be referred to as Alice, Bob and Charlie.

- Alice 👩 will be playing the part of the driver.

  - In this scenario it is a drive by wire vehicle, so the accelerator pedal is not mechanically linked to anything.
  - Pressing the pedal causes a signal to be sent to the engine control unit (ECU) to perform the appropriate action. 
- Bob 👨 will be playing the part of the vehicle.

  - We are just going to simulate the Instrument Cluster (IC) for this exercise.
    
    - In a traditional vehicle this may be handled by a dedicated microcontroller.
    - In more modern vehicle or in the future this may be handled by a container process running on a more general purpose HPC (High Performance Computer).

  - But the same principles apply to the engine control unit (ECU) and other vehicle systems.
- Charlie 😈 will be playing a malicious attacker.

  - They have gained access to the CAN bus and can send and receive messages.

--------------------------------

CAN bus attacks like this have been demonstrated repeatedly on the production vehicles.

- In 2015 a group of researchers were able to take control of a Jeep Cherokee by sending CAN frames over the vehicle's entertainment system.

  - [Wired.com story.](https://www.wired.com/2015/07/hackers-remotely-kill-jeep-highway/)

- In 2016 a group of researchers were able to take control of a Tesla Model S by sending CAN frames over the vehicle's entertainment system.

  - [Black Hat Europe paper.](https://www.blackhat.com/docs/us-17/thursday/us-17-Nie-Free-Fall-Hacking-Tesla-From-Wireless-To-CAN-Bus-wp.pdf)


!?[Wired.com report on the 2015 Jeep hack](https://www.youtube.com/watch?v=MK0SrxBC1xs "Wired.com report on the 2015 Jeep hack")

{{1}}
> ~~Step 1:~~
>
> **Decide in your groups who will be Alice, Bob and Charlie.**


<!--
style="background-color: firebrick; color: white"
-->
>⚠️**Warning**
>
> Make sure to pay attention to the step numbers as some tasks will require you to you to do things at the same time as other group members.

```ascii

💻👩   💻😈   💻👨
 |      |      | 
 *------*------*
```

## Hardware setup

@Classroom.defaultManager

This is the setup we are emulating. 

![](assets/images/placeholder.jpg "Vehicle CAN bus")

{{0-1}}
> ~~Step 2:~~
>
> **Make sure you are connected to the emulated CAN bus.**
>
> - The CAN bus status is shown at the top of the page.
>
>   - It it says **Emulated**<!-- style="color: green;" --> then move on to the next step.
> - If it says **Disconnected**<!-- style="color: red;" --> then you need to connect to the classroom.
>
>   1. Click on the share <i class="icon icon-social lia-btn__icon"></i> icon in the top right corner of the page.
>   2. Click on the "Classroom" button.
>   3. Use the provided settings.
>
>     - via Backend: <i class="icon icon-gundb icon-xs"></i> GUN 
>     - room: *Use the provided room name*
>     - maybe password: *Leave blank*
>     - relay server: https://peer.wallie.io/gun
>     - persistent storage: *Leave blank*
>     - Allow scripts to be executed in the chat: *Leave blank*
>   4. Click on the "connect" button.
>


{{1-2}}
> ~~Step 3:~~
>
> **Go to the page that corresponds to your role.**
>
> - Alice 👩, Bob 👨 or Charlie 😈.
> 
>   - You can use the navigation bar on the left or the arrow buttons below.


-------------------------

When we conduct this activity in the lab we setup an actual CAN bus using Arduino boards and send real CAN frames between them.

- Each group member connected via USB to one of the Arduino circuit boards.
- The Arduino board connected via CAN into a simple CAN bus.
- The CAN bus terminated by appropriate resistors at each end.

Because you are running this practical activity remotely we are using an emulated CAN bus instead, but
the data we are sending is the same as it would be in a real CAN frame.

<section class="flex-container">

<!-- class="flex-child" style="min-width: 500px;" -->
```ascii
             .-------------------. .-------------------.
+--------+   |      +--------+   | |      +--------+   |
|        |   +-.    |        |   | |      |        |   +-.  
|   CANL o <-+ |    |   CANL o <-.-.      |   CANL o <-+ |
|        |     #    |        |            |        |     #
|        |     #    |        |            |        |     # Resistor
|        |     #    |        |            |        |     #
|   CANH * <-+ |    |   CANH * <-.-.      |   CANH * <-+ |
|USB     |   +-.    |USB     |   | |      |USB     |   +-.
+-#------+   |      +-#------+   | |      +-#------+   |
  |          |        |          | |        |          |
 💻👩        |       💻😈        | |       🚗          |
             .-------------------. .-------------------.
```

<!-- class="flex-child" style="min-width: 200px;" -->
![](assets/images/placeholder.jpg "CAN bus setup in the lab")

</section>









## 👩 Alice 

@Classroom.defaultManager

{{0-1}}
> ~~Step 4:~~
>
> **Use the controls below to simulate driving the vehicle.**
>
> - When you interact with the controls, the corresponding CAN frames will be sent to the CAN bus.
>
>   - These frames will be picked up by the other devices on the bus e.g. Bob.
>   - These CAN frames are based on *real* frames. E.g. the accelerator pedal frame was taken from a 2010 Toyota Prius.
>
> <script input="submit" default="Press for hint">
"Try using the indicators."
</script>

{{1-2}}
> ~~Step 5:~~
>
> **Confirm with Bob 👨 that the instrument cluster is responding to your controls.**

{{2-3}}
> ~~Step 6:~~
>
> **Work with Charlie 😈 to identify the CAN frames that are being sent.**

{{3-4}}
> ~~Step 7:~~
>
> **Wait while Charlie 😈 sends some CAN frames to the bus.**

{{4-5}}
> ~~Step 8:~~
>
> **Check to see if you still have control of the vehicle.**
>
> <script input="submit" default="Press for hint">
"Try using the accelerator."
</script>

{{5-6}}
> ~~Step 9:~~
>
> **While Charlie 😈 sends some CAN frames to the bus.**
>
> - Try and control the vehicle.

{{6-7}}
> ~~Step 10:~~
>
> **Discuss with Bob 👨 and Charlie 😈 what is happening.**
>
> - What is the effect of the frames that Charlie 😈 is sending?

<section class="flex-container">
<div class="flex-child" style="min-width: 200px; max-width: 50%;">
@can.alice
</div>
<div class="flex-child" style="min-width: 560px;">
@Dashboard.display
</div>
</section>


## 👨 Bob 

@Classroom.defaultManager

{{5}}
> **Check that the IC is responding correctly to the CAN frames that Alice is sending.** 
>
> <script input="submit" default="Press for hint">
"Check the indicators."
</script>

{{6}}
> **Work with Charlie 😈 to identify the CAN frames that are being sent.**

{{7}}
> **Wait while Charlie 😈 sends some CAN frames to the bus.**

{{8}}
> **Check that the IC is responding to the frames that Charlie 😈 is sending.**
>
> <script input="submit" default="Press for hint">
"Are both indicators on?"
</script>

{{9}}
> **While Charlie 😈 sends some CAN frames to the bus.**
>
> - Check to see if Alice 👩 still has control of the vehicle.

{{10}}
> **Discuss with Alice 👩 and Charlie 😈 what is happening.**
>
> - What is the effect of the frames that Charlie 😈 is sending?

@Dashboard.display


## 😈 Charlie 

Charlie's role has two parts:

1. Interception.

    - Where we identify the CAN frames that correspond to specific actions.
2. Retransmission.

    - Where we resend CAN frames we have intercepted previously to take control of the vehicle.

### Interception

@Classroom.defaultManager

The Intercept table will show the CAN frames that are being sent and received on the CAN bus.

In this case the information that is being sent between Alice and Bob.
This is the first step in a man-in-the-middle attack.

For a CAN bus this is passive action and does not need to be literally in the middle.
As long as Charlie is on the same CAN bus, they can see all the messages being sent.

{{5}}
> **Try and identify the CAN frames that correspond to the actions that Alice 👩 is taking.**
>
> - Importantly, we don't need to decode or understand the CAN data, just identify which frames correspond to which actions.
>
>   - You may want to make notes.
>
> <script input="submit" default="Press for hint">
"E.g. Every time the indicators are used, a frame with ID 203 is intercepted."
</script>

<script run-once="true" style="display: block" modify="false">
    console.log("Intercept module loaded");

    if (typeof window.buffer === 'undefined') {
        window.buffer = [];
    }
    
    let bufferMaxSize = 10;

    function addToBuffer(line) 
    {
        buffer.push([Date.now(), ...line]);
        if (buffer.length > bufferMaxSize) 
            buffer.shift();
    }

    function displayBuffer()
    {
        let liatable =  "<!-- data-type='none' \n" +
                        "     data-title='Received CAN frames' \n" + 
                        "     data-sortable='false' -"+"->\n" + // bodge for macro parser
                        "| Timestamp | CAN Frame ID | Data |\n" +
                        "|-|-|------|\n"

        for (let i = 0; i < buffer.length; ++i) {  
            let hex = buffer[i][2].map(byte => byte.toString(16).padStart(2, '0').toUpperCase()).join('');
            liatable += `| ${buffer[i][0]} | ${buffer[i][1]} | 0x${hex} |\n`;
        }

        send.lia( "LIASCRIPT: "+liatable );
    }

    LIA.classroom.subscribe("can-frame", (message) => {
        addToBuffer([message["id"], message["data"]]);
        displayBuffer();
    });

    displayBuffer();

    "LIA: wait"
</script>


### Retransmission

@Classroom.defaultManager

Using the form below, Charlie can transmit arbitrary CAN frames to the CAN bus.

{{7}}
> **Send a CAN frame**
>
> - Use the information from one of the frames that you intercepted previously.
>
> <script input="submit" default="Press for hint">
document.getElementById("can_frame_id").value = 203;
document.getElementById("can_frame_data").value = "0x2000000000000000";
document.getElementById("can_frame_duration").value = 1;
document.getElementById("can_frame_hz").value = 1;

"Send a frame to turn both indicators on."
</script>

{{8}}
> **Check with Bob 👨 that the IC is responding to your retransmitted CAN frames.**
>
> - Sending a single frame could have a noticeable effect on the vehicle.
>
>   - E.g. unlocking doors, turning on lights, etc.
> - More subtle attacks could be to send a frame that causes the dashboard to display incorrect information.
> <script input="submit" default="Press for hint">
"Both indicators should have turned on."
</script>

{{9}}
> **Send multiple frames**
>
> - Use the form below to send multiple frames.
> 
>   - Adjust the Duration and Rate values to control how many frames are sent and how quickly.
> - By "flooding" the CAN bus with frames we can overwhelm or drown out legitimate frames.
> 
> <script input="submit" default="Press for hint">
document.getElementById("can_frame_id").value = 81;
document.getElementById("can_frame_data").value = "0x0000C80000000000";
document.getElementById("can_frame_duration").value = 30;
document.getElementById("can_frame_hz").value = 100;
document.getElementById("can_frame_duration").dispatchEvent(new Event('input'));
document.getElementById("can_frame_hz").dispatchEvent(new Event('input'));

"Flooding the bus with frames saying the accelerator is fully pressed."
</script>

{{10}}
> **Discuss with Alice 👩 and Bob 👨 what is happening.**
>
> - What is the effect of the frames that you are sending?

@can.retransmit



# Summary

In this activity you have seen how a malicious attacker can intercept and retransmit CAN frames.

- This is an example of a replay attack where the attacker was able to capture real data and then replay it to the vehicle.
  - Another example of a replay attack would be to capture the signal from the key fob and then replay it to unlock the vehicle.

CAN is extremely vulnerable to these types of attacks as it was designed to be simple and robust, not secure.

- It pre-dates the kind of connectivity present in modern vehicles.


## Mitigation

There are a number of ways to mitigate or limit the efficacy of these types of attacks on CAN networks.

Other network technologies such as Ethernet have improved security due to a combination of designed in security features and inherent structure.

- But come at both a complexity and financial cost.

--------------------------

1. **Message Authentication Codes (MACs)**

    - Use cryptographic techniques to ensure the authenticity of messages.
    - Helps in verifying that the message has not been altered.

2. **Encryption**

    - Encrypt CAN messages to prevent unauthorized access and tampering.
    - Ensure that only authorized nodes can decrypt and understand the messages.

3. **Rolling Codes**

    - Use rolling codes for critical commands to prevent replay attacks.
    - Each command is valid only once, making it difficult for attackers to reuse captured messages.

4. **Intrusion Detection Systems (IDS)**

    - Implement IDS to monitor CAN traffic for anomalies.
    - Detect and alert on suspicious activities or patterns that indicate an attack.

5. **Segmentation**

    - Segment the CAN network into smaller, isolated sections.
    - Limit the impact of a compromised node by containing the attack within a segment.

6. **Rate Limiting**

    - Implement rate limiting to control the frequency of messages sent on the CAN bus.
    - Prevent attackers from flooding the network with malicious messages.

7. **Message Filtering**

    - Use message filters to allow only legitimate messages to be processed.
    - Discard any messages that do not match predefined criteria.

-----------------------

By implementing these methods, the security of CAN networks can be significantly enhanced, reducing the risk of attacks and ensuring the integrity and reliability of the communication system.



