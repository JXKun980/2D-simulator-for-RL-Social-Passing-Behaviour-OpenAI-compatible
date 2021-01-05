def listOfSize(size, initValue):
    ll = []
    for i in range(size):
        if isinstance(initValue, list):
            temp = initValue[:]
        else:
            temp = initValue
        ll.append(temp)
    return ll

def setAIParams(paramsList):
    epochs = paramsList[0]
    steps = paramsList[1]
    updateTargetNetwork = paramsList[2]
    explorationRate = paramsList[3]
    epsilon_decay = paramsList[4]
    minibatch_size = paramsList[5]
    learnStart = paramsList[6]
    learningRate = paramsList[7]
    discountFactor = paramsList[8]
    memorySize = paramsList[9]
    network_inputs = paramsList[10]
    network_outputs = paramsList[11]
    network_structure = paramsList[12]
    current_epoch = paramsList[13]
    return epochs, steps, updateTargetNetwork, explorationRate, epsilon_decay, minibatch_size, learnStart, learningRate, discountFactor, memorySize, network_inputs, network_outputs, network_structure, current_epoch
