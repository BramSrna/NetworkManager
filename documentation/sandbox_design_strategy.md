# Sandbox Design Stratgy
The core of this project is based around studying swarm robotics and swarm techniques. As such, the project will sacrifice efficiency and security to prioritize testing. The main techniques used to ensure this strategy are:
- Plug-and-play (inheritance): To make comparison between various implementations easier to test, the development of the system shall be centred around the ability to swap out components where possible. This will be done by using OOP inheritance practices.
- Heavy Logging: The system shall have heavy logging to make debugging as easy as possible