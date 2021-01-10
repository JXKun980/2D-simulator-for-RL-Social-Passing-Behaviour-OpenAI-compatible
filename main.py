import pygame, sys
from pygame.locals import *
import math
import random
import os
import json
import numpy
from datetime import datetime

import dispUtils
import dataUtils
import AI
import ObsNRewards
import planner

# USER SETTINGS
#Time settings
updatesPerSecond = 1
realTimeFactor = 10

# Multiagent Setting
numberOfAgents = 2

#Spawn Boxs?
spawnBox = True
numberOfBoxes = 1

# Goals per Epoch
goalPerEpoch = 1

map_type = ""
# map_type = "twoRooms"
# map_type = "complex"


# AI Settings
# AImode
# 0: Fresh training
# 1: Continue training from resume_epoch
# 2: Start fresh training but load weights from loaded_training_name
# 3: Run AI for evaluation

AImode = 1

# training_name = '2D_3Agent_twoRooms_noCollide'
# resume_epoch = '1144' # change to epoch to continue from

# training_name = '2D_3Agents_2Rooms'
# resume_epoch = '140000' # change to epoch to continue from

# training_name = '2D_1Agent_social_corridor_Social_narrow'
# resume_epoch = '49168' # change to epoch to continue from

# training_name = '2D_1Agent_social_corridor_Social_narrow'
# resume_epoch = '49168' # change to epoch to continue from

# training_name = '2D_1Agent_social_corridor_noSocial'
# resume_epoch = '1363' # change to epoch to continue from11

training_name = 'My_Training_2_Agents_with_1_box'
resume_epoch = '1153'

loaded_training_name = '2D_1Agent_social_corridor_Social_narrow'

saveRate = 10000 #Saves the weights and parameters every x epochs

# Performance Check?
performaceCheck = False
numberOfEpochsToTest = 10
testingInterval = 200
startTesting = 1000

##END OF USER SETTINGS

# Timing how long the training took
startTime = datetime.now()

# set up pygame
pygame.init()
mainClock = pygame.time.Clock()

# set up the window
WINDOWWIDTH = 1200
WINDOWHEIGHT = 1200
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('2D Training')

#Generate Map
map_data = dispUtils.mapGeneration(windowSurface,map_type)
windowSurface.fill(map_data[1])
dispUtils.drawObstacles(windowSurface, map_data[2], map_data[0])

# movement Parameters
forawardSpeed = {'linearSpeed': 50/updatesPerSecond, 'angularSpeed': 0/updatesPerSecond}
leftSpeed = {'linearSpeed': 0/updatesPerSecond, 'angularSpeed': -0.6/updatesPerSecond}
rightSpeed = {'linearSpeed': 0/updatesPerSecond, 'angularSpeed': 0.6/updatesPerSecond}
stopSpeed = {'linearSpeed': 0, 'angularSpeed': 0}

# spawn walls and other obstacles
BOXSIZE = WINDOWWIDTH - 100
WALLWIDTH = 50
obstacles = dispUtils.createWalls(windowSurface,BOXSIZE,WALLWIDTH)
dispUtils.drawObstacles(windowSurface, [0,0,0], obstacles)

# box
boxX = int(random.uniform(200, 800))
boxY = int(random.uniform(200, 800))

blacklist = []
while not dispUtils.noCollideSpawnCheck(boxX,boxY,blacklist,200):
    boxX = int(random.uniform(200, 800))
    boxY = int(random.uniform(200, 800))

box = {'position':[boxX,boxY], 'width':80, 'height': 120}
if spawnBox:
    obstacles.append(dispUtils.centreRecttoPoly(box))

def redrawBox():
    boxX = int(random.uniform(200, 800))
    boxY = int(random.uniform(200, 800))
    blacklist = []
    blacklist.extend(robots)
    blacklist.extend(goals)
    while not dispUtils.noCollideSpawnCheck(boxX,boxY,blacklist,200):
        boxX = int(random.uniform(200, 800))
        boxY = int(random.uniform(200, 800))

    box['position'] = [boxX,boxY]
    obstacles[-1] = dispUtils.centreRecttoPoly(box)



# create the AI
path = os.path.dirname(os.path.abspath(__file__)) + '/training_results/' + training_name + '_ep'
reward_file = os.path.dirname(os.path.abspath(__file__)) + '/training_results/' + training_name + '_reward'
performacneReward_file = os.path.dirname(os.path.abspath(__file__)) + '/training_results/' + training_name + '_Performance'

if AImode == 0:
    #Fresh training
    resume_epoch = '0'
    resume_path = os.path.dirname(os.path.abspath(__file__)) + '/training_results/dqn_ep0'
    params_json  = resume_path + '.json'

    dataUtils.create_csv(reward_file)
    if performaceCheck:
        dataUtils.create_csv(performacneReward_file)

    AIparams = dataUtils.loadAIParams(params_json)
    epochs, steps, updateTargetNetwork, explorationRate, epsilon_decay, minibatch_size, learnStart, learningRate, discountFactor, memorySize, network_inputs, network_outputs, network_structure, current_epoch = dataUtils.setAIParams(AIparams)
    network_inputs = network_inputs + (3 - 1)*4

elif AImode == 1:
    #continue training
    resume_path = path + resume_epoch
    weights_path = resume_path + '.h5'
    params_json  = resume_path + '.json'

    AIparams = dataUtils.loadAIParams(params_json)
    epochs, steps, updateTargetNetwork, explorationRate, epsilon_decay, minibatch_size, learnStart, learningRate, discountFactor, memorySize, network_inputs, network_outputs, network_structure, current_epoch = dataUtils.setAIParams(AIparams)

elif AImode == 2:
    #fresh training but with old weights
    params_json  = os.path.dirname(os.path.abspath(__file__)) + '/training_results/dqn_ep0.json'
    weights_path = os.path.dirname(os.path.abspath(__file__)) + '/training_results/' + loaded_training_name + '_ep' + resume_epoch + '.h5'

    dataUtils.create_csv(reward_file)
    if performaceCheck:
        dataUtils.create_csv(performacneReward_file)
    AIparams = dataUtils.loadAIParams(params_json)
    epochs, steps, updateTargetNetwork, explorationRate, epsilon_decay, minibatch_size, learnStart, learningRate, discountFactor, memorySize, network_inputs, network_outputs, network_structure, current_epoch = dataUtils.setAIParams(AIparams)
    network_inputs = network_inputs + (3 - 1)*4

else:
    #start running
    resume_path = path + resume_epoch
    weights_path = resume_path + '.h5'
    params_json  = resume_path + '.json'

    AIparams = dataUtils.loadAIParams(params_json)
    epochs, steps, updateTargetNetwork, explorationRate, epsilon_decay, minibatch_size, learnStart, learningRate, discountFactor, memorySize, network_inputs, network_outputs, network_structure, current_epoch = dataUtils.setAIParams(AIparams)
    explorationRate = 0.01 #Since we dont want any more learning

brain = AI.DeepQ(network_inputs, network_outputs, memorySize, discountFactor, learningRate, learnStart)
brain.initNetworks(network_structure)


# create the training variables
if not AImode == 0:
    brain.loadWeights(weights_path)
    if not AImode == 2:
        epoch = int(current_epoch)
    else:
        epoch = 0
else:
    epoch = 0

episode_steps = 0
stepCounter = 0
cumulated_reward = 0
highest_reward = 0
done = False
highest_performance = 200

# Reward Function variablesm
goal_Distance = dataUtils.listOfSize(numberOfAgents,10000)
goal_ang = dataUtils.listOfSize(numberOfAgents,180)
previousVisibility = dataUtils.listOfSize(numberOfAgents,False)

# MultiAgent variables
observation = dataUtils.listOfSize(numberOfAgents,0)
reward = dataUtils.listOfSize(numberOfAgents,0)
action = dataUtils.listOfSize(numberOfAgents,0)
lastAction = dataUtils.listOfSize(numberOfAgents,0)
pathdata = dataUtils.listOfSize(numberOfAgents,0)
currentSubgoalIndex = dataUtils.listOfSize(numberOfAgents,-1)
goalsHit = dataUtils.listOfSize(numberOfAgents,0)
last20 = dataUtils.listOfSize(numberOfAgents,dataUtils.listOfSize(20,0))

# Spawn All Agents and Goals
# Agent colours
agentColours = [[255,0,0],[0,255,0],[0,0,255],[255,255,0],[255,0,255]]
pathColours = [[255,128,0],[0,255,128],[128,0,255],[255,255,128],[255,128,255]]

robots = []
goals = []
subgoalIndex = []
for i in range(numberOfAgents):
    # create agent
    robots.append({'position':[100,100], 'size':25 , 'dir':0, 'linearSpeed': 50, 'angularSpeed': 0.1})
    dispUtils.noCollideSpawn(windowSurface,robots[-1],robots[:-1],200)

    # spawn goalpoint
    blacklist = []
    blacklist.extend(robots)
    blacklist.extend(goals)
    goals.append({'position':[100,100], 'size':100})
    dispUtils.noCollideSpawn(windowSurface,goals[-1],blacklist,200)

    # If the agent does not have a sight of a wide enough path to walk though to goal, then plan path
    if dispUtils.corridorOfSight(windowSurface,robots[-1],goals[-1],55,65)==False:
        pathdata[i] = planner.planPath(windowSurface,robots[i],goals[i])
        subgoalIndex.append(len(pathdata[i][1])-1)
    else:
        pathdata[i] = 0
        subgoalIndex.append(-1)

# PerformanceCheck variables
PerformanceCheckEpochCounter = 0
performanceReward = 0
inPerformanceCheck = False
prePerformanceCheckExplorationRate = 0
checkComplete = False

# run the game loop
while True:
    #Fill Screen with background colour
    windowSurface.fill(map_data[1])

    # check for the surfaceQUIT event
    for event in pygame.event.get():
        if event.type == QUIT:
            print(highest_reward)
            print(datetime.now() - startTime)
            dataUtils.plotReward(reward_file,'Culmuilated Reward Over Training')

            if performaceCheck:
                dataUtils.plotReward(performacneReward_file,'Culmuilated Reward Each Performance Check')

            dataUtils.showPlots(False)

            if AImode!=3 and stepCounter>10000:
                brain.saveModel(path+str(epoch)+'.h5')
                parameter_keys = ['epochs','steps','updateTargetNetwork','explorationRate','epsilon_decay','minibatch_size','learnStart','learningRate','discountFactor','memorySize','network_inputs','network_outputs','network_structure','current_epoch']
                parameter_values = [epochs, steps, updateTargetNetwork, explorationRate,epsilon_decay, minibatch_size, learnStart, learningRate, discountFactor, memorySize, network_inputs, network_outputs, network_structure, epoch]
                parameter_dictionary = dict(zip(parameter_keys, parameter_values))
                with open(path+str(epoch)+'.json', 'w') as outfile:
                    json.dump(parameter_dictionary, outfile)

            pygame.quit()
            sys.exit()

    #Quit sim if number of epochs is reached in training mode
    if epoch == epochs and AImode != 3:
        print(highest_reward)
        print(datetime.now() - startTime)
        dataUtils.plotReward(reward_file,'Culmuilated Reward Over Training')

        if performaceCheck:
            dataUtils.plotReward(performacneReward_file,'Culmuilated Reward Each Performance Check')

        dataUtils.showPlots(False)
        #Save the weights at the end of the sim
        brain.saveModel(path+str(epoch)+'.h5')
        parameter_keys = ['epochs','steps','updateTargetNetwork','explorationRate','epsilon_decay','minibatch_size','learnStart','learningRate','discountFactor','memorySize','network_inputs','network_outputs','network_structure','current_epoch']
        parameter_values = [epochs, steps, updateTargetNetwork, explorationRate,epsilon_decay, minibatch_size, learnStart, learningRate, discountFactor, memorySize, network_inputs, network_outputs, network_structure, epoch]
        parameter_dictionary = dict(zip(parameter_keys, parameter_values))
        with open(path+str(epoch)+'.json', 'w') as outfile:
            json.dump(parameter_dictionary, outfile)
        pygame.quit()
        sys.exit()

    # Draw all the goals and obstacles
    for g in range(len(goals)):
        dispUtils.drawGoal(windowSurface,goals[g],agentColours[g%len(agentColours)])
    dispUtils.drawObstacles(windowSurface, [0,0,0], obstacles)

    dispUtils.drawObstacles(windowSurface, map_data[2], map_data[0])

    # Simulate Each Agent
    if sum(goalsHit) < (goalPerEpoch+1)*numberOfAgents:
        for i in range(numberOfAgents):
            if goalsHit[i]<goalPerEpoch+1:
                #Generate the laser scan data for each agent and check for any collisions
                laserScanData = dispUtils.laserScan(windowSurface, [100,100,100], robots[i], agentColours, 10, [-math.pi/2,math.pi/2], 500,54)
                if dispUtils.checkCollision(laserScanData,55) == True:
                    done = True
                    isFinal = True
                #print(laserScanData)

                # Create list of other Agents
                others = robots[:i]
                others.extend(robots[(i+1):])

                # Check for collisions with other robots
                for otherRobot in others:
                    if dispUtils.getInterAgentDistace(robots[i],otherRobot)< robots[i]['size']*2:
                        done = True
                        isFinal = True

                # Draw the robot and create the new observation list
                dispUtils.drawAgent(windowSurface,agentColours[i%len(agentColours)],robots[i])

                #draw astar Pathfinding
                if pathdata[i]!=0:

                    for j in range(currentSubgoalIndex[i]+1,len(pathdata[i][1])):
                        pygame.draw.circle(windowSurface, pathColours[i%len(pathColours)], pathdata[i][1][j]['position'], 5)

                    if len(pathdata[i][0])>1:
                        pygame.draw.lines(windowSurface, pathColours[i%len(pathColours)],False, pathdata[i][0])


                if currentSubgoalIndex[i] == subgoalIndex[i]:
                    lastleg = True
                    currentTarget = goals[i]
                else:
                    lastleg = False
                    currentTarget = pathdata[i][1][currentSubgoalIndex[i]+1]

                # dispUtils.corridorOfSight(windowSurface,robots[i],currentTarget,54,108)

                newObservation = ObsNRewards.getObsevation(windowSurface,laserScanData,robots[i],currentTarget,others,lastleg)
                # print(newObservation)
                reward[i], goal_ang[i], goal_Distance[i] = ObsNRewards.getReward(windowSurface, robots[i], currentTarget, others, newObservation, action[i], goal_ang[i], goal_Distance[i])
                cumulated_reward += reward[i]
                if cumulated_reward > highest_reward:
                    highest_reward = cumulated_reward



                # Check if the previous action has lead to an ending state ie collison or goal
                if newObservation[-1] == 1 and lastleg:
                    isFinal = True
                    print(reward[i])

                # add this memory to the AI, this only happens after the AI has made a decision and observed the result
                if stepCounter > 0 and AImode != 3 and not inPerformanceCheck:
                    brain.addMemory(numpy.array(observation[i]), action[i], reward[i], numpy.array(newObservation), isFinal)


                isFinal = False

                if i == 0:
                    print(str(observation[i]) + 'action:' + str(action[i]) + 'reward:' +str(reward[i]))


                if episode_steps == steps-1:
                    done = True


                # Begin learning from the collected memories once a sufficient number have been collected
                if stepCounter >= learnStart and stepCounter%minibatch_size == 0 and AImode != 3 and not inPerformanceCheck:
                    #print('learning')
                    if stepCounter <= updateTargetNetwork:
                        brain.learnOnMiniBatch(minibatch_size, False)
                    else :
                        brain.learnOnMiniBatch(minibatch_size, True)

                #AI makes decision
                lastAction[i] = action[i]
                qValues = brain.getQValues(numpy.array(newObservation))
                action[i] = brain.selectAction(qValues, explorationRate)
                last20[i][episode_steps%20] = action[i]


                if episode_steps>20:
                    last20Odd = last20[i][::2]
                    if last20Odd[1:] == last20Odd[:-1] and (last20Odd[0]== 1 or last20Odd[0]==2 or last20Odd[0]==3) :
                        action[i] = random.randint(0,2)
                        last20[i][episode_steps%20]
                        print('infinite loop detected')
                        if not (inPerformanceCheck or AImode==3):
                            explorationRate /= epsilon_decay
                            explorationRate = min(1, explorationRate)
                            print('Epoch: ' + str(epoch) + ', Exploration Rate: ' + str(explorationRate))

                # action[i] = 1
                # print(qValues.flatten())
                # if action[i] == 3:
                #     # print(qValues.flatten())
                #
                #     action[i] = numpy.argsort(qValues.flatten())[-2]
                #     if action[i] == 3:
                #         action[i] = random.randint(0,2)
                #
                #
                # if min(laserScanData[3:6])<1.25 and (action[i] == 0 or action[i] == 3):
                #     # print(qValues.flatten())
                #
                #     action[i] = numpy.argsort(qValues.flatten())[-2]
                #     if action[i] == 0 or action[i] == 3:
                #         action[i] = random.randint(1,2)

                # if min(laserScanData[3:6])<1.25 and (action[i] == 0):
                #     # print(qValues.flatten())
                #
                #     action[i] = numpy.argsort(qValues.flatten())[-2]
                #     if action[i] == 0:
                #         action[i] = random.randint(1,3)

                # Process action
                if action[i] == 0:  # FORWARD
                    robots[i]['linearSpeed'] = forawardSpeed['linearSpeed']
                    robots[i]['angularSpeed'] = forawardSpeed['angularSpeed']
                elif action[i] == 1:  # LEFT
                    robots[i]['linearSpeed'] = leftSpeed['linearSpeed']
                    robots[i]['angularSpeed'] = leftSpeed['angularSpeed']
                elif action[i] == 2:  # RIGHT
                    robots[i]['linearSpeed'] = rightSpeed['linearSpeed']
                    robots[i]['angularSpeed'] = rightSpeed['angularSpeed']
                elif action[i] == 3:  # STOP
                    robots[i]['linearSpeed'] = stopSpeed['linearSpeed']
                    robots[i]['angularSpeed'] = stopSpeed['angularSpeed']
                # Observations are now old
                observation[i] = newObservation

                if goalsHit[i]==goalPerEpoch:
                    goalsHit[i]+=1

            else:
                dispUtils.drawAgent(windowSurface,agentColours[i%len(agentColours)],robots[i])
                robots[i]['linearSpeed'] = stopSpeed['linearSpeed']
                robots[i]['angularSpeed'] = stopSpeed['angularSpeed']
    else:
        done = True

    if done == True:
        if inPerformanceCheck or epoch%saveRate == 0:
            map_data = dispUtils.mapGeneration(windowSurface,map_type)
            windowSurface.fill(map_data[1])
            dispUtils.drawObstacles(windowSurface, [0,0,0], obstacles)
            dispUtils.drawObstacles(windowSurface, map_data[2], map_data[0])
        # If we're spawning boxs then reset that too
        if spawnBox:
            redrawBox()

        # This is for when the robots have collided or taken too many steps

        if numberOfAgents == 2:
            side = random.randint(0, 1)
            if side == 0:
                desiredPoints = [(WINDOWWIDTH/4, WINDOWHEIGHT/2),(WINDOWWIDTH*3/4, WINDOWHEIGHT/2)]
            else:
                desiredPoints = [(WINDOWWIDTH*3/4, WINDOWHEIGHT/2),(WINDOWWIDTH/4, WINDOWHEIGHT/2)]

        for i in range(numberOfAgents):
            # reset start points
            if numberOfAgents == 2:
                dispUtils.noCollideSpawnWithinRadius(windowSurface,robots[i],robots[:i],150,desiredPoints[i],100)
            else:
                dispUtils.noCollideSpawn(windowSurface,robots[i],robots[:i],200)




            # reset goals goalpoint
            blacklist = []
            blacklist.extend(robots)
            blacklist.extend(goals[:i])

            if numberOfAgents == 2:
                dispUtils.noCollideSpawnWithinRadius(windowSurface,goals[i],[],100,desiredPoints[(i+1)%2],100)
            else:
                dispUtils.noCollideSpawn(windowSurface,goals[i],blacklist,200)

            goalsHit[i] = 0

            if map_type!= '':
                los_flip = random.uniform(0, 2)
                failcount = 0
                if los_flip>=0.5:
                    while dispUtils.corridorOfSight(windowSurface,robots[i],goals[i],54,65) and failcount<1000:
                        dispUtils.noCollideSpawn(windowSurface,goals[i],blacklist,200)
                        failcount +=1


            if dispUtils.corridorOfSight(windowSurface,robots[i],goals[i],54,65) ==False:
                pathdata[i] = planner.planPath(windowSurface,robots[i],goals[i])
                subgoalIndex[i] = len(pathdata[i][1])-1
            else:
                pathdata[i] = 0
                subgoalIndex[i] = -1
            currentSubgoalIndex[i] = -1
        # If we're training then save the reward from that epoch
        if AImode != 3 and not inPerformanceCheck:
            dataUtils.save_rewards(reward_file,epoch,cumulated_reward,stepCounter)

        # Save the model if we've hit saveRate number of epochs
        if (epoch)%saveRate==0 and epoch>=100 and AImode != 3 and not inPerformanceCheck:
            #save model weights and monitoring data every 100 epochs.
            brain.saveModel(path+str(epoch)+'.h5')
            parameter_keys = ['epochs','steps','updateTargetNetwork','explorationRate','epsilon_decay','minibatch_size','learnStart','learningRate','discountFactor','memorySize','network_inputs','network_outputs','network_structure','current_epoch']
            parameter_values = [epochs, steps, updateTargetNetwork, explorationRate,epsilon_decay, minibatch_size, learnStart, learningRate, discountFactor, memorySize, network_inputs, network_outputs, network_structure, epoch]
            parameter_dictionary = dict(zip(parameter_keys, parameter_values))
            with open(path+str(epoch)+'.json', 'w') as outfile:
                json.dump(parameter_dictionary, outfile)


        if inPerformanceCheck:
            if PerformanceCheckEpochCounter >= numberOfEpochsToTest-1:
                performanceResult = performanceReward/numberOfEpochsToTest
                print('Performance Check Complete. Reward Obtained: ' + str(performanceResult))
                inPerformanceCheck = False
                dataUtils.save_rewards(performacneReward_file,epoch,performanceResult,stepCounter)
                explorationRate = prePerformanceCheckExplorationRate
                epoch += 1
                checkComplete = True
                if highest_performance < performanceResult:
                    highest_performance = performanceResult
                    brain.saveModel(path+'max.h5')
                    parameter_keys = ['epochs','steps','updateTargetNetwork','explorationRate','epsilon_decay','minibatch_size','learnStart','learningRate','discountFactor','memorySize','network_inputs','network_outputs','network_structure','current_epoch']
                    parameter_values = [epochs, steps, updateTargetNetwork, explorationRate,epsilon_decay, minibatch_size, learnStart, learningRate, discountFactor, memorySize, network_inputs, network_outputs, network_structure, epoch]
                    parameter_dictionary = dict(zip(parameter_keys, parameter_values))
                    with open(path+'max.json', 'w') as outfile:
                        json.dump(parameter_dictionary, outfile)

            PerformanceCheckEpochCounter += 1
            performanceReward += cumulated_reward

        if performaceCheck and not inPerformanceCheck and epoch%testingInterval == 0 and AImode != 3 and epoch>=startTesting:
            print('Starting Performance Check. Epoch: ' + str(epoch))
            inPerformanceCheck = True
            PerformanceCheckEpochCounter = 0
            performanceReward = 0
            prePerformanceCheckExplorationRate = explorationRate
            explorationRate  = 0.05
        else:
            if not inPerformanceCheck:
                if checkComplete:
                    checkComplete = False
                else:
                    epoch += 1
                stepCounter += 1

        episode_steps = 0
        done = False
        cumulated_reward = 0

        #Decrease exploration
        if explorationRate > 0.05:
            explorationRate *= epsilon_decay
            explorationRate = max(0.05, explorationRate)
            if epoch%200==0:
                print('Epoch: ' + str(epoch) + ', Exploration Rate: ' + str(explorationRate))
    else:
        for i in range(numberOfAgents):
            # Reset that agents goal if they reached it
            if observation[i][-1]==1 and currentSubgoalIndex[i] == subgoalIndex[i] and goalsHit[i]<goalPerEpoch:
                blacklist = []
                blacklist.extend(robots)
                blacklist.extend(goals[:i])
                blacklist.extend(goals[(i+1):])
                dispUtils.noCollideSpawn(windowSurface,goals[i],blacklist,200)
                goalsHit[i] += 1

                if map_type!= '':
                    los_flip = random.uniform(0, 2)
                    failcount = 0
                    if los_flip>=0.5:
                        while dispUtils.corridorOfSight(windowSurface,robots[i],goals[i],54,65) and failcount<1000:
                            dispUtils.noCollideSpawn(windowSurface,goals[i],blacklist,200)
                            failcount +=1

                if dispUtils.corridorOfSight(windowSurface,robots[i],goals[i],54,65) ==False:
                    pathdata[i] = planner.planPath(windowSurface,robots[i],goals[i])
                    subgoalIndex[i] = len(pathdata[i][1])-1
                else:
                    pathdata[i] = 0
                    subgoalIndex[i] = -1
                currentSubgoalIndex[i] = -1
            elif observation[i][-1]==1 and currentSubgoalIndex[i] != subgoalIndex[i]:
                currentSubgoalIndex[i] += 1
            # Update agent's position
            dispUtils.updateAgent(robots[i])

        if not inPerformanceCheck:
            stepCounter += 1

        episode_steps += 1

    if stepCounter % updateTargetNetwork == 0 and AImode != 3 and not inPerformanceCheck:
        brain.updateTargetNetwork()
        print ("Step " + str(stepCounter) + ": updating target network")

    pygame.display.update()
    mainClock.tick(updatesPerSecond * realTimeFactor)
