from sklearn.datasets import make_regression
import random
from tqdm import tqdm
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from keras.models import Sequential
from keras.layers import Dense
import random
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")

class GA_Keras_Dense:
    
  def __init__(self,X_train, y_train, X_test, y_test, input_shape, num_generations=10, size_population=10, prob_cruz=0.4, prob_mut=0.5, qt_fits_max=5, max_iter=50):
    self.data = []
    self.X_train = X_train
    self.y_train = y_train
    self.X_test = X_test
    self.y_test = y_test
    self.num_generations = num_generations
    self.size_population = size_population
    self.prob_cruz = prob_cruz
    self.prob_mut = prob_mut
    self.qt_fits_max = qt_fits_max
    self.max_iter = max_iter
    self.input_shape = input_shape
    
  def gen_population(self):   
    population = [['']]*self.size_population
    optimizer = ['SGD', 'adam', 'rmsprop','Adagrad']
    activation = ['elu', 'selu', 'tanh', 'relu','linear']
    for i in range(0, self.size_population):
      population[i] = [random.randint(50, 100), random.randint(10, 50),
                       random.randint(1, 10), random.choice(activation), 
                       random.choice(activation), random.choice(activation), random.choice(optimizer), 10]# primeira camada
      #segunda, terceira, func_at_primeira, func_at_segunda, func_at_terceira, otimizador
      
      
    return population

  def set_fitness(self, population):
    for i in range(0, len(population)):
      model = Sequential()
      #print(population[i][0], population[i][1], population[i][2])
      model = Sequential([Dense(population[i][0], activation=population[i][3], input_dim=self.input_shape),
                          Dense(population[i][1], activation = population[i][4]),
                         Dense(population[i][2], activation = population[i][5]),
                         Dense(1, activation = 'linear')])
      
      model.compile(optimizer=population[i][6], loss='mae')
      
      #try:
      qt_fits=0
      mae_fits = np.zeros(self.qt_fits_max)
      while qt_fits < self.qt_fits_max:
        model.fit(self.X_train, self.y_train, epochs=self.max_iter, verbose=False)
        mae_fits[qt_fits] = model.evaluate(self.X_test, self.y_test, verbose=False)
        qt_fits = qt_fits + 1

      population[i][-1] = np.average(mae_fits)
      #except:
      #  pass
    return population

  def new_gen(self, population):

    def takeLast(elem):
      return elem[:][-1]

    def cruzamento(population, prob_cruz = self.prob_cruz):
      qt_cross = len(population[0])
      pop_ori = population

      for p in range(0, int(len(pop_ori)/2)):
        if np.random.rand() > prob_cruz:
          population[p][0:int(qt_cross/2)] = pop_ori[p][0:int(qt_cross/2)]
          population[p][int(qt_cross/2):qt_cross] = pop_ori[2*p][int(qt_cross/2):qt_cross]

      for p in range(0, int(len(pop_ori)/2)):
        if np.random.rand() > prob_cruz:
          population[p][0:int(qt_cross/2)] = pop_ori[int(p/2)][0:int(qt_cross/2)]
          population[p][int(qt_cross/2):qt_cross] = pop_ori[int(p/2)][int(qt_cross/2):qt_cross]

      return population

    def mutation(population, prob_mut = self.prob_mut):
      for p in range(0, len(population)):
        if np.random.rand() > prob_mut:
          population[p][0] = population[p][0] + np.random.randint(1,50)
          population[p][1] = population[p][1] + np.random.randint(1,50)
          population[p][2] = population[p][2] + np.random.randint(1,10)

      return population
    
    population = sorted(population, key=takeLast)
    population = cruzamento(population)
    population = mutation(population)
    population = self.set_fitness(population)

    return population
  
  def search_best(self):
    def takeLast(elem):
      return elem[:][-1]
    
    ng = 0
    population = self.gen_population()
    population = self.set_fitness(population)
    for ng in tqdm(range(0, self.num_generations)):
      population = self.new_gen(population)
      print(population)
    
    best = sorted(population, key=takeLast)[0][:]
    
    return best


if __name__ == "__main__":
  X, y = make_regression(n_features=4, n_informative=2,
                       random_state=0, shuffle=False)
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
  X_train.shape[1]
  GA_Keras_Dense(X_train, y_train, X_test, y_test, input_shape=X_train.shape[1], num_generations=5, size_population=10, prob_cruz=0.4, prob_mut=0.5, qt_fits_max=3, max_iter=100).search_best()

