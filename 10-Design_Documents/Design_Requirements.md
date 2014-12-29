## R-COG Design
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

#  Reference Based Cognition
  + We believe our robots shouldn't need to perform all of their cognitive processing internally, but rather have access to a more powerful source of information.  This source could be a computer on your LAN, or an internet based source.
  + Network connectivity is therefore required and in order to support our other goals and the current state of technology we believe that WIFI is the best option.  Other connectivity options like bluetooth and wireless UARTs would work, but have more limited range, bandwidth or lack the portability of WIFI.
  + Reference software TBD
  + 
  
# Mobility
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

# Portability
  + Portability really comes down to being able to set up and operate the robot in as many locations as possible. To support this goal I propose the COG have the following features.
    - Ad-hoc WIFI
      - While WIFI is very prevalant, allowing our bots the ability to operate on an ad-hoc netowrk makes location options essentially limitless.  As long as you have a wireless device that supports ad-hoc, your bot can operate
    - Low Power
      - While not strictly necessary, in some locals it is difficult to source power for bot charging (e.g. out camping) so a low power COG would allow for better operation.
    
#Navigation
#Manipulation
#Affordability

#Interactivity
#Robustness
#World Domination
