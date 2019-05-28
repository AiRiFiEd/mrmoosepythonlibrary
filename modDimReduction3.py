# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 22:44:31 2018

@author: LIM YUAN QING
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class PCA():
    def __init__(self, data, variance_threshold = 95):
        if isinstance(data, pd.DataFrame):
            self.__np_data = data.values
        elif isinstance(data, np.ndarray):
            self.__np_data = data
        elif isinstance(data, list):
            self.__np_data = np.array(data)
            
        self.__covariance = np.cov(self.__np_data,rowvar=False)
        self.__eigenvalues, self.__eigenvectors = np.linalg.eig(self.__covariance)
        idx = self.__eigenvalues.argsort()[::-1]
        self.__eigenvalues = self.__eigenvalues[idx]
        self.__eigenvectors = self.__eigenvectors[:, idx]
        
        self.__cum_variance_explained = 100*self.__eigenvalues.cumsum()/self.__eigenvalues.sum()
        self.__num_of_components = len(self.__cum_variance_explained) - (self.__cum_variance_explained>=variance_threshold).sum() + 1        
        self.__variance_explained = self.__cum_variance_explained[self.__num_of_components]
        
    def visualise(self):
        
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(16,8))
        axes[0].plot(np.arange(0,len(self.__eigenvalues))+1, 
                     self.__eigenvalues, 
                     linewidth=2, 
                     color='red',
                     marker='o', 
                     markersize=7)
        axes[0].set_title('Scree Plot', fontsize =20)
        axes[0].set_xlabel('component', fontsize=14)
        axes[0].set_xticks(np.arange(1, len(self.__eigenvalues)+1, 1.0))
        axes[0].set_ylabel('Eigenvalue ($\lambda$)', fontsize=14)
                
        axes[1].plot(np.arange(0,len(self.__eigenvalues))+1,
                     self.__cum_variance_explained,                      
                     linewidth=2,
                     color='blue',                     
                     marker='o',
                     markersize=7)
        axes[1].set_title('Variance Explained', fontsize=20)
        axes[1].set_xlabel('component', fontsize=14)
        axes[1].set_xticks(np.arange(1, len(self.__eigenvalues)+1, 1.0))
        axes[1].set_ylabel('%', fontsize=14)
        
        plt.tight_layout()
        plt.show()
        
    def gen_components(self, data):
        return np.matmul(data, self.__eigenvectors[:,self.__num_of_components])
    
    def __del__(self):
        pass
    
    def __str__(self):
        pass
    
    def __len__(self):
        pass
    
    def get_inputs(self):
        return self.__np_data
    
    def get_covariance_mat(self):
        return self.__covariance
    
    def get_eigen_vectors(self):
        return self.__eigenvectors
    
    def get_eigen_values(self):
        return self.__eigenvalues
    
    def get_num_of_components(self):
        return self.__num_of_components
    
    def get_variance_explained(self):
        return self.__variance_explained
    
    def set_num_of_components(self, num_of_components):
        self.__num_of_components = num_of_components
        self.__variance_explained = self.__cum_variance_explained[self.__num_of_components]