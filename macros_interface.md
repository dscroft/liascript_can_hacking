<!--
attribute: 
version:  0.0.1
language: en
narrator: UK English Female
title: Module Macros for WebSerial
comment:  This is placeholder module to save macros used in other modules.



@version_history 

@end

@onload
    console.log("Loading interface module");

    // can_message_handler should be called whenever a CAN message is received
    window.can_message_handler = function(frameid, data) {
        console.log( "CAN message handler" );
       
        if( frameid == 203 ) // SCM_FEEDBACK
        {   
            // data[1] is an array of multiple integers where each element represents the value of a byte
            // convert into a single integer where the lsb were contained in element 0

            // true if bit 6 of data is set
            window.turnSignalsStates.left = (data[0] & (1 << 6)) !== 0;     
            window.turnSignalsStates.right = (data[0] & (1 << 5)) !== 0;
        }   
        else if( frameid == 81 ) // GAS_PEDAL
        {
            window.tacho = data[2] * 0.005;
        }
        else if( frameid == 20 ) // SEATS_DOORS
        {
            console.log("seats_doors");
            
            // oh god this code is terrible, figure out javascript conditional logic at some point
            window.iconsStates.seatBelt = (data[7] & (1 << 6)) !== 0 ? 1 : 0;
            window.iconsStates.doors = (data[5] & (1 << 5)) !== 0 || 
                                       (data[5] & (1 << 4)) !== 0 ||
                                       (data[5] & (1 << 3)) !== 0 ||
                                       (data[5] & (1 << 2)) ? 1 : 0;
        }
        else if( frameid == 40 ) // LIGHT_STALK
        {
            console.log("light stalk");
            window.iconsStates.dippedBeam = (data[0] & (1 << 5)) !== 0 ? 1 : 0;
            window.iconsStates.highBeam = (data[0] & (1 << 6)) !== 0 ? 1 : 0;
        }
    }
@end

@_l
<input type="checkbox" id="left">
@end

@_r
<input type="checkbox" id="right">
@end

@_o
<input type="radio" name="headlights" value="off">
@end

@_d
<input type="radio" name="headlights" value="low">
@end 

@_f
<input type="radio" name="headlights" value="high">
@end

@_fl
<input type="checkbox" id="fl_door">
@end

@_fr
<input type="checkbox" id="fr_door">
@end

@_rl
<input type="checkbox" id="rl_door">
@end

@_rr
<input type="checkbox" id="rr_door">
@end

@_s
<input type="checkbox" id="seatbelt">
@end

@_a
<input type="range" min="0" max="200" value="0" id="accelerator">
@end

@_al
<span id="accelerator_level"></span>
@end

@can.alice_ui
```ascii
            '--------+---------'
            | Left ← | → Right |
            +--------+---------+
Indicators  |  "@_l" |  "@_r"  |
            +--------+---------+
Front doors |  "@_fl"|  "@_fr" |
            |        |         |
Rear  doors |  "@_rl"|  "@_rr" |
            '--------+---------'
        '------+--------+------'
 Head   | Off  | Dipped | Full |
lights  | "@_o"|  "@_d" | "@_f"|
        '------+--------+------'

Driver seatbelt "@_s"

Accelerator "@_a               "
"@_al"
```
@end

@can.alice_scripts
<script> <!-- accelerator -->
function update_accel_status()
{
    console.log("Sending accelerator message");

    let value = document.getElementById("accelerator").value;
    document.getElementById("accelerator_level").innerHTML = (value * 0.005).toFixed(3);

    /*Toyota prius
      BO_ 581 GAS_PEDAL: 8 XXX
        SG_ GAS_PEDAL : 23|8@0+ (0.005,0) [0|1] "" XXX*/
    let data = Math.min(200,Math.max(0,parseInt(value)));   
    let bytes = [ 0, 0, data, 0, 0, 0, 0, 0 ];
    try {
        console.log( bytes );
        window.send_can_frame( 81, bytes );
    } catch (error) {
        //console.error("An error occurred:", error);
    }
}

document.getElementById("accelerator").addEventListener("input", update_accel_status );
update_accel_status();
</script>

<script> <!-- doors -->
function update_door_status()
{
    console.log("Sending door message");

    /*BO_ 1568 SEATS_DOORS: 8 XXX
        SG_ SEATBELT_DRIVER_UNLATCHED : 62|1@0+ (1,0) [0|1] "" XXX
        SG_ DOOR_OPEN_FL : 45|1@0+ (1,0) [0|1] "" XXX
        SG_ DOOR_OPEN_RL : 42|1@0+ (1,0) [0|1] "" XXX
        SG_ DOOR_OPEN_RR : 43|1@0+ (1,0) [0|1] "" XXX
        SG_ DOOR_OPEN_FR : 44|1@0+ (1,0) [0|1] "" XXX*/
    let byte5 = ( document.getElementById('fl_door').checked ? (1 << 5) : 0 ) +
                ( document.getElementById('fr_door').checked ? (1 << 4) : 0 ) +
                ( document.getElementById('rl_door').checked ? (1 << 3) : 0 ) +
                ( document.getElementById('rr_door').checked ? (1 << 2) : 0 );
    let byte7 = document.getElementById('seatbelt').checked ? (1 << 6) : 0;
    let bytes = [ 0, 0, 0, 0, 0, byte5, 0, byte7 ];

    console.log( bytes );
    try {
        window.send_can_frame( 20, bytes );
    } catch (error) {
        //console.error("An error occurred:", error);
    }
}

document.getElementById('seatbelt').addEventListener('click', update_door_status);
document.getElementById('fl_door').addEventListener('click', update_door_status);
document.getElementById('fr_door').addEventListener('click', update_door_status);
document.getElementById('rl_door').addEventListener('click', update_door_status);
document.getElementById('rr_door').addEventListener('click', update_door_status);
</script>

<script> <!-- headlights -->
let sendLightStatus = function()
{
  /*BO_ 1570 LIGHT_STALK: 8 SCM
      SG_ AUTO_HIGH_BEAM : 37|1@0+ (1,0) [0|1] "" XXX
      SG_ FRONT_FOG : 27|1@0+ (1,0) [0|1] "" XXX
      SG_ PARKING_LIGHT : 28|1@0+ (1,0) [0|1] "" XXX
      SG_ LOW_BEAM : 29|1@0+ (1,0) [0|1] "" XXX
      SG_ HIGH_BEAM : 30|1@0+ (1,0) [0|1] "" XXX
      SG_ DAYTIME_RUNNING_LIGHT : 31|1@0+ (1,0) [0|1] "" XXX*/

    console.log("Sending light message");

    let selectedHeadlight = document.querySelector('input[name="headlights"]:checked').value;

    console.log( selectedHeadlight );

    let byte0 = ( selectedHeadlight == 'auto' ? (1 << 1) : 0 ) +
                ( selectedHeadlight == 'low' ? (1 << 5) : 0 ) +
                ( selectedHeadlight == 'high' ? (1 << 6) : 0 );
    let bytes = [ byte0, 0, 0, 0, 0, 0, 0, 0 ];

    try
    {
        window.send_can_frame( 40, bytes );
    }
    catch (error)
    {
        //console.error("An error occurred:", error);
    }
}

document.querySelectorAll('input[name="headlights"]').forEach(element => {
  element.addEventListener('change', sendLightStatus);
});
</script>

<script> <!-- indicators -->
let sendSignalMsg = function()
{
    console.log("Sending signal message");

    let byte0 = ( document.getElementById('left').checked ? (1 << 6) : 0 ) +
                ( document.getElementById('right').checked ? (1 << 5) : 0 );
    let bytes = [ byte0, 0, 0, 0, 0, 0, 0, 0 ];

    try {
      window.send_can_frame( 203, bytes );
    }
    catch (error) {
        //console.error("An error occurred:", error);
    }
}

document.getElementById('left').addEventListener('click', sendSignalMsg);
document.getElementById('right').addEventListener('click', sendSignalMsg);
</script>
@end

@can.alice
@can.alice_ui
@can.alice_scripts
@end

@can.retransmit
<label>CAN Frame ID: </label><input class="lia-quiz__input" type="text" id="can_frame_id" placeholder="123">
<label>CAN Data: </label><input class="lia-quiz__input" type="text" id="can_frame_data" placeholder="A1B2C3D4E5F6">
<label>Duration: </label><span id="duration"></span><input type="range" min="1" max="30" value="1" id="can_frame_duration">
<label>Rate: </label><span id="hz"></span><input type="range" min="1" max="100" value="1" id="can_frame_hz">

<script>
  function update_frame_duration()
  {
    let value = document.getElementById("can_frame_duration").value;
    document.getElementById("duration").innerHTML = value + " second/s";
  }

  function update_frame_hz()
  {
    let value = document.getElementById("can_frame_hz").value;
    document.getElementById("hz").innerHTML = value + " Hz";
  }

  document.getElementById("can_frame_duration").addEventListener("input", update_frame_duration);
  update_frame_duration();

  document.getElementById("can_frame_hz").addEventListener("input", update_frame_hz);
  update_frame_hz();
</script>

<script input="submit" default="Send">
  let id = parseInt(document.getElementById("can_frame_id").value);

  let data = document.getElementById("can_frame_data").value.toUpperCase();
  if( data.startsWith("0X") ) data = data.slice(2);
  data = data.match(/.{2}/g).map(byte => parseInt(byte, 16));

  let duration = parseFloat(document.getElementById("can_frame_duration").value);
  let hz = parseFloat(document.getElementById("can_frame_hz").value);
  let num = duration * hz;

  send.lia("Sending "+num+" messages");

  let interval = setInterval(() => {
    window.send_can_frame( id, data );
    num -= 1;
    send.lia( "Messages remaining: "+num );

    
    if (num <= 0) {
      clearInterval(interval);
      send.lia("Send");
    }
  }, 1000 / hz);

</script>
@end

@can.intercept

<script style="display: block" modify="false">
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

    "LIA: wait"
</script>
@end
-->

# Module Macros

