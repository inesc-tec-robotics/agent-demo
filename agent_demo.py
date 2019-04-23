#!/usr/bin/python3

import asyncio
import websockets
import json
from time import sleep
from copy import deepcopy
import sys


# sends a message to the broker
async def send_msg(msg, websocket, debug=False):

  await websocket.send(msg)

  if debug:
    print("Message sent: {}".format(msg))


# waits for a message from the broker
async def get_msg(websocket, debug=False):

  msg = await websocket.recv()

  if debug:
    print("Message received: {}".format(msg))
    
  return msg


# simulates the execution of a task
def execute(agent):

  task = 'Executing task'
  
  if agent == 'PhoXi':
    task = 'Detecting position'
    
  elif agent == 'CoatingRobot':
    task = 'Coating'

  print(task + '... ', end='\r')
  
  sleep(5)
  
  print(task + '... Finished.')


# generates a response message
def gen_resp(msg_in):

  # use msg_in as template
  msg_out = deepcopy(msg_in)
  msg_out['Topic'] = 'task_completed'
  msg_out['SenderID'], msg_out['Receivers'] = msg_out['Receivers'], msg_out['SenderID']

  # recreate Body
  msg_out['Body'] = {}
  msg_out['Body']['EventID'] = ''
  msg_out['Body']['Variables'] = {}
  msg_out['Body']['Entity'] = 'Task'
  msg_out['Body']['State'] = 'Completed'
  msg_out['Body']['Event_Type'] = 'task_completed'
  msg_out['Body']['Event_Class'] = 'Progress'

  # create Details dict
  msg_out['Body']['Details'] = {}
  msg_out['Body']['Details']['process_instance_id'] = msg_in['Body']['process_instance_id']
  msg_out['Body']['Details']['task_instance_id'] = msg_in['Body']['task_instance_id']
  msg_out['Body']['Details']['task_id'] = msg_in['Body']['task_id']

  return msg_out


# main function
async def agent_demo(address, port):

  # set agent name
  agent = 'KMR_Agent'
  if len(sys.argv) > 1 and sys.argv[1] != 'debug':
    agent = sys.argv[1]

  # set debug flag
  debug = True if sys.argv[-1] == 'debug' else False

  print('Attempting to connect to server on \'ws://' + str(address) +
    ':' + str(port) + '/horse/message\' as \'' + agent + '\'...', end='\r')

  async with websockets.connect('ws://' + str(address) + ':' + str(port) + '/horse/message') as websocket:

    # register agent with broker
    await send_msg('___CONTROL___{"ID":"' + agent + '","Operation":"connect"}', websocket, debug)
    
    print('Attempting to connect to server on \'ws://' + str(address) +
          ':' + str(port) + '/horse/message\' as \'' + agent + '\'... Connected.')

    while True:

      # wait for broker response
      msg_in = await get_msg(websocket, debug)

      # wait for task_assigned message
      print('Waiting for \'task_assigned\' messages...')
      msg_in = json.loads(await get_msg(websocket, debug))
      
      if msg_in['Topic'] != 'task_assigned':
        print('Unexpected topic: ' + msg_in['Topic'])
        return
        
      print('\'task_assigned\' message received!')

      # simulate task execution
      execute(agent)

      # reply with task_completed message
      await send_msg(json.dumps(gen_resp(msg_in)), websocket, debug)


if __name__ == "__main__":

  asyncio.get_event_loop().run_until_complete(agent_demo('127.0.0.1', '10282'))
