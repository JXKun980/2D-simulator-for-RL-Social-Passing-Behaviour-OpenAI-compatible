import os
import json
import csv
import matplotlib.pyplot as plt

def create_csv(directory):
    with open(directory,'w') as file:
        writer = csv.DictWriter(file, fieldnames = ['epoch','steps','reward'])
        writer.writeheader()

def save_rewards(directory,epoch,reward,steps):
    with open(directory,'a') as file:
        writer = csv.DictWriter(file, fieldnames = ['epoch','steps','reward'])
        writer.writerow({'epoch':epoch,'steps':steps,'reward':reward})

def readRewardCsv(directory):
    csvdata = {'epoch':[],'steps':[],'reward':[]}
    with open(directory, mode='r') as file:
        csv_reader = csv.DictReader(file)
        line_count = 0
        for row in csv_reader:
            csvdata['epoch'].append(float(row['epoch']))
            csvdata['steps'].append(float(row['steps']))
            csvdata['reward'].append(float(row['reward']))

    return csvdata

def plotReward(directory, title):
    data = readRewardCsv(directory)
    plt.figure()
    plt.plot(data['epoch'], data['reward'])
    plt.title(title)
    plt.ylabel('Culmulated Reward')
    plt.xlabel('Epochs')
    plt.draw()

def showPlots(interactive):
    if interactive:
        plt.ion()
    else:
        plt.show()


def loadAIParams(paramPath):
    with open(paramPath) as outfile:
        d = json.load(outfile)
        epochs = d.get('epochs')
        steps = d.get('steps')
        updateTargetNetwork = d.get('updateTargetNetwork')
        explorationRate = d.get('explorationRate')
        epsilon_decay = d.get('epsilon_decay')
        minibatch_size = d.get('minibatch_size')
        learnStart = d.get('learnStart')
        learningRate = d.get('learningRate')
        discountFactor = d.get('discountFactor')
        memorySize = d.get('memorySize')
        network_inputs = d.get('network_inputs')
        network_outputs = d.get('network_outputs')
        network_structure = d.get('network_structure')
        current_epoch = d.get('current_epoch')

    AIparams = [epochs, steps, updateTargetNetwork, explorationRate, epsilon_decay, minibatch_size, learnStart, learningRate, discountFactor, memorySize, network_inputs, network_outputs, network_structure, current_epoch]
    return AIparams
