import numpy as np


def batch_iter(tensor, batch_size, shuffle=False):
    batches_count = tensor.shape[0] // batch_size

    if shuffle:
        shuffle_indices = np.random.permutation(np.arange(tensor.shape[0]))
        data = tensor[shuffle_indices]
    else:
        data = tensor

    neg_shuffle_indices = np.random.permutation(np.arange(tensor.shape[0]))
    negative_data = tensor[neg_shuffle_indices]

    for batch_num in range(batches_count):
        start_index = batch_num * batch_size
        end_index = min((batch_num + 1)*batch_size, tensor.shape[0])
        yield data[start_index:end_index]


def neg_sampling_iter(tensor, batch_size, count, seed=None):
    batches_count = tensor.shape[0] // batch_size
    trials = 0
    np.random.seed(seed)
    shuffle_indices = np.random.permutation(np.arange(tensor.shape[0]))
    #print("shuffle indices")
    #print(shuffle_indices)
    
    data = tensor[shuffle_indices]
    #print(data)
    #print(data.shape)
    #j = input('Waiting')
    for batch_num in range(batches_count):
        trials += 1
        start_index = batch_num * batch_size
        end_index = min((batch_num + 1)*batch_size, tensor.shape[0])
        if trials > count:
            return
        else:
            #print("printing data shape")
            #print(data[start_index:end_index].shape)
            yield data[start_index:end_index]


def new_neg_sampling_iter(tensor, batch_size, count, seed=None):
    batches_count = tensor.shape[0] // batch_size
    neg_sample_data = list()
    trials = 0
    np.random.seed(seed)
    shuffle_indices = np.random.permutation(np.arange(tensor.shape[0]))
    #print("shuffle indices")
    #print(shuffle_indices)
    
    data = tensor[shuffle_indices]
    #j = input('Waiting')
    #print(data)
    for batch_num in range(batches_count):
        trials += 1
        start_index = batch_num * batch_size
        end_index = min((batch_num + 1)*batch_size, tensor.shape[0])
        if trials > count:
            return neg_sample_data
        else:
            #print("printing data shape")
            #print(data[start_index:end_index].shape)
            #yield data[start_index:end_index]
            neg_sample_data.append(data[start_index:end_index])

    return neg_sample_data


