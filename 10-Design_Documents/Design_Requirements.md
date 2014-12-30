R-COG Design
============

Note:  I expect the below paragraph to go away at some point.

- Per our phone discussion 12-27-14 and the desire to create a list of "core" functionality and/or sensors for our robots I decided to create this document to record these and other requirements for our robot's "brain".  I expect this to be a "living" document, updated and modified as necessary to reflect our current design goals.


+ Core Goals
  - Reference Based Cognition
  - Mobility
  - Portability
  - Navigation
  - Manipulation
  - Affordability

+ Stretch Goals
  - Interactivity
  - Robustness
  - World Domination :)

###  Reference Based Cognition
  + We believe our robots shouldn't need to perform all of their cognitive processing internally, but rather have access to a more powerful source of information.  This source could be a computer on your LAN, or an internet based source.
  + Network connectivity is therefore required and in order to support our other goals and the current state of technology we believe that WIFI is the best option.  Other connectivity options like bluetooth and wireless UARTs would work, but have more limited range, bandwidth or lack the portability of WIFI.
  + Reference software TBD
  
### Mobility
  + Mobility as it relates to the COG is really a matter of interface and optamization to what ever robot hardware is most appropriate for the given operating environment.  With the possible infinate variety of robotic hardware to interface with it is probably best to offload the actual motor drivers and high current power supplies outside of the COG and interface with them via a data bus of some kind.  Therefore, the following breakdown will focus on various mobility types and their impact on the COG itself.

  + A list of popular mobility types we should consider and their requirements:
    - Differential Wheeled
      1. Unbalanced
          - No additional requirements other than core processing ability
      2. Balanced
          - 2 axis accelerometer and gyro required
    - Legged
      - No additional requirements
    - Proportional and Vectored Thrust
      - 3 axis accelerometer and gyro required

  + Due to inexpensive device availability I propose a 3 axis accel/gyro sensor be included in the COG

### Portability
  + Portability really comes down to being able to set up and operate the robot in as many locations as possible. To support this goal I propose the COG have the following features.
    - Ad-hoc WIFI
      - While WIFI is very prevalant, allowing our bots the ability to operate on an ad-hoc netowrk makes location options essentially limitless.  As long as you have a wireless device that supports ad-hoc, your bot can operate
    - Low Power
      - While not strictly necessary, in some places it is difficult to source power for bot charging (e.g. out camping) so a low power COG would allow for better operation.
      - I propose 3 things to keep power low.
        1. Switching requlators should be used wherever possible.
        2. If low power hardware can be sourced for minimal cost increase, it be done.
        3. Weight be kept to a minimum.
    
### Navigation
  + Navigaion can be done in many ways.  Its possible that the COG won't be able to support them all, but several major ones and their requirements are listed below.
  
  + Guided Path
    - This navigation method would require some kind of path detection sensor in the COG, but is usually applied to robots with low portability.  As such, I propose that the COG not support this method natively but through external sensors. 
  + Dead Reconing
    - This method of navigation uses direction and speed data to calculate the position of the robot.  This can be done with drive feedback only, but I propose that a magnetic compass would be an inexpensive and effective way to improve this type of navigation.
  + Inertial
    - Navigating this way requires 2 or 3 axis gyros and accelerometers which I propose be included in the COG

  + Landmark Recognition
    - Tactile Recognition/Mapping
      -Recognizing the environment through touch.  A great way to navigate in some environments, however I propose that the sensors required would be misplaced if included in the COG.  External sensor support only.

    - Fixed Beacon
      - This can be done using a variety of methods, however common ones are GPS and radio telemetry.  To include these in the COG would require a GPS receiver and a scanning radio receiver respectively.  While I don't see any issue with including these natively in the COG I would propose we do so with consideration of the cost.
      - Another interesting way to do this would be through ultrasonic beacons.  Due to their low cost and the possibility of sharing the sensor(s) with the Interactivity goal, this might be a good option.
      
    - Ultrasonic Mapping
      - A processor non-intensive way of range finding, I propose not including this in the COG soley because other options below should product better results for the same cost.
      
    - Infared Mapping
      - A processor non-intensive way of range finding, I propose not including this in the COG soley because other options below should product better results for the same cost.
      
    - Laser Mapping
      - Typically a higly accurate way of rangefinding, it trades accuracy for cost but not to the extent that it becomes useless.  I propose we incorporate a low cost laser in conjunction with a camera in the COG.
      
    - Image Recognition
      - Would require a single video or still camera which can be shared with other goals like Interactivity. This option has a high communication bandwidth/processing tradeoff, but has proven feasable in study.  I propose incorporating at least 1 video camera in the COG.
      
    - Stereoscopic Recognition/Mapping
      -This requires 2 video or still cameras which equates to a double hit to bandwidth and processing.  The cameras should be within budget, but I propose that the ripple effects to processing and network hardware be evaluated before approval for integration in the COG. 

### Manipulation
  + The ability to manipulate the environment (e.g. arms and hands, tools, weapons...)
  + I propose that these would have no additional impact on the COG as they would share data bus communications with the propulsion systems and sensors with the navigation systems.
  
### Affordability
  + Reflecting on my personal finances and that I pursue robotics as a hobby I would set a goal price of $100.00 for a complete COG.  This, of course, does not include development costs.

### Interactivity
  + The ability to respond to inputs from the environment (e.g. vocal/gestured commands, radio control, response to moving objects, loud noises...)
  + I propose that impacts to the COG be limited to sensors that share purpose with other core goals.

### Robustness
  + Not that we would designing something that wasn't robust, this goal is focused more on making the COG "bullet proof" or at least "idiot proof".
  + This being a stretch goal, and since the initial design of the COG isn't done, I propose this goal be shelved at least until a working COG prototype exists to evaluate.

### World Domination
  + I'm tired after only writing this document.  World domination sounds exhausting.
