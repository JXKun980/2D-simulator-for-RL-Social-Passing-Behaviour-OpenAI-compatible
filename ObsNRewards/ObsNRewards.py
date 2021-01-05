import math

import dispUtils

# Observation: [10*laser_scan, distance_to_goal, speed, (o_dist, o_angle, o_speed, o_facing), (o_dist, o_angle, o_speed, o_facing), angle_to_goal, goal_active, goal_reached]

# The State the robot will observe
def getObsevation(surface,LS,agent,target,otherAgents,goalActive):
    newObs = []
    newObs.extend(LS) #Add the laserscan data
    newObs.append(round(dispUtils.getInterAgentDistace(agent,target)/100,2)) #Distance to goal

    # #The robot knows if it can see its goal
    # if dispUtils.lineOfSight(surface,agent,target,54):
    #     visibleGoal = 1
    # else:
    #     visibleGoal = 0
    #
    # newObs.append(visibleGoal)

    # The angle its facing
    if agent['dir'] < 0:
        obsAngle = agent['dir'] + 2*math.pi
    else:
        obsAngle = agent['dir']

    # Our own speed
    newObs.append(round(float(agent['linearSpeed'])/100,1))

    closetAgentsID = [0,0]
    closestAgentsDist = [1000000,1000000]
    IDcounter = 0
    closestAgents = []
    for otherAgent in otherAgents:
        obsRelAngle = dispUtils.getInterAgentTheta(agent,otherAgent)

        relAngleDif = obsRelAngle - obsAngle

        if relAngleDif > math.pi:
            relAngleDif = relAngleDif-2*math.pi
        elif relAngleDif < -math.pi:
            relAngleDif = relAngleDif+2*math.pi


        if relAngleDif< math.pi/2 and relAngleDif> -math.pi/2:
            if dispUtils.getInterAgentDistace(agent,otherAgent)<=closestAgentsDist[0]:
                closestAgentsDist[1] = closestAgentsDist[0]
                closetAgentsID[1] = closetAgentsID[0]
                closestAgentsDist[0] = dispUtils.getInterAgentDistace(agent,otherAgent)
                closetAgentsID[0] = IDcounter
            elif dispUtils.getInterAgentDistace(agent,otherAgent)<=closestAgentsDist[1]:
                closestAgentsDist[1] = dispUtils.getInterAgentDistace(agent,otherAgent)
                closetAgentsID[1] = IDcounter
        IDcounter += 1

    if len(otherAgents) == 0:
        newObs.append(round(500/100,2))
        newObs.append(round(abs(math.degrees(0)),1))
        newObs.append(0)
        newObs.append(round(abs(math.degrees(0)),1))
        newObs.append(round(500/100,2))
        newObs.append(round(abs(math.degrees(0)),1))
        newObs.append(0)
        newObs.append(round(abs(math.degrees(0)),1))
    elif len(otherAgents) == 1:
        closestAgents = otherAgents[:]
    else:
        closestAgents = [otherAgents[closetAgentsID[0]],otherAgents[closetAgentsID[1]]]


    for otherAgent in closestAgents:
        #distance to nearest 2 other robot
        if dispUtils.getInterAgentDistace(agent,otherAgent) <= 500:
            newObs.append(round(dispUtils.getInterAgentDistace(agent,otherAgent)/100,2))
            # The angle between the robot and the other robot relative to the front of robot
            obsRelAngle = dispUtils.getInterAgentTheta(agent,otherAgent)

            relAngleDif = obsRelAngle - obsAngle

            if relAngleDif > math.pi:
                relAngleDif = relAngleDif-2*math.pi
            elif relAngleDif < -math.pi:
                relAngleDif = relAngleDif+2*math.pi

            newObs.append(round(math.degrees(relAngleDif),1))

            #speed of other robot
            newObs.append(round(float(otherAgent['linearSpeed'])/100,1))
            #orientation of other robot relative to front of robot
            obsRelAngle = otherAgent['dir']

            relAngleDif = obsRelAngle - obsAngle

            if relAngleDif > math.pi:
                relAngleDif = relAngleDif-2*math.pi
            elif relAngleDif < -math.pi:
                relAngleDif = relAngleDif+2*math.pi

            newObs.append(round(math.degrees(relAngleDif),1))

        else:
            newObs.append(round(500/100,2))
            newObs.append(round(abs(math.degrees(0)),1))
            newObs.append(0)
            newObs.append(round(abs(math.degrees(0)),1))


    if len(otherAgents) == 1:
        newObs.append(round(500/100,2))
        newObs.append(round(abs(math.degrees(0)),1))
        newObs.append(0)
        newObs.append(round(abs(math.degrees(0)),1))

    #newObs.append(round(math.degrees(obsAngle),1))

    # The angle between the robot and the goal relative to the world
    obsRelAngle = dispUtils.getInterAgentTheta(agent,target)
    #newObs.append(round(abs(math.degrees(obsRelAngle)),1))

    # The angle between the robot and the goal relative to the front of the robot
    relAngleDif = obsRelAngle - obsAngle

    if relAngleDif > math.pi:
        relAngleDif = relAngleDif-2*math.pi
    elif relAngleDif < -math.pi:
        relAngleDif = relAngleDif+2*math.pi

    newObs.append(round(math.degrees(relAngleDif),1))

    if goalActive:
        active = 1
    else:
        active = 0

    newObs.append(active)

    # If the robot is at the goal or not
    if goalActive:
        goalrad = 50
    else:
        goalrad = 50

    if dispUtils.getInterAgentDistace(agent,target) < goalrad:
        arrived = 1
    else:
        arrived = 0

    newObs.append(arrived)
    return newObs

def getReward(surface, agent, target, otherAgents, observation, action, prevtargetAng, prevtargetDist):
    #REWARD FUNCTION
    # Determine the reward for the previous action taken
    # Reward for movement
    reward = 0
    if action == 0:  # FORWARD
        # if min(observation[2:7])<1.25:
        #     reward -= 10
        # else:
        #     reward += 1
        reward += 0
    elif action == 1:  # LEFT
        # if min(observation[0:3])<1.25:
        #     reward -= 10
        reward += 0
    elif action == 2:  # RIGHT
        # if min(observation[6:9])<1.25:
        #     reward -= 10
        reward += 0
    elif action == 3:  # STOP
        if min(observation[0:9])<2:
            reward -= 0
        else:
            reward -= 1

    # if min(observation[0:9])<1.5:
    #     reward -= 20

    otherAgentDataIndex = [12,16]

    #check if another agent is in the way

    pathClear = True
    blockingDist = 100
    for i in otherAgentDataIndex:
        correctAng = abs(math.atan(25/(dispUtils.getInterAgentDistace(agent,target)+1)))
        relAngleDif = math.radians(observation[i+1]) - math.radians(observation[-3])

        if relAngleDif > math.pi:
            relAngleDif = relAngleDif-2*math.pi
        elif relAngleDif < -math.pi:
            relAngleDif = relAngleDif+2*math.pi



        # if relAngleDif > -correctAng*2 and relAngleDif < correctAng*2:
        #     if observation[i] < dispUtils.getInterAgentDistace(agent,target):
        #         pathClear = False
        if observation[i]*math.sin(relAngleDif) > -0.5 and observation[i]*math.sin(relAngleDif) < 0.5:
            if observation[i]*math.cos(relAngleDif) > 0 and observation[i]*math.cos(relAngleDif) < dispUtils.getInterAgentDistace(agent,target)/100:
                pathClear = False
                if observation[i]*math.cos(relAngleDif) < blockingDist:
                    blockingDist = observation[i]*math.cos(relAngleDif)
                # print("path not Clear" + str(observation[i]*math.cos(relAngleDif))+ str(dispUtils.getInterAgentDistace(agent,target)/100))

    # if pathClear:
        # Reward for facing the goal or moving toward facing the goal
        # correctAng = abs(math.degrees(math.atan(25/(dispUtils.getInterAgentDistace(agent,target)+1))))
        # if correctAng < 2:
        #     correctAng = 2

        # if observation[-3] <= correctAng and observation[-3] >= -correctAng:
        #     if action != 3 and action != 2 and action != 1:
        #         reward+=3
        # else:
        #     if observation[-3] > 0 and prevtargetAng>=0:
        #         if prevtargetAng > observation[-3] or observation[-3] < correctAng:
        #             reward+=1
        #         else:
        #             reward-=3
        #     elif observation[-3] < 0 and prevtargetAng <= 0:
        #         if prevtargetAng < observation[-3] or observation[-3] > -correctAng:
        #             reward+=1
        #         else:
        #             reward-=3
        #     else:
        #         reward-=3
        # prevtargetAng = observation[-3]
    # else:
    #     correctAng = abs(math.degrees(math.atan(25/blockingDist)))
    #     if correctAng < 2:
    #         correctAng = 2
    #
    #
    #     if (observation[-3] >= correctAng and observation[-3] <= correctAng+45):
    #         if action != 3 and action != 2 and action != 1:
    #             reward+=2
    #     elif (observation[-3] <= -correctAng and observation[-3] >= -(correctAng+45)):
    #         if action != 3:
    #             reward-=0
    #     else:
    #         if observation[-3] > 0 and prevtargetAng >= 0:
    #             if observation[-3] < correctAng and prevtargetAng < observation[-3]:
    #                 reward+=1
    #             elif observation[-3] > correctAng+45 and prevtargetAng > observation[-3]:
    #                 reward+=1
    #             else:
    #                 reward-=3
    #         elif observation[-3] < 0 and prevtargetAng <= 0:
    #             if observation[-3] > -correctAng and prevtargetAng < observation[-3]:
    #                 reward+=1
    #             elif observation[-3] < -correctAng-45 and prevtargetAng < observation[-3]:
    #                 reward+=1
    #             else:
    #                 reward-=3
    #         else:
    #             reward-=3
    #
    #     prevtargetAng = observation[-3]


    # Agent to Agent reward
    # Dont get too close
    for oi in range(len(otherAgents)):
        # Punish collision
        if dispUtils.getInterAgentDistace(agent,otherAgents[oi])< agent['size']*2.5:
            reward-=100

    for i in otherAgentDataIndex:
        #Punish Distance to Other Agents
        if observation[i]< 1.5:
            reward-=5
            if observation[i] < 1:
                reward-= 5 + (1-observation[i]/1)*5

        if observation[i+2] > 0 and observation[11]>0 and observation[i]<5 :
            otherAgentHeading = math.radians(observation[i+3])
            relativeAngToOtherAgent = math.radians(observation[i+1])
            relativeAngFromOtherAgent = relativeAngToOtherAgent - math.pi - otherAgentHeading

            if relativeAngFromOtherAgent > math.pi:
                relativeAngFromOtherAgent = relAngleDif-2*math.pi
            elif relativeAngFromOtherAgent < -math.pi:
                relativeAngFromOtherAgent = relAngleDif+2*math.pi

            if otherAgentHeading<= math.pi/4 and otherAgentHeading>= -math.pi/4 :
                if relativeAngFromOtherAgent > - 3*math.pi/4  and relativeAngFromOtherAgent < -math.pi/2:
                    reward-=10
            # elif otherAgentHeading< 3 * math.pi/4 and otherAgentHeading> math.pi/4:
            #     if relativeAngFromOtherAgent < math.pi/4 and relativeAngFromOtherAgent > -math.pi/4:
            #         reward-=0.5
            # elif otherAgentHeading> -3 * math.pi/4 and otherAgentHeading< -math.pi/4:
            #     if relativeAngFromOtherAgent > -math.pi/4 and relativeAngFromOtherAgent < math.pi/4:
            #         reward-=0.5
            elif otherAgentHeading<= -3 * math.pi/4 or otherAgentHeading>= 3*math.pi/4:
                if  relativeAngFromOtherAgent > -math.pi/2 and relativeAngFromOtherAgent < 0:
                    reward-=10



                # if (relativeAngToOtherAgent < 0 and relativeAngToOtherAgent > -math.pi/2) or (relativeAngToOtherAgent >= 0 and observation[i]*math.sin(relativeAngToOtherAgent)<0.7):
                #     reward-=1



        # else:
        #     if observation[i+3]<= math.pi/4 and observation[i+3]>= -math.pi/4 :
        #         if observation[i+1] > math.pi/4 and observation[i+1] < math.pi/2:
        #             reward-=1

    # Goal and Obstacle related Reward
    if observation[-1]==1:
        reward += 100 #at Goal
    elif dispUtils.checkCollision(observation[0:9],55) == True:
        reward -= 100 #collide with obstacle
    # elif dispUtils.getInterAgentDistace(agent,target) < 100:
    #     reward -= 0
    # elif dispUtils.getInterAgentDistace(agent,target) < prevtargetDist - 5:
    #     reward += 6 # Closer to goal
    # elif dispUtils.getInterAgentDistace(agent,target) < prevtargetDist + 5 and dispUtils.getInterAgentDistace(agent,target) > prevtargetDist - 5:
    #     reward -= 0
    # else:
    #     reward -= 6


    # prevtargetDist = dispUtils.getInterAgentDistace(agent,target)

    # Punnish driving foward close to walls
    # for scan in observation[0:9]:
    #     if scan <= 1.5:
    #         reward-=0.5
    #         if scan <= 1:
    #             reward-= 0.2 + ((1-scan)/1)*0.2
    #             if scan <= 0.65:
    #                 reward-= 2

    return reward, prevtargetAng, prevtargetDist
