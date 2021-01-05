import math
import pygame
import random

def drawAgent(surface, agentColor, agent):

    mainColor = [agentColor[0],agentColor[1],agentColor[2]]
    lineColor = [255,255,255]

    pygame.draw.circle(surface, mainColor, agent['position'], agent['size'])
    pygame.draw.line(surface, lineColor, agent['position'], lineEndPoint(agent))

def lineEndPoint(agent):
    centre = agent['position']
    radius = agent['size']
    angle = agent['dir']

    endPointx = centre[0] + (radius * math.cos(angle))
    endPointy = centre[1] + (radius * math.sin(angle))
    return [endPointx,endPointy]

def updateAgent(agent):
    centre = agent['position']
    angle = float(agent['dir'])
    radius = agent['size']
    linSpeed = float(agent['linearSpeed'])
    angSpeed = float(agent['angularSpeed'])

    newCentreX = int(centre[0] + (linSpeed * math.cos(angle+angSpeed)))
    newCentreY = int(centre[1] + (linSpeed * math.sin(angle+angSpeed)))

    agent['position'] = [newCentreX,newCentreY]
    agent['dir'] = angle+angSpeed
    if agent['dir'] > math.pi:
        agent['dir'] = agent['dir'] - 2*math.pi
    elif agent['dir'] < -math.pi:
        agent['dir'] = agent['dir'] + 2*math.pi



def drawGoal(surface,goal,agentColor):
    goalColor = agentColor[:]
    drawColor = agentColor[:]
    for i in range(3):
        drawColor[0] = max(0,goalColor[0] - 10 - 50*(3-i))
        drawColor[1] = max(0,goalColor[1] - 10 - 50*(3-i))
        drawColor[2] = max(0,goalColor[2] - 10 - 50*(3-i))
        pygame.draw.circle(surface, drawColor, goal['position'], goal['size']/(i+1))

def drawObstacles(surface, agentColor, obsList):
    for shape in obsList:
        pygame.draw.polygon(surface, agentColor, shape)

def laserScan(surface, scanColour, agent, blackListColours, divisions, AngRange, scanDis, minScanRange):
    laserScanData = []
    centre = agent['position']
    divisions = divisions - 1
    for i in range(divisions+1):
        scanAng = AngRange[0] + agent['dir'] + i*(AngRange[1]-AngRange[0])/divisions
        scanEndX = int(centre[0] + (minScanRange * math.cos(scanAng)))
        scanEndY = int(centre[1] + (minScanRange * math.sin(scanAng)))
        for scanReach in range(math.floor(minScanRange/10) +1, math.floor(scanDis/10)+1):
            if scanEndX < surface.get_width() and scanEndX > 0 and scanEndY < surface.get_height() and scanEndY > 0:
                collision = False
                for colour in blackListColours:
                    if isColor(surface.get_at((scanEndX,scanEndY))[:3],colour):
                        collision = True
                        break
                if isColor(surface.get_at((scanEndX,scanEndY))[:3],[0,0,0]) or collision:
                    break
                else:
                    scanEndX = int(centre[0] + (float(scanReach)*10 * math.cos(scanAng)))
                    scanEndY = int(centre[1] + (float(scanReach)*10 * math.sin(scanAng)))
            else:
                break

        pygame.draw.line(surface, scanColour, agent['position'],[scanEndX,scanEndY])
        laserScanData.append(round((math.hypot(scanEndX - centre[0], scanEndY - centre[1]))/100,1))
    return laserScanData

def lineOfSight(surface,agent,otherAgent,minScanRange):
    visible = True
    centre = agent['position']
    focus = otherAgent['position']
    distance = math.hypot(focus[0] - centre[0], focus[1] - centre[1])
    sightAng = getInterAgentTheta(agent,otherAgent)
    visibleDistance = minScanRange
    scanEndX = int(float(centre[0]) +visibleDistance)
    scanEndY = int(float(centre[1]) +visibleDistance)
    while visibleDistance <= distance:
        scanEndX = int(float(centre[0]) + (float(visibleDistance) * math.cos(sightAng)))
        scanEndY = int(float(centre[1]) + (float(visibleDistance) * math.sin(sightAng)))
        if isColor(surfaceColour(surface,(scanEndX,scanEndY)),[0,0,0]):
            visible = False
            # pygame.draw.line(surface, [200,100,0], agent['position'],[scanEndX,scanEndY])
            # print('goal not Visible: ' + str(visibleDistance) + ' distance: ' +  str(round(distance,2)) + ' Angle: ' +str(round(sightAng,2)) + ' Goal: ' +str(otherAgent['position']) + ' endPoint: ' +  str([scanEndX,scanEndY]))
            # pygame.display.update()
            # raw_input("Press Enter to continue...")
            break
        else:
            visibleDistance += 10
    #print('goal Visible: ' + str(visible))
    #pygame.draw.line(surface, [200,100,0], agent['position'],[scanEndX,scanEndY])
    return visible

def corridorOfSight(surface,agent,otherAgent,minScanRange,corridoorWidth):
    visible = lineOfSight(surface,agent,otherAgent,minScanRange)
    if visible:
        sightAng = getInterAgentTheta(agent,otherAgent)
        criticalAngs = [sightAng+math.pi/2,sightAng-math.pi/2]
        agentCorridorEnd = [agent['position'][:],agent['position'][:]]
        focusCorridorEnd = [otherAgent['position'][:],otherAgent['position'][:]]

        for i in range(len(agentCorridorEnd)):
            agentCorridorEnd[i][0] = agentCorridorEnd[i][0] + corridoorWidth*math.cos(criticalAngs[i])
            agentCorridorEnd[i][1] = agentCorridorEnd[i][1] + corridoorWidth*math.sin(criticalAngs[i])
            focusCorridorEnd[i][0] = focusCorridorEnd[i][0] + corridoorWidth*math.cos(criticalAngs[i])
            focusCorridorEnd[i][1] = focusCorridorEnd[i][1] + corridoorWidth*math.sin(criticalAngs[i])

        for i in range(len(agentCorridorEnd)):
            end1 = {'position': agentCorridorEnd[i]}
            end2 = {'position': focusCorridorEnd[i]}
            visible = visible and lineOfSight(surface,end1,end2,minScanRange)
            if not visible:
                break
            # else:
            #     pygame.draw.line(surface, [200,100,0], agentCorridorEnd[i],focusCorridorEnd[i])

    return visible

def checkCollision(laserScanData,minScanRange):
    for scan in laserScanData:
        if scan <= float(minScanRange)/100:
            return True
    return False

def surfaceColour(surface,pos):
    if pos[0] < surface.get_width() and pos[0] > 0 and pos[1] < surface.get_height() and pos[1] > 0:
        colour = surface.get_at(pos)[:3]
    else:
        colour = [0,0,0]
    return colour

def isColor(RGB1,RGB2):
    if(RGB1[0] == RGB2[0] and RGB1[1] == RGB2[1] and RGB1[2] == RGB2[2]):
        return True
    else:
        return False

def getInterAgentDistace(agent1,agent2):
    position1 = agent1['position']
    position2 = agent2['position']

    distance = math.hypot(position1[0] - position2[0], position1[1] - position2[1])
    return distance

def getInterAgentTheta(agent1,agent2):
    position1 = agent1['position']
    position2 = agent2['position']

    theta = math.atan2(position2[1] - position1[1],position2[0] - position1[0])
    return theta

def noCollideSpawnCheck(xPos, yPos, blackListOjects, safeDistance):
    safe = True
    for obj in blackListOjects:
        position = obj['position']
        if math.hypot(xPos - position[0], yPos - position[1]) < safeDistance:
            safe = False
    return safe

def centreRecttoPoly(objDat):
    position = objDat['position']
    width = objDat['width']
    height = objDat['height']

    point1 = [position[0] - width/2, position[1] - height/2]
    point2 = [position[0] + width/2, position[1] - height/2]
    point3 = [position[0] + width/2, position[1] + height/2]
    point4 = [position[0] - width/2, position[1] + height/2]

    return [point1,point2,point3,point4]

def cornerRecttoPoly(objDat):
    position = objDat['position']
    width = objDat['width']
    height = objDat['height']

    point1 = [position[0], position[1]]
    point2 = [position[0] + width, position[1]]
    point3 = [position[0] + width, position[1] + height]
    point4 = [position[0], position[1] + height]

    return [point1,point2,point3,point4]

def blackWithinRadius(surface, xpos, ypos, radius):
    containsBlack = False
    checkRadius = radius
    checkPoints = 20

    if not isColor(surfaceColour(surface,(xpos,ypos)),[0,0,0]):
        for i in range(checkPoints):
            Ang = (2*math.pi/float(checkPoints)) * i
            checkX = int(xpos + (float(radius) * math.cos(Ang)))
            checkY = int(ypos+ (float(radius) * math.sin(Ang)))
            if isColor(surfaceColour(surface,(checkX,checkY)),[0,0,0]):
                containsBlack = True
                break
        if not containsBlack:
            checkRadius = radius*2/3
            for i in range(checkPoints):
                Ang = (2*math.pi/float(checkPoints)) * i
                checkX = int(xpos + (float(radius) * math.cos(Ang)))
                checkY = int(ypos+ (float(radius) * math.sin(Ang)))
                if isColor(surfaceColour(surface,(checkX,checkY)),[0,0,0]):
                    containsBlack = True
                    break
        if not containsBlack:
            checkRadius = radius/3
            for i in range(checkPoints):
                Ang = (2*math.pi/float(checkPoints)) * i
                checkX = int(xpos + (float(radius) * math.cos(Ang)))
                checkY = int(ypos+ (float(radius) * math.sin(Ang)))
                if isColor(surfaceColour(surface,(checkX,checkY)),[0,0,0]):
                    containsBlack = True
                    break
    else:
        containsBlack = True

    return containsBlack

def noCollideSpawn(surface, obj, blacklist,distance):
    maxX = surface.get_width() - 200
    maxY = surface.get_height() - 200


    objX = int(random.uniform(200, maxX))
    objY = int(random.uniform(200, maxY))
    tryDist = distance
    attemptCounter = 0
    maxAttempts = 1000
    while not noCollideSpawnCheck(objX,objY,blacklist,tryDist) or blackWithinRadius(surface, objX, objY, 100) or objX<100 or objY<100 or objX>surface.get_width()-100 or objY>surface.get_height()-100:
        objX = int(random.uniform(200, maxX))
        objY = int(random.uniform(200, maxY))
        attemptCounter += 1
        if attemptCounter > maxAttempts:
            print(str(tryDist))
            tryDist = (0.75) * float(tryDist)
            print('Error: Tried ' + str(maxAttempts) + ' spawn locations, reducing safe distance to ' + str(tryDist))
            attemptCounter = 0
            if tryDist <= 50:
                print('failed to find good spawn point')
                break

    obj['position'] = [objX,objY]


def noCollideSpawnWithinRadius(surface, obj, blacklist,distance,desiredPoint,spawnRadius):
    sp = spawnRadius
    objX = int(random.uniform(desiredPoint[0]-spawnRadius, desiredPoint[0]+spawnRadius))
    objY = int(random.uniform(desiredPoint[1]-spawnRadius, desiredPoint[1]+spawnRadius))
    tryDist = distance
    attemptCounter = 0
    maxAttempts = 100
    while not noCollideSpawnCheck(objX,objY,blacklist,tryDist) or blackWithinRadius(surface, objX, objY, tryDist) or objX<100 or objY<100 or objX>surface.get_width()-100 or objY>surface.get_height()-100:
        objX = int(random.uniform(desiredPoint[0]-spawnRadius, desiredPoint[0]+spawnRadius))
        objY = int(random.uniform(desiredPoint[1]-spawnRadius, desiredPoint[1]+spawnRadius))
        attemptCounter += 1
        if attemptCounter > maxAttempts:
            # print(str(spawnRadius))
            spawnRadius = (1.25) * float(spawnRadius)
            # print('Error: Tried ' + str(maxAttempts) + ' spawn locations, increasing spawn radius to ' + str(spawnRadius))
            attemptCounter = 0
            if spawnRadius >= 200:
                tryDist = (0.75) * float(tryDist)
                spawnRadius = sp
                if tryDist <= 50:
                    print('failed to find good spawn point')
                    break

    obj['position'] = [objX,objY]
