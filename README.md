# agent-demo

This repository holds the script for a test agent, developed in the scope of the HORSE FLEXCoating experiment.

The script simulates a real agent integrated in the HORSE framework. It connects to a local Broker of the HORSE Cyber-Physical Middleware and waits for a *task_assigned* message sent from the HORSE Manufacturing Process Management Software (MPMS). It then simulates the execution of a task by waiting for 5 seconds and generates an appropriate *task_completed* message, which it sends back to the MPMS through the Broker.
