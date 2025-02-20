import random
import numpy as np
from torchvision import datasets, transforms
# Let's read the mnist dataset


def load_mnist(path='.'):
    train_set = datasets.MNIST(path, train=True, download=True)
    x_train = train_set.data.numpy()
    _y_train = train_set.targets.numpy()
    
    test_set = datasets.MNIST(path, train=False, download=True)
    x_test = test_set.data.numpy()
    _y_test = test_set.targets.numpy()
    
    x_train = x_train.reshape((x_train.shape[0],28*28)) / 255.
    x_test = x_test.reshape((x_test.shape[0],28*28)) / 255.

    y_train = np.zeros((_y_train.shape[0], 10))
    y_train[np.arange(_y_train.shape[0]), _y_train] = 1
    
    y_test = np.zeros((_y_test.shape[0], 10))
    y_test[np.arange(_y_test.shape[0]), _y_test] = 1

    return (x_train, y_train), (x_test, y_test)

(x_train, y_train), (x_test, y_test) = load_mnist()


def sigmoid(z):
    return 1.0/(1.0+np.exp(-z))


def sigmoid_prime(z):
    # Derivative of the sigmoid
    return sigmoid(z)*(1-sigmoid(z))


class Network(object):
    def __init__(self, sizes, degrees):
        # initialize biases and weights with random normal distr.
        # weights are indexed by target node first
        assert len(sizes)-1 == len(degrees)
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.degrees = degrees
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x) 
                        for x, y in zip(sizes[:-1], sizes[1:])]

    def feedforward(self, a, connections):
        # Run the network on a batch
        a = a.T
        for b, w, c in zip(self.biases, self.weights, connections):
            a = sigmoid(np.matmul(w[:,c], a[c,:])+b)
        return a
    
    def update_mini_batch(self, mini_batch, eta, connections):
        # Update networks weights and biases by applying a single step
        # of gradient descent using backpropagation to compute the gradient.
        # The gradient is computed for a mini_batch which is as in tensorflow API.
        # eta is the learning rate      
        nabla_b, nabla_w = self.backprop(mini_batch[0].T,mini_batch[1].T, connections)
            
        #self.weights = [w[:,c]-(eta/len(mini_batch[0]))*nw 
        #                for w, nw, c in zip(self.weights, nabla_w, connections)]
        for i in range(len(self.weights)):
            self.weights[i][:,connections[i]] -= (eta/len(mini_batch[0]))*nabla_w[i]

        self.biases = [b-(eta/len(mini_batch[0]))*nb 
                       for b, nb in zip(self.biases, nabla_b)]
        
    def backprop(self, x, y, connections):
        # For a mini-batch of (x,y) return a pair of lists.
        # First contains gradients over biases, second over weights.
        gs = [x] # list to store all the gs, layer by layer
        fs = [] # list to store all the fs, layer by layer
        for b, w, c in zip(self.biases, self.weights, connections):
            gs[-1] = gs[-1][c,:]
            f = np.dot(w[:,c], gs[-1])+b
            fs.append(f)
            gs.append(sigmoid(f))
        # backward pass 
        dLdg = self.cost_derivative(gs[-1], y)
        dLdfs = []
        for w, g, c1, c2 in reversed(list(zip(self.weights, gs[1:], connections[:-1], connections[1:]))):
            dLdf = np.multiply(dLdg, np.multiply(g,1-g))
            dLdfs.append(dLdf)
            dLdg = np.matmul(w[np.ix_(c2, c1)].T, dLdf)
        
        dLdWs = [np.matmul(dLdf,g.T) for dLdf,g in zip(reversed(dLdfs),gs[:-1])]
        dLdBs = [np.sum(dLdf,axis=1).reshape(dLdf.shape[0],1) for dLdf in reversed(dLdfs)] 
        return (dLdBs,dLdWs)

    def evaluate(self, test_data, connections):
        # Count the number of correct answers for test_data
        pred = np.argmax(self.feedforward(test_data[0], connections),axis=0)
        corr = np.argmax(test_data[1],axis=1).T
        return np.mean(pred==corr)
    
    def cost_derivative(self, output_activations, y):
        return (output_activations-y) 
    
    def SGD(self, training_data, epochs, mini_batch_size, eta, test_data=None):
        x_train, y_train = training_data
        if test_data:
            x_test, y_test = test_data
        connections = [] #trzyma indeksy, które indeksy wybiore
        for size, degree in zip(self.sizes[:-1], self.degrees):
            assert degree <= size
            connections.append(random.sample(range(size), degree))
        for j in range(epochs):
            for i in range(x_train.shape[0] // mini_batch_size):
                x_mini_batch = x_train[(mini_batch_size*i):(mini_batch_size*(i+1))]
                y_mini_batch = y_train[(mini_batch_size*i):(mini_batch_size*(i+1))]
                self.update_mini_batch((x_mini_batch, y_mini_batch), eta, connections)
            if test_data:
                print("Epoch: {0}, Accuracy: {1}".format(j, self.evaluate((x_test, y_test), connections)))
            else:
                print("Epoch: {0}".format(j))


#network = Network([784,30,10])
# The above line should probably change to:
network = Network([784,100,10],[100,50])

network.SGD((x_train, y_train), epochs=30, mini_batch_size=100, eta=3.0, test_data=(x_test, y_test))
