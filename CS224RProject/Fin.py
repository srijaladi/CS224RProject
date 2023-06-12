import torchimport torch.nn as nnimport randomimport numpy as npimport DQNBasefrom DQNBase import DQNimport State2048Filefrom State2048File import State2048import Conv_Statefrom Conv_State import CONV_STATEFOLDER_PREFIX = "CL/"TOTAL_SQUARES = 16TOTAL_OPTIONS = 20TOTAL_ACTIONS = 4SEED = 42np.random.seed(SEED)random.seed(SEED)torch.random.manual_seed(SEED)torch.manual_seed(SEED)def reward_function(state, new_max, non_term, valid_move):    if not(valid_move) or not(non_term):        return -1000    elif not(new_max):        return -1    else:        return 1000    iterations_per = 2000SAMPLE_SIZE = 64start_lr = 1e-4epsilon = 1GAMMA = 1.0model_save_freq = 100eps_decay_rate = 0.8state_version = "base"state_conv = {"old" : 4 * 4 * TOTAL_OPTIONS, "base" : 4 * 4 * 2 * 3, "each" : 4 * 4 * 5, "alt" : 4}ENV = State2048("Log", reward_function)ENCODER = CONV_STATE(state_version, ENV)IN_DIM = int(state_conv[state_version])OUT_DIM = TOTAL_ACTIONSlayers = [nn.Linear(IN_DIM,128), nn.ReLU(), nn.Linear(128,64), nn.ReLU(), nn.Linear(64,32), nn.ReLU(), nn.Linear(32,16), nn.ReLU(), nn.Linear(16,8), nn.ReLU(), nn.Linear(8,OUT_DIM)]DQNetwork = DQN(layers, start_lr, TOTAL_ACTIONS)#DQNetwork.load_state_dict(torch.load("CL_model_params.txt"))def greedy_action(model, state):    action_values = model(state)    action = torch.argmax(action_values)    return int(action), action_values[action]def greedy_action_full(all_models, state):    action_values = np.zeros(4)    for action in range(4):        action_values[action] = all_models[action](state)    action = np.argmax(action_values)    return int(action), action_values[action]def buffer_train(D, episode_samples, g, model):    sample = random.sample(D, min(len(D),episode_samples))    loss = 0    for episode in sample:        for s,a,r,s_next,n_t,v_m in episode[::-1]:            tv = r            if n_t and v_m: tv += g * greedy_action(model, s_next)[1].item()            loss += model.backprop_single(s, a, tv)    avg_loss = loss/len(sample)    return avg_lossvalid_move_rate = []action_freq = np.zeros(4)avg_losses = []total_moves = []total_score = []highest_tile = []D = []upto = 100allowed_moves = 1000for target in range(4,12):    for iteration in range(1,iterations_per+1):        moves, real_moves, valid_moves, trains, loss = 0, 0, 0, 0, 0        non_term, valid_move = True, True                epsilon *= eps_decay_rate                state_np = ENV.initialize_state()                episode = []                while non_term and valid_move and moves < allowed_moves and np.amax(state_np) < target:            state = ENCODER.convert(state_np, target)                        action = -1            rand = False            if random.uniform(0,1) <= epsilon:                action = random.choice([0,1,2,3])                rand = True            else:                action, predicted_action_value = greedy_action(DQNetwork, state)                        state_next_np, non_term, valid_move = ENV.transition(state_np, action)            new_max = np.amax(state_np) != np.amax(state_next_np)            state_next = ENCODER.convert(state_next_np, target)            reward = ENV.state_score(state_next_np, new_max, non_term, valid_move)                        if not(rand): real_moves += 1            moves += 1            valid_moves += (not(rand) and valid_move)            if not(rand): action_freq[action] += 1                        episode.append((state,action,reward,state_next,non_term,valid_move))                        state_np = np.copy(state_next_np)                    D.append(episode)        # HER EPISODIC MODIFICATION        fin = episode[-1][3]        bests = [torch.amax(fin[:8,i,j]) for i in range(4) for j in range(4)]        bests = sorted(list(set(sorted(bests))))        ep2 = episode.copy()        for i in range(len(ep2)):            state,action,reward,state_next,non_term,valid_move = ep2[i]            cb = max([torch.amax(state[:8,i,j]) for i in range(4) for j in range(4)])            if cb >= bests[-1]:                continue            above = [i for i in bests if i > cb]            idx = np.random.randint(0,len(above))            nb = above[idx]            state[8,:,:] = nb            state_next[8,:,:] = nb            ep2[i] = (state,action,reward,state_next,non_term,valid_move)        D,append(ep2)                            avg_loss = buffer_train(D, SAMPLE_SIZE, GAMMA, DQNetwork)                    ##### PURE LOGGING #####        if iteration%100 == 0:            print(iteration)                    if iteration%model_save_freq:            torch.save(DQNetwork.state_dict(), FOLDER_PREFIX + "model_params.txt")                    avg_losses.append(avg_loss)        if real_moves: valid_move_rate.append(valid_moves/real_moves)        else: valid_move_rate.append(0)        total_moves.append(moves)        total_score.append(np.sum(state_np))        highest_tile.append(int(2 ** (np.amax(state_np))))                np.savetxt(FOLDER_PREFIX + "valid_move_rate.txt", np.array(valid_move_rate))        np.savetxt(FOLDER_PREFIX + "action_freq.txt", action_freq)        np.savetxt(FOLDER_PREFIX + "avg_losses.txt", np.array(avg_losses))        np.savetxt(FOLDER_PREFIX + "total_moves.txt", np.array(total_moves))        np.savetxt(FOLDER_PREFIX + "total_score.txt", np.array(total_score))        np.savetxt(FOLDER_PREFIX + "highest_tile.txt", np.array(highest_tile))              